from pathlib import Path
from difflib import get_close_matches
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(BASE_DIR / "facilities.csv", dtype={"phone": str})
pathway_df = pd.read_csv(BASE_DIR / "care_pathways.csv")
medicine_df = pd.read_csv(BASE_DIR / "medicines.csv")

df["phone"] = df["phone"].fillna("Not Available").astype(str).str.strip()
medicine_df["price_inr"] = pd.to_numeric(medicine_df["price_inr"], errors="coerce").fillna(0.0)


# ============================================================
# SERVICE ALIASES & FACILITY MAPPING
# ============================================================

service_aliases = {
    "blood test": ["blood test", "blood testing", "blood investigation", "laboratory blood test", "blood screening"],
    "mri": ["mri", "mri scan", "magnetic resonance imaging", "magnetic resonance scan"],
    "ct scan": ["ct scan", "ct", "computed tomography", "computed tomography scan", "cat scan"],
    "blood donation": ["blood donation", "blood donor", "blood donation service", "blood bank"],
    "dialysis": ["dialysis", "hemodialysis", "haemodialysis", "kidney dialysis", "dialysis treatment"],
    "physiotherapy": [
        "physiotherapy", "physical therapy", "physio", "physiotherapy treatment",
        "physical rehabilitation", "rehabilitation therapy", "physio therapy"
    ],
    "x-ray": ["x-ray", "xray", "radiography", "digital x-ray"],
    "general consultation": ["general consultation", "general practitioner", "gp consultation", "primary care consultation", "consultation"],
    "orthopaedic consultation": ["orthopaedic consultation", "orthopedic consultation", "ortho consultation", "orthopaedic checkup"],
    "nephrology consultation": ["nephrology consultation", "kidney consultation", "nephrologist visit"],
    "follow-up": ["follow-up", "follow up", "post-op checkup", "review consultation"],
}

service_mapping = {
    "blood test": ["Hospital", "Diagnostic Laboratory", "Diagnostic Lab", "Multispecialty Diagnostic Center", "Diagnostic Centre", "Diagnostic Center"],
    "mri": ["Hospital", "Diagnostic Imaging Center", "Hospital Imaging Center", "Multispecialty Diagnostic Center", "Diagnostic Centre", "Diagnostic Center"],
    "ct scan": ["Hospital", "Diagnostic Imaging Center", "Hospital Imaging Center", "Multispecialty Diagnostic Center", "Diagnostic Centre", "Diagnostic Center"],
    "blood donation": ["Blood Bank", "Voluntary Blood Bank", "Hospital Blood Bank", "Voluntary Blood Centre", "Blood Centre", "Blood Center"],
    "dialysis": ["Dialysis Centre", "Dialysis Center", "Hospital Dialysis Unit", "NGO Dialysis Centre", "NGO Dialysis Center"],
    "physiotherapy": ["Physiotherapy Clinic", "Physiotherapy Centre", "Physiotherapy Center", "Physiotherapy & Spine Clinic", "Physiotherapy & Rehab Centre", "Physiotherapy & Rehab Center"],
    "x-ray": ["Hospital", "Diagnostic Imaging Center", "Diagnostic Center", "Diagnostic Centre", "Multispecialty Diagnostic Center"],
    "general consultation": ["Hospital", "Clinic", "General Clinic", "Multispecialty Hospital", "Primary Health Center"],
    "orthopaedic consultation": ["Hospital", "Orthopaedic Clinic", "Orthopedic Clinic", "Multispecialty Hospital"],
    "nephrology consultation": ["Hospital", "Kidney Care Center", "Dialysis Centre", "Multispecialty Hospital"],
    "follow-up": ["Hospital", "Clinic", "General Clinic", "Multispecialty Hospital"],
}


# ============================================================
# HELPERS & DEDUPLICATION
# ============================================================

def clean_text(value):
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().lower().split())


def calculate_service_count(services):
    if pd.isna(services):
        return 0
    return len([s.strip() for s in str(services).split(",") if s.strip()])


def deduplicate_facilities(results_df):
    if results_df.empty:
        return results_df
    temp = results_df.copy()
    temp["_dedup_name"] = temp["facility_name"].apply(clean_text)
    temp["_dedup_address"] = temp["address"].apply(clean_text)
    temp = temp.drop_duplicates(subset=["_dedup_name", "_dedup_address"], keep="first")
    return temp.drop(columns=["_dedup_name", "_dedup_address"]).reset_index(drop=True)


def get_canonical_service(service):
    service = clean_text(service)
    if not service:
        return None
    if service in service_aliases:
        return service
    for canonical, aliases in service_aliases.items():
        if any(service == clean_text(a) for a in aliases):
            return canonical

    all_options = []
    for canonical, aliases in service_aliases.items():
        all_options.append(canonical)
        all_options.extend(aliases)

    matches = get_close_matches(service, all_options, n=1, cutoff=0.70)
    if matches:
        matched = matches[0]
        for canonical, aliases in service_aliases.items():
            if matched == canonical or matched in aliases:
                return canonical
    return None


def has_service(services, requested_service):
    req = get_canonical_service(requested_service)
    if req is None or pd.isna(services):
        return False
    return any(get_canonical_service(s) == req for s in str(services).split(","))


def calculate_match_score(facility_services, requested_services):
    if pd.isna(facility_services):
        return 0
    available = {
        get_canonical_service(s)
        for s in str(facility_services).split(",")
        if get_canonical_service(s)
    }
    return sum(1 for s in requested_services if get_canonical_service(s) in available)


# ============================================================
# DROPDOWN & LOOKUP HELPERS
# ============================================================

def get_available_services():
    found = set()
    for s_list in df["services"].dropna():
        for s in str(s_list).split(","):
            c = get_canonical_service(s)
            if c:
                found.add(c)
    return sorted(found)


def get_available_areas():
    return sorted(df["area"].dropna().astype(str).str.strip().loc[lambda s: s != ""].unique().tolist())


def get_facility_types():
    return sorted(df["facility_type"].dropna().astype(str).str.strip().loc[lambda s: s != ""].unique().tolist())


def get_available_pathways():
    if "condition" not in pathway_df.columns:
        return []
    return sorted(pathway_df["condition"].dropna().astype(str).str.strip().loc[lambda s: s != ""].unique().tolist())


def get_available_medicines():
    if "medicine_name" not in medicine_df.columns:
        return []
    return sorted(medicine_df["medicine_name"].dropna().astype(str).str.strip().loc[lambda s: s != ""].unique().tolist())


def get_matching_area(area):
    area = clean_text(area)
    if not area:
        return None
    cleaned_areas = {clean_text(v): v for v in get_available_areas()}
    if area in cleaned_areas:
        return cleaned_areas[area]
    for c_area, orig in cleaned_areas.items():
        if area in c_area or c_area in area:
            return orig
    matches = get_close_matches(area, list(cleaned_areas.keys()), n=1, cutoff=0.70)
    return cleaned_areas[matches[0]] if matches else None


def calculate_facility_type_score(facility_type, requested_service):
    req = get_canonical_service(requested_service)
    if req is None:
        return 0
    f_type = clean_text(facility_type)
    allowed = [clean_text(v) for v in service_mapping.get(req, [])]
    if f_type in allowed:
        return 100
    if any(a in f_type or f_type in a for a in allowed):
        return 80
    return 50


# ============================================================
# SEARCH & RECOMMENDATION FUNCTIONS
# ============================================================

def recommend_by_area(service, area=None, facility_type=None, sort_by="recommendation", top_n=None):
    canonical = get_canonical_service(service)
    if canonical is None:
        return pd.DataFrame(columns=df.columns)

    results = df[df["services"].apply(lambda x: has_service(x, canonical))].copy()

    if area and clean_text(area) != "all":
        matched_area = get_matching_area(area)
        if matched_area is None:
            return pd.DataFrame(columns=df.columns)
        c_area = clean_text(matched_area)
        results = results[results["area"].apply(lambda x: c_area in clean_text(x))]

    if facility_type and clean_text(facility_type) != "all":
        c_type = clean_text(facility_type)
        results = results[results["facility_type"].apply(lambda x: clean_text(x) == c_type)]

    results = deduplicate_facilities(results)

    if not results.empty:
        results["facility_type_score"] = results["facility_type"].apply(
            lambda x: calculate_facility_type_score(x, canonical)
        )
        results["service_count"] = results["services"].apply(calculate_service_count)
        results["recommendation_score"] = (results["facility_type_score"] * 0.7) + (results["service_count"] * 5)

        if sort_by == "recommendation":
            results = results.sort_values(by=["recommendation_score", "service_count"], ascending=False)
        elif sort_by == "name":
            results = results.sort_values(by="facility_name")
        elif sort_by == "type":
            results = results.sort_values(by="facility_type")
        elif sort_by == "area":
            results = results.sort_values(by="area")

    if top_n is not None:
        results = results.head(top_n)

    return results.reset_index(drop=True)


def recommend_multiple_services(services, area=None, top_n=None):
    valid = [get_canonical_service(s) for s in services if get_canonical_service(s)]
    if not valid:
        return pd.DataFrame(columns=df.columns)

    results = df.copy()
    if area and clean_text(area) != "all":
        matched_area = get_matching_area(area)
        if matched_area is None:
            return pd.DataFrame(columns=df.columns)
        c_area = clean_text(matched_area)
        results = results[results["area"].apply(lambda x: c_area in clean_text(x))]

    results = deduplicate_facilities(results)
    if results.empty:
        return results

    results["match_score"] = results["services"].apply(lambda x: calculate_match_score(x, valid))
    results = results[results["match_score"] > 0].copy()
    if results.empty:
        return results

    results["service_count"] = results["services"].apply(calculate_service_count)
    results["overall_score"] = (results["match_score"] * 100) + results["service_count"]
    results = results.sort_values(by="overall_score", ascending=False)

    if top_n:
        results = results.head(top_n)

    return results.reset_index(drop=True)


def search_facility(facility_name):
    q = clean_text(facility_name)
    if not q:
        return pd.DataFrame(columns=df.columns)
    results = df[df["facility_name"].apply(lambda x: q in clean_text(x))].copy()
    return deduplicate_facilities(results)


def get_care_pathway(condition):
    cond = clean_text(condition)
    pathway = pathway_df[pathway_df["condition"].str.lower() == cond]
    if pathway.empty:
        return None
    return pathway.iloc[0].to_dict()


def recommend_from_pathway(condition, area=None, top_n=None):
    pathway = get_care_pathway(condition)
    if pathway is None or pd.isna(pathway.get("steps")):
        return pd.DataFrame()
    steps = [s.strip() for s in str(pathway["steps"]).split(",") if s.strip()]
    return recommend_multiple_services(steps, area=area, top_n=top_n)


def medicine_lookup(query):
    q = clean_text(query)
    if not q:
        return pd.DataFrame(columns=medicine_df.columns)

    matches = medicine_df[
        medicine_df["medicine_name"].str.lower().str.contains(q, na=False, regex=False)
        | medicine_df["category"].str.lower().str.contains(q, na=False, regex=False)
        | medicine_df["common_uses"].str.lower().str.contains(q, na=False, regex=False)
    ].copy()

    if not matches.empty:
        return matches.reset_index(drop=True)

    token_map = {}
    for idx, row in medicine_df.iterrows():
        for token in str(row["medicine_name"]).split("/"):
            clean_tok = clean_text(token)
            if clean_tok:
                token_map[clean_tok] = idx

    close = get_close_matches(q, list(token_map.keys()), n=3, cutoff=0.65)
    if close:
        indices = list(dict.fromkeys(token_map[c] for c in close))
        return medicine_df.loc[indices].reset_index(drop=True)

    return pd.DataFrame(columns=medicine_df.columns)


def get_medicines_for_pathway(condition):
    cond = clean_text(condition)
    if not cond:
        return pd.DataFrame(columns=medicine_df.columns)
    return medicine_df[
        medicine_df["common_uses"].str.lower().str.contains(cond, na=False, regex=False)
    ].reset_index(drop=True)