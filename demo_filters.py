# the geo json geometry object we got from geojson.io
geo_json_geometry = {
  "type": "Polygon",
  "coordinates": [[[-123.45886230468749,39.499802162332884],[-123.44238281249997,39.24501680713314],[-123.1182861328125,39.24501680713314],[-123.08532714843749,39.47860556892209],[-123.45886230468749,39.499802162332884]]]
}

# filter for items the overlap with our chosen geometry
geometry_filter = {
  "type": "GeometryFilter",
  "field_name": "geometry",
  "config": geo_json_geometry
}

redding_reservoir = {
  "type": "AndFilter",
  "config": [geometry_filter]
}
