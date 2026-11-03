# scripts/ingest.py
import time
import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import shape

def fetch_arcgis_layer(url, where="1=1", out_fields="*", page_size=2000, timeout=90, max_retries=3, bbox=None):
    """Query an ArcGIS FeatureServer/MapServer layer with pagination, return GeoDataFrame."""
    all_features = []
    offset = 0
    while True:
        for attempt in range(1, max_retries + 1):
            try:
                params = {
                    "where": where,
                    "outFields": out_fields,
                    "f": "geojson",
                    "resultOffset": offset,
                    "resultRecordCount": page_size,
                }
                if bbox:
                    params.update({
                        "geometry": ",".join(str(c) for c in bbox),
                        "geometryType": "esriGeometryEnvelope",
                        "spatialRel": "esriSpatialRelIntersects",
                        "inSR": 4326,
                    })
                resp = requests.get(f"{url}/query", params=params, timeout=timeout)
                resp.raise_for_status()
                data = resp.json()
                break
            except (requests.exceptions.RequestException, ValueError) as e:
                if attempt == max_retries:
                    raise
                wait = 5 * attempt
                print(f"  offset {offset}: attempt {attempt} failed ({e}), retrying in {wait}s...")
                time.sleep(wait)

        features = data.get("features", [])
        if not features:
            break
        all_features.extend(features)
        print(f"  ...{len(all_features)} features fetched so far (offset {offset})")
        if len(features) < page_size:
            break
        offset += page_size

    if not all_features:
        raise ValueError(f"No features returned from {url}")

    gdf = gpd.GeoDataFrame.from_features(all_features)
    gdf = gdf.set_crs(epsg=4326)
    return gdf

def ingest_source(name, config, target_crs=26917):
    """Fetch, reproject, rename fields, and save one source per the config table."""
    print(f"Ingesting '{name}'...")
    gdf = fetch_arcgis_layer(
        config["url"],
        where=config.get("where", "1=1"),
        out_fields=config.get("out_fields", "*"),
        page_size=config.get("page_size", 2000),
        bbox=config.get("bbox", None),
    )

    # Set source CRS explicitly if the service doesn't declare one correctly (e.g. soil layer)
    if "source_crs_override" in config:
        gdf = gdf.set_crs(epsg=config["source_crs_override"], allow_override=True)
    elif gdf.crs is None:
        raise ValueError(f"'{name}': no CRS detected and no override given — check manually")

    gdf = gdf.to_crs(epsg=target_crs)

    # Keep and rename only the fields we care about
    keep_cols = list(config["fields"].keys())
    missing = [c for c in keep_cols if c not in gdf.columns]
    if missing:
        print(f"  WARNING: missing fields in '{name}': {missing}")
    keep_cols = [c for c in keep_cols if c in gdf.columns] + ["geometry"]
    gdf = gdf[keep_cols].rename(columns=config["fields"])

    out_path = f"data/raw/{name}.gpkg"
    gdf.to_file(out_path, driver="GPKG")
    print(f"  Saved {len(gdf)} features to {out_path}")
    return gdf