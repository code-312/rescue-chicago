import streamlit as st
import altair as alt
import pandas as pd
import pfglobals

if "selected_locations" not in st.session_state:
    st.session_state['selected_locations'] = ["Chicago"]

st.set_page_config(layout="wide")

monthly_trends_tab, yearly_trends_tab = st.tabs(["Monthly Trends", "Yearly Trends"])

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
SELECT COUNT(id) as count_dogs, TO_CHAR(published_at, 'YYYY-MM') as date, gender FROM "%s" %s GROUP BY date, gender ORDER BY date
""" % (pfglobals.DATABASE_TABLE, location_clause)

with monthly_trends_tab:
    st.markdown("# Rescue Dog Trends")
    st.markdown("## Trends Over Time")

    st.markdown("### How does intake vary over time?")
    st.caption("Use the sidebar filter to add or remove locations.")
    st.markdown("#")

    monthly_df = pfglobals.create_data_frame(pfglobals.run_query(monthly_query,  pfglobals.conn_dict), index_column="date")
    monthly_df = monthly_df.reset_index(drop=False)
    monthly_df['date'] = pd.to_datetime(monthly_df['date']).dt.strftime('%B %Y')

    monthly_trends_chart = alt.Chart(monthly_df, title=f"{', '.join(st.session_state['selected_locations'])} Trends by Month").mark_bar(size=5, align='center').encode(
        x=alt.X('date:T', title='Trends Over Time'),
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
    st.markdown("# Rescue Dog Trends")
    st.markdown("## Trends Over Time")
    st.markdown("### How does intake vary over time?")
    st.caption("Use the sidebar filter to add or remove locations.")
    st.markdown("#")

    yearly_query = """
    SELECT count(id) as count_dogs
        , extract('year' from published_at) as status_changed_at_year
    FROM petfinder_with_dates %s GROUP by 2 ORDER by 2
    """ % (location_clause)

    yearly_df = pfglobals.create_data_frame(pfglobals.run_query(yearly_query,  pfglobals.conn_dict), index_column="status_changed_at_year")

    yearly_trends_chart = alt.Chart(yearly_df.reset_index(), title=f"{', '.join(st.session_state['selected_locations'])} Trends by Year").mark_bar(size=50, align='center', color='#30a2da').encode(
        x=alt.X('year(status_changed_at_year):T', title='Trends Over Time'),
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
    )
    st.altair_chart(yearly_trends_chart, theme=None, use_container_width=True)

# with los_trends_tab:
#     st.markdown("# Rescue Dog Trends")
#     st.markdown("## Trends Over Time")
#     st.markdown("### How does intake vary over time?")
#     st.caption("Use the sidebar filter to add or remove locations.")
#     st.markdown("#")

#     los_query = """
#     SELECT AVG(los)::bigint as LoS, TO_CHAR(published_at, 'YYYY-MM') as date FROM "%s" %s GROUP BY 2 ORDER BY 2
#     """ % (pfglobals.DATABASE_TABLE, location_clause)

#     los_df = pfglobals.create_data_frame(pfglobals.run_query(los_query,  pfglobals.conn_dict), index_column="date")
#     los_df = los_df.reset_index(drop=False)
#     print(los_df)

#     los_trends_chart = alt.Chart(los_df, title=f"{', '.join(st.session_state['selected_locations'])} Trends by Length of Stay").mark_bar().encode(
#         x=alt.X('date:T', title='Trends Over Time'),
#         y=alt.Y('los', title='Length of Stay'),
#         tooltip=[alt.Tooltip('year(date):T', title='Year'),
#                 alt.Tooltip('los', title='Average Length of Stay')]
#     ).properties(
#         height=500
#     ).configure_title(
#         fontSize=17,
#         anchor='middle'
#     ).configure_axis(
#         labelFontSize=15,
#         titleFontSize=15,
#         titleFontWeight=600
#     ).interactive()
#     st.altair_chart(los_trends_chart, use_container_width=True)
