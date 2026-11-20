# scripts/features.py
#
# Shared, generic feature-engineering logic. Same split as wrangle.py /
# join.py: these functions don't know a specific column name — every
# detail comes from the config passed in (see feature_sources.py's
# FEATURE_CONFIG).

import geopandas as gpd


def compute_ratio_pct(gdf, numerator, denominator):
    """
    Return numerator / denominator * 100 as a plain pandas Series.

    If either column is null for a row, pandas division just produces
    null for that row's result (no error, no crash) — so rows that
    didn't match a layer in the join stage automatically end up with a
    null derived feature too, instead of needing special-case handling
    here. We confirmed separately that denominator is never 0 in this
    data, so there's no divide-by-zero case to guard against.
    """
    return gdf[numerator] / gdf[denominator] * 100


def compute_minmax_scale(gdf, source):
    """
    Rescale a column onto 0-1, where 0 = this column's own lowest real
    value in the data and 1 = its own highest. Every other value lands
    somewhere between, in proportion to where it sits in that range.

    .min()/.max() skip nulls automatically (pandas default), so a null
    row doesn't distort the range for every other row, and the null
    itself stays null here — it still has no value to place on the
    scale. Filling it with a neutral placeholder is a deliberate, later
    step (fill_neutral), not something this function should decide on
    its own.
    """
    col = gdf[source]
    low, high = col.min(), col.max()
    return (col - low) / (high - low)


def fill_neutral(series, value=0.5):
    """
    Replace any remaining null in an already-scaled (0-1) column with a
    fixed neutral value — 0.5, the midpoint, by default.

    Only meaningful AFTER compute_minmax_scale has run: 0.5 is "neutral"
    specifically because the scale's own range is 0-1, so its midpoint
    is a clearly-defined middle, not a guess at what the real value
    might have been.
    """
    return series.fillna(value)


def compute_feature(gdf, output_column, config):
    """
    Compute one derived column, driven entirely by its config entry.
    Mirrors wrangle_source()/join_source()'s role: one function that
    dispatches to the right generic logic based on config["method"].
    """
    method = config["method"]

    if method == "ratio_pct":
        gdf[output_column] = compute_ratio_pct(
            gdf, config["numerator"], config["denominator"]
        )
    elif method == "minmax_scale":
        gdf[output_column] = compute_minmax_scale(gdf, config["source"])
        if "fill_null" in config:
            gdf[output_column] = fill_neutral(gdf[output_column], config["fill_null"])
    else:
        raise ValueError(f"Unknown feature method for '{output_column}': {method}")

    return gdf


def report_feature_diagnostics(gdf, output_column, config):
    """
    Print a short summary so you can confirm a derived feature actually
    looks reasonable, rather than trusting it silently.
    """
    col = gdf[output_column]
    print(f"=== feature: {output_column} ===")
    print(f"  non-null: {col.notna().sum()} / {len(col)}")
    print(f"  range: {col.min():.4f} to {col.max():.4f}")
    if "drop_columns" in config:
        print(f"  dropped source columns: {config['drop_columns']}")


def build_features(gdf, feature_config):
    """
    Run the full feature-engineering pass over candidate_sites.gpkg,
    driven entirely by FEATURE_CONFIG. Mirrors wrangle_source()/
    join_source()'s role one stage further down the pipeline.
    """
    for output_column, config in feature_config.items():
        gdf = compute_feature(gdf, output_column, config)
        report_feature_diagnostics(gdf, output_column, config)

        for col in config.get("drop_columns", []):
            gdf = gdf.drop(columns=[col])

    return gdf