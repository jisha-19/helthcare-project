import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from recommendations import *

# ---------------------------
# PAGE CONFIG
# ---------------------------

st.set_page_config(
    page_title="Healthcare Service Discovery",
    page_icon="🏥",
    layout="wide"
)

# ---------------------------
# CUSTOM CSS
# ---------------------------

st.markdown("""
<style>

.main-title {
    text-align: center;
    padding: 20px;
}

.metric-container {
    text-align: center;
}

.result-card {
    padding: 15px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# LOAD DATA
# ---------------------------

df = pd.read_csv("facilities.csv")

# ---------------------------
# SIDEBAR
# ---------------------------

st.sidebar.title("🏥 Healthcare Menu")

page = st.sidebar.selectbox(
    "Navigation",
    [
        "Home",
        "Search Service",
        "Analytics Dashboard"
    ]
)

# ===================================================
# HOME PAGE
# ===================================================

if page == "Home":

    st.markdown("""
    <div class="main-title">
        <h1>🏥 Healthcare Service Discovery Platform</h1>
        <h4>Bengaluru Healthcare Resource Navigator</h4>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        """
        This platform helps users discover healthcare facilities
        based on required healthcare services such as:

        • Blood Tests 
        • MRI Scans 
        • CT Scans 
        • Blood Banks 
        • Dialysis Services 
        • Physiotherapy Services 
        """
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🏥 Total Facilities",
            len(df)
        )

    with col2:
        st.metric(
            "📍 Areas Covered",
            df["area"].nunique()
        )

    with col3:
        st.metric(
            "🔬 Facility Types",
            df["facility_type"].nunique()
        )

    st.divider()

    st.subheader("Available Healthcare Services")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.success("🩸 Blood Test")
        st.success("🔍 MRI")

    with c2:
        st.success("🖥️ CT Scan")
        st.success("💉 Dialysis")

    with c3:
        st.success("🏃 Physiotherapy")
        st.success("🩸 Blood Bank")

# ===================================================
# SEARCH PAGE
# ===================================================

elif page == "Search Service":

    st.title("🔍 Search Healthcare Facilities")

    service = st.selectbox(
        "Select Required Service",
        get_available_services()
    )

    area = st.selectbox(
        "Select Area",
        get_available_areas()
    )

    if st.button("Search Facilities"):

        results = recommend_by_area(
            service,
            area
        )

        if results.empty:

            st.error(
                f"No facilities found for {service} in {area}."
            )

        else:

            st.success(
                f"✅ Found {len(results)} facilities offering {service} in {area}"
            )

            st.divider()

            facility_icons = {
                "Hospital": "🏥",
                "Blood Bank": "🩸",
                "Diagnostic Lab": "🔬",
                "Dialysis Centre": "💉",
                "Physiotherapy Centre": "🏃",
                "Clinic": "🩺"
            }

            for _, row in results.iterrows():

                icon = facility_icons.get(
                    row["facility_type"],
                    "📍"
                )

                with st.container(border=True):

                    st.subheader(
                        f"{icon} {row['facility_name']}"
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(
                            f"**Facility Type:** {row['facility_type']}"
                        )

                        st.write(
                            f"**Area:** {row['area']}"
                        )

                    with col2:
                        st.write(
                            f"**Phone:** {row['phone']}"
                        )

                    st.write(
                        f"**Address:** {row['address']}"
                    )

                    st.write("**Services Offered:**")

                    services = str(
                        row["services"]
                    ).split(",")

                    badge_cols = st.columns(
                        min(4, len(services))
                    )

                    for i, service_name in enumerate(services):

                        badge_cols[
                            i % len(badge_cols)
                        ].success(
                            service_name.strip()
                        )

                    maps_link = (
                        "https://www.google.com/maps/search/?api=1&query="
                        + str(row["address"])
                    )

                    st.link_button(
                        "📍 View on Google Maps",
                        maps_link
                    )

# ===================================================
# ANALYTICS PAGE
# ===================================================

elif page == "Analytics Dashboard":

    st.title("📊 Analytics Dashboard")

    facility_count = (
        df["facility_type"]
        .value_counts()
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Most Common Facility Type",
            facility_count.idxmax()
        )

    with col2:
        st.metric(
            "Total Categories",
            len(facility_count)
        )

    st.divider()

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )

    facility_count.plot(
        kind="bar",
        color="teal",
        ax=ax
    )

    ax.set_title(
        "Healthcare Facilities by Type"
    )

    ax.set_xlabel(
        "Facility Type"
    )

    ax.set_ylabel(
        "Count"
    )

    plt.xticks(rotation=30)

    st.pyplot(fig)

    st.divider()

    area_count = (
        df["area"]
        .value_counts()
        .head(10)
    )

    st.subheader(
        "Top Areas by Facility Availability"
    )

    fig2, ax2 = plt.subplots(
        figsize=(8, 5)
    )

    area_count.plot(
        kind="bar",
        color="orange",
        ax=ax2
    )

    ax2.set_title(
        "Healthcare Facilities By Area"
    )

    ax2.set_xlabel(
        "Area"
    )

    ax2.set_ylabel(
        "Facility Count"
    )

    plt.xticks(rotation=45)

    st.pyplot(fig2)

# ===================================================
# FOOTER
# ===================================================

st.divider()

st.caption(
    "Healthcare Service Discovery Platform | Bengaluru Prototype"
)