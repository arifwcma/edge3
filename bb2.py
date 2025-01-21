import ee
import geemap
import rasterio
from PIL import Image
import numpy as np

ee.Initialize(project='edge3-448100')

geojson_files = ['site_1.geojson','site_2.geojson','site_3.geojson','site_4.geojson']

for i, file in enumerate(geojson_files, 1):
    roi = geemap.geojson_to_ee(file)
    bounding_box = roi.geometry().bounds().buffer(2000).bounds()

    sentinel2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    latest_image = sentinel2.filterBounds(bounding_box).sort('system:time_start', False).first()
    rgb_image = latest_image.select(['B4', 'B3', 'B2']).visualize(min=0, max=3000)

    empty_image = ee.Image().byte()
    boundary_layer = empty_image.paint(roi, 1, 2).visualize(palette=['red'])

    final_image = ee.ImageCollection([rgb_image, boundary_layer]).mosaic()

    tif_output_path = f"roi_{i}_rgb.tif"
    geemap.download_ee_image(
        final_image,
        filename=tif_output_path,
        region=bounding_box.getInfo()['coordinates'],
        scale=10,
        crs='EPSG:4326'
    )
    print(f"ROI {i} image saved as {tif_output_path}")

    png_output_path = f"roi_{i}_rgb.png"
    with rasterio.open(tif_output_path) as src:
        array = src.read([1, 2, 3])
        array = np.moveaxis(array, 0, -1)
        img = Image.fromarray(array.astype('uint8'))
        img.save(png_output_path)
    print(f"ROI {i} image converted to {png_output_path}")