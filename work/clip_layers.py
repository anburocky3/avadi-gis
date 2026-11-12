"""Roads, pipelines and drainage inside Avadi as expanded (boundaries/avadi_boundaries.geojson), copied from the
local TNGIS archive (tngis-data/data, pulled from tngis.tn.gov.in/tngismaps/wfs) and the TNGIS road network
shapefile in ~/Downloads. Each layer is clipped to the expanded outline and tagged with whether it lies in the
current corporation. Source files are only read."""

import os, sys, time
import geopandas as gpd
import pandas as pd
from shapely import make_valid

OUT = os.path.expanduser("~/Desktop/avadi_gis")
D = os.path.expanduser("~/Desktop/projects/tngis-data/data/")
# cma/ugddata, cma/road_details and generic_viewer/tnrd_rural_roads are identical to ulb_under_ground_drainage,
# ulb_roads and rural_roads_gis inside Avadi (same features, same km), so they are not copied twice.
LAYERS = {  # group, output name: source
    ("pipelines", "water_pipeline_ulb"): D
    + "Pm_Gati_Sakthi/ulb_water_pipeline.geojson",
    ("pipelines", "water_flow_direction_ulb"): D
    + "Pm_Gati_Sakthi/ulb_water_flow_direction.geojson",
    ("pipelines", "underground_drainage_ulb"): D
    + "Pm_Gati_Sakthi/ulb_under_ground_drainage.geojson",
    ("pipelines", "ulb_utility"): D + "Pm_Gati_Sakthi/ulb_utility.geojson",
    ("pipelines", "cmwssb_metrowater_pipeline"): D
    + "generic_viewer/cmwssb_metrowater_pipeline.geojson",
    ("pipelines", "cmwssb_sewage_pipeline"): D
    + "generic_viewer/cmwssb_sewage_pipeline.geojson",
    ("pipelines", "cmwssb_new_sewer_main"): D
    + "generic_viewer/cmwssb_new_sewer_main.geojson",
    ("pipelines", "cmwssb_new_machinehole"): D
    + "generic_viewer/cmwssb_new_machinehole.geojson",
    ("pipelines", "sewerage_pumping_station"): D
    + "generic_viewer/sewerage_pumping_station.geojson",
    ("roads", "roads_ulb"): D + "Pm_Gati_Sakthi/ulb_roads.geojson",
    ("roads", "all_roads_tamilnadu"): D
    + "generic_viewer/all_roads_tamilnadu_gis.geojson",
    ("roads", "major_district_roads"): D
    + "generic_viewer/major_district_roads.geojson",
    ("roads", "other_district_roads"): D
    + "generic_viewer/other_district_roads.geojson",
    ("roads", "rural_roads"): D + "generic_viewer/rural_roads_gis.geojson",
    ("roads", "tnrd_roads"): D + "tnrd/roads.geojson",
    ("roads", "village_roads"): D + "generic_viewer/village_roads.geojson",
    ("roads", "road_network_tngis"): os.path.expanduser(
        "~/Downloads/Road Network/Road_Network.shp"
    ),
    ("drainage", "natural_drainage"): D + "generic_viewer/drainage.geojson",
}

b = gpd.read_file(os.path.join(OUT, "boundaries/avadi_boundaries.geojson"))
cur, new = b.geometry.iloc[0], b.geometry.iloc[1]
mask = gpd.GeoDataFrame(geometry=[new], crs=4326)
want = sys.argv[1:]
rows = []
for (grp, name), src in LAYERS.items():
    if want and name not in want:
        continue
    t = time.time()
    try:
        g = gpd.read_file(
            src,
            bbox=(
                tuple(mask.to_crs(gpd.read_file(src, rows=1).crs).total_bounds)
                if src.endswith(".shp")
                else tuple(new.bounds)
            ),
        )
    except Exception as e:
        print(name, "read failed", e, flush=True)
        continue
    n_box = len(g)
    if len(g):
        if g.crs and g.crs.to_epsg() != 4326:
            g = g.to_crs(4326)
        g = g[g.geometry.notna()]
        g["geometry"] = g.geometry.apply(lambda x: x if x.is_valid else make_valid(x))
        kind = (
            "Line"
            if g.geom_type.str.contains("Line").any()
            else ("Polygon" if g.geom_type.str.contains("Polygon").any() else "Point")
        )
        g = gpd.clip(g, mask).explode(index_parts=False)
        g = g[
            g.geom_type.str.contains(kind) & ~g.geometry.is_empty
        ]  # clipping leaves stray points and collections
    if len(g):
        g["in_current_avadi"] = g.geometry.intersects(cur)
        g["source_layer"] = os.path.relpath(src, os.path.expanduser("~"))
        os.makedirs(os.path.join(OUT, grp), exist_ok=True)
        g.to_file(os.path.join(OUT, grp, name + ".geojson"), driver="GeoJSON")
        gtypes = ",".join(sorted(set(g.geom_type)))
        m = g.to_crs(32644)
        km = round(m.length.sum() / 1000, 1) if "Line" in gtypes else ""
    else:
        gtypes, km = "", ""
    rows.append(
        {
            "group": grp,
            "layer": name,
            "features": len(g),
            "in_bbox": n_box,
            "geometry": gtypes,
            "km": km,
            "in_current": int(g.in_current_avadi.sum()) if len(g) else 0,
            "source": os.path.relpath(src, os.path.expanduser("~")),
        }
    )
    print(rows[-1], round(time.time() - t), "s", flush=True)
pd.DataFrame(rows).to_csv(
    os.path.join(
        OUT, "work", "clip_report" + ("_" + "_".join(want) if want else "") + ".csv"
    ),
    index=False,
)
