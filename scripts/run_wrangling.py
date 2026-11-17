# scripts/run_wrangling.py
#
# Runner for the wrangling stage — mirrors run_ingestion.py's role, just one
# stage later in the pipeline. For each of the 9 sources: read its raw
# ingested file from data/raw/, look up its cleaning rules in WRANGLE_CONFIG,
# run it through wrangle_source(), and save the cleaned result to data/clean/.
#
# Must be run from the repo root (same reasoning as run_ingestion.py) —
# the data/raw/ and data/clean/ paths below are relative to the current
# working directory, not to this script's own location.

import os
import geopandas as gpd

from wrangle import wrangle_source
from wrangle_sources import WRANGLE_CONFIG

RAW_DIR = "data/raw"
CLEAN_DIR = "data/clean"

if __name__ == "__main__":
    os.makedirs(CLEAN_DIR, exist_ok=True)

    for name, config in WRANGLE_CONFIG.items():
        raw_path = f"{RAW_DIR}/{name}.gpkg"
        clean_path = f"{CLEAN_DIR}/{name}.gpkg"

        try:
            gdf = gpd.read_file(raw_path)
            cleaned = wrangle_source(name, gdf, config)
            cleaned.to_file(clean_path, driver="GPKG")
            print(f"  Saved {len(cleaned)} features to {clean_path}")
        except Exception as e:
            print(f"  FAILED '{name}': {e}")