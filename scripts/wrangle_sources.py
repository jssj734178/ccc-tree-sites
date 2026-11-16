# scripts/wrangle_sources.py

WRANGLE_CONFIG = {
    "zoning": {
        "fix_geometry": True,
        "null_rules": {"geometry": "drop_row"},
        "notes": "7 null geoms, 12 invalid",
    },
    "woodlands": {
        "fix_geometry": True,
        "null_rules": {"is_core": "fill_false"},
        "notes": "78% null is_core — treat as 'not core woodland'",
    },

    "parcels": {
        "fix_geometry": True,
        "null_rules": {},
        "dedupe_on": {"parcel_id": "assign_new_id"},
        "notes": "3 rows had duplicated id, they were sanity checked to reveal to be 3 different parcels and have been accounted for",
        
    },

    "flood_engineered": {
        "fix_geometry": True,
        "null_rules": {},
        "notes" : "6 entries had invalid geometries; additionally only 45% of flood engineered bbox overlap with parcels, null values will be considred neutral in scoring",
    },

    "flood_estimated":{
        "fix_geometry" : True,
        "null_rules": {},
        "notes": "32% of all estimated floods are invalid, need to be looked and verified closely",


    },

    "canopy": {
        "fix_geometry": True,
        "null_rules": {},
        "notes": "1 invalid geometry",
    },

    "heat": {
        "fix_geometry": True,
        "null_rules": {},
        "notes": "1 null heat_index out of 282 rows — left untouched intentionally, to be treated as neutral in scoring, consistent with the flood-layer policy",
    },

    "equity": {
        "fix_geometry": True,
        "null_rules": {},
        "notes": "clean source, no invalid geometries or nulls found",
    },

    "soil": {
        "fix_geometry": True,
        "null_rules": {},
        "notes": "clean source; bbox restricts coverage to Peel but still overlaps 98.4% of parcels, so no coverage concern",
    },
    

}