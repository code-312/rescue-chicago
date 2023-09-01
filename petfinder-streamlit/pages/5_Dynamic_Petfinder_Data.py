import os
import streamlit as st
import pfglobals
import requests
import json

st.set_page_config(layout="wide")

token = pfglobals.get_token()

url_types = "https://api.petfinder.com/v2/types"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url_types, headers=headers)
r = response.json()
animals = [t for t in r['types']]
types = [t['name'] for t in animals]
# print(json.dumps(r, indent=2))
print(types)
animal_type = st.sidebar.selectbox('Select a animal.', types)

params = {
    "type": f"{animal_type}",
    "status": "adopted",
    "organization": None,
    "location": "Chicago, IL",
    "sort": "distance",
    "distance": 100,
    "limit": 1,
    "page": 1,
}
# Animal type, location, if they are adopted or not
url = "https://api.petfinder.com/v2/animals"
type_response = requests.get(url, headers=headers, params=params)
r_type = type_response.json()
print(json.dumps(r_type, indent=2))
