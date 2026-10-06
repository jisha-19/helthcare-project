import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from recommendations import *

st.set_page_config(
    page_title="Healthcare Service Discovery",
    page_icon="🏥",
    layout="wide"
)

df = pd.read_csv("facilities.csv")

st.sidebar.title("🏥 Healthcare Menu")

page = st.sidebar.selectbox(
    "Navigation",
    ["Home", "Search Service", "Analytics Dashboard"]
)

if page == "Home":

    st.title("🏥 Healthcare Service Discovery Platform")

    st.markdown(
        """
        ### Bengaluru Healthcare Recommendation System

        Find:

        - Blood Test
        - MRI
        - CT Scan
        - Blood Bank
        - Dialysis
        - Physiotherapy
        """
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Facilities",
            len(df)
        )

    with col2:
        st.metric(
            "Areas Covered",
            df["area"].nunique()
        )

    with col3:
        st.metric(
            "Facility Types",
            df["facility_type"].nunique()
        )

    st.subheader("Available Services")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("Blood Test")

    with col2:
        st.success("MRI")

    with col3:
        st.success("CT Scan")

    col4, col5, col6 = st.columns(3)

    with col4:
        st.success("Blood Bank")

    with col5:
        st.success("Dialysis")

    with col6:
        st.success("Physiotherapy")

elif page == "Search Service":

    st.title("Search Healthcare Facilities")

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

        if results.empty:
            st.error("No facilities found")

        else:

            st.success(
                f"{len(results)} facilities found"
            )

            for _, row in results.iterrows():

                st.subheader(
                    row["facility_name"]
                )

                st.write(
                    f"Type: {row['facility_type']}"
                )

                st.write(
                    f"Area: {row['area']}"
                )

                st.write(
                    f"Phone: {row['phone']}"
                )

                st.write(
                    f"Address: {row['address']}"
                )

                st.write(
                    f"Services: {row['services']}"
                )

                st.divider()

elif page == "Analytics Dashboard":

    st.title("Analytics Dashboard")

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

st.divider()

st.caption(
    "Healthcare Service Discovery Platform | Bengaluru Prototype"
)