# scripts/wrangle_sources.py

WRANGLE_CONFIG = {
    "zoning": {
        "fix_geometry": True,
        "null_rules": {"geometry": "drop_row"},
        "notes": "7 null geoms, 12 invalid. Considered dropping sliver "
                 "polygons below an area threshold, but rejected: small "
                 "area_ha doesn't mean junk here — 667 of 792 rows below "
                 "0.0001 ha are land_use_code='PROW' (right-of-way strips), "
                 "which are legitimately narrow, not broken. Left as-is; "
                 "a handful of near-zero (~1.4e-9 ha) rows remain, treated "
                 "as negligible noise rather than worth a fragile filter.",
    },
    "woodlands": {
        "fix_geometry": True,
        "null_rules": {},
        "notes": "78% null is_core — REVISED: is_core isn't boolean, non-null "
                 "values are category codes explaining WHY a woodland is core "
                 "('SIZE', 'SPECIAL - PROPR'), not a yes/no flag. Filling null "
                 "with False wrongly conflated 'confirmed not core' with "
                 "'never evaluated'. Now left untouched (null), to be treated "
                 "as neutral in scoring, same policy as the flood layers.",
    },

    "parcels": {
        "fix_geometry": True,
        "null_rules": {},
        "dedupe_on": {"parcel_id": "assign_new_id"},
        "min_value_rules": {"area_sqm": 0},
        "notes": "3 rows had duplicated id, they were sanity checked to reveal to be 3 different parcels and have been accounted for. "
                 "1 row had area_sqm == 0 (not a real property) — dropped via min_value_rules.",

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
        "sentinel_rules": {"drainage": "NA"},
        "null_rules": {},
        "case_rules": {"soil_class": "upper"},
        "notes": "bbox restricts coverage to Peel but still overlaps 98.4% of "
                 "parcels, so no coverage concern. drainage column had the "
                 "literal text 'NA' as a disguised null — converted to a "
                 "real null via sentinel_rules (left untouched afterward, "
                 "neutral in scoring). soil_class had both upper/lowercase "
                 "versions of the same letters (e.g. 'C' and 'c') — "
                 "normalized to uppercase; NOT CONFIRMED whether case was "
                 "actually meaningful in the source's own documentation, "
                 "this is an assumption, revisit if it turns out to matter.",
    },
    

}