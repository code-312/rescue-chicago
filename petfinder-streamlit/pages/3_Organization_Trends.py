import streamlit as st
from psycopg2.extras import RealDictCursor
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import pfglobals

st.set_page_config(layout="wide")

if "selected_orgs" not in st.session_state:
    st.session_state['selected_orgs'] = []

st.sidebar.markdown("## Location Settings")
pfglobals.org_locations()

org_scatterplot_tab, org_tab = st.tabs(["Organization Scatter Plot", "-----------"])

with org_scatterplot_tab:
    st.markdown("# Rescue Dog Trends")
    st.markdown("## Organization Trends from Petfinder Data")
    st.markdown("### Organization Statistics based off average length of time from intake to adoption.")
    st.markdown("Use the sidebar filter to sort Organizations by location.")
    list_orgs_query = """
        SELECT DISTINCT(organization_name) FROM "%s" WHERE city = '%s' ORDER BY organization_name ASC;
        """ % (pfglobals.DATABASE_TABLE, pfglobals.org_location)

    orgs_results = pfglobals.run_query(list_orgs_query, pfglobals.conn_no_dict)

    orgs_array = []
    for org in orgs_results:
        orgs_array.append(org[0])

    selected_org = st.selectbox('Choose the organization you want to see', orgs_array)
    formatted_org = selected_org.replace("'", "'\'")

    selected_org_query = """WHERE organization_name = '%s';
    """ % (formatted_org)

    los_by_org_altair_query = """
        SELECT * FROM "%s" %s;
        """ % (pfglobals.DATABASE_TABLE, selected_org_query)

    altair_df = pfglobals.create_data_frame(pfglobals.run_query(los_by_org_altair_query, pfglobals.conn_dict), "organization_name")
    selected_org_city = altair_df['city'][0]
    selected_org_state = altair_df['state'][0]
    # scale = alt.Scale(domain=['Female', 'Male'], range=['#7C33FF', '#0867a1'])
    org_chart = alt.Chart(altair_df, title=f'{selected_org} in {selected_org_city}, {selected_org_state}').mark_circle(size=60).encode(
        x=alt.X('published_at:T', title='Date Posted'),
        y=alt.Y('los', title='Length of Stay by Days'),
        # color=alt.Color('gender', scale=scale),
        color=alt.Color('gender', title='Gender'),
        tooltip=[alt.Tooltip('name', title='Name'), alt.Tooltip('los', title='Days Stayed'),
        alt.Tooltip('breed_primary', title='Breed'), alt.Tooltip('age', title='Age'),
        alt.Tooltip('size', title='Size')],
    ).properties(
        height=500
    ).configure_legend(
        titleFontSize=16,
        labelFontSize=16,
        orient='top-right'
    ).configure_title(
        fontSize=17
    ).configure_axis(
        labelFontSize=15,
        titleFontSize=15,
        titleFontWeight=600
    ).interactive()
    st.altair_chart(org_chart, use_container_width=True)

with org_tab:
    pass
