# scripts/join.py
#
# Shared, generic join logic used to combine every non-base layer onto
# parcels, one layer at a time. Same split as wrangle.py: these functions
# don't know a specific layer's name or columns — every detail comes from
# the config passed in (see join_sources.py's JOIN_CONFIG).
#
# Each layer is joined and collapsed back to one row per parcel BEFORE the
# next layer is joined — never all at once (see the earlier explanation of
# why: multi-matches from different layers would multiply together).

import geopandas as gpd
import shapely


def join_flag(parcels, layer, output_column):
    """
    Collapse a layer down to a single True/False column on parcels:
    True if the parcel touches ANY feature in this layer at all.

    Used for layers where only presence matters, not which specific
    feature was touched or its attributes (flood_engineered,
    flood_estimated) — so any number of matches (0, 1, or many) reduces
    to the same True/False answer, with no "which one wins" question to
    resolve.
    """
    # Keep only geometry from each side for this check — we don't need
    # any of the layer's own columns, just whether a geometry exists there.
    candidates = gpd.sjoin(
        parcels[["parcel_id", "geometry"]],
        layer[["geometry"]],
        how="inner",
        predicate="intersects",
    )
    # candidates has one row per matching (parcel, feature) pair. A parcel
    # that matched 3 features appears 3 times here — we only need to know
    # IT matched at all, so collapsing to a set of matched IDs discards
    # the repeat rows rather than trying to pick one.
    matched_ids = set(candidates["parcel_id"])

    parcels = parcels.copy()
    parcels[output_column] = parcels["parcel_id"].isin(matched_ids)
    return parcels


def join_dominant(parcels, layer, fields):
    """
    Attach this layer's columns (`fields`) onto parcels, one value per
    parcel, by picking whichever matched feature covers the LARGEST SHARE
    of that parcel's area.

    Used for layers whose actual attribute values matter (zoning,
    woodlands, canopy, heat, equity, soil) — unlike join_flag, we can't
    just reduce to True/False, we need to decide WHICH feature's values
    "belong" to this parcel when more than one touches it. When a parcel
    only matches one feature, this rule has nothing to compare against,
    so it just picks that one — the same logic handles the single-match
    case and the multi-match case without a separate branch.
    """
    base = parcels[["parcel_id", "geometry"]].copy()
    right = layer[fields + ["geometry"]].copy()

    # how="inner": unmatched parcels are dropped here, not kept with
    # nulls — they get added back in at the end via the left-merge below,
    # so this step only needs to work out the winner among actual matches.
    joined = gpd.sjoin(base, right, how="inner", predicate="intersects")

    # sjoin carries over the LEFT (parcel) index as-is, so a parcel that
    # matched 3 features appears 3 times under the SAME index label (not
    # 3 distinct labels). That breaks idxmax() below: idxmax() returns
    # the label with the largest value, but .loc[] on a label that's
    # duplicated returns EVERY row with that label, not just the winning
    # one — so the "pick one winner" step would silently let all of a
    # parcel's multi-matches back in. Resetting to a fresh, unique index
    # first makes every row individually addressable.
    joined = joined.reset_index(drop=True)

    # sjoin keeps the LEFT geometry (parcels) in the result and gives us
    # "index_right", the row position of the matched feature in `layer`.
    # To measure how much of the parcel each match actually covers, we
    # need both geometries at once — sjoin alone doesn't compute that,
    # it only tells us THAT they intersect, not by how much.
    #
    # shapely.intersection/area (not the GeoSeries .intersection() method)
    # work directly on plain arrays of geometries, matched up by position
    # rather than by pandas index — that sidesteps an index-alignment
    # mismatch between the two sides that the GeoSeries method hits here.
    left_geoms = joined.geometry.values
    right_geoms = layer.geometry.values[joined["index_right"].values]
    overlaps = shapely.intersection(left_geoms, right_geoms)
    joined["_overlap_area"] = shapely.area(overlaps)

    # For each parcel_id, idxmax() gives the ROW LABEL (not position) of
    # its largest _overlap_area — i.e. the single winning match out of
    # however many that parcel had. groupby().idxmax() is doing the
    # "pick the dominant one" step in one call, rather than looping.
    winner_idx = joined.groupby("parcel_id")["_overlap_area"].idxmax()
    winners = joined.loc[winner_idx, ["parcel_id"] + fields]

    # Left merge: every original parcel is kept. A parcel with no match
    # in this layer gets null in every one of `fields` — not dropped,
    # not zero, genuinely "unknown for this layer", to be handled the
    # same way the wrangling stage already treats other nulls (neutral
    # in scoring, per the notes in WRANGLE_CONFIG).
    result = parcels.merge(winners, on="parcel_id", how="left")
    return result


def report_join_diagnostics(before, after, name, config):
    """
    Print a short summary of what a layer's join actually did, so you can
    confirm it behaved as expected rather than trusting it silently.
    """
    print(f"=== joined: {name} ===")
    if config["method"] == "flag":
        col = config["output_column"]
        n_true = after[col].sum()
        print(f"  {col}: {n_true} / {len(after)} parcels = True")
    else:
        first_field = config["fields"][0]
        n_matched = after[first_field].notna().sum()
        print(f"  matched: {n_matched} / {len(after)} parcels "
              f"(rest null -> neutral in scoring)")
    print(f"  row count unchanged: {len(before)} -> {len(after)}")


def join_source(parcels, layer, name, config):
    """
    Run the join for one layer onto parcels, driven entirely by its config
    entry in JOIN_CONFIG. Mirrors wrangle_source()'s role in wrangle.py.
    """
    before = parcels

    if config["method"] == "flag":
        result = join_flag(parcels, layer, config["output_column"])
    elif config["method"] == "dominant":
        result = join_dominant(parcels, layer, config["fields"])
    else:
        raise ValueError(f"Unknown join method for '{name}': {config['method']}")

    report_join_diagnostics(before, result, name, config)
    return result