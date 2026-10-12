import pandas as pd
from difflib import get_close_matches


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv("facilities.csv")
pathway_df = pd.read_csv("care_pathways.csv")
medicine_df = pd.read_csv("medicines.csv")


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
    ],
    "x-ray": [
        "x-ray",
        "xray",
        "radiography",
        "digital x-ray"
    ],
    "general consultation": [
        "general consultation",
        "general practitioner",
        "gp consultation",
        "primary care consultation",
        "consultation"
    ],
    "orthopaedic consultation": [
        "orthopaedic consultation",
        "orthopedic consultation",
        "ortho consultation",
        "orthopaedic checkup"
    ],
    "nephrology consultation": [
        "nephrology consultation",
        "kidney consultation",
        "nephrologist visit"
    ],
    "follow-up": [
        "follow-up",
        "follow up",
        "post-op checkup",
        "review consultation"
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
    ],
    "x-ray": [
        "Hospital",
        "Diagnostic Imaging Center",
        "Diagnostic Center",
        "Diagnostic Centre",
        "Multispecialty Diagnostic Center"
    ],
    "general consultation": [
        "Hospital",
        "Clinic",
        "General Clinic",
        "Multispecialty Hospital",
        "Primary Health Center"
    ],
    "orthopaedic consultation": [
        "Hospital",
        "Orthopaedic Clinic",
        "Orthopedic Clinic",
        "Multispecialty Hospital"
    ],
    "nephrology consultation": [
        "Hospital",
        "Kidney Care Center",
        "Dialysis Centre",
        "Multispecialty Hospital"
    ],
    "follow-up": [
        "Hospital",
        "Clinic",
        "General Clinic",
        "Multispecialty Hospital"
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

        results["service_count"] = results["services"].apply( calculate_service_count )

        results["recommendation_score"] = (
        (results["facility_type_score"] * 0.7) +(results["service_count"] * 5)
)

    # ========================================================
    # SORTING
    # ========================================================

    if sort_by == "recommendation":

        if "recommendation_score" in results.columns:

          results = results.sort_values(
        by=[
            "recommendation_score",
            "service_count"
        ],
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
# ============================================================
# SERVICE COUNT
# ============================================================

def calculate_service_count(
    services
):

    if pd.isna(services):
        return 0

    return len(
        [
            service.strip()
            for service in str(
                services
            ).split(",")
            if service.strip()
        ]
    )
# ============================================================
# MULTI SERVICE MATCH SCORE
# ============================================================

def calculate_match_score(
    facility_services,
    requested_services
):

    if pd.isna(facility_services):
        return 0

    available_services = []

    for service in str(
        facility_services
    ).split(","):

        canonical = get_canonical_service(
            service
        )

        if canonical:
            available_services.append(
                canonical
            )

    matches = 0

    for service in requested_services:

        canonical = get_canonical_service(
            service
        )

        if canonical in available_services:
            matches += 1

    return matches

# ============================================================
# MULTI SERVICE RECOMMENDATION
# ============================================================

def recommend_multiple_services(
    services,
    area=None,
    top_n=None
):

    results = df.copy()

    valid_services = []

    for service in services:

        canonical = get_canonical_service(
            service
        )

        if canonical:
            valid_services.append(
                canonical
            )

    if not valid_services:

        return pd.DataFrame(
            columns=df.columns
        )

    if area:

        matching_area = get_matching_area(
            area
        )

        if matching_area:

            cleaned_area = clean_text(
                matching_area
            )

            results = results[
                results["area"].apply(
                    lambda x:
                    cleaned_area
                    in clean_text(x)
                )
            ]

    results["match_score"] = results[
        "services"
    ].apply(
        lambda x:
        calculate_match_score(
            x,
            valid_services
        )
    )

    results = results[
        results["match_score"] > 0
    ]

    results["service_count"] = results[
        "services"
    ].apply(
        calculate_service_count
    )

    results["overall_score"] = (
        (results["match_score"] * 100)
        +
        results["service_count"]
    )

    results = results.sort_values(
        by="overall_score",
        ascending=False
    )

    if top_n:

        results = results.head(
            top_n
        )

    return results.reset_index(
        drop=True
    )
# ============================================================
# LOAD CARE PATHWAYS & MEDICINES DATA
# ============================================================

pathway_df = pd.read_csv("care_pathways.csv")
medicine_df = pd.read_csv("medicines.csv")


# ============================================================
# 3. CARE PATHWAYS
# ============================================================

def get_care_pathway(condition):
    pathway = pathway_df[
        pathway_df["condition"] == condition
    ]
    
    if pathway.empty:
        return None
        
    return pathway.iloc[0]


# ============================================================
# 4. CONVERT PATHWAY → RECOMMENDATIONS
# ============================================================

def recommend_from_pathway(condition, area):
    pathway = get_care_pathway(condition)
    
    if pathway is None:
        return pd.DataFrame()
        
    required_services = []
    
    for column in ["step1", "step2", "step3"]:
        value = pathway[column]
        
        if pd.notna(value):
            required_services.append(value)
            
    return recommend_multiple_services(
        required_services,
        area
    )


# ============================================================
# 5. MEDICINE LOOKUP
# ============================================================

def medicine_lookup(medicine):
    medicine = clean_text(medicine)
    
    result = medicine_df[
        medicine_df["brand"]
        .str.lower()
        == medicine
    ]
    
    if result.empty:
        return None
        
    return result.iloc[0].to_dict()
# ============================================================
# CARE PATHWAYS (Dynamic Steps)
# ============================================================

def get_care_pathway(condition):
    condition = clean_text(condition)
    pathway = pathway_df[pathway_df["condition"].str.lower() == condition]
    
    if pathway.empty:
        return None
        
    return pathway.iloc[0]


def recommend_from_pathway(condition, area):
    pathway = get_care_pathway(condition)
    
    if pathway is None:
        return pd.DataFrame()
        
    steps_raw = pathway["steps"]
    if pd.isna(steps_raw):
        return pd.DataFrame()
    
    # Dynamically parses any number of comma-separated steps
    required_services = [
        service.strip() 
        for service in str(steps_raw).split(",") 
        if service.strip()
    ]
    
    return recommend_multiple_services(
        required_services,
        area
    )


# ============================================================
# MEDICINE LOOKUP (With Cost)
# ============================================================

def medicine_lookup(medicine):
    medicine = clean_text(medicine)
    
    result = medicine_df[
        medicine_df["brand"]
        .str.lower()
        == medicine
    ]
    
    if result.empty:
        return None
        
    return result.iloc[0].to_dict()