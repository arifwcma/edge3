import ee
import geemap
import json
import os

ee.Initialize(project='edge3-448100')

sites = [
    {'name': 'site_1', 'geojson_path': 'site_1.geojson'},
    {'name': 'site_2', 'geojson_path': 'site_2.geojson'},
    {'name': 'site_3', 'geojson_path': 'site_3.geojson'},
    {'name': 'site_4', 'geojson_path': 'site_4.geojson'},
]

output_folder = "central"
os.makedirs(output_folder, exist_ok=True)

for site in sites:
    name = site['name']
    geojson_path = site['geojson_path']

    with open(geojson_path) as f:
        geojson = json.load(f)

    polygon = ee.Geometry.Polygon(geojson['features'][0]['geometry']['coordinates'])
    center = polygon.centroid()
    highlight_square = center.buffer(50).bounds()

    collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(polygon) \
        .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 5) \
        .sort('system:time_start', False)

    latest_image = collection.first()

    true_color_vis = latest_image.visualize(
        bands=['TCI_R', 'TCI_G', 'TCI_B'],
        min=0, max=255
    )

    highlight_area = ee.Image().paint(highlight_square, 1).visualize(
        palette=['red']
    )

    combined_image = ee.ImageCollection([true_color_vis, highlight_area]).mosaic()

    output_path = os.path.join(output_folder, f"{name}_highlight.tif")
    geemap.ee_export_image(
        combined_image,
        filename=output_path,
        scale=10,
        region=polygon,
        file_per_band=False
    )

    print(f"Image for {name} saved to {output_path}")