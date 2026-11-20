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

    # --- Scaled versions of every remaining numeric criterion. ---
    # Each one keeps the ORIGINAL raw column too (not replaced) — the raw
    # value stays useful to look at directly, but a scoring formula needs
    # the 0-1 version so no single column's raw magnitude (e.g. income,
    # in the hundred-thousands) swamps the others just because its
    # numbers happen to be bigger. fill_null: 0.5 implements each
    # column's existing "null = neutral" policy from the wrangling/join
    # notes as an actual number, now that there's a defined 0-1 scale
    # for 0.5 to be the midpoint of.
    "heat_index_scaled": {
        "method": "minmax_scale",
        "source": "heat_index",
        "fill_null": 0.5,
        "notes": "17 null heat_index (never evaluated) -> neutral (0.5) "
                 "on the scaled column, per the existing wrangling policy.",
    },
    "median_hh_income_scaled": {
        "method": "minmax_scale",
        "source": "median_hh_income",
        "fill_null": 0.5,
        "notes": "17 null (parcels outside equity layer coverage) -> "
                 "neutral (0.5).",
    },
    "low_income_pct_scaled": {
        "method": "minmax_scale",
        "source": "low_income_pct",
        "fill_null": 0.5,
        "notes": "17 null (same uncovered parcels as median_hh_income) "
                 "-> neutral (0.5).",
    },
    "core_housing_need_pct_scaled": {
        "method": "minmax_scale",
        "source": "core_housing_need_pct",
        "fill_null": 0.5,
        "notes": "17 null (same uncovered parcels) -> neutral (0.5).",
    },
    "canopy_pct_scaled": {
        "method": "minmax_scale",
        "source": "canopy_pct",
        "fill_null": 0.5,
        "notes": "Must run AFTER the canopy_pct entry above (dict order "
                 "matters here — build_features() processes entries in "
                 "the order they're listed, and this one depends on "
                 "canopy_pct already existing in the table). 18 null "
                 "(parcels that didn't match the canopy layer in the "
                 "join) -> neutral (0.5).",
    },
}