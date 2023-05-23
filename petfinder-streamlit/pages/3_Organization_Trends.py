import streamlit as st
from psycopg2.extras import RealDictCursor
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import pfglobals

st.set_page_config(layout="wide")

if "selected_orgs" not in st.session_state:
    st.session_state['selected_orgs'] = []
if "selected_locations" not in st.session_state:
    st.session_state['selected_locations'] = ["Chicago"]

org_scatterplot_tab, org_trends_tab = st.tabs(["Organization Scatter Plot", "Organization Trends by Length of Stay"])

with org_trends_tab:
    st.markdown("# Rescue Dog Trends")
    st.markdown("## Organization Trends from Petfinder Data")
    st.markdown("### How does an Organization affect average length of time from intake to adoption?")
    st.markdown("Use the location widget in the "
                "sidebar to select a location (default is Chicago). "
                "Use the Filter widget in the sidebar to exclude length of stay greater than the specified value (default is 60 days). ")

    #######################################################
    # Sidebar inputs for users to customize their results #
    #######################################################

    st.sidebar.markdown("## Location Settings")
    pfglobals.location_sidepanel()
    st.sidebar.caption("Note: Location setting only applies to the main chart.")
    st.sidebar.markdown("## Filter Settings")
    pfglobals.max_los_sidepanel()
    pfglobals.max_count_sidepanel()
    #######################################################
    #               End sidebar inputs                    #
    #######################################################

    col1, col2 = st.columns([3,1])
    with col2:
        number_of_orgs_slider = pfglobals.place_orgs_in_sidepanel()
        pfglobals.place_los_sort_in_sidepanel(number_of_orgs_slider)

    # Set up where clause for only the orgs the user has selected, if they selected any
    num_iterations = 0
    where_clause = ''
    if len(pfglobals.orgs_list) > 0 and len(pfglobals.orgs_list) < len(pfglobals.orgs_array):
        where_clause = " AND organization_name IN ("
        for org in pfglobals.orgs_list:
            if num_iterations > 0:
                where_clause += ","
            where_clause += "'%s'" % org
            num_iterations += 1
        where_clause += ") "

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

    if len(where_clause) > 0:
        los_by_org_query = """
            SELECT organization_name,AVG(los)::bigint as "%s",Count(*) as "%s" FROM "%s" %s %s %s GROUP BY organization_name %s %s %s;
            """ % (pfglobals.LENGTH_OF_STAY_TEXT, pfglobals.COUNT_TEXT, pfglobals.DATABASE_TABLE, pfglobals.max_los, where_clause, location_clause,  pfglobals.min_animal_count, pfglobals.los_sort, pfglobals.limit_query)
    else:
        los_by_org_query = """
            SELECT organization_name,AVG(los)::bigint as "%s",Count(*) as "%s" FROM "%s" %s %s GROUP BY organization_name %s %s %s;
            """ % (pfglobals.LENGTH_OF_STAY_TEXT, pfglobals.COUNT_TEXT, pfglobals.DATABASE_TABLE, pfglobals.max_los, location_clause, pfglobals.min_animal_count, pfglobals.los_sort, pfglobals.limit_query)

    if pfglobals.showQueries:
        st.markdown("#### Query")
        st.markdown(los_by_org_query)
    df = pfglobals.create_data_frame(pfglobals.run_query(los_by_org_query, pfglobals.conn_dict), "organization_name")
    with col1:
        pfglobals.show_bar_chart(df, pfglobals.LENGTH_OF_STAY_TEXT, pfglobals.COUNT_TEXT, True)

    #######################################################
    #                Side by Side Charts                  #
    #######################################################
    st.markdown("### How do different dog characteristics (gender, size, coat length, age, etc.) interact with Organizations to "
                "affect length of stay?")
    st.markdown("Use the filter widget in the sidebar to select specific breeds to visualize, or to select a specific "
                "number of random breeds to see visualized at one time. Then select values for other characteristics from "
                "the drop down lists below to compare on the graphs. These side-by-side graphs illustrate how these "
                "characteristics impact average length of stay for dogs of the selected breeds.")

    group_labels = ['Group 1', 'Group 2']

    leftCol, rightCol = st.columns(2)

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
        pfglobals.create_select_boxes("organization_name", "Organization", leftCol, rightCol, False, "orgs"),
        pfglobals.create_select_boxes("gender", "Gender", leftCol, rightCol, False, "orgs"),
        pfglobals.create_select_boxes("size", "Size", leftCol, rightCol, False, "orgs"),
        pfglobals.create_select_boxes("coat", "Coat", leftCol, rightCol, False, "orgs"),
        pfglobals.create_select_boxes("age", "Age", leftCol, rightCol, False, "orgs"),
        pfglobals.create_select_boxes("city", "City", leftCol, rightCol, False, "orgs"),
        pfglobals.create_select_boxes("state", "State", leftCol, rightCol, False, "orgs"),
        pfglobals.create_select_boxes("good_with_children", "Good With Children", leftCol, rightCol, True, "orgs"),
        pfglobals.create_select_boxes("good_with_dogs", "Good With Dogs", leftCol, rightCol, True, "orgs"),
        pfglobals.create_select_boxes("good_with_cats", "Good With Cats", leftCol, rightCol, True, "orgs"),
        pfglobals.create_select_boxes("breed_mixed", "Is Mixed Breed?", leftCol, rightCol, True, "orgs"),
        pfglobals.create_select_boxes("attribute_special_needs", "Special Needs?", leftCol, rightCol, True, "orgs"),
        pfglobals.create_select_boxes("attribute_shots_current", "Up To Date On Shots?", leftCol, rightCol, True, "orgs")
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

    df = pfglobals.get_comparison_dataframe(left_values, right_values, original_where_clause, "organization_name", "los")
    fig = go.Figure()

    for col in ["left_group"]:
        fig.add_bar(x=df.index, y=df[col], name="Group 1")
    for col in ["right_group"]:
        fig.add_bar(x=df.index, y=df[col], name="Group 2")
    st.plotly_chart(fig, use_container_width=True)

with org_scatterplot_tab:
    st.markdown("# Rescue Dog Trends")
    st.markdown("## Organization Trends from Petfinder Data")
    st.markdown("#### Details from a specific Organization displayed via Altair Scatter Plot chart.")
    st.caption("Note: No sidebar settings apply to this chart.")

    list_orgs_query = """
        SELECT DISTINCT(organization_name) FROM "%s" ORDER BY organization_name ASC;
        """ % pfglobals.DATABASE_TABLE

    orgs_results = pfglobals.run_query(list_orgs_query, pfglobals.conn_no_dict)

    orgs_array = []
    for org in orgs_results:
        orgs_array.append(org[0])

    selected_org = st.selectbox('Choose the organization you want to see', orgs_array)


    selected_org_query = """WHERE organization_name = '%s';
    """ % (selected_org)
    los_by_org_altair_query = """
        SELECT * FROM "%s" %s;
        """ % (pfglobals.DATABASE_TABLE, selected_org_query)
    # print(los_by_org_altair_query)
    altair_df = pfglobals.create_data_frame(pfglobals.run_query(los_by_org_altair_query, pfglobals.conn_dict), "organization_name")
    # print(altair_df)
    org_chart = alt.Chart(altair_df).mark_circle(size=60).encode(
        x='published_at',
        y='los',
        color='gender',
        tooltip=['name', 'los', 'breed_primary', 'age', 'size']
    ).interactive()

    st.altair_chart(org_chart, use_container_width=True)
