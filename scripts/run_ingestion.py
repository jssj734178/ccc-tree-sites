# scripts/run_ingestion.py
from sources import SOURCES, TARGET_CRS
from ingest import ingest_source

if __name__ == "__main__":
    for name, config in SOURCES.items():
        try:
            ingest_source(name, config, target_crs=TARGET_CRS)
        except Exception as e:
            print(f"  FAILED '{name}': {e}")