import streamlit as st
import pfglobals
import requests
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Pawsitive Finder", page_icon="🐇", layout="wide")

if "page_number" not in st.session_state:
    st.session_state['page_number'] = 0
if "petfinder_animals" not in st.session_state:
    st.session_state['petfinder_animals'] = []

st.title(":blue[Pawsitive Finder]")
st.markdown("Live data pulled from Petfinder. Click the Petfinder link for more detailed information!")

token = pfglobals.get_token()
headers = {"Authorization": f"Bearer {token}"}

def reset_session_state():
    st.session_state['petfinder_animals'] = []
    st.session_state['page_number'] = 0

animal_type = st.sidebar.selectbox('Select an Animal Type', ['Dog', 'Cat', 'Rabbit', 'Small & Furry', 'Horse', 'Bird', 'Scales, Fins & Other', 'Barnyard'], on_change=reset_session_state)
adoption_status = st.sidebar.selectbox('Select Adoption Status', ['Adoptable', 'Adopted', 'Found'], on_change=reset_session_state)
location = st.sidebar.text_input('Set a Location', help='Postal Code or City, State', value='Chicago, IL', placeholder='Chicago, IL', on_change=reset_session_state)
sort = st.sidebar.selectbox('Sort By', ['Recent', 'Distance'], on_change=reset_session_state, help='Within 500 miles')
sorted = 'recent' if sort == 'Recent' else 'distance'
url = "https://api.petfinder.com/v2/animals"
params = {
    "type": f"{animal_type}",
    "status": f"{adoption_status}",
    "organization": None,
    "location": f"{location}",
    "sort": {sorted},
    "distance": 500,
    "limit": 100,
    "page": 1,
}

if st.session_state['petfinder_animals'] == []:
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            st.session_state['petfinder_animals'] = []
        else:
            st.session_state['petfinder_animals'] = response.json()
    except:
        st.session_state['petfinder_animals'] = []

page_number = st.session_state['page_number']
col1, col2 = st.columns([1, 2])

if st.session_state['petfinder_animals'] == []:
    st.divider()
    st.markdown(f"No Results for :green[{animal_type}] Animal Type with adoption status of :blue[{adoption_status}] in :orange[{location}]")
elif st.session_state['petfinder_animals']['animals'] == []:
    st.divider()
    st.markdown(f"No Results for :green[{animal_type}] Animal Type with adoption status of :blue[{adoption_status}] in :orange[{location}]")
else:
    animals = [animal for animal in st.session_state['petfinder_animals']["animals"]]
    last_page = len(animals)
    link = animals[page_number]["url"]
    age = animals[page_number]["age"]
    gender = animals[page_number]["gender"]
    n = animals[page_number]["name"]
    name = n.replace("$", "")
    breed = animals[page_number]["breeds"]["primary"]
    spayed_neutered = animals[page_number]["attributes"]["spayed_neutered"]
    d = animals[page_number]["description"] if animals[page_number]["description"] != None else "No Description Available."
    des = d.replace("&#039;", "'")
    description = des.replace("&amp;#39;", "'")
    secondary_breed = animals[page_number]["breeds"]["secondary"] if animals[page_number]["breeds"]["secondary"] != None else ""
    location = animals[page_number]["contact"]["address"]["city"] + ", " + animals[page_number]["contact"]["address"]["state"]
    with col1:
        if animals[page_number]["primary_photo_cropped"] == None:
            st.image("noimages.webp", use_column_width="always")
        else:
            image = animals[page_number]['photos'][0]['large']
            st.image(image, use_column_width="auto")
            st.markdown("""
            <style>
            .css-1v0mbdj img {
                width: 425px !important;
                height: 425px !important;
                object-fit: cover !important;
                border-radius: 10px !important;
            }
            </style>""", unsafe_allow_html=True
            )
    with col2:
        st.subheader(f'{name} - [{name}\'s Petfinder Link]({link})', divider="rainbow")
        st.markdown(f"#### {breed} :gray[•] {gender} :gray[•] {age}")
        if secondary_breed != "":
            st.markdown(f":blue[**Secondary Breed:**] {secondary_breed}")
        # if animals[page_number]["type"] == "Dog" and adoption_status == "Adoptable":
        #     st.text(f"Median Length of Stay: ")
        if spayed_neutered == True:
            st.markdown(f":blue[**Spayed or Neutered:**] Yes")
        else:
            st.markdown(f":blue[**Spayed or Neutered:**] No")
        st.markdown(f":blue[**Location:**] {location}")
        if adoption_status == "Adopted":
            status_changed_at = pd.to_datetime(animals[page_number]["status_changed_at"])
            published = pd.to_datetime(animals[page_number]["published_at"])
            los = (status_changed_at - published).days
            st.markdown(f":blue[**Length of Stay:**]  {los} days")
        st.code(f"Description:\n{description}", language=None)

_, prev, next = st.columns([6, 5, 7])
if int(page_number) + 1 == int(last_page):
    is_last_page = True
else:
    is_last_page = False

if int(page_number) == 0:
    is_first_page = True
else:
    is_first_page = False

def next_page():
    st.session_state['page_number'] += 1
    components.html(
        f"""
            <p>{st.session_state['page_number']}</p>
            <script>
                window.parent.document.querySelector('section.main').scrollTo(0, 0);
            </script>
        """,
        height=0
    )

next.button("Next", on_click=next_page, disabled=is_last_page)

def prev_page():
    st.session_state['page_number'] -= 1
    components.html(
        f"""
            <p>{st.session_state['page_number']}</p>
            <script>
                window.parent.document.querySelector('section.main').scrollTo(0, 0);
            </script>
        """,
        height=0
    )

prev.button("Previous", on_click=prev_page, disabled=is_first_page)
