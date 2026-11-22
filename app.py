from pathlib import Path
import streamlit as st
import pandas as pd
import recommendations as bk

BASE_DIR = Path(__file__).resolve().parent

# ============================================================
# PAGE CONFIGURATION & STYLING
# ============================================================
st.set_page_config(
    page_title="CareCompass | Bengaluru Healthcare Navigator",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 2.5rem 2rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.025em;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #cbd5e1;
        font-weight: 400;
    }
    .card-container {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border-color: #cbd5e1;
    }
    .badge-type {
        background-color: #eff6ff;
        color: #1d4ed8;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
        border: 1px solid #bfdbfe;
    }
    .badge-area {
        background-color: #f1f5f9;
        color: #475569;
        padding: 0.25rem 0.6rem;
        border-radius: 0.375rem;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .service-pill {
        background-color: #f0fdf4;
        color: #166534;
        padding: 0.15rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: 500;
        border: 1px solid #bbf7d0;
        display: inline-block;
        margin: 0.1rem;
    }
    .price-tag {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.25rem 0.6rem;
        border-radius: 0.375rem;
        font-weight: 700;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SAFE DATA & BACKEND HELPERS
# ============================================================
def _load_csv_if_exists(attr_name, filename):
    if hasattr(bk, attr_name) and isinstance(getattr(bk, attr_name), pd.DataFrame):
        return getattr(bk, attr_name)
    path = BASE_DIR / filename
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def get_facilities_df():
    return _load_csv_if_exists("df", "facilities.csv")


def get_pathways_df():
    return _load_csv_if_exists("pathway_df", "care_pathways.csv")


def get_medicines_df():
    return _load_csv_if_exists("medicine_df", "medicines.csv")


def safe_call(func_name, *args, default=None, **kwargs):
    fn = getattr(bk, func_name, None)
    if callable(fn):
        return fn(*args, **kwargs)
    return default


# ============================================================
# HERO HEADER
# ============================================================
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🧭 CareCompass</div>
    <div class="hero-subtitle">Intelligent Healthcare Facility Navigator & Clinical Care Pathways for Bengaluru</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR NAVIGATION & FILTERS
# ============================================================
st.sidebar.markdown("### 🎛️ Navigation Hub")
app_mode = st.sidebar.radio(
    "Choose Mode",
    [
        "🏥 Facility Search & Filter",
        "🗺️ Clinical Care Pathways",
        "⚡ Multi-Service Planner",
        "💊 Medicine & Cost Lookup",
        "🏢 Direct Facility Lookup"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dataset Overview")

fac_df = get_facilities_df()
path_df = get_pathways_df()
med_all_df = get_medicines_df()

facilities_count = len(fac_df)
pathways_count = len(safe_call("get_available_pathways", default=[])) or len(path_df)
medicines_count = len(safe_call("get_available_medicines", default=[])) or len(med_all_df)

st.sidebar.metric("Total Facilities", facilities_count)
st.sidebar.metric("Care Pathways", pathways_count)
st.sidebar.metric("Listed Medicines", medicines_count)

if not (BASE_DIR / "care_pathways.csv").exists():
    st.sidebar.caption("ℹ️ Add `care_pathways.csv` to enable Care Pathways.")
if not (BASE_DIR / "medicines.csv").exists():
    st.sidebar.caption("ℹ️ Add `medicines.csv` to enable Medicine Lookup.")


# ============================================================
# TAB 1: FACILITY SEARCH & FILTER
# ============================================================
if app_mode == "🏥 Facility Search & Filter":
    st.markdown("### 🏥 Find Healthcare Facilities")
    st.markdown("Search for hospitals, diagnostic labs, blood banks, dialysis units, and clinics across Bengaluru.")

    col1, col2, col3, col4 = st.columns(4)

    services_list = safe_call("get_available_services", default=[])
    areas_list = ["All"] + safe_call("get_available_areas", default=[])
    types_list = ["All"] + safe_call("get_facility_types", default=[])

    with col1:
        selected_service = st.selectbox("Select Service", services_list)
    with col2:
        selected_area = st.selectbox("Select Area", areas_list)
    with col3:
        selected_type = st.selectbox("Facility Type", types_list)
    with col4:
        sort_option = st.selectbox("Sort By", ["recommendation", "name", "type", "area"])

    if st.button("🔍 Search Facilities", type="primary", use_container_width=True):
        results = safe_call(
            "recommend_by_area",
            selected_service,
            selected_area,
            facility_type=selected_type,
            sort_by=sort_option,
            default=pd.DataFrame()
        )

        if results.empty:
            st.warning("⚠️ No matching facilities found for your selected criteria. Try changing the area or facility type filter.")
        else:
            st.success(f"Found **{len(results)}** matching facilities in Bengaluru.")
            for _, row in results.iterrows():
                services_pills = "".join([f"<span class='service-pill'>{s.strip()}</span>" for s in str(row['services']).split(",")])
                st.markdown(f"""
                <div class="card-container">
                    <span class="badge-type">{row['facility_type']}</span>
                    <span class="badge-area">📍 {row['area']}</span>
                    <h3 style="margin: 0.5rem 0; color: #1e293b; font-size: 1.25rem;">{row['facility_name']}</h3>
                    <p style="color: #64748b; margin-bottom: 0.5rem; font-size: 0.9rem;">🏠 {row['address']}</p>
                    <p style="color: #0f172a; margin-bottom: 0.75rem; font-weight: 600;">📞 Phone: {row['phone']}</p>
                    <div style="margin-top: 0.5rem;">
                        <strong>Offered Services:</strong><br>{services_pills}
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ============================================================
# TAB 2: CLINICAL CARE PATHWAYS
# ============================================================
elif app_mode == "🗺️ Clinical Care Pathways":
    st.markdown("### 🗺️ End-to-End Clinical Care Pathways")
    st.markdown("Select a medical condition or health checkup routine to view its standardized step-by-step roadmap, recommended facilities, and prescribed medicines.")

    pathways_list = safe_call("get_available_pathways", default=[])
    if not pathways_list and not path_df.empty and "condition" in path_df.columns:
        pathways_list = sorted(path_df["condition"].dropna().astype(str).str.strip().unique().tolist())

    if not pathways_list:
        st.info("📄 Please place `care_pathways.csv` in your project folder to use Clinical Care Pathways.")
    else:
        areas_list = ["All"] + safe_call("get_available_areas", default=[])
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_condition = st.selectbox("Select Condition / Health Goal", pathways_list)
        with col2:
            selected_area = st.selectbox("Filter by Area (Optional)", areas_list)

        if selected_condition:
            pathway_info = safe_call("get_care_pathway", selected_condition, default=None)
            if pathway_info is not None:
                steps = [s.strip() for s in str(pathway_info["steps"]).split(",") if s.strip()]
                st.markdown("#### 🛣️ Step-by-Step Care Roadmap")
                step_cols = st.columns(len(steps))
                for i, step in enumerate(steps):
                    with step_cols[i]:
                        st.markdown(f"""
                        <div style="border-left: 4px solid #2563eb; padding: 0.75rem; background: #eff6ff; border-radius: 0.375rem;">
                            <span style="font-size: 0.75rem; font-weight: 700; color: #1d4ed8;">STEP {i+1}</span>
                            <div style="font-weight: 600; color: #1e293b; text-transform: capitalize;">{step}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")
                tab_fac, tab_med = st.tabs(["🏥 Recommended Facilities for this Pathway", "💊 Commonly Prescribed Medicines"])

                with tab_fac:
                    facility_results = safe_call("recommend_from_pathway", selected_condition, area=selected_area, default=pd.DataFrame())
                    if facility_results.empty:
                        st.info("No single facility in this area covers all pathway steps simultaneously, but you can search individual steps in Tab 1.")
                    else:
                        st.success(f"Found **{len(facility_results)}** top-tier facilities matching this clinical journey.")
                        for _, row in facility_results.iterrows():
                            services_pills = "".join([f"<span class='service-pill'>{s.strip()}</span>" for s in str(row['services']).split(",")])
                            st.markdown(f"""
                            <div class="card-container">
                                <span class="badge-type">{row['facility_type']}</span>
                                <span class="badge-area">📍 {row['area']}</span>
                                <h4 style="margin: 0.5rem 0; color: #1e293b;">{row['facility_name']}</h4>
                                <p style="color: #64748b; font-size: 0.85rem;">🏠 {row['address']} | 📞 {row['phone']}</p>
                                <div>{services_pills}</div>
                            </div>
                            """, unsafe_allow_html=True)

                with tab_med:
                    med_results = safe_call("get_medicines_for_pathway", selected_condition, default=pd.DataFrame())
                    if med_results.empty:
                        st.info("No specific medications linked directly to this pathway in the database.")
                    else:
                        for _, med in med_results.iterrows():
                            st.markdown(f"""
                            <div class="card-container" style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <span class="badge-type">{med['category']}</span>
                                    <h4 style="margin: 0.25rem 0; color: #1e293b;">{med['medicine_name']}</h4>
                                    <p style="color: #64748b; font-size: 0.85rem; margin: 0;">Form: <strong>{med['dosage_form']}</strong> ({med['unit']})</p>
                                </div>
                                <div>
                                    <span class="price-tag">₹{med['price_inr']}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)


# ============================================================
# TAB 3: MULTI-SERVICE PLANNER
# ============================================================
elif app_mode == "⚡ Multi-Service Planner":
    st.markdown("### ⚡ Multi-Service One-Stop Planner")
    st.markdown("Need multiple tests or consultations in a single visit? Select multiple services to find facilities that cover all your requirements.")

    all_services = safe_call("get_available_services", default=[])
    selected_services = st.multiselect("Select Required Services", all_services, default=all_services[:2] if len(all_services) >= 2 else all_services)

    areas_list = ["All"] + safe_call("get_available_areas", default=[])
    selected_area = st.selectbox("Preferred Area", areas_list)

    if st.button("🚀 Find One-Stop Facilities", type="primary", use_container_width=True):
        if not selected_services:
            st.warning("⚠️ Please select at least one service.")
        else:
            multi_results = safe_call("recommend_multiple_services", selected_services, area=selected_area, default=pd.DataFrame())
            if multi_results.empty:
                st.warning("⚠️ No facilities found covering these exact combinations in this area.")
            else:
                st.success(f"Found **{len(multi_results)}** facilities capable of handling your multi-service requirements.")
                for _, row in multi_results.iterrows():
                    services_pills = "".join([f"<span class='service-pill'>{s.strip()}</span>" for s in str(row['services']).split(",")])
                    st.markdown(f"""
                    <div class="card-container">
                        <span class="badge-type">{row['facility_type']}</span>
                        <span class="badge-area">📍 {row['area']}</span>
                        <h3 style="margin: 0.5rem 0; color: #1e293b;">{row['facility_name']}</h3>
                        <p style="color: #64748b; font-size: 0.9rem;">🏠 {row['address']} | 📞 {row['phone']}</p>
                        <div>{services_pills}</div>
                    </div>
                    """, unsafe_allow_html=True)


# ============================================================
# TAB 4: MEDICINE & COST LOOKUP
# ============================================================
elif app_mode == "💊 Medicine & Cost Lookup":
    st.markdown("### 💊 Medicine & Cost Explorer")
    st.markdown("Look up brand names, generic formulations, categories, or therapeutic uses with transparent pricing (INR).")

    if med_all_df.empty:
        st.info("📄 Please place `medicines.csv` in your project folder to use Medicine & Cost Lookup.")
    else:
        search_query = st.text_input("🔍 Search medicine (e.g., 'Paracetamol', 'Dolo', 'Antidiabetic', 'Insulin')", "")
        med_df = safe_call("medicine_lookup", search_query, default=med_all_df) if search_query else med_all_df

        if med_df.empty:
            st.info("No medicines matched your search query.")
        else:
            st.markdown(f"Showing **{len(med_df)}** medication options:")
            for _, med in med_df.iterrows():
                st.markdown(f"""
                <div class="card-container" style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="badge-type">{med['category']}</span>
                        <h3 style="margin: 0.25rem 0; color: #1e293b; font-size: 1.15rem;">{med['medicine_name']}</h3>
                        <p style="color: #64748b; font-size: 0.85rem; margin: 0;">Form: <strong>{med['dosage_form']}</strong> | Pack: <strong>{med['unit']}</strong></p>
                        <p style="color: #475569; font-size: 0.8rem; margin-top: 0.25rem;"><em>Common Uses: {med['common_uses']}</em></p>
                    </div>
                    <div style="text-align: right; min-width: 100px;">
                        <span class="price-tag">₹{med['price_inr']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ============================================================
# TAB 5: DIRECT FACILITY LOOKUP
# ============================================================
elif app_mode == "🏢 Direct Facility Lookup":
    st.markdown("### 🏢 Direct Facility & Branch Explorer")
    st.markdown("Look up a specific hospital, diagnostic chain, or blood bank by name to view all its branches and contact details.")

    facility_query = st.text_input("Hospital or Lab Name (e.g., 'Manipal', 'Fortis', 'Aster', 'Thyrocare')", "")

    if facility_query:
        fac_results = safe_call("search_facility", facility_query, default=pd.DataFrame())
        if fac_results.empty:
            st.warning("⚠️ No facility found with that name.")
        else:
            st.success(f"Found **{len(fac_results)}** matching branch locations.")
            for _, row in fac_results.iterrows():
                services_pills = "".join([f"<span class='service-pill'>{s.strip()}</span>" for s in str(row['services']).split(",")])
                st.markdown(f"""
                <div class="card-container">
                    <span class="badge-type">{row['facility_type']}</span>
                    <span class="badge-area">📍 {row['area']}</span>
                    <h3 style="margin: 0.5rem 0; color: #1e293b;">{row['facility_name']}</h3>
                    <p style="color: #64748b; font-size: 0.9rem;">🏠 {row['address']}</p>
                    <p style="color: #0f172a; font-weight: 600;">📞 {row['phone']}</p>
                    <div style="margin-top: 0.5rem;">{services_pills}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("💡 Type a hospital or lab name above to inspect its branches and services.")