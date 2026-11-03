# scripts/sources.py

SOURCES = {
    "parcels": {
        "url": "https://services6.arcgis.com/hM5ymMLbxIyWTjn2/ArcGIS/rest/services/City_of_Mississauga_Parcels/FeatureServer/0",
        "fields": {
            "CITY_PIN": "parcel_id",
            "GIS_AREA": "area_sqm",
        },
        "where": "1=1",
    },
    "zoning": {
        "url": "https://services6.arcgis.com/hM5ymMLbxIyWTjn2/ArcGIS/rest/services/2025_Existing_Land_Use1/FeatureServer/2",
        "fields": {
            "elu_code": "land_use_code",
            "elu_description": "land_use_desc",
            "elu_category": "land_use_category",
            "area_ha": "area_ha",
            "WARD": "ward",
        },
        "where": "elu_code IN ('OS','VAC','PROW','PUB','SCH')",
    },
    
    "woodlands": {
        "url": "https://services6.arcgis.com/ONZht79c8QWuX759/arcgis/rest/services/Woodlands/FeatureServer/0",
        "fields": {
            "LANDUSE": "land_use",
            "WOODLAND": "woodland_flag",
            "CORE": "is_core",
            "MUN_NAME": "municipality",
        },
        "where": "1=1",
    },
    "canopy": {
        "url": "https://services6.arcgis.com/ONZht79c8QWuX759/arcgis/rest/services/StreetscapeCharacteristics/FeatureServer/1",
        "fields": {
            "Canopy": "canopy_area",
            "NonCanopy": "noncanopy_area",
            "TotalArea_ha": "total_area_ha",
            "CSDNAME": "municipality",
            "DAUID": "dissemination_area_id",
        },
        "where": "1=1",
    },
    "heat": {
        "url": "https://services6.arcgis.com/ONZht79c8QWuX759/arcgis/rest/services/Extreme_Heat_Vulnerability_Index/FeatureServer/0",
        "fields": {
            "CTUID": "census_tract_id",
            "Index_Nrm": "heat_index",
            "PHDZ": "phdz_id",
        },
        "where": "1=1",
    },
    "equity": {
        "url": "https://services6.arcgis.com/ONZht79c8QWuX759/arcgis/rest/services/PHDZ_2021_Dashboard/FeatureServer/0",
        "fields": {
            "PHDZ": "phdz_id",
            "Income_MedHH": "median_hh_income",
            "LIMAT_All_Per": "low_income_pct",
            "HH_CoreNeed_Per": "core_housing_need_pct",
        },
        "where": "1=1",
    },
    "flood_engineered": {
        "url": "https://services1.arcgis.com/d0ZCwU7eGKVeNiEE/ArcGIS/rest/services/TRCA_Regulation_2025/FeatureServer/28",
        "fields": {
            "OBJECTID": "flood_id",
        },
        "where": "1=1",
    },
    "flood_estimated": {
        "url": "https://services1.arcgis.com/d0ZCwU7eGKVeNiEE/ArcGIS/rest/services/TRCA_Regulation_2025/FeatureServer/29",
        "fields": {
            "OBJECTID": "flood_id",
        },
        "where": "1=1",
    },
    "soil": {
        "url": "https://ws.lioservices.lrc.gov.on.ca/arcgis2/rest/services/LIO_OPEN_DATA/LIO_Open05/MapServer/9",
        "fields": {
            "SOILTYPE1": "soil_type",
            "DRAINAGE1": "drainage",
            "CLASS1": "soil_class",
        },
        "where": "1=1",
        "source_crs_override": 4269,  # geographic, needs explicit reprojection
        "out-fields": "SOILTYPE1,DRAINAGE1,CLASS1",
        "page_size": 200,
        "bbox": (-79.9, 43.55, -79.45, 43.95),
    },
}

TARGET_CRS = 26917  # UTM Zone 17N, meters