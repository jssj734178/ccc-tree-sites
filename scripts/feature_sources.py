# scripts/feature_sources.py
#
# Per-feature engineering configuration — pure data, no logic (same split
# as wrangle_sources.py / join_sources.py). Each entry describes ONE
# derived column to add to candidate_sites.gpkg, and how to compute it.

FEATURE_CONFIG = {
    "canopy_pct": {
        "method": "ratio_pct",
        "numerator": "canopy_area",
        "denominator": "total_area_ha",
        "drop_columns": ["canopy_area", "noncanopy_area"],
        "notes": "canopy_area and total_area_ha are both in hectares "
                 "(confirmed: canopy_area never exceeds total_area_ha, "
                 "same units). Raw canopy_area isn't comparable across "
                 "differently-sized parcels, so convert to a 0-100% share "
                 "of the parcel instead. 18 parcels have null in both "
                 "source columns (didn't match the canopy layer in the "
                 "join) -> canopy_pct comes out null for those too, same "
                 "'neutral in scoring' policy as everywhere else. Original "
                 "canopy_area/noncanopy_area dropped afterward since "
                 "canopy_pct replaces what they were needed for.",
    },
}
