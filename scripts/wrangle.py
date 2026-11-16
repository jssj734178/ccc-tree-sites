# scripts/wrangle.py
#
# Shared, generic cleaning logic used by every source.
# None of these functions know a specific source name or column name —
# every source-specific detail comes in through the config passed to them
# (see wrangle_sources.py's WRANGLE_CONFIG). Same split as ingest.py/sources.py.

import geopandas as gpd


def fix_geometries(gdf):
    """
    Repair invalid (usually self-intersecting) polygon geometries.

    make_valid() retraces a broken shape's boundary and reconstructs it into
    one or more simple (non-self-intersecting) polygons — it doesn't invent
    new area, it resolves the geometry using the coordinates already there.
    Safe to call even when nothing is actually broken (it's a no-op on an
    already-valid shape), so we don't need per-source branching here.
    """
    gdf.geometry = gdf.geometry.make_valid()
    return gdf


def handle_nulls(gdf, null_rules):
    """
    Apply a null-handling policy per column, as described by null_rules —
    a dict of {column_name: action_string}, e.g. {"geometry": "drop_row"}.

    Supported actions:
      "drop_row"   -> delete any row where this column is null
      "fill_false" -> replace nulls in this column with False

    null_rules is expected to be a dict (possibly empty — {} means "nothing
    to do for this source"). handle_nulls never hardcodes a column name;
    it just loops over whatever columns/actions the config for this
    particular source actually lists.
    """
    for col, action in null_rules.items():
        if action == "drop_row":
            # gdf[col].notna() -> a True/False Series, one value per row,
            # True where that row's value in `col` is NOT null.
            # gdf[boolean_series] -> boolean indexing: keep only the rows
            # where the condition is True. This is a vectorized filter,
            # not a row-by-row loop.
            gdf = gdf[gdf[col].notna()]
        elif action == "fill_false":
            # fillna() replaces every null in this column with the given
            # value, without removing any rows.
            gdf[col] = gdf[col].fillna(False)
    return gdf


def dedupe(gdf, dedupe_rules):
    """
    Apply a duplicate-handling policy per column, as described by
    dedupe_rules — a dict of {column_name: action_string}.

    Supported actions:
      "assign_new_id" -> for every row whose value in this column is
                          shared with at least one other row, replace
                          that value with a freshly generated, guaranteed-
                          unique one. Use this when a repeated value is a
                          placeholder/default (e.g. parcel_id == 0 standing
                          in for "no ID assigned upstream") rather than a
                          genuine duplicate record — it does NOT drop any
                          rows, since dropping would silently delete real,
                          distinct data (this is exactly what we found when
                          we actually inspected parcels' 3 duplicate-ID rows
                          and confirmed they were 3 different real parcels).

    dedupe_rules is expected to be a dict (possibly empty for sources that
    don't need this, e.g. {} — the loop below then just does nothing).
    """
    for col, action in dedupe_rules.items():
        if action == "assign_new_id":
            # keep=False marks EVERY row involved in a duplicate group as
            # True, not just the "extra" copies after the first — we want
            # to treat every row in the group equally, since none of them
            # is the "real" original here.
            dup_mask = gdf[col].duplicated(keep=False)

            # dup_mask is computed once, over the whole column, before any
            # value changes — so every row sharing a duplicate value is
            # already identified as part of the group up front. Assigning
            # new values to all of them happens in one batch operation,
            # not sequentially, so there's no "leftover" row that still
            # looks like a duplicate afterward.
            gdf.loc[dup_mask, col] = [
                f"{col}_auto_{i}" for i in gdf.index[dup_mask]
            ]
    return gdf


def report_diagnostics(before, after, name):
    """
    Print a before/after summary for one source's wrangling pass, so you
    can confirm a fix actually did what it was supposed to (rather than
    eyeballing individual rows).
    """
    print(f"=== {name} ===")
    print(f"  rows: {len(before)} -> {len(after)} "
          f"({len(before) - len(after)} dropped)")
    print(f"  invalid geometries: {(~before.geometry.is_valid).sum()} -> "
          f"{(~after.geometry.is_valid).sum()}")
    print(f"  null geometries: {before.geometry.isna().sum()} -> "
          f"{after.geometry.isna().sum()}")


def wrangle_source(name, gdf, config):
    """
    Run the full wrangling pass for one source, driven entirely by its
    config entry in WRANGLE_CONFIG. Mirrors ingest_source()'s role in
    ingest.py: one function that ties the generic steps together using
    whatever this specific source's config says to do.
    """
    before = gdf.copy()

    if config.get("fix_geometry", False):
        gdf = fix_geometries(gdf)

    gdf = handle_nulls(gdf, config.get("null_rules", {}))
    gdf = dedupe(gdf, config.get("dedupe_on", {}))

    report_diagnostics(before, gdf, name)
    return gdf