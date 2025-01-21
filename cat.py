import ee
import geemap
import requests
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

for idx, geojson in enumerate(geojson_files, 1):
    roi = geemap.geojson_to_ee(geojson).geometry()
    buffered_roi = roi.buffer(2000).bounds()
    sentinel2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED').filterBounds(buffered_roi).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
    latest_image = sentinel2.sort('system:time_start', False).first()

    capture_date = latest_image.date().format('yyyy_MM_dd').getInfo()
    rgb_image = latest_image.select(['B4', 'B3', 'B2']).visualize(min=0, max=3000)
    boundary_layer = ee.Image().byte().paint(roi, 1, 2).visualize(palette=['red'])
    combined_image = ee.ImageCollection([rgb_image, boundary_layer]).mosaic()
    boundary_url = combined_image.getThumbURL({'region': buffered_roi.getInfo(), 'scale': 100})
    inset_path = f"site_{idx}_inset.png"

    boundary_response = requests.get(boundary_url, stream=True)
    if boundary_response.status_code == 200:
        with open(inset_path, 'wb') as f:
            for chunk in boundary_response.iter_content(1024):
                f.write(chunk)
        print(f"Saved: {inset_path}")
    else:
        print(f"Failed to download inset image for {geojson}")

    for index_name, index_function in spectral_indices.items():
        index_image = index_function(latest_image)
        vis_params = {'min': -1, 'max': 1, 'palette': ['blue', 'white', 'green']}
        thumb = index_image.visualize(**vis_params).getThumbURL({'region': roi.getInfo(), 'scale': 10})

        response = requests.get(thumb, stream=True)
        si_path = f"site_{idx}_{index_name}.png"

        if response.status_code == 200:
            with open(si_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Saved: {si_path}")

            with Image.open(si_path) as si_img, Image.open(inset_path) as inset_img:
                new_width = si_img.width + int(inset_img.width * 1.5)
                new_height = max(si_img.height, int(inset_img.height * 1.5))
                combined = Image.new("RGB", (new_width, new_height))
                combined.paste(si_img, (0, 0))
                inset_img_resized = inset_img.resize((int(inset_img.width * 1.5), int(inset_img.height * 1.5)))
                combined.paste(inset_img_resized, (si_img.width, 0))
                combined_output = f"{index_name}_{idx}_{capture_date}.png"
                combined.save(combined_output)
                print(f"Saved combined image: {combined_output}")
        else:
            print(f"Failed to download {index_name} for {geojson}")
