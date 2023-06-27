import streamlit as st
import pfglobals

st.set_page_config(layout="wide")

st.markdown("# Chicago Rescue Dog Trends")
st.markdown("## Trends Over Time")


conn = pfglobals.conn_dict
# table_name = pfglobals.DATABASE_TABLE # petfinder_with_dates

st.markdown("### How Length of Stay Has Varied Over Time - 🚧IN PROGRESS🚧")
# TODO


st.markdown("### How the Number of Dogs Has Varied Over Time - 🚧IN PROGRESS🚧")

query = """
-- return the total count of dogs in shelters grouped by year

select count(id) as count_dogs
    , extract('year' from published_at) as status_changed_at_year
from petfinder_with_dates
group by 2
order by 2

"""

data = pfglobals.run_query(query, conn) # returns list of tuples
# print(data)

df = pfglobals.create_data_frame(data, index_column="status_changed_at_year")

pfglobals.show_bar_chart(data_frame=df, plotly_y="count_dogs", plotly_text=None, remove_count=False)





##### NOTES  #####

# pfglobals.run_query(los_by_attribute_query, pfglobals.conn_dict), selected_list["db_column"]
