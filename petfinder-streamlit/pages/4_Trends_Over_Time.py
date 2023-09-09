import streamlit as st
import altair as alt
import pandas as pd
import pfglobals

if "selected_locations" not in st.session_state:
    st.session_state['selected_locations'] = ["Chicago"]

curr_locations = st.session_state['selected_locations']

st.set_page_config(page_title="Trends Over Time", page_icon="🐕‍🦺", layout="wide")

monthly_trends_tab, yearly_trends_tab, los_trends_tab = st.tabs(["Monthly Trends", "Yearly Trends", "Length of Stay Trends"])

st.sidebar.markdown("## Location Settings")
pfglobals.location_sidepanel()
location_iterations = 0
location_clause = ''
if len(pfglobals.location_list) > 0:
    location_clause = " WHERE city IN ("
    for location in pfglobals.location_list:
        if location_iterations > 0:
            location_clause += ","
        location_clause += "'%s'" % location
        location_iterations += 1
    location_clause += ") "
else:
    location_clause = ''

monthly_query = """
SELECT COUNT(id) as count_dogs, TO_CHAR(published_at, 'YYYY-MM') as date, gender FROM "%s" %s
GROUP BY date, gender ORDER BY date
""" % (pfglobals.DATABASE_TABLE, location_clause)

with monthly_trends_tab:
    st.markdown("## Trends Over Time")

    st.markdown("### How does intake vary over time?")
    st.markdown("Sorted monthly starting from February 2010. Use the sidebar filter to add or remove locations.")
    st.markdown("#")

    monthly_df = pfglobals.create_data_frame(pfglobals.run_query(monthly_query,  pfglobals.conn_dict), index_column="date")
    monthly_df = monthly_df.reset_index(drop=False)

    # For mutating the chart, not the query with a selectbox
    # year = st.sidebar.selectbox("Year", ["2010", "2011"])
    # monthly_df = monthly_df[monthly_df['date'] > year]
    monthly_df = monthly_df[monthly_df['date'] > '2010-01']
    monthly_df = monthly_df[monthly_df['date'] < '2023-04']
    # For mutating the chart, not the query with a multiselectbox
    # loc = st.sidebar.multiselect("Location", ["Chicago", "Denver"])
    # monthly_df = monthly_df[monthly_df['city'].str.contains('|'.join(loc))]
    monthly_df['date'] = pd.to_datetime(monthly_df['date']).dt.strftime('%B %Y')
    monthly_trends_chart = alt.Chart(monthly_df, title=f"{', '.join(curr_locations)} Trends by Month").mark_bar(size=5, align='center').encode(
        x=alt.X('yearmonth(date):T', title='Trends Over Time'),
        y=alt.Y('count_dogs', title='Total Dogs per Month'),
        color=alt.Color('gender:N', title='Gender'),
        tooltip=[alt.Tooltip('month(date):T', title='Month'),
                alt.Tooltip('year(date):T', title='Year'),
                alt.Tooltip('gender', title='Gender'),
                alt.Tooltip('count_dogs', title='Total')]
    ).properties(
        height=500
    ).configure_title(
        fontSize=17,
        anchor='middle'
    ).configure_axis(
        labelFontSize=15,
        titleFontSize=15,
        titleFontWeight=600
    ).configure_legend(
        titleFontSize=13,
        labelFontSize=13,
        orient='top-left'
    ).interactive()
    st.altair_chart(monthly_trends_chart, use_container_width=True)

with yearly_trends_tab:
    st.markdown("## Trends Over Time")
    st.markdown("### How does intake vary over time?")
    st.markdown("Sorted yearly starting from 2010. Use the sidebar filter to add or remove locations.")
    st.markdown("#")

    yearly_query = """
    SELECT count(id) as count_dogs
        , extract('year' from published_at) as status_changed_at_year
    FROM petfinder_with_dates %s GROUP by 2 ORDER by 2
    """ % (location_clause)

    yearly_df = pfglobals.create_data_frame(pfglobals.run_query(yearly_query,  pfglobals.conn_dict), index_column="status_changed_at_year")
    yearly_df = yearly_df.reset_index(drop=False)
    yearly_df = yearly_df.astype({"status_changed_at_year": str})
    yearly_df = yearly_df[yearly_df['status_changed_at_year'] > '2010']
    yearly_trends_chart = alt.Chart(yearly_df, title=f"{', '.join(curr_locations)} Trends by Year").mark_bar(size=60, align='center').encode(
        x=alt.X('year(status_changed_at_year):O', title='Trends Over Time'),
        y=alt.Y('count_dogs', title='Total Dogs per Year'),
        tooltip=[alt.Tooltip('year(status_changed_at_year):T', title='Year'),
                alt.Tooltip('count_dogs', title='Total Dogs')]
    ).properties(
        height=500
    ).configure_title(
        fontSize=17,
        anchor='middle'
    ).configure_axis(
        labelFontSize=15,
        titleFontSize=15,
        titleFontWeight=600
    ).configure_mark(
        color='#a3c7ea',
    )
    st.altair_chart(yearly_trends_chart, theme=None, use_container_width=True)

with los_trends_tab:
    st.markdown("## Trends Over Time")
    st.markdown("### How does length of stay vary over time?")
    st.markdown("Sorted monthly starting from January 2013. Use the sidebar filter to add or remove locations.")
    st.markdown("#")
    col1, col2 = st.columns([1,4])
    with col1:
        max_los_slider_value = st.slider(
            'Filter Length of Stay by days',
            1, 730, (365), help="Set Length of Stay by maximum amount of days stayed in a shelter. \n"
            "\n Example: A dog is listed as having stayed for 600 days. It will be filtered out if the slider is set below 600 days. \n"
            "This is useful for filtering outliers where data logged may be inaccurate."
        )
        if location_clause != '':
            max_los = """ AND los <= %d """ % (max_los_slider_value)
        else:
            max_los = """ WHERE los <= %d """ % (max_los_slider_value)

    with col2:
        st.markdown("#")
        st.write(max_los_slider_value, 'days.')
    st.markdown("#")
    los_query = """
    SELECT AVG(los)::bigint as LoS, TO_CHAR(published_at, 'YYYY-MM') as date FROM "%s" %s %s GROUP BY 2 ORDER BY 2
    """ % (pfglobals.DATABASE_TABLE, location_clause, max_los)
    los_df = pfglobals.create_data_frame(pfglobals.run_query(los_query,  pfglobals.conn_dict), index_column="date")
    los_df = los_df.reset_index(drop=False)
    los_df = los_df[los_df['date'] > '2013-01']
    los_df = los_df[los_df['date'] < '2023-04']
    los_trends_chart = alt.Chart(los_df, title=f"{', '.join(st.session_state['selected_locations'])} Trends by Length of Stay").mark_bar().encode(
        x=alt.X('yearmonth(date):T', title='Trends Over Time'),
        y=alt.Y('los', title='Average Length of Stay'),
        tooltip=[alt.Tooltip('month(date):T', title='Month'),
                alt.Tooltip('year(date):T', title='Year'),
                alt.Tooltip('los', title='Average Length of Stay')]
    ).properties(
        height=500
    ).configure_title(
        fontSize=17,
        anchor='middle'
    ).configure_axis(
        labelFontSize=15,
        titleFontSize=15,
        titleFontWeight=600
    ).configure_mark(
        color='#e08366',
    ).interactive()
    st.altair_chart(los_trends_chart, use_container_width=True)
