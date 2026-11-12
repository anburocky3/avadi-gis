# Avadi: current wards, the G.O. 201 expansion, roads and pipelines

All layers are WGS84 (EPSG:4326). Each is provided three ways:

- GeoJSON in the folders;
- Shapefile in `shapefiles/` (field names cut to 10 characters);
- together in `avadi_gis.gpkg`, one file to open in QGIS.

`avadi_expanded_check.png` is a picture of the result.

Everything here is new. The source files were only read.

## The expansion

The source is G.O. (Ms) No. 201, MAWS (Elections), 31 Dec 2024, printed in the Tamil Nadu Government Gazette Extraordinary No. 429, Part II-2, Table Sl. 11. It declares the **intention** to add 20 local areas to Avadi Corporation, each to its full extent:

- 3 municipalities: Poonamallee, Tiruverkadu and Tirunindravur;
- 4 village panchayats in Villivakkam union: Vellanur, Ayappakkam, Palavedu and Morai;
- 13 village panchayats in Poonamallee union: Nemilicheri, Nadukuthagai, Kattupakkam, Senneerkuppam, Varadarajapuram, Nazarethpettai, Agaramel, Banaveduthottam, Parivakkam, Kannapalayam, Soranjeri, Karunakaracheri and Meppur.

Adayalampattu and Vanagaram, which border Avadi, go to Chennai under Sl. 12 of the same notice, not to Avadi. New ward numbers for the enlarged corporation have not been published, so the added areas keep their old units.

|                                 | km²       |
| ------------------------------- | --------- |
| Avadi now (48 wards)            | 65.0      |
| Added under the G.O. (20 areas) | 105.6     |
| **Avadi expanded**              | **170.7** |

## Boundary files (`boundaries/`)

| File                         | What it is                                                                                                                                                       |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `avadi_wards_current`        | The 48 wards as used on the reclaimchennai `/lb` map. These are TNGIS wards with the slivers between wards given to the nearest ward.                            |
| `avadi_wards_tngis_original` | The same 48 wards exactly as TNGIS publishes them (62.1 km²), for comparison.                                                                                    |
| `avadi_go429_added_areas`    | The 20 added areas, one feature each. Each carries its gazette item, panchayat union, LGD code and area; `tngis_vp_km2` is the panchayat's full TNGIS area.      |
| `avadi_expanded_units`       | The whole expanded corporation as 88 units with no gaps or overlaps: Avadi's 48 wards, Poonamallee's 21 wards, Tiruverkadu, Tirunindravur and the 17 panchayats. |
| `avadi_boundaries`           | Two outlines: current and expanded.                                                                                                                              |

How the boundaries were put together:

- **Municipalities:** the TNGIS ULB wards as corrected for `/lb`. TNGIS's own Tiruverkadu polygon is only 2.8 km². The Survey of India layer (`~/Downloads/TAMILNADU`, revenue villages, updated 20 Aug 2025) has Tiruverkadu (M) at 18.8 km², and the `/lb` version (18.2 km²) is used.
- **Village panchayats:** TNGIS village panchayat polygons. These predate the 2019 corporation, so each gives up whatever already lies inside Avadi or one of the three municipalities. Kannapalayam drops from 17.6 to 6.1 km² and Soranjeri from 6.5 to 1.9 km², because Avadi already took most of them. The Survey of India layer has revenue villages, which are smaller than panchayats (Soranjeri A is only part of Soranjeri), so it was used to check the panchayats, not to replace them.
- **Slivers:** the TNGIS layers leave 119 slivers, 0.54 km² in all, inside the new outline. Each went to the added area the Survey of India village there belongs to, else to the neighbour sharing the longest border.
- **Notches in the outline:** these are bodies the G.O. leaves out: Thirumazhisai Town Panchayat, Kosavanpalayam and Voyalanallur panchayats, Chennai on the east, and Mangadu to the south.

## Roads, pipelines, drainage

Each layer is copied from the TNGIS archive (`tngis-data`, pulled from TNGIS's public map server) and clipped to the expanded outline. Every feature has `in_current_avadi` (true if it is in today's corporation) and `source_layer`.

| Layer                                                       | Features          | km              | What                                                                       |
| ----------------------------------------------------------- | ----------------- | --------------- | -------------------------------------------------------------------------- |
| `pipelines/water_pipeline_ulb`                              | 3,987             | 258             | Water supply mains (PM Gati Shakti, ULB)                                   |
| `pipelines/underground_drainage_ulb`                        | 15,111            | 416             | Sewer lines (PM Gati Shakti, ULB)                                          |
| `pipelines/water_flow_direction_ulb`                        | 579               | 11              | Flow-direction arrows for the sewer network                                |
| `pipelines/ulb_utility`                                     | 744               | points          | Utility points (PM Gati Shakti)                                            |
| `pipelines/cmwssb_metrowater_pipeline`                      | 6                 | 21              | Chennai Metrowater trunk mains crossing the area                           |
| `pipelines/cmwssb_new_sewer_main`, `cmwssb_new_machinehole` | 114 / 88          | 3               | Chennai Metrowater new sewer main and manholes at the edge                 |
| `roads/road_network_tngis`                                  | 11,494            | 2,022           | TNGIS statewide road network (the shapefile in `~/Downloads/Road Network`) |
| `roads/all_roads_tamilnadu`                                 | 11,361            | 2,035           | TNGIS all-roads layer                                                      |
| `roads/roads_ulb`                                           | 16,172            | 1,060           | Corporation roads with names and widths (PM Gati Shakti)                   |
| `roads/village_roads`, `rural_roads`, `tnrd_roads`          | 1,722 / 416 / 607 | 531 / 158 / 316 | Rural Development roads                                                    |
| `roads/major_district_roads`, `other_district_roads`        | 5 / 17            | 8 / 36          | Highways Department roads                                                  |
| `drainage/natural_drainage`                                 | 124               | 48              | Streams and channels                                                       |

Some layers were left out because they hold nothing here or repeat another layer:

- CMWSSB sewage pipeline and sewerage pumping stations have no features in the area.
- `cma/ugddata`, `cma/road_details` and `tnrd_rural_roads` are exact duplicates of the ULB drainage, ULB roads and rural roads layers. They were not copied twice; the copies are in `work/superseded_duplicates/`.

## Gaps

- **Pipelines exist only for today's corporation.** TNGIS publishes the water and sewer networks for Avadi Corporation only. I asked its live map server on 10 Nov 2026, and it returned nothing for Poonamallee, Tiruverkadu, Tirunindravur or the panchayats. Roads cover the whole expanded area.
- **The G.O. is a notice of intention.** Check for the final notification before treating the expanded outline as settled.
- **Population fields:** the `total_population` and household fields in the ward files hold the 2011 total for old Avadi municipality on every ward. They are not per-ward figures.
- **Boundaries are indicative.** Survey numbers decide the legal limits.

`work/` holds the build scripts (`build_boundaries.py`, `clip_layers.py`), their reports and the source cuts.

# Credits

- [reclaimchennai](https://github.com/reclaimchennai)
