import streamlit as st

st.set_page_config(page_title="Rescue Dog Trends", page_icon="🐶", layout="wide")

st.header("Rescue Dog Trends", divider='blue')
intro_text = "In 2021 alone, Chicago Animal Care and Control, the city's only publicly funded shelter, took in 4," \
            "122 stray, surrendered, or confiscated dogs. While some of the dogs who end up in the municipal shelter " \
            "will be returned to their owner or adopted out directly, more than half of these animals are " \
            "transferred to another animal rescue organization through the shelter's Homeward Bound partnerships. To " \
            "learn more about the journeys of these rescued pups, we pulled data from the Petfinder API for dogs " \
            "located within 100 miles of Chicago and other cities. Petfinder is the most widely used online database of adoptable " \
            "pets. Many animal rescue organizations maintain their own organization pages and adoptable pet " \
            "listings on the site. The interactive data visualizations on various pages can " \
            "be used to illustrate how different dog characteristics affect the average length of stay of these " \
            "dogs in a shelter or foster placement prior to adoption. "
st.write(intro_text)

st.header("Visualization Pages", divider='violet')
st.markdown("- <a href=\"/Trends_by_Length_of_Stay\" target=\"_self\">Trends by Length of Stay</a><p>How dog breed affects average length of time from intake to adoption.</p>", unsafe_allow_html=True)
st.markdown("* <a href=\"/Trends_by_Count\" target=\"_self\">Trends by Count</a><p>How dog breed relates to the number of dogs waiting to be adopted.</p>", unsafe_allow_html=True)
st.markdown("* <a href=\"/Organization_Trends\" target=\"_self\">Organization Trends</a><p>Individual Organization data related to length of stay from intake to adoption.", unsafe_allow_html=True)
st.markdown("* <a href=\"/Trends_Over_Time\" target=\"_self\">Trends Over Time</a><p>How intake and length of stay vary over time.</p>", unsafe_allow_html=True)
st.markdown("* <a href=\"/Dynamic_Petfinder_Data\" target=\"_self\">Pet Slideshow</a><p>Live data from Petfinder in a slideshow format.</p>", unsafe_allow_html=True)

st.header("Acknowledgements", divider='green')
cfc_github_link = "<a href=\"https://github.com/Code-For-Chicago/rescue-chicago\" target=\"_blank\">Github</a>"
rescue_chicago_link = "<a href=\"https://rescuechi.org/\" target=\"_blank\">Rescue Chicago</a>"
petfinder_link = "<a href=\"https://www.petfinder.com/\" target=\"_blank\">Petfinder</a>"
acknowledgements_text = f"Project documentation is available on {cfc_github_link}. The {petfinder_link} API is easily accessible through " \
                        "the Petfinder for Developers webpage. This project was originally inspired by conversations " \
                        f"that the Code for Chicago data workgroup had with {rescue_chicago_link} about how data could inform " \
                        "their efforts to support and unify Chicago's shelter and rescue community. This application " \
                        "was built by Evan Cooperman, Kayla Robinson, Cara Karter, Joseph Adorno, E. Chris Lynch, Jared Kunhart and Jhen Dimaano."
st.write(acknowledgements_text, unsafe_allow_html=True)
