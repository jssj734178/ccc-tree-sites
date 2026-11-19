# scripts/join_sources.py
#
# Per-layer join configuration — pure data, no logic (same split as
# wrangle_sources.py). Each entry says HOW to collapse that layer's
# parcel-matches back down to one row per parcel, and which columns from
# the layer should end up on the final parcel-level table.
#
# Two join methods, decided by real-data testing (see notes below):
#
#   "flag"     -> we only care WHETHER a parcel touches this layer at all,
#                 not which specific feature it touched. Any number of
#                 matches collapses to a single True/False column.
#
#   "dominant" -> we need this layer's actual attribute values on the
#                 parcel. When a parcel matches more than one feature,
#                 the feature covering the LARGEST SHARE of the parcel's
#                 area wins, and its listed columns are copied over.
#                 When a parcel matches exactly one feature, this rule
#                 trivially picks that one — so "dominant" is just the
#                 general case, not a special one.
#
# "expect single match" was tested directly against the real cleaned data
# and dropped: even heat, equity, and soil (assumed to tile the region
# without overlap) had a small number of parcels genuinely straddling two
# polygons (1615 / 531 / 10 parcels respectively). "dominant" handles that
# correctly in every case, so there was no reason to keep a 3rd category.

JOIN_CONFIG = {
    "flood_engineered": {
        "method": "flag",
        "output_column": "near_flood_engineered",
    },
    "flood_estimated": {
        "method": "flag",
        "output_column": "near_flood_estimated",
    },

    "zoning": {
        "method": "dominant",
        "fields": ["land_use_code", "land_use_desc", "land_use_category", "ward"],
    },
    "woodlands": {
        "method": "dominant",
        "fields": ["land_use", "woodland_flag", "is_core"],
    },
    "canopy": {
        "method": "dominant",
        "fields": ["canopy_area", "noncanopy_area", "total_area_ha"],
    },
    "heat": {
        "method": "dominant",
        "fields": ["heat_index"],
    },
    "equity": {
        "method": "dominant",
        "fields": ["median_hh_income", "low_income_pct", "core_housing_need_pct"],
    },
    "soil": {
        "method": "dominant",
        "fields": ["soil_type", "drainage", "soil_class"],
    },
}