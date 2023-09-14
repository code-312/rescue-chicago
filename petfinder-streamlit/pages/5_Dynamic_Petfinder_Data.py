import os
import streamlit as st
from streamlit_carousel import carousel
from datetime import datetime
import pfglobals
import requests
import json
import pandas as pd

st.set_page_config(page_title="Pawsitive Finder", page_icon="🐇", layout="wide")
"""

"""
if "page_number" not in st.session_state:
    st.session_state['page_number'] = 0
if "petfinder_animals" not in st.session_state:
    st.session_state['petfinder_animals'] = []

st.title("Pawsitive Finder")
st.markdown("Live data pulled from Petfinder in a slideshow format. If you are interested in the animal, please click the Petfinder link for more detailed information!")
st.markdown("# ")
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
            # print(response.json())
    except:
        st.session_state['petfinder_animals'] = []
    # 'pagination': {'count_per_page': 5, 'total_count': 5165, 'current_page': 1, 'total_pages': 1033,
    #                '_links': {'next': {'href': '/v2/animals?distance=100&limit=5&location=Chicago,%20IL&page=2&sort=recent&status=Adoptable&type=Cat'}}}}

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
    name = animals[page_number]["name"]
    petfinder_link = f"<a href=\"{link}\" target=\"_blank\">{name}'s Petfinder Link</a>"
    breed = animals[page_number]["breeds"]["primary"]
    description = animals[page_number]["description"] if animals[page_number]["description"] != None else "No Description Available."
    # description = des.replace('\n', ' ')
    secondary_breed = animals[page_number]["breeds"]["secondary"] if animals[page_number]["breeds"]["secondary"] != None else ""
    size = animals[page_number]["size"] if animals[page_number]["size"] != None else ""
    location = animals[page_number]["contact"]["address"]["city"] + ", " + animals[page_number]["contact"]["address"]["state"]
    published_at = animals[page_number]["published_at"][:10]
    images = []
    if animals[page_number]["primary_photo_cropped"] != None:
        for image in animals[page_number]["photos"]:
            images.append(dict(
                interval=5000,
                img=image['large'],
                title=name,
                text=breed,
            ))
    with col1:
        if animals[page_number]["primary_photo_cropped"] == None:
            st.image("noimages.webp", use_column_width="always")
        else:
            if len(images) > 1:
                carousel(items=images, width=1, height=600)
            else:
                st.image(images[0]['img'], use_column_width="auto")
    with col2:
        st.subheader(f'{name} - [{name}\'s Petfinder Link]({link})', divider="rainbow")
        col3, col4 = st.columns([1, 2])
        with col3:
            st.markdown(f":blue[**Date Posted:**]  {str(published_at)}")
            if animals[page_number]["type"] == "Dog" and adoption_status == "Adoptable":
                st.write(f":blue[**Expected Average Length of Stay:**]  ")
                st.write(f":blue[**Expected Median Length of Stay:**]  ")
            if adoption_status == "Adopted":
                status_changed_at = pd.to_datetime(animals[page_number]["status_changed_at"])
                published = pd.to_datetime(animals[page_number]["published_at"])
                los = (status_changed_at - published).days
                st.markdown(f":blue[**Length of Stay:**]  {los} days")
            st.markdown(f":blue[**Breed:**]  {breed}")
            st.markdown(f":blue[**Secondary Breed:**]  {secondary_breed}")
            st.markdown(f":blue[**Age:**]  {age}")
            st.markdown(f":blue[**Gender:**]  {gender}")
            st.markdown(f":blue[**Size:**]  {size}")
            st.markdown(f":blue[**Location:**]  {location}")
        with col4:
            st.markdown(":blue[**Description:**]")
            st.caption(f"{description}")
            st.markdown("# ")
        _, prev ,next = st.columns([2, 10, 5])
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

        next.button("Next", on_click=next_page, disabled=is_last_page)
        def prev_page():
            st.session_state['page_number'] -= 1

        prev.button("Previous", on_click=prev_page, disabled=is_first_page)
