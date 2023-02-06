import os
import pandas as pd
import requests
import sqlalchemy
from pathlib import Path
import pickle
import data_getter, data_cleaner, data_putter
from halo import Halo
from config import DATABASE_URL, HEROKU_URL

DATA_DIR = Path(__file__).parent / "data"

spinner = Halo(spinner='dots')
location = input('-Enter your location ("City, ST") to Query. Example: Chicago, IL \n')
pages = input('-How many pages of data to return? Example: 10 \n -Use 0 to specify the MAX amount of pages. (Returning MAX amount of pages may use up all your API Key requests for the day.) \n')
data = input('-Where would you like to store the data? Heroku or Local \n')
# clean = input('Delete the petfinder-data/data/backup folder? Yes/No')
# -Type Heroku to push to Heroku\'s Database \n -Type Local to store all that data locally.

def get_organizations(location) -> pd.DataFrame:
    """
    Returns
    -------
    List of all organizations listed on PetFinder within 100 miles of your city, state, formatted
    in a pandas DataFrame
    """

    token = data_getter.get_token()
    # this is where we'll save our results
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    url = "https://api.petfinder.com/v2/organizations"

    headers = {"Authorization": f"Bearer {token}"}

    params = {
        "location": location,
        "sort": "distance",
        "distance": 100,
        "limit": 100,
        "page": 1,
    }

    # make the first call, and check how many total pages there are
    response = requests.get(url, headers=headers, params=params)

    # make sure that it actually worked

    assert response.status_code == 200

    # save temp results to file, so that we have them if something goes awry
    with open(DATA_DIR / "backup" / "orgs_page_1.pkl", "wb") as f:
        pickle.dump(response.json()["organizations"], f)

    pagination = response.json()["pagination"]

    # this is how many pages we need to iterate over
    num_pages = pagination["total_pages"]

    # this is how many total orgs we expect to catch
    total_count = pagination["total_count"]

    print(f"Found {total_count} organizations in {location}")
    spinner.start()
    # start a list of orgs that we'll append to
    all_orgs = response.json()["organizations"]

    # iterate over all pages, starting with the 2nd page
    for page in range(2, num_pages + 1):
        # update params for current page
        params["page"] = page

        # make the call
        response = requests.get(url, headers=headers, params=params)

        # append orgs to master list
        all_orgs += response.json()["organizations"]

        # save temp results to file, so that we have them if something goes awry
        with open(DATA_DIR / "backup" / f"orgs_page_{page}.pkl", "wb") as f:
            pickle.dump(response.json()["organizations"], f)

    # check that we acutally got all organizations
    assert len(all_orgs) == total_count

    # convert to pandas
    df_orgs = pd.DataFrame(all_orgs)

    # save to pickle file
    spinner.stop()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Saving to a pickle and csv file in petfinder-data/data/{location.replace(', ', '_').lower()}_orgs.pkl")
    df_orgs.to_pickle(DATA_DIR / f"{location.replace(', ', '_').lower()}_orgs.pkl")
    df_orgs.to_csv(DATA_DIR / f"{location.replace(', ', '_').lower()}_orgs.csv", index=False)
    return df_orgs

def get_animals(location, pages, type="dog", status="adopted", organization=None) -> pd.DataFrame:
    """
    Parameters
    ----------
    organization: string, optional
        String of organization ID, or comma-separated list of organization IDs
    type: string, optional
        Animal type, possible options can be looked up with PetFinder's Animal Types
        endpoint
    status: string, optional
        Accepted values include adoptable, adopted, found
    max_pages: int, optional
        Maximum number of pages to query over. Default is to collect all available pages

    Returns
    -------
    List of all animals listed on PetFinder within 100 miles of your city and state, formatted
    in a pandas DataFrame. If max_pages is specified, then returns 100 * max_pages
    animals sorted by proximity to your city and state
    """

    token = data_getter.get_token()

    # this is where we'll save our results
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "backup").mkdir(parents=True, exist_ok=True)

    url = "https://api.petfinder.com/v2/animals"

    headers = {"Authorization": f"Bearer {token}"}

    params = {
        "type": type,
        "status": status,
        "organization": organization,
        "location": location,
        "sort": "distance",
        "distance": 100,
        "limit": 100,
        "page": 1,
    }

    # make the first call, and check how many total pages there are
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 400:
        quit("Invalid City - Is the spelling/syntax correct? \n Example: Indianapolis, IN")

    # make sure that it actually worked
    assert response.status_code == 200

    # save temp results to file, so that we have them if something goes awry
    with open(DATA_DIR / "backup" / f"animals_page_1.pkl", "wb") as f:
        pickle.dump(response.json()["animals"], f)

    pagination = response.json()["pagination"]

    # this is how many pages we need to iterate over
    num_pages = pagination["total_pages"]
    total_pages = pagination["total_pages"]
    # this is how many total animals we expect to catch
    total_count = pagination["total_count"]

    # Make sure user input can be converted to a Integer
    try:
        num_pages = int(pages)
        if num_pages == 0:
            num_pages = pagination["total_pages"]
        elif num_pages > pagination["total_pages"]:
            num_pages = pagination["total_pages"]
    except ValueError:
        quit("Invalid Page Count \n Could not convert data to an integer. \n Use 0 for max pages or specify a number. Example: 10")

    print(f"Found {total_count} animals in {total_pages} pages. \n Fetching data based off of your specified page count of {num_pages}, this may take a while...")
    spinner.start()
    # start a list of animals that we'll append to
    all_animals = response.json()["animals"]

    # iterate over all remaining pages, starting with the 2nd page
    # if we set a value for max number of pages, only pull that many

    for page in range(2, num_pages + 1):
        # update params for current page
        params["page"] = page

        # make the call
        response = requests.get(url, headers=headers, params=params)

        # if it was not successful, finish and save results collected so far
        if response.status_code != 200:
            print(f"Completed pages 1 - {page-1} out of the requested {num_pages}")
            break

        # save temp results to file, so that we have them if something goes awry
        with open(DATA_DIR / "backup" / f"animals_page_{page}.pkl", "wb") as f:
            pickle.dump(response.json()["animals"], f)

        # append orgs to master list
        all_animals += response.json()["animals"]

    # convert to pandas
    df_animals = pd.DataFrame(all_animals)

    # save to pickle and csv file
    spinner.stop()
    print(f"Saving to a pickle and csv file in petfinder-data/data/{location.replace(', ', '_').lower()}_animals.pkl")
    df_animals.to_pickle(DATA_DIR / f"{location.replace(', ', '_').lower()}_animals.pkl")
    df_animals.to_csv(DATA_DIR / f"{location.replace(', ', '_').lower()}_animals.csv", index=False)
    return df_animals

def data_sorter(location):
    data_spinner = Halo(text='Cleaning that data and calculating length of stay...', spinner='dots')
    data_spinner.start()
    data_file = DATA_DIR / f"{location.replace(', ', '_').lower()}_animals.pkl"
    org_data_file = DATA_DIR / f"{location.replace(', ', '_').lower()}_orgs.pkl"
    df_raw = pd.read_pickle(data_file)
    org_df_raw = pd.read_pickle(org_data_file)

    # find the org name by id
    org_info = ["id", "name"]
    org_id = ["organization_id"]
    org = data_cleaner.find_org(df_raw[org_id], org_df_raw[org_info])
    los = data_cleaner.calc_los(df_raw["published_at"], df_raw["status_changed_at"])

    # clean up the columns that are dictionaries
    breeds = data_cleaner.explode_column(df_raw["breeds"], "breed")
    colors = data_cleaner.explode_column(df_raw["colors"], "color")
    environ = data_cleaner.explode_column(df_raw["environment"], "good_with")
    attributes = data_cleaner.explode_column(df_raw["attributes"], "attribute")

    cols_as_is = ["id", "age", "gender", "size", "coat", "name"]

    df_final = pd.concat([df_raw[cols_as_is], org, los, breeds, colors, environ, attributes], axis=1)

    loc = location.split(', ')
    df_final['city'] = loc[0]
    df_final['state'] = loc[1]

    df_final.to_pickle(DATA_DIR / f"{location.replace(', ', '_').lower()}_animals_cleaned.pkl")
    spinner.stop()
    print(f"Data Cleaned at petfinder-data/data/{location.replace(', ', '_').lower()}_animals_cleaned.pkl")
    return

def get_uri(data):
    if data == "Local":
        uri = DATABASE_URL
    else:
        uri = HEROKU_URL
    if uri is not None:
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
        return uri
    else:
        raise EnvironmentError(
            """
              To run this script, you'll need to set the Heroku Postgres URI as an
              environment variable called `HEROKU_POSTGRESQL_AMBER_URL`.
            """
        )

def data_pusher(engine):
    data_pusher = Halo(text='Appending data to table. Checking for duplicate rows.', spinner='dots')
    data_pusher.start()
    file = f"{location.replace(', ', '_').lower()}_animals_cleaned.pkl"
    data_putter.append_to_table(engine, file)
    data_putter.drop_duplicate_rows(engine)
    data_pusher.stop()
    data_putter.print_row_count(engine)
    return


if __name__ == '__main__':
    get_animals(location, pages)
    get_organizations(location)
    data_sorter(location)
    uri = get_uri(data)
    engine = sqlalchemy.create_engine(uri, echo=False)
    data_pusher(engine)
    print("Data Runner Finished.")
