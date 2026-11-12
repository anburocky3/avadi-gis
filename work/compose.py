import geopandas as gpd
from shapely import make_valid
from shapely.ops import unary_union
from shapely.geometry import Polygon

box = (79.95, 12.95, 80.25, 13.25)
lbu = gpd.read_file(
    "/Users/admin/Desktop/projects/maps-site/lb/data/tn_urban_local_bodies.geojson",
    bbox=box,
)
vp = gpd.read_file("vp_box.geojson")
for g in (lbu, vp):
    g["geometry"] = g.geometry.apply(make_valid).buffer(0)
U = lambda g: unary_union(list(g.geometry))
km2 = lambda geom: round(
    gpd.GeoSeries([geom], crs=4326).to_crs(32644).area.iloc[0] / 1e6, 3
)
ULBS = ["Avadi", "Poonamallee", "Thiruverkadu", "Thirunindravur"]
VPS = {
    "Villivakkam": ["Vellanoor", "Ayappakkam", "Palavedu", "Morai"],
    "Poonamallee": [
        "Nemilicheri",
        "Nadukuthagai",
        "Kattupakkam",
        "Senneerkuppam",
        "Varadharajapuram",
        "Nasarathpettai",
        "Agaramel",
        "Banavedu thottam",
        "Parivakkam",
        "Kannapalayam",
        "Soranjeri",
        "Karunakaracheri",
        "Meppur",
    ],
}
parts = [(n, "ulb", U(lbu[lbu.ulb_name == n])) for n in ULBS]
for b, ns in VPS.items():
    for n in ns:
        m = vp[(vp.village_name == n) & (vp.block_name == b)]
        assert len(m) == 1, (n, len(m))
        parts.append((n, "vp", m.geometry.iloc[0]))
