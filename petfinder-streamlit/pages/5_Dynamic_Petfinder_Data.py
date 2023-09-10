import os
import streamlit as st
import pfglobals
import requests
import json

st.set_page_config(page_title="Pet Slideshow", page_icon="🐇", layout="centered")

if "page_number" not in st.session_state:
    st.session_state['page_number'] = 0
if "petfinder_animals" not in st.session_state:
    st.session_state['petfinder_animals'] = []
# if "api_call_count" not in st.session_state:
#     st.session_state['api_call_count'] = 0
#session_state to keep track of API Calls



token = pfglobals.get_token()
headers = {"Authorization": f"Bearer {token}"}

def reset_session_state():
    st.session_state['petfinder_animals'] = []
    st.session_state['page_number'] = 0

animal_type = st.sidebar.selectbox('Select an Animal Type.', ['Dog', 'Cat', 'Rabbit', 'Small & Furry', 'Horse', 'Bird', 'Scales, Fins & Other', 'Barnyard'], on_change=reset_session_state)
adoption_status = st.sidebar.selectbox('Select Adoption Status.', ["Adoptable", "Adopted", "Found"], on_change=reset_session_state)
location = st.sidebar.text_input('Location', help="Postal Code or City, State", value="Chicago, IL", placeholder="Chicago, IL", on_change=reset_session_state)

url = "https://api.petfinder.com/v2/animals"
params = {
    "type": f"{animal_type}",
    "status": f"{adoption_status}",
    "organization": None,
    "location": f"{location}",
    "sort": "recent",
    "distance": 100,
    "limit": 5,
    "page": 1,
}

if st.session_state['petfinder_animals'] == []:
    response = requests.get(url, headers=headers, params=params)
    st.session_state['petfinder_animals'] = response.json()

# animals = dict((key,d[key]) for d in st.session_state['petfinder_animals']["animals"] for key in d)
# print(animals)
def animals():
    for animal in st.session_state['petfinder_animals']["animals"]:
        print(animal)
animals()

if st.session_state['petfinder_animals']['animals'] == []:
    st.write("No Results")
else:
    last_page = len(st.session_state['petfinder_animals']['animals'])
    dog_link_url = st.session_state['petfinder_animals']['animals'][st.session_state['page_number']]["url"]
    age = st.session_state['petfinder_animals']['animals'][st.session_state['page_number']]["age"]
    gender = st.session_state['petfinder_animals']['animals'][st.session_state['page_number']]["gender"]
    name = st.session_state['petfinder_animals']['animals'][st.session_state['page_number']]["name"]
    description = st.session_state['petfinder_animals']['animals'][st.session_state['page_number']]["description"]
    if st.session_state['petfinder_animals']['animals'][st.session_state['page_number']]["primary_photo_cropped"] == None:
        image = "No images"
    else:
        image = st.session_state['petfinder_animals']['animals'][st.session_state['page_number']]["primary_photo_cropped"]["full"]
    st.write(dog_link_url)
    st.write(age)
    st.write(gender)
    st.write(name)
    st.write(description)
    if st.session_state['petfinder_animals']['animals'][0]["primary_photo_cropped"] == None:
        st.write("No images")
    else:
       st.image(image, width=None)


prev, _ ,next = st.columns([1, 4, 1])

if int(st.session_state['page_number']) + 1 == int(last_page):
    boo = True
else:
    boo = False

def next_page():
    st.session_state['page_number'] += 1

next.button("Next", on_click=next_page, disabled=boo)

def prev_page():
    st.session_state['page_number'] -= 1

prev.button("Previous", on_click=prev_page)
