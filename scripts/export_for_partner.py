# scripts/export_for_partner.py
#
# One-off export: turns the geometry-bearing candidate_sites_features.gpkg
# into a plain .csv with the geometry column dropped, so the MCDA/scoring
# side can start working with pandas alone — no geopandas, no GIS
# libraries — unless/until their model actually needs the shapes.
#
# parcel_id is kept as the join key, so geometry can be reattached later
# (by merging back onto candidate_sites_features.gpkg on parcel_id) if it
# turns out the MCDA model needs it after all.
#
# Must be run from the repo root, same as the other runners.

import geopandas as gpd

IN_PATH = "data/clean/candidate_sites_features.gpkg"
OUT_PATH = "data/clean/candidate_sites_features.csv"

if __name__ == "__main__":
    gdf = gpd.read_file(IN_PATH)
    df = gdf.drop(columns=["geometry"])
    df.to_csv(OUT_PATH, index=False)
    print(f"Saved {len(df)} rows, {len(df.columns)} columns to {OUT_PATH}")
    print(f"Columns: {list(df.columns)}")
