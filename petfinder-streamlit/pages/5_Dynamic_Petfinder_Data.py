import os
import streamlit as st
import pfglobals
import requests
import json

st.set_page_config(layout="wide")

token = pfglobals.get_token()
headers = {"Authorization": f"Bearer {token}"}

animal_type = st.sidebar.selectbox('Select an Animal Type.', ['Dog', 'Cat', 'Rabbit', 'Small & Furry', 'Horse', 'Bird', 'Scales, Fins & Other', 'Barnyard'])
adoption_status = st.sidebar.selectbox('Select Adoption Status.', ["Adoptable", "Adopted", "Found"])
location = st.sidebar.text_input('Location', help="Postal Code or City, State", value="Chicago, IL", placeholder="Chicago, IL")

params = {
    "type": f"{animal_type}",
    "status": f"{adoption_status}",
    "organization": None,
    "location": f"{location}",
    "sort": "recent",
    "distance": 100,
    "limit": 1,
    "page": 1,
}

url = "https://api.petfinder.com/v2/animals"
response = requests.get(url, headers=headers, params=params)
r = response.json()
animal = dict((key,d[key]) for d in r["animals"] for key in d)
print(json.dumps(r, indent=2))
if r['animals'] == []:
    st.write("No Results")
else:
    st.write(animal["url"])
    st.write(animal["age"])
    st.write(animal["gender"])
    st.write(animal["name"])
    st.write(animal["description"])
    if animal["primary_photo_cropped"] == None:
        st.write("No images")
    else:
       st.image(animal["primary_photo_cropped"]["full"], width=None)
