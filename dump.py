import ee
import geemap
from matplotlib import pyplot as plt
import numpy as np
import requests
from io import BytesIO
from PIL import Image

ee.Initialize(project='edge3-448100')

geojson_files = ['site_1.geojson', 'site_2.geojson', 'site_3.geojson', 'site_4.geojson']
spectral_indices = {
    "NDVI": lambda img: img.normalizedDifference(['B8', 'B4']),
    "EVI": lambda img: img.expression(
        '2.5 * ((B8 - B4) / (B8 + 6 * B4 - 7.5 * B2 + 1))',
        {
            'B2': img.select('B2'),
            'B4': img.select('B4'),
            'B8': img.select('B8')
        }
    ),
    "SAVI": lambda img: img.expression(
        '((B8 - B4) / (B8 + B4 + 0.5)) * (1.0 + 0.5)',
        {
            'B4': img.select('B4'),
            'B8': img.select('B8')
        }
    ),
    "NDWI": lambda img: img.normalizedDifference(['B3', 'B8A']),
    "PRI": lambda img: img.expression(
        '((B3 - B4) / (B3 + B4))',
        {
            'B3': img.select('B3'),
            'B4': img.select('B4')
        }
    ),
    "MSAVI": lambda img: img.expression(
        '(2 * B8 + 1 - ((2 * B8 + 1) ** 2 - 8 * (B8 - B4)) ** 0.5) / 2',
        {
            'B4': img.select('B4'),
            'B8': img.select('B8')
        }
    ),
    "NDBI": lambda img: img.normalizedDifference(['B11', 'B8']),
    "NDII": lambda img: img.normalizedDifference(['B8', 'B11']),
    "Chlorophyll_Index": lambda img: img.expression(
        'B8A / B5 - 1',
        {
            'B5': img.select('B5'),
            'B8A': img.select('B8A')
        }
    )
}

for geojson in geojson_files:
    roi = geemap.geojson_to_ee(geojson).geometry()
    sentinel2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    latest_image = sentinel2.filterBounds(roi).sort('system:time_start', False).first()

    for index_name, index_function in spectral_indices.items():
        index_image = index_function(latest_image)
        vis_params = {'min': -1, 'max': 1, 'palette': ['blue', 'white', 'green']}
        thumb = index_image.visualize(**vis_params).getThumbURL({'region': roi.getInfo(), 'scale': 10})

        response = requests.get(thumb, stream=True)
        output_path = f"{geojson.split('.')[0]}_{index_name}.png"

        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Saved: {output_path}")
        else:
            print(f"Failed to download {index_name} for {geojson}")
