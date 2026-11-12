"""Avadi Corporation as it stands, and as expanded under G.O. (Ms) No. 201, MAWS (Elections), 31 Dec 2024
(TN Gazette Extraordinary No. 429, Part II-2, Table Sl. 11): Poonamallee, Tiruverkadu and Tirunindravur
municipalities and 17 village panchayats (Villivakkam and Poonamallee unions), all to their full extent.

Sources (read only, copied):
  ULBs and Avadi wards  maps-site/lb/data/tn_urban_local_bodies.geojson   TNGIS wards as corrected for /lb
                        (gap-filled; Tiruverkadu's TNGIS polygon is 2.8 km^2, /lb restores 18.2 km^2 from the
                        Survey of India layer)
  original TNGIS wards  maps-work/tn-boundaries/web/urban_local_bodies.geojson
  village panchayats    tngis-data/data/generic_viewer/tn_village_panchayat_boundary.geojson (TNGIS)
  Survey of India       ~/Downloads/TAMILNADU/TAMILNADU.shp (revenue villages, SOI, DBF 20 Aug 2025)

A panchayat's TNGIS polygon predates the 2019 corporation, so it gives up what is already in a ULB
(Kannapalayam loses 11.6 km^2 to Avadi). Slivers enclosed by the new outline that no source layer
covers are given to the added unit the SOI village there belongs to, else to the unit with the
longest shared border.
"""

import json
import os
import geopandas as gpd
import pandas as pd
from shapely import make_valid
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

OUT = os.path.expanduser("~/Desktop/avadi_gis")
BOX = (79.95, 12.95, 80.25, 13.25)
UTM = 32644
GO = "G.O.(Ms) No.201 MAWS (Elections) 31.12.2024; TN Gaz. Extra. No.429 Pt II-2, Sl.11"

ULB = [
    ("Poonamallee", "Poonamallee Municipal Council", "(i)"),
    ("Thiruverkadu", "Tiruverkadu Municipal Council", "(ii)"),
    ("Thirunindravur", "Tirunindravur Municipal Council", "(iii)"),
]
VP = [  # TNGIS name, gazette name, panchayat union, gazette item
    ("Vellanoor", "Vellanur", "Villivakkam", "(iv)"),
    ("Ayappakkam", "Ayappakkam", "Villivakkam", "(v)"),
    ("Palavedu", "Palavedu", "Villivakkam", "(vi)"),
    ("Morai", "Morai", "Villivakkam", "(vii)"),
    ("Nemilicheri", "Nemilicheri", "Poonamallee", "(viii)"),
    ("Nadukuthagai", "Nadukuthagai", "Poonamallee", "(ix)"),
    ("Kattupakkam", "Kattupakkam", "Poonamallee", "(x)"),
    ("Senneerkuppam", "Senneerkuppam", "Poonamallee", "(xi)"),
    ("Varadharajapuram", "Varadarajapuram", "Poonamallee", "(xii)"),
    ("Nasarathpettai", "Nazarethpettai", "Poonamallee", "(xiii)"),
    ("Agaramel", "Agaramel", "Poonamallee", "(xiv)"),
    ("Banavedu thottam", "Banaveduthottam", "Poonamallee", "(xv)"),
    ("Parivakkam", "Parivakkam", "Poonamallee", "(xvi)"),
    ("Kannapalayam", "Kannapalayam", "Poonamallee", "(xvii)"),
    ("Soranjeri", "Soranjeri", "Poonamallee", "(xviii)"),
    ("Karunakaracheri", "Karunakaracheri", "Poonamallee", "(xix)"),
    ("Meppur", "Meppur", "Poonamallee", "(xx)"),
]


def valid(g):
    g = g.copy()
    g["geometry"] = g.geometry.apply(make_valid).buffer(0)
    return g


def polys(geom):
    """Only the polygon parts (make_valid and differences can leave lines and points)."""
    if geom.geom_type == "Polygon":
        return geom
    ps = [
        p
        for p in getattr(geom, "geoms", [])
        if p.geom_type in ("Polygon", "MultiPolygon")
    ]
    return unary_union(ps) if ps else Polygon()


def km2(geom):
    return round(gpd.GeoSeries([geom], crs=4326).to_crs(UTM).area.iloc[0] / 1e6, 3)


def main():
    lbu = valid(
        gpd.read_file(
            os.path.expanduser(
                "~/Desktop/projects/maps-site/lb/data/tn_urban_local_bodies.geojson"
            ),
            bbox=BOX,
        )
    )
    vp = valid(
        gpd.read_file(
            os.path.expanduser(
                "~/Desktop/projects/tngis-data/data/generic_viewer/tn_village_panchayat_boundary.geojson"
            ),
            bbox=BOX,
        )
    )
    soi = valid(gpd.read_file(os.path.join(OUT, "work/soi_box.geojson")))
    orig = gpd.read_file(
        os.path.expanduser(
            "~/Desktop/projects/maps-work/tn-boundaries/web/urban_local_bodies.geojson"
        ),
        bbox=BOX,
    )

    keep = [
        "district_name",
        "ulb_name",
        "ulb_type",
        "ulb_lgd_code",
        "ward_number",
        "zone_number",
        "zone_name",
        "ward_lgd_code",
        "ward_lgd_code_new",
        "zone_lgd_code",
        "tngis_id",
    ]
    wards = lbu[lbu.ulb_name == "Avadi"][keep + ["geometry"]].copy()
    wards["ward_number"] = wards.ward_number.astype(int)
    wards = wards.sort_values("ward_number").reset_index(drop=True)
    wards["geometry"] = wards.geometry.apply(polys)
    ow = orig[orig.ulb_name == "Avadi"][keep + ["geometry"]].copy()
    ow["ward_number"] = ow.ward_number.astype(int)
    ow = ow.sort_values("ward_number").reset_index(drop=True)
    for g in (wards, ow):
        g["area_km2"] = (g.to_crs(UTM).area / 1e6).round(3)

    # the 20 added units
    taken = unary_union(
        list(lbu[lbu.ulb_name.isin(["Avadi"] + [u[0] for u in ULB])].geometry)
    )
    rows = []
    for tn, gaz, item in ULB:
        g = lbu[lbu.ulb_name == tn]
        rows.append(
            {
                "name": gaz.replace(" Municipal Council", ""),
                "gazette_name": gaz,
                "unit_type": "Municipality",
                "panchayat_union": "",
                "go_item": item,
                "extent": "Full",
                "source": "TNGIS ULB wards (as corrected for /lb)",
                "lgd_code": int(g.ulb_lgd_code.iloc[0]),
                "geometry": polys(unary_union(list(g.geometry))),
            }
        )
    for tn, gaz, union, item in VP:
        g = vp[(vp.village_name == tn) & (vp.block_name == union)]
        assert len(g) == 1, (tn, len(g))
        full = g.geometry.iloc[0]
        rows.append(
            {
                "name": gaz,
                "gazette_name": f"{gaz} Village Panchayat",
                "unit_type": "Village Panchayat",
                "panchayat_union": union,
                "go_item": item,
                "extent": "Full",
                "source": "TNGIS village panchayat, less what is already in a ULB",
                "lgd_code": int(g.village_lgd_code.iloc[0]),
                "tngis_vp_km2": km2(full),
                "geometry": polys(full.difference(taken)),
            }
        )
    add = gpd.GeoDataFrame(rows, crs=4326)

    # fill the slivers the new outline encloses
    whole = unary_union(list(wards.geometry) + list(add.geometry))
    holes = [
        Polygon(r)
        for p in getattr(whole, "geoms", [whole])
        if p.geom_type == "Polygon"
        for r in p.interiors
    ]
    filled = []
    for h in holes:
        h = polys(h.difference(whole))
        if h.is_empty:
            continue
        s = soi[soi.intersects(h)]
        best = None
        if len(s):
            sv = s.assign(a=s.geometry.intersection(h).area).sort_values("a").iloc[-1]
            hit = add[add.geometry.buffer(1e-6).intersects(sv.geometry)]
            hit = hit.assign(a=hit.geometry.intersection(sv.geometry).area).sort_values(
                "a"
            )
            if len(hit) and hit.a.iloc[-1] > 0:
                best = hit.index[-1]
        if best is None:
            border = add.geometry.apply(
                lambda g: g.buffer(2e-5).intersection(h.boundary).length
            )
            best = border.idxmax() if border.max() > 0 else None
        if best is None:  # enclosed by existing wards only: nearest ward
            i = wards.geometry.distance(h).idxmin()
            wards.at[i, "geometry"] = polys(unary_union([wards.geometry[i], h]))
            filled.append(("ward " + str(wards.ward_number[i]), km2(h)))
            continue
        add.at[best, "geometry"] = polys(unary_union([add.geometry[best], h]))
        filled.append((add.name[best], km2(h)))
    add["area_km2"] = (add.to_crs(UTM).area / 1e6).round(3)
    add.insert(0, "go_ref", GO)

    # expanded units: existing wards, Poonamallee's wards, then the rest whole
    pw = lbu[lbu.ulb_name == "Poonamallee"].copy()
    pw["ward_number"] = pw.ward_number.astype(int)
    pw = pw.sort_values("ward_number")
    ex = [
        {
            "unit": f"Avadi ward {r.ward_number}",
            "unit_type": "Avadi Corporation ward",
            "former_body": "Avadi Corporation",
            "avadi_ward_2019": r.ward_number,
            "former_ward": r.ward_number,
            "zone": r.zone_name if r.zone_name not in (None, "0") else "",
            "geometry": r.geometry,
        }
        for r in wards.itertuples()
    ]
    poon = add[add.name == "Poonamallee"].geometry.iloc[0]
    pw_geom = [polys(g.intersection(poon)) for g in pw.geometry]
    rest = polys(
        poon.difference(unary_union(pw_geom))
    )  # filled slivers given to Poonamallee: nearest ward
    if not rest.is_empty:
        for part in getattr(rest, "geoms", [rest]):
            j = min(range(len(pw_geom)), key=lambda k: pw_geom[k].distance(part))
            pw_geom[j] = polys(unary_union([pw_geom[j], part]))
    for r, g in zip(pw.itertuples(), pw_geom):
        ex.append(
            {
                "unit": f"Poonamallee ward {r.ward_number}",
                "unit_type": "Municipal ward (added)",
                "former_body": "Poonamallee Municipality",
                "avadi_ward_2019": None,
                "former_ward": r.ward_number,
                "zone": "",
                "geometry": g,
            }
        )
    for r in add[add.name != "Poonamallee"].itertuples():
        ex.append(
            {
                "unit": r.name,
                "unit_type": (
                    "Municipality (added)"
                    if r.unit_type == "Municipality"
                    else "Village Panchayat (added)"
                ),
                "former_body": r.gazette_name,
                "avadi_ward_2019": None,
                "former_ward": None,
                "zone": "",
                "geometry": r.geometry,
            }
        )
    ex = gpd.GeoDataFrame(ex, crs=4326)
    ex["area_km2"] = (ex.to_crs(UTM).area / 1e6).round(3)

    def clean(geom, tol=1e-8):  # outline only: drop sub-100 m^2 specks and pinholes
        ps = [
            Polygon(p.exterior, [r for r in p.interiors if Polygon(r).area > tol])
            for p in getattr(geom, "geoms", [geom])
            if p.area > tol
        ]
        return ps[0] if len(ps) == 1 else MultiPolygon(ps)

    cur = clean(unary_union(list(wards.geometry)))
    new = clean(unary_union(list(ex.geometry)))
    bnd = gpd.GeoDataFrame(
        [
            {
                "name": "Avadi Corporation (current, 48 wards)",
                "status": "current",
                "go_ref": "",
                "area_km2": km2(cur),
                "geometry": cur,
            },
            {
                "name": "Avadi Corporation (expanded, proposed)",
                "status": "proposed under G.O. 201 / Gazette 429 (intention notice)",
                "go_ref": GO,
                "area_km2": km2(new),
                "geometry": new,
            },
        ],
        crs=4326,
    )

    os.makedirs(os.path.join(OUT, "boundaries"), exist_ok=True)
    layers = {
        "avadi_wards_current": wards,
        "avadi_wards_tngis_original": ow,
        "avadi_go429_added_areas": add,
        "avadi_expanded_units": ex,
        "avadi_boundaries": bnd,
    }
    for n, g in layers.items():
        g.to_file(os.path.join(OUT, "boundaries", n + ".geojson"), driver="GeoJSON")
    json.dump(
        {
            "filled_slivers": filled,
            "areas": {
                n: round(float(g.to_crs(UTM).area.sum() / 1e6), 3)
                for n, g in layers.items()
            },
        },
        open(os.path.join(OUT, "work/boundaries_report.json"), "w"),
        indent=1,
        default=str,
    )
    print(add[["name", "unit_type", "go_item", "area_km2"]].to_string())
    print(
        "current",
        km2(cur),
        "expanded",
        km2(new),
        "slivers",
        len(filled),
        round(sum(a for _, a in filled), 3),
    )
    nb = list(getattr(new, "geoms", [new]))
    print(
        "expanded pieces",
        len(nb),
        "holes",
        sum(len(p.interiors) for p in nb if p.geom_type == "Polygon"),
    )
    ov = 0.0
    eg = list(ex.geometry)
    for i in range(len(eg)):
        for j in range(i + 1, len(eg)):
            ov += eg[i].intersection(eg[j]).area
    print(
        "overlap among expanded units km2",
        km2(Polygon()) if ov == 0 else round(ov * 111.32 * 108.5, 4),
    )


if __name__ == "__main__":
    main()
