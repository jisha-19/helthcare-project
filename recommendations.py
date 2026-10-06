import pandas as pd
from difflib import get_close_matches


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv("facilities.csv")


# ============================================================
# SERVICE ALIASES
# ============================================================

service_aliases = {
    "blood test": [
        "blood test",
        "blood testing",
        "blood investigation",
        "laboratory blood test",
        "blood screening"
    ],

    "mri": [
        "mri",
        "mri scan",
        "magnetic resonance imaging",
        "magnetic resonance scan"
    ],

    "ct scan": [
        "ct scan",
        "ct",
        "computed tomography",
        "computed tomography scan",
        "cat scan"
    ],

    "blood donation": [
        "blood donation",
        "blood donor",
        "blood donation service",
        "blood bank"
    ],

    "dialysis": [
        "dialysis",
        "hemodialysis",
        "haemodialysis",
        "kidney dialysis",
        "dialysis treatment"
    ],

    "physiotherapy": [
        "physiotherapy",
        "physical therapy",
        "physio",
        "physiotherapy treatment",
        "physical rehabilitation",
        "rehabilitation therapy",
        "physio therapy"
    ]
}


# ============================================================
# SERVICE → SUITABLE FACILITY TYPES
# ============================================================

service_mapping = {
    "blood test": [
        "Hospital",
        "Diagnostic Laboratory",
        "Diagnostic Lab",
        "Multispecialty Diagnostic Center",
        "Diagnostic Centre",
        "Diagnostic Center"
    ],

    "mri": [
        "Hospital",
        "Diagnostic Imaging Center",
        "Hospital Imaging Center",
        "Multispecialty Diagnostic Center",
        "Diagnostic Centre",
        "Diagnostic Center"
    ],

    "ct scan": [
        "Hospital",
        "Diagnostic Imaging Center",
        "Hospital Imaging Center",
        "Multispecialty Diagnostic Center",
        "Diagnostic Centre",
        "Diagnostic Center"
    ],

    "blood donation": [
        "Blood Bank",
        "Voluntary Blood Bank",
        "Hospital Blood Bank",
        "Voluntary Blood Centre",
        "Blood Centre",
        "Blood Center"
    ],

    "dialysis": [
        "Dialysis Centre",
        "Dialysis Center",
        "Hospital Dialysis Unit",
        "NGO Dialysis Centre",
        "NGO Dialysis Center"
    ],

    "physiotherapy": [
        "Physiotherapy Clinic",
        "Physiotherapy Centre",
        "Physiotherapy Center",
        "Physiotherapy & Spine Clinic",
        "Physiotherapy & Rehab Centre",
        "Physiotherapy & Rehab Center"
    ]
}


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(value):

    if pd.isna(value):
        return ""

    value = str(value).strip().lower()

    return " ".join(
        value.split()
    )


# ============================================================
# SERVICE CANONICALIZATION
# ============================================================

def get_canonical_service(service):

    service = clean_text(service)

    # Exact canonical service
    if service in service_aliases:
        return service

    # Exact alias
    for canonical_service, aliases in service_aliases.items():

        for alias in aliases:

            if service == clean_text(alias):
                return canonical_service

    # Fuzzy matching for small typos
    all_options = []

    for canonical_service, aliases in service_aliases.items():

        all_options.append(canonical_service)
        all_options.extend(aliases)

    matches = get_close_matches(
        service,
        all_options,
        n=1,
        cutoff=0.70
    )

    if matches:

        matched_value = matches[0]

        for canonical_service, aliases in service_aliases.items():

            if matched_value == canonical_service:
                return canonical_service

            if matched_value in aliases:
                return canonical_service

    return None


# ============================================================
# SERVICE CHECK
# ============================================================

def has_service(services, requested_service):

    requested_service = get_canonical_service(
        requested_service
    )

    if requested_service is None:
        return False

    if pd.isna(services):
        return False

    facility_services = str(
        services
    ).split(",")

    for service in facility_services:

        facility_service = get_canonical_service(
            service
        )

        if facility_service == requested_service:
            return True

    return False


# ============================================================
# AVAILABLE SERVICES
# ============================================================

def get_available_services():

    services = set()

    for service_list in df["services"].dropna():

        for service in str(
            service_list
        ).split(","):

            canonical = get_canonical_service(
                service
            )

            if canonical:
                services.add(canonical)

    return sorted(services)


# ============================================================
# AVAILABLE AREAS
# ============================================================

def get_available_areas():

    areas = set()

    for area in df["area"].dropna():

        area = str(area).strip()

        if area:
            areas.add(area)

    return sorted(areas)


# ============================================================
# FIND AREA
# Handles small spelling differences
# ============================================================

def get_matching_area(area):

    area = clean_text(area)

    if not area:
        return None

    available_areas = get_available_areas()

    cleaned_areas = {
        clean_text(value): value
        for value in available_areas
    }

    # Exact match
    if area in cleaned_areas:
        return cleaned_areas[area]

    # Partial match
    for cleaned_area, original_area in cleaned_areas.items():

        if area in cleaned_area:
            return original_area

        if cleaned_area in area:
            return original_area

    # Fuzzy match
    matches = get_close_matches(
        area,
        list(cleaned_areas.keys()),
        n=1,
        cutoff=0.70
    )

    if matches:
        return cleaned_areas[matches[0]]

    return None


# ============================================================
# AVAILABLE FACILITY TYPES
# ============================================================

def get_facility_types():

    types = set()

    for facility_type in df["facility_type"].dropna():

        facility_type = str(
            facility_type
        ).strip()

        if facility_type:
            types.add(facility_type)

    return sorted(types)


# ============================================================
# FACILITY TYPE SUITABILITY
# ============================================================

def calculate_facility_type_score(
    facility_type,
    requested_service
):

    requested_service = get_canonical_service(
        requested_service
    )

    if requested_service is None:
        return 0

    facility_type = clean_text(
        facility_type
    )

    allowed_types = service_mapping.get(
        requested_service,
        []
    )

    allowed_types = [
        clean_text(value)
        for value in allowed_types
    ]

    # Exact suitable type
    if facility_type in allowed_types:
        return 100

    # Partial type match
    for allowed_type in allowed_types:

        if allowed_type in facility_type:
            return 80

        if facility_type in allowed_type:
            return 80

    # Service is still valid because the service
    # column is the main source of truth.
    return 50


# ============================================================
# SEARCH BY SERVICE
# ============================================================

def search_by_service(service):

    canonical_service = get_canonical_service(
        service
    )

    if canonical_service is None:
        return pd.DataFrame(
            columns=df.columns
        )

    results = df[
        df["services"].apply(
            lambda x:
            has_service(
                x,
                canonical_service
            )
        )
    ].copy()

    return results.reset_index(
        drop=True
    )


# ============================================================
# SEARCH BY SERVICE + AREA
# ============================================================

def search_by_service_area(
    service,
    area
):

    canonical_service = get_canonical_service(
        service
    )

    matching_area = get_matching_area(
        area
    )

    if canonical_service is None:
        return pd.DataFrame(
            columns=df.columns
        )

    if matching_area is None:
        return pd.DataFrame(
            columns=df.columns
        )

    cleaned_area = clean_text(
        matching_area
    )

    results = df[
        df["services"].apply(
            lambda x:
            has_service(
                x,
                canonical_service
            )
        )
        &
        df["area"].apply(
            lambda x:
            cleaned_area in clean_text(x)
        )
    ].copy()

    return results.reset_index(
        drop=True
    )


# ============================================================
# RECOMMEND BY SERVICE
# ============================================================

def recommend(service):

    return search_by_service(
        service
    )


# ============================================================
# RECOMMEND BY SERVICE + AREA
# ============================================================

def recommend_by_area(
    service,
    area,
    facility_type=None,
    sort_by="recommendation",
    top_n=None
):

    canonical_service = get_canonical_service(
        service
    )

    matching_area = get_matching_area(
        area
    )

    # Invalid service
    if canonical_service is None:
        return pd.DataFrame(
            columns=df.columns
        )

    # Invalid area
    if matching_area is None:
        return pd.DataFrame(
            columns=df.columns
        )

    cleaned_area = clean_text(
        matching_area
    )

    # ========================================================
    # SERVICE + AREA FILTER
    # ========================================================

    results = df[
        df["services"].apply(
            lambda x:
            has_service(
                x,
                canonical_service
            )
        )
        &
        df["area"].apply(
            lambda x:
            cleaned_area in clean_text(x)
        )
    ].copy()


    # ========================================================
    # FACILITY TYPE FILTER
    # ========================================================

    if facility_type:

        cleaned_type = clean_text(
            facility_type
        )

        results = results[
            results["facility_type"].apply(
                lambda x:
                clean_text(x) == cleaned_type
            )
        ]


    # ========================================================
    # RECOMMENDATION SCORE
    # ========================================================

    if not results.empty:

        results["facility_type_score"] = results[
            "facility_type"
        ].apply(
            lambda x:
            calculate_facility_type_score(
                x,
                canonical_service
            )
        )

        # Service is already matched,
        # so give service match the larger weight.
        results["recommendation_score"] = (
            results["facility_type_score"] * 0.30
        ) + 70


    # ========================================================
    # SORTING
    # ========================================================

    if sort_by == "recommendation":

        if "recommendation_score" in results.columns:

            results = results.sort_values(
                by="recommendation_score",
                ascending=False
            )

    elif sort_by == "name":

        results = results.sort_values(
            by="facility_name"
        )

    elif sort_by == "type":

        results = results.sort_values(
            by="facility_type"
        )

    elif sort_by == "area":

        results = results.sort_values(
            by="area"
        )


    # ========================================================
    # TOP N
    # ========================================================

    if top_n is not None:

        results = results.head(
            top_n
        )


    return results.reset_index(
        drop=True
    )


# ============================================================
# SEARCH FACILITY BY NAME
# ============================================================

def search_facility(
    facility_name
):

    facility_name = clean_text(
        facility_name
    )

    if not facility_name:
        return pd.DataFrame(
            columns=df.columns
        )

    results = df[
        df["facility_name"].apply(
            lambda x:
            facility_name in clean_text(x)
        )
    ].copy()

    return results.reset_index(
        drop=True
    )


# ============================================================
# GET FACILITY DETAILS
# ============================================================

def get_facility_details(
    service=None,
    area=None,
    facility_name=None
):

    results = df.copy()


    # ========================================================
    # SERVICE FILTER
    # ========================================================

    if service:

        canonical_service = get_canonical_service(
            service
        )

        if canonical_service is None:

            return []

        results = results[
            results["services"].apply(
                lambda x:
                has_service(
                    x,
                    canonical_service
                )
            )
        ]


    # ========================================================
    # AREA FILTER
    # ========================================================

    if area:

        matching_area = get_matching_area(
            area
        )

        if matching_area is None:

            return []

        cleaned_area = clean_text(
            matching_area
        )

        results = results[
            results["area"].apply(
                lambda x:
                cleaned_area in clean_text(x)
            )
        ]


    # ========================================================
    # FACILITY NAME FILTER
    # ========================================================

    if facility_name:

        facility_name = clean_text(
            facility_name
        )

        results = results[
            results["facility_name"].apply(
                lambda x:
                facility_name in clean_text(x)
            )
        ]


    # ========================================================
    # RETURN DETAILS
    # ========================================================

    return results[
        [
            "facility_id",
            "facility_name",
            "facility_type",
            "area",
            "address",
            "phone",
            "services"
        ]
    ].to_dict(
        orient="records"
    )