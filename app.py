import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from recommendations import *

df = pd.read_csv("facilities.csv")

st.title("Healthcare Service Discovery Platform")

page = st.sidebar.selectbox(
    "Choose Page",
    ["Home", "Search", "Dashboard"]
)

if page == "Home":

    st.header("Welcome")

    st.write(
        "Find Healthcare Facilities in Bengaluru"
    )

    st.metric(
        "Total Facilities",
        len(df)
    )

elif page == "Search":

    st.header("Search Facilities")

    service = st.selectbox(
        "Select Service",
        get_available_services()
    )

    area = st.selectbox(
        "Select Area",
        get_available_areas()
    )

    if st.button("Search"):

        results = recommend_by_area(
            service,
            area
        )

        st.dataframe(
            results[
                [
                    "facility_name",
                    "facility_type",
                    "area",
                    "phone"
                ]
            ]
        )

elif page == "Dashboard":

    st.header("Analytics Dashboard")

    facility_count = (
        df["facility_type"]
        .value_counts()
    )

    fig, ax = plt.subplots()

    facility_count.plot(
        kind="bar",
        ax=ax
    )

    st.pyplot(fig)