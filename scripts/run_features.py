# scripts/run_features.py
#
# Runner for the feature-engineering stage — mirrors run_join.py's role,
# one stage further down the pipeline. Loads the joined candidate-site
# table, derives any configured features, and saves the result.
#
# Must be run from the repo root, same reasoning as the other runners.

import geopandas as gpd

from features import build_features
from feature_sources import FEATURE_CONFIG

IN_PATH = "data/clean/candidate_sites.gpkg"
OUT_PATH = "data/clean/candidate_sites_features.gpkg"

if __name__ == "__main__":
    gdf = gpd.read_file(IN_PATH)
    print(f"Loaded {len(gdf)} candidate sites\n")

    gdf = build_features(gdf, FEATURE_CONFIG)

    gdf.to_file(OUT_PATH, driver="GPKG")
    print(f"\nSaved {len(gdf)} rows to {OUT_PATH}")
    print(f"Columns: {list(gdf.columns)}")
