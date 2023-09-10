import streamlit as st
import pandas as pd
import numpy as np
import time
import math
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.express as px
import pfglobals

import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(page_title="Trends By Length of Stay", page_icon="🐕‍🦺", layout="wide")


breed_trends_tab, other_trends_tab = st.tabs([":blue[📉 Breed Trends by Length of Stay]", ":blue[📉 Other Trends by Length of Stay]"])

if "selected_breeds" not in st.session_state:
    st.session_state['selected_breeds'] = []

if "selected_locations" not in st.session_state:
    st.session_state['selected_locations'] = ["Chicago"]

#######################################################
#          Breed Trends by Length of Stay Tab         #
#######################################################

with breed_trends_tab:
    st.markdown("## Breed Trends from Petfinder Data")
    st.markdown("### How does dog breed affect average length of time from intake to adoption?")
    st.markdown("Use the location widget in the "
                "sidebar to select a location (default is Chicago). "
                "Use the Filter widget in the sidebar to exclude length of stay greater than the specified value (default is 365 days). ")
    st.sidebar.markdown("## Location Settings")
    pfglobals.location_sidepanel()
    st.sidebar.caption("<b>Note: Location setting only applies to the main chart.</b>", unsafe_allow_html=True)
    st.sidebar.markdown("## Filter Settings")
    pfglobals.max_los_sidepanel()
    pfglobals.max_count_sidepanel()

    #######################################################
    #                     Main Chart                      #
    #######################################################
    col1, col2 = st.columns([3,1])
    # Set up where clause for only the breeds the user has selected, if they selected any
    with col2:
        st.markdown("### Chart Settings")
        st.caption("<b>Note: These settings also apply to the comparison chart below.</b>", unsafe_allow_html=True)
        number_of_breeds_slider = pfglobals.place_breeds_in_sidepanel()
        pfglobals.place_los_sort_in_sidepanel(number_of_breeds_slider)
    with col1:
        num_iterations = 0
        where_clause = ''
        if len(pfglobals.breeds_list) > 0 and len(pfglobals.breeds_list) < len(pfglobals.breeds_array):
            where_clause = " AND breed_primary IN ("
            for breed in pfglobals.breeds_list:
                if num_iterations > 0:
                    where_clause += ","
                where_clause += "'%s'" % breed
                num_iterations += 1
            where_clause += ") "

        # Set up where clause for only the locations the user has selected, default is chicago
        location_iterations = 0
        location_clause = ''
        if len(pfglobals.location_list) > 0:
            location_clause = " AND city IN ("
            for location in pfglobals.location_list:
                if location_iterations > 0:
                    location_clause += ","
                location_clause += "'%s'" % location
                location_iterations += 1
            location_clause += ") "
        else:
            location_clause = ''

        if len(where_clause) > 0:
            los_by_breed_query = """
                SELECT breed_primary,AVG(los)::bigint as "%s",Count(*) as "%s" FROM "%s" %s %s %s GROUP BY breed_primary %s %s %s;
                """ % (pfglobals.LENGTH_OF_STAY_TEXT, pfglobals.COUNT_TEXT, pfglobals.DATABASE_TABLE, pfglobals.max_los, where_clause, location_clause,  pfglobals.min_animal_count, pfglobals.los_sort, pfglobals.limit_query)
        else:
            los_by_breed_query = """
                SELECT breed_primary,AVG(los)::bigint as "%s",Count(*) as "%s" FROM "%s" %s %s GROUP BY breed_primary %s %s %s;
                """ % (pfglobals.LENGTH_OF_STAY_TEXT, pfglobals.COUNT_TEXT, pfglobals.DATABASE_TABLE, pfglobals.max_los, location_clause, pfglobals.min_animal_count, pfglobals.los_sort, pfglobals.limit_query)

        if pfglobals.showQueries:
            st.markdown("#### Query")
            st.markdown(los_by_breed_query)

        if pfglobals.run_query(los_by_breed_query, pfglobals.conn_dict) == []:
            results = '<br><br><p style="font-family:Courier; color:Red; font-size: 20px; font-weight: Bold;">No results were found with this criteria.</p><br><br>'
            st.markdown(results, unsafe_allow_html=True)
        else:
            df = pfglobals.create_data_frame(pfglobals.run_query(los_by_breed_query, pfglobals.conn_dict), "breed_primary")
            pfglobals.show_bar_chart(df, pfglobals.LENGTH_OF_STAY_TEXT, pfglobals.COUNT_TEXT, True)

    #######################################################
    #                Side by Side Charts                  #
    #######################################################
        st.markdown("### How do different dog characteristics (gender, size, coat length, age, etc.) interact with breed to "
                    "affect length of stay?")
        st.markdown("Use the filter widget above to select specific breeds to visualize, or to select a specific "
                    "number of random breeds to see visualized at one time. Then select values for other characteristics from "
                    "the drop down lists to compare on the graphs. These side-by-side graphs illustrate how these "
                    "characteristics impact average length of stay for dogs of the selected breeds.")

    group_labels = ['Group 1', 'Group 2']
    # leftCol, rightCol = st.columns(2)
    chartCol, leftCol, rightCol = st.columns([5,1,1])

    with leftCol:
        st.header(group_labels[0])
    with rightCol:
        st.header(group_labels[1])

    # now find all selected values to use to build queries
    left_values = []
    right_values = []

    # limit_query = ""
    original_where_clause = where_clause

    # create the select boxes for all the comparison attributes
    all_select_boxes = [
        pfglobals.create_select_boxes("gender", "Gender", leftCol, rightCol, False, "breed_trends"),
        pfglobals.create_select_boxes("size", "Size", leftCol, rightCol, False, "breed_trends"),
        pfglobals.create_select_boxes("coat", "Coat", leftCol, rightCol, False, "breed_trends"),
        pfglobals.create_select_boxes("age", "Age", leftCol, rightCol, False, "breed_trends"),
        pfglobals.create_select_boxes("city", "City", leftCol, rightCol, False, "breed_trends"),
        pfglobals.create_select_boxes("state", "State", leftCol, rightCol, False, "breed_trends"),
        pfglobals.create_select_boxes("good_with_children", "Good With Children", leftCol, rightCol, True, "breed_trends"),
        pfglobals.create_select_boxes("good_with_dogs", "Good With Dogs", leftCol, rightCol, True, "breed_trends"),
        pfglobals.create_select_boxes("good_with_cats", "Good With Cats", leftCol, rightCol, True, "breed_trends"),
        pfglobals.create_select_boxes("breed_mixed", "Is Mixed Breed?", leftCol, rightCol, True, "breed_trends"),
        pfglobals.create_select_boxes("attribute_special_needs", "Special Needs?", leftCol, rightCol, True, "breed_trends"),
        pfglobals.create_select_boxes("attribute_shots_current", "Up To Date On Shots?", leftCol, rightCol, True, "breed_trends")
    ]

    for select_boxes in all_select_boxes:
        left_values.append({"db_column": select_boxes["db_column"], "db_col_type": select_boxes["db_col_type"], "select_box": select_boxes["left"]})
        right_values.append({"db_column": select_boxes["db_column"], "db_col_type": select_boxes["db_col_type"], "select_box": select_boxes["right"]})

    if list(value for value in left_values if value['db_column'] == 'city' and value['select_box'] != 'No value applied'):
        for value in left_values:
            if value['db_column'] == 'state':
                value['select_box'] = 'No value applied'

    if list(value for value in right_values if value['db_column'] == 'city' and value['select_box'] != 'No value applied'):
        for value in right_values:
            if value['db_column'] == 'state':
                value['select_box'] = 'No value applied'

    df = pfglobals.get_comparison_dataframe(left_values, right_values, original_where_clause, "breed_primary", "los")
    fig = go.Figure()

    for col in ["left_group"]:
        fig.add_bar(x=df.index, y=df[col], name="Group 1")
    for col in ["right_group"]:
        fig.add_bar(x=df.index, y=df[col], name="Group 2")
    with chartCol:
        st.plotly_chart(fig, use_container_width=True)

#######################################################
#           Other Trends by Length of Stay Tab        #
#######################################################
with other_trends_tab:
    st.markdown("## Other Trends from Petfinder Data")
    st.markdown("### How do different dog characteristics (gender, size, coat length, age) affect length of stay?")
    st.markdown("These graphs illustrate how these characteristics impact average length of stay for dogs of all "
                "breeds. Use the location widget in the sidebar to select a location (default is Chicago).")
    attribute_info = [
        {"db_column": "gender", "text": "Gender"},
        {"db_column": "size", "text": "Size"},
        {"db_column": "coat", "text": "Coat"},
        {"db_column": "age", "text": "Age"}
    ]

    other_trends_col1, other_trends_col2 = st.columns([3,1])

    with other_trends_col2:
        st.markdown("### Chart Settings")
        st.caption("Note: These settings also apply to the comparison chart below.")
        st.markdown("##### Choose one or more values from a single attribute you'd like to see")
        attribute_lists = pfglobals.place_other_attributes_in_sidepanel(attribute_info)
        st.markdown("##### Sorting Options")
        los_sort_selectbox = st.selectbox(
            'Sort by number of results',
            ('DESC', 'ASC', 'NONE')
        )
    # Set up where clause for only the attributes the user has selected, if they selected any
    selected_list = []
    for attribute_list in attribute_lists:
        num_iterations = 0
        attr_where_clause = ''
        if len(attribute_list["selectbox"]) > 0:
            selected_list = attribute_list
            attr_where_clause = " AND %s IN (" % attribute_list["db_column"]
            for attribute_value in attribute_list["value_list"]:
                if num_iterations > 0:
                    attr_where_clause += ","
                attr_where_clause += "'%s'" % attribute_value
                num_iterations += 1
            attr_where_clause += ") "
            break

    attr_location_iterations = 0
    attr_location_clause = ''
    if len(pfglobals.location_list) > 0:
        attr_location_clause = " AND city IN ("
        for attr_location in pfglobals.location_list:
            if attr_location_iterations > 0:
                attr_location_clause += ","
            attr_location_clause += "'%s'" % attr_location
            attr_location_iterations += 1
        attr_location_clause += ") "
    else:
        attr_location_clause = ''

    los_by_attribute_query = """
        SELECT %s,AVG(los)::bigint as "%s",Count(*) as "%s" FROM "%s" %s %s %s GROUP BY %s %s %s %s;
        """ % (selected_list["db_column"], pfglobals.LENGTH_OF_STAY_TEXT, pfglobals.COUNT_TEXT, pfglobals.DATABASE_TABLE, pfglobals.max_los, attr_where_clause, attr_location_clause, selected_list["db_column"], pfglobals.min_animal_count, pfglobals.los_sort, pfglobals.limit_query)

    if pfglobals.showQueries:
        st.markdown("#### Query")
        st.markdown(los_by_attribute_query)
    df = pfglobals.create_data_frame(pfglobals.run_query(los_by_attribute_query, pfglobals.conn_dict), selected_list["db_column"])
    with other_trends_col1:
        pfglobals.show_bar_chart(df, pfglobals.LENGTH_OF_STAY_TEXT, pfglobals.COUNT_TEXT, True)

    #######################################################
    #                Side by Side Charts                  #
    #######################################################
        st.markdown("#")
        st.markdown("#")
        st.markdown("#")
        st.markdown("### How do different dog characteristics (gender, size, coat length, age, etc.) interact with other "
                    "attributes to affect length of stay?")
        st.markdown("Use the filter widget above to select a specific attribute to visualize.  Then select values "
                    "for other characteristics from the drop down lists to compare on the graphs. These side-by-side "
                    "graphs illustrate how these characteristics impact average length of stay for dogs with the specified "
                    "attributes.")

    group_labels = ['Group 1', 'Group 2']
    chartCol, leftCol, rightCol = st.columns([5,1,1])
    # leftCol, rightCol = st.columns(2)

    with leftCol:
        st.header(group_labels[0])
    with rightCol:
        st.header(group_labels[1])

    # now find all selected values to use to build queries
    left_values = []
    right_values = []

    # limit_query = ""
    original_where_clause = where_clause

    # create objects with fields to later create them as select boxes
    select_boxes_to_be_created = [
        {"label": "gender", "title": "Gender", "is_boolean": False},
        {"label": "size", "title": "Size", "is_boolean": False},
        {"label": "coat", "title": "Coat", "is_boolean": False},
        {"label": "age", "title": "Age", "is_boolean": False},
        {"label": "city", "title": "City", "is_boolean": False},
        {"label": "state", "title": "State", "is_boolean": False},
        {"label": "good_with_children", "title": "Good With Children", "is_boolean": True},
        {"label": "good_with_dogs", "title": "Good With Dogs", "is_boolean": True},
        {"label": "good_with_cats", "title": "Good With Cats", "is_boolean": True},
        {"label": "breed_mixed", "title": "Is Mixed Breed?", "is_boolean": True},
        {"label": "attribute_special_needs", "title": "Special Needs?", "is_boolean": True},
        {"label": "attribute_shots_current", "title": "Up To Date On Shots?", "is_boolean": True},
    ]

    # create the select boxes for all the comparison attributes
    all_select_boxes = []

    # loop through all select boxes to be created and only create them and append them to all_select_boxes
    # if they do not match with the current selected_list['db_column'] ex: if "gender" is our current selected_list['db_column'] it will not be created & appended
    for select_box in select_boxes_to_be_created:
        if selected_list['db_column'] != select_box['label']:
            all_select_boxes.append(pfglobals.create_select_boxes(select_box['label'], select_box['title'], leftCol, rightCol, select_box["is_boolean"], "other_trends"))

    for select_boxes in all_select_boxes:
        left_values.append({"db_column": select_boxes["db_column"], "db_col_type": select_boxes["db_col_type"], "select_box": select_boxes["left"]})
        right_values.append({"db_column": select_boxes["db_column"], "db_col_type": select_boxes["db_col_type"], "select_box": select_boxes["right"]})

    if list(value for value in left_values if value['db_column'] == 'city' and value['select_box'] != 'No value applied'):
        for value in left_values:
            if value['db_column'] == 'state':
                value['select_box'] = 'No value applied'

    if list(value for value in right_values if value['db_column'] == 'city' and value['select_box'] != 'No value applied'):
        for value in right_values:
            if value['db_column'] == 'state':
                value['select_box'] = 'No value applied'

    df = pfglobals.get_comparison_dataframe(left_values, right_values, original_where_clause, selected_list['db_column'], "los")
    fig = go.Figure()

    for col in ["left_group"]:
        fig.add_bar(x=df.index, y=df[col], name="Group 1")
    for col in ["right_group"]:
        fig.add_bar(x=df.index, y=df[col], name="Group 2")
    with chartCol:
        st.plotly_chart(fig, use_container_width=True)
