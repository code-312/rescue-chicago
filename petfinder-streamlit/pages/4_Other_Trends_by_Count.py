import streamlit as st
import pandas as pd
import numpy as np
import time
import math
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import pfglobals
import plotly.graph_objects as go

st.markdown("# Chicago Rescue Dog Trends")
st.markdown("## Other Trends from Petfinder Data")
st.markdown("### How do different dog characteristics (gender, size, coat length, age) affect the number of dogs "
            "waiting to be adopted?")
st.markdown("Use the filter widget in the sidebar to select values for characteristics to compare on the graphs "
            "below. These graphs illustrate how these characteristics impact number of dogs waiting to be adopted for "
            "dogs of all breeds.")

#######################################################
# Sidebar inputs for users to customize their results #
#######################################################
st.sidebar.markdown("### Choose one or more values from a single attribute you'd like to see")
st.sidebar.markdown("#### First selected option will be used")

attribute_info = [
    {"db_column": "gender", "text": "Gender"},
    {"db_column": "size", "text": "Size"},
    {"db_column": "coat", "text": "Coat"},
    {"db_column": "age", "text": "Age"}
]

attribute_lists = pfglobals.place_other_attributes_in_sidepanel(attribute_info)

# st.write(st.session_state)
st.sidebar.markdown("### Sorting Options")

los_sort_selectbox = st.sidebar.selectbox(
    'Sort by number of results',
    ('DESC', 'ASC', 'NONE')
)

#######################################################
#               End sidebar inputs                    #
#######################################################

# Set up where clause for only the attributes the user has selected, if they selected any
selected_list = []
for attribute_list in attribute_lists:
    num_iterations = 0
    where_clause = ''
    if len(attribute_list["selectbox"]) > 0:
        selected_list = attribute_list
        where_clause = " WHERE %s IN (" % attribute_list["db_column"]
        for attribute_value in attribute_list["value_list"]:
            if num_iterations > 0:
                where_clause += ","
            where_clause += "'%s'" % attribute_value
            num_iterations += 1
        where_clause += ") "
        break

los_by_attribute_query = """
    SELECT %s,Count(*) as "%s" FROM "%s" %s GROUP BY %s %s %s;
    """ % (selected_list["db_column"], pfglobals.COUNT_TEXT, pfglobals.DATABASE_TABLE, where_clause, selected_list["db_column"], pfglobals.los_sort, pfglobals.limit_query)

if pfglobals.showQueries:
    st.markdown("#### Query")
    st.markdown(los_by_attribute_query)

df = pfglobals.create_data_frame(pfglobals.run_query(los_by_attribute_query, pfglobals.conn_dict), selected_list["db_column"])
pfglobals.show_bar_chart(df, pfglobals.COUNT_TEXT, "", False)

#######################################################
#                Side by Side Charts                  #
#######################################################
st.markdown("### How do different dog characteristics (gender, size, coat length, age, etc.) interact with other "
            "attributes to affect number of dogs waiting to be adopted?")
st.markdown("Use the filter widget in the sidebar to select a specific attribute to visualize.  Then select values "
            "for other characteristics from the drop down lists below to compare on the graphs. These side-by-side "
            "graphs illustrate how these characteristics impact the number of dogs waiting for adoption for dogs with "
            "the specified attributes.")

group_labels = ['Group 1', 'Group 2']

leftCol, rightCol = st.columns(2)

with leftCol:
    st.header(group_labels[0])
with rightCol:
    st.header(group_labels[1])

# limit_query = ""
original_where_clause = where_clause

# create the select boxes for all the comparison attributes
all_select_boxes = [
    pfglobals.create_select_boxes("gender", "Gender", leftCol, rightCol, False),
    pfglobals.create_select_boxes("size", "Size", leftCol, rightCol, False),
    pfglobals.create_select_boxes("coat", "Coat", leftCol, rightCol, False),
    pfglobals.create_select_boxes("age", "Age", leftCol, rightCol, False),
    pfglobals.create_select_boxes("good_with_children", "Good With Children", leftCol, rightCol, True),
    pfglobals.create_select_boxes("good_with_dogs", "Good With Dogs", leftCol, rightCol, True),
    pfglobals.create_select_boxes("good_with_cats", "Good With Cats", leftCol, rightCol, True),
    pfglobals.create_select_boxes("breed_mixed", "Is Mixed Breed?", leftCol, rightCol, True),
    pfglobals.create_select_boxes("attribute_special_needs", "Special Needs?", leftCol, rightCol, True),
    pfglobals.create_select_boxes("attribute_shots_current", "Up To Date On Shots?", leftCol, rightCol, True)
]

# now find all selected values to use to build queries
left_values = []
right_values = []
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
st.plotly_chart(fig)

# Create comparison charts
# pfglobals.create_comparison_chart(leftCol, left_values, original_where_clause, selected_list["db_column"], False)
# pfglobals.create_comparison_chart(rightCol, right_values, original_where_clause, selected_list["db_column"], False)
#######################################################
#             End of Side by Side Charts              #
#######################################################
