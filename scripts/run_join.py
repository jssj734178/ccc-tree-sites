# scripts/run_join.py
#
# Runner for the join stage — mirrors run_wrangling.py's role, one stage
# later in the pipeline. Loads the cleaned parcels (base layer), then
# joins each of the other 8 cleaned layers onto it ONE AT A TIME, saving
# the single combined candidate-site table at the end.
#
# Must be run from the repo root, same reasoning as the other runners.

import geopandas as gpd

from join import join_source
from join_sources import JOIN_CONFIG

CLEAN_DIR = "data/clean"
OUT_PATH = "data/clean/candidate_sites.gpkg"

if __name__ == "__main__":
    parcels = gpd.read_file(f"{CLEAN_DIR}/parcels.gpkg")
    print(f"Starting from {len(parcels)} parcels (base layer)\n")

    for name, config in JOIN_CONFIG.items():
        layer = gpd.read_file(f"{CLEAN_DIR}/{name}.gpkg")
        parcels = join_source(parcels, layer, name, config)

    parcels.to_file(OUT_PATH, driver="GPKG")
    print(f"\nSaved {len(parcels)} candidate sites to {OUT_PATH}")
    print(f"Columns: {list(parcels.columns)}")