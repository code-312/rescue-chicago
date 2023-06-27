import os
import streamlit as st
import pfglobals
import requests
import json

st.set_page_config(layout="wide")

st.markdown("🚧Coming Soon🚧")

token = pfglobals.get_token()


url = "https://api.petfinder.com/v2/animals"
headers = {"Authorization": f"Bearer {token}"}

#Look up params in petfinder docs https://www.petfinder.com/developers/v2/docs/ - Make them dynamic (different pets etc).

#I set limit to 1 and page to 1 to not use up so many requests. Be careful with your usage, every refresh will make a get request
#https://www.petfinder.com/user/developer-settings/
#Today's request usage: 0 / 1,000
#Daily usage count reset at 12:00am UTC
#Rate Limit
#100 requests/second


params = {
    "type": "dog",
    "status": "adopted",
    "organization": None,
    "location": "Chicago, IL",
    "sort": "distance",
    "distance": 100,
    "limit": 1,
    "page": 1,
}

response = requests.get(url, headers=headers, params=params)
r = response.json()
print(json.dumps(r, indent=2))

# You can turn it into a data frame from here.
