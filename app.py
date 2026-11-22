from pathlib import Path
from urllib.parse import quote_plus
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
        padding: 2.25rem 2rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 1.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .hero-title {
        font-size: 2.35rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
        letter-spacing: -0.025em;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #cbd5e1;
        font-weight: 400;
    }
    .card-container {
        background: white;
        padding: 1.4rem;
        border-radius: 0.75rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
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
        display: inline-block;
    }
    .price-sub {
        display: block;
        color: #78350f;
        font-size: 0.72rem;
        margin-top: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

FACILITY_ICONS = {
    "Hospital": "🏥",
    "Multispeciality Hospital": "🏥",
    "Multispecialty Hospital": "🏥",
    "Teaching Hospital": "🏥",
    "Government Hospital": "🏥",
    "Women's Hospital": "🏥",
    "Women's & Children's Hospital": "🏥",
    "Children's Hospital": "🏥",
    "Speciality Hospital": "🏥",
    "Orthopaedic Hospital": "🦴",
    "Cardiac Hospital": "❤️",
    "Blood Bank": "🩸",
    "Voluntary Blood Bank": "🩸",
    "Voluntary Blood Centre": "🩸",
    "Hospital Blood Bank": "🩸",
    "Diagnostic Lab": "🔬",
    "Diagnostic Laboratory": "🔬",
    "Diagnostic Imaging Center": "🔬",
    "Hospital Imaging Center": "🔬",
    "Multispecialty Diagnostic Center": "🔬",
    "Hospital Diagnostic Centre": "🔬",
    "Speciality Diagnostic Centre": "🔬",
    "Dialysis Centre": "💉",
    "Dialysis Center": "💉",
    "Hospital Dialysis Unit": "💉",
    "NGO Dialysis Centre": "💉",
    "Physiotherapy Centre": "🏃",
    "Physiotherapy Clinic": "🏃",
    "Physiotherapy & Spine Clinic": "🏃",
    "Clinic": "🩺",
}


# ============================================================
# SAFE DATA, MAPS & BACKEND HELPERS
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


def get_gmaps_url(row):
    parts = [
        str(row.get("facility_name", "")).strip(),
        str(row.get("address", "")).strip(),
        str(row.get("area", "")).strip(),
        "Bengaluru",
    ]
    query = ", ".join([p for p in parts if p and p.lower() != "nan"])
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(query)}"


def get_facility_icon(facility_type):
    f_type = str(facility_type or "").strip()
    if f_type in FACILITY_ICONS:
        return FACILITY_ICONS[f_type]
    low = f_type.lower()
    if "blood" in low:
        return "🩸"
    if "dialysis" in low:
        return "💉"
    if "physio" in low:
        return "🏃"
    if "diag" in low or "imag" in low or "lab" in low:
        return "🔬"
    if "hospital" in low:
        return "🏥"
    if "clinic" in low:
        return "🩺"
    return "📍"


def render_classic_facility_card(row):
    icon = get_facility_icon(row.get("facility_type"))
    with st.container(border=True):
        st.subheader(f"{icon} {row['facility_name']}")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Facility Type:** {row['facility_type']}")
            st.write(f"**Area:** {row['area']}")
        with col2:
            st.write(f"**Phone:** {row['phone']}")

        st.write(f"**Address:** {row['address']}")
        st.write("**Services Offered:**")

        services = [s.strip() for s in str(row.get("services", "")).split(",") if s.strip()]
        if services:
            badge_cols = st.columns(min(4, len(services)))
            for i, service_name in enumerate(services):
                badge_cols[i % len(badge_cols)].success(service_name)

        st.link_button("📍 View on Google Maps", get_gmaps_url(row))


def render_styled_facility_card(row, compact=False):
    services_list = [s.strip() for s in str(row.get("services", "")).split(",") if s.strip()]
    services_pills = "".join([f"<span class='service-pill'>{s}</span>" for s in services_list])
    maps_url = get_gmaps_url(row)

    heading_tag = "h4" if compact else "h3"
    heading_style = "margin: 0.5rem 0; color: #1e293b;" if compact else "margin: 0.5rem 0; color: #1e293b; font-size: 1.25rem;"
    contact_line = (
        f"<p style='color: #64748b; font-size: 0.85rem; margin-bottom: 0.5rem;'>🏠 {row['address']} | 📞 {row['phone']}</p>"
        if compact
        else f"<p style='color: #64748b; margin-bottom: 0.5rem; font-size: 0.9rem;'>🏠 {row['address']}</p><p style='color: #0f172a; margin-bottom: 0.75rem; font-weight: 600;'>📞 Phone: {row['phone']}</p>"
    )
    services_block = services_pills if compact else f"<strong>Offered Services:</strong><br>{services_pills}"

    st.markdown(f"""
    <div class="card-container">
        <span class="badge-type">{row['facility_type']}</span>
        <span class="badge-area">📍 {row['area']}</span>
        <{heading_tag} style="{heading_style}">{row['facility_name']}</{heading_tag}>
        {contact_line}
        <div style="margin-top: 0.5rem;">
            {services_block}
        </div>
        <div style="margin-top: 0.75rem;">
            <a href="{maps_url}" target="_blank" rel="noopener noreferrer"
               style="display: inline-block; background-color: #1d4ed8; color: white; padding: 0.35rem 0.75rem; border-radius: 0.375rem; text-decoration: none; font-size: 0.85rem; font-weight: 600;">
                📍 View on Google Maps
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_medicine_card(med, compact=False):
    heading_tag = "h4" if compact else "h3"
    heading_style = "margin: 0.25rem 0; color: #1e293b;" if compact else "margin: 0.25rem 0; color: #1e293b; font-size: 1.15rem;"
    uses_html = (
        ""
        if compact
        else f"<p style='color: #475569; font-size: 0.8rem; margin-top: 0.25rem;'><em>Common Uses: {med['common_uses']}</em></p>"
    )

    card_html = (
        f'<div class="card-container" style="display: flex; justify-content: space-between; align-items: center;">'
        f'<div>'
        f'<span class="badge-type">{med["category"]}</span>'
        f'<{heading_tag} style="{heading_style}">{med["medicine_name"]}</{heading_tag}>'
        f'<p style="color: #64748b; font-size: 0.85rem; margin: 0;">Form: <strong>{med["dosage_form"]}</strong> | Pack: <strong>{med["unit"]}</strong></p>'
        f'{uses_html}'
        f'</div>'
        f'<div style="text-align: right; min-width: 130px;">'
        f'<span class="price-tag">₹{med["price_inr"]}</span>'
        f'<span class="price-sub">approximate MRP, may vary</span>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


# ============================================================
# HERO HEADER
# ============================================================
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🧭 CareCompass</div>
    <div class="hero-subtitle">Bengaluru Healthcare Facility Directory & Curated Care Pathways</div>
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
        "🗺️ Care Pathways",
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
# TAB 1: FACILITY SEARCH & FILTER (CLASSIC PROTOTYPE STYLE)
# ============================================================
if app_mode == "🏥 Facility Search & Filter":
    st.title("🔍 Search Healthcare Facilities")

    services_list = safe_call("get_available_services", default=[])
    areas_list = ["All"] + safe_call("get_available_areas", default=[])

    col1, col2 = st.columns(2)
    with col1:
        selected_service = st.selectbox("Select Required Service", services_list)
    with col2:
        selected_area = st.selectbox("Select Area", areas_list)

    if st.button("Search Facilities"):
        results = safe_call(
            "recommend_by_area",
            selected_service,
            selected_area,
            default=pd.DataFrame()
        )

        if results.empty:
            st.error(f"No facilities found for {selected_service} in {selected_area}.")
        else:
            st.success(f"✅ Found {len(results)} facilities offering {selected_service} in {selected_area}")
            st.divider()
            for _, row in results.iterrows():
                render_classic_facility_card(row)


# ============================================================
# TAB 2: CARE PATHWAYS
# ============================================================
elif app_mode == "🗺️ Care Pathways":
    st.markdown("### 🗺️ Care Pathways")
    st.markdown("Select a condition or checkup routine to view typical steps from our curated pathway list, matching facilities, and related medicines.")

    pathways_list = safe_call("get_available_pathways", default=[])
    if not pathways_list and not path_df.empty and "condition" in path_df.columns:
        pathways_list = sorted(path_df["condition"].dropna().astype(str).str.strip().unique().tolist())

    if not pathways_list:
        st.info("📄 Please place `care_pathways.csv` in your project folder to use Care Pathways.")
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
                st.markdown("#### 🛣️ Typical Steps (Curated Reference)")
                step_cols = st.columns(len(steps))
                for i, step in enumerate(steps):
                    with step_cols[i]:
                        st.markdown(f"""
                        <div style="border-left: 4px solid #2563eb; padding: 0.75rem; background: #eff6ff; border-radius: 0.375rem;">
                            <span style="font-size: 0.75rem; font-weight: 700; color: #1d4ed8;">TYPICAL STEP {i+1}</span>
                            <div style="font-weight: 600; color: #1e293b; text-transform: capitalize;">{step}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")
                tab_fac, tab_med = st.tabs([
                    "🏥 Facilities Offering Typical Steps",
                    "💊 Medicines commonly used for this condition (information only, never self-medicate)"
                ])

                with tab_fac:
                    facility_results = safe_call("recommend_from_pathway", selected_condition, area=selected_area, default=pd.DataFrame())
                    if facility_results.empty:
                        st.info("No single facility in this area covers all typical steps at once, but you can search individual services in Facility Search & Filter.")
                    else:
                        st.success(f"Found **{len(facility_results)}** facilities matching typical steps for this pathway.")
                        for _, row in facility_results.iterrows():
                            render_styled_facility_card(row, compact=True)

                with tab_med:
                    med_results = safe_call("get_medicines_for_pathway", selected_condition, default=pd.DataFrame())
                    if med_results.empty:
                        st.info("No medications linked to this condition in the local dataset.")
                    else:
                        st.caption("Prices shown are approximate MRP, may vary. Always consult a qualified healthcare professional.")
                        for _, med in med_results.iterrows():
                            render_medicine_card(med, compact=True)


# ============================================================
# TAB 3: MULTI-SERVICE PLANNER
# ============================================================
elif app_mode == "⚡ Multi-Service Planner":
    st.markdown("### ⚡ Multi-Service One-Stop Planner")
    st.markdown("Need multiple tests or consultations in a single visit? Select multiple services to find facilities that offer those services.")

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
                st.warning("⚠️ No facilities found covering these services in this area.")
            else:
                st.success(f"Found **{len(multi_results)}** facilities matching your selected services.")
                for _, row in multi_results.iterrows():
                    render_styled_facility_card(row, compact=False)


# ============================================================
# TAB 4: MEDICINE & COST LOOKUP
# ============================================================
elif app_mode == "💊 Medicine & Cost Lookup":
    st.markdown("### 💊 Medicine & Cost Explorer")
    st.markdown("Look up medicine names, categories, or common uses. Listed prices are **approximate MRP, may vary**.")

    if med_all_df.empty:
        st.info("📄 Please place `medicines.csv` in your project folder to use Medicine & Cost Lookup.")
    else:
        search_query = st.text_input("🔍 Search medicine (e.g., 'Paracetamol', 'Dolo', 'Antidiabetic', 'Insulin')", "")
        med_df = safe_call("medicine_lookup", search_query, default=med_all_df) if search_query else med_all_df

        if med_df.empty:
            st.info("No medicines matched your search query.")
        else:
            st.markdown(f"Showing **{len(med_df)}** medication entries (approximate MRP, may vary):")
            for _, med in med_df.iterrows():
                render_medicine_card(med, compact=False)


# ============================================================
# TAB 5: DIRECT FACILITY LOOKUP
# ============================================================
elif app_mode == "🏢 Direct Facility Lookup":
    st.markdown("### 🏢 Direct Facility & Branch Explorer")
    st.markdown("Look up a hospital, diagnostic chain, or blood bank by name to view listed branches and contact details.")

    facility_query = st.text_input("Hospital or Lab Name (e.g., 'Manipal', 'Fortis', 'Aster', 'Thyrocare')", "")

    if facility_query:
        fac_results = safe_call("search_facility", facility_query, default=pd.DataFrame())
        if fac_results.empty:
            st.warning("⚠️ No facility found with that name.")
        else:
            st.success(f"Found **{len(fac_results)}** matching branch locations.")
            for _, row in fac_results.iterrows():
                render_styled_facility_card(row, compact=False)
    else:
        st.info("💡 Type a hospital or lab name above to inspect its branches and services.")

st.divider()
st.caption(
    "Disclaimer: This app is for informational purposes only and is not medical advice. "
    "Facility listings, curated care pathway steps, and medicine prices (approximate MRP, may vary) "
    "may change; always verify details directly with providers and consult a qualified healthcare professional."
)
st.caption("CareCompass | Bengaluru Healthcare Directory & Curated Care Pathways")