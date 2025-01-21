import ee
import geemap
import requests
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.colors import LinearSegmentedColormap

ee.Initialize(project='edge3-448100')

geojson_files = ['site_1.geojson', 'site_2.geojson', 'site_3.geojson', 'site_4.geojson']
spectral_indices = {
    "NDVI": {
        "function": lambda img: img.normalizedDifference(['B8', 'B4']),
        "vis_params": {"min": -0.1, "max": 0.9, "palette": ["brown", "yellow", "green"]}
    },
    "EVI": {
        "function": lambda img: img.expression(
            '2.5 * ((B8 - B4) / (B8 + 6 * B4 - 7.5 * B2 + 1))',
            {'B2': img.select('B2'), 'B4': img.select('B4'), 'B8': img.select('B8')}
        ),
        "vis_params": {"min": -1, "max": 1, "palette": ["white", "lightgreen", "darkgreen"]}
    },
    "NDWI": {
        "function": lambda img: img.normalizedDifference(['B3', 'B8A']),
        "vis_params": {"min": -1, "max": 1, "palette": ["blue", "white", "lightblue"]}
    },
    "SAVI": {
        "function": lambda img: img.expression(
            '((B8 - B4) / (B8 + B4 + 0.5)) * (1.0 + 0.5)',
            {'B4': img.select('B4'), 'B8': img.select('B8')}
        ),
        "vis_params": {"min": 0, "max": 1, "palette": ["yellow", "lightgreen", "green"]}
    },
    "NDII": {
        "function": lambda img: img.normalizedDifference(['B8', 'B11']),
        "vis_params": {"min": -0.5, "max": 1, "palette": ["blue", "white", "green"]}
    }
}

os.makedirs("temp", exist_ok=True)

for idx, geojson in enumerate(geojson_files, 1):
    roi = geemap.geojson_to_ee(geojson).geometry()
    buffered_roi = roi.buffer(2000).bounds()
    sentinel2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED').filterBounds(buffered_roi).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
    latest_image = sentinel2.sort('system:time_start', False).first()

    capture_date = latest_image.date().format('yyyy_MM_dd').getInfo()
    rgb_image = latest_image.select(['B4', 'B3', 'B2']).visualize(min=0, max=3000)
    boundary_layer = ee.Image().byte().paint(roi, 1, 2).visualize(palette=['red'])
    combined_image = ee.ImageCollection([rgb_image, boundary_layer]).mosaic()
    boundary_url = combined_image.getThumbURL({'region': buffered_roi.getInfo(), 'scale': 25})
    inset_path = f"temp/site_{idx}_inset.png"

    boundary_response = requests.get(boundary_url, stream=True)
    if boundary_response.status_code == 200:
        with open(inset_path, 'wb') as f:
            for chunk in boundary_response.iter_content(1024):
                f.write(chunk)
    else:
        continue

    for index_name, index_data in spectral_indices.items():
        index_function = index_data["function"]
        vis_params = index_data["vis_params"]

        index_image = index_function(latest_image)
        thumb = index_image.visualize(**vis_params).getThumbURL({'region': roi.getInfo(), 'scale': 10})

        response = requests.get(thumb, stream=True)
        si_path = f"temp/site_{idx}_{index_name}.png"

        if response.status_code == 200:
            with open(si_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            palette = vis_params["palette"]
            cmap = LinearSegmentedColormap.from_list('custom', palette)

            si_img_array = np.array(Image.open(si_path).convert('RGB'))
            fig, ax = plt.subplots(figsize=(10, 8))
            cax = ax.imshow(si_img_array)
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vis_params["min"], vmax=vis_params["max"]))
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, orientation='vertical', fraction=0.03, pad=0.04)
            cbar.set_label(f"{index_name} Value", rotation=90, labelpad=15)
            ax.axis('off')

            plt_path = f"temp/site_{idx}_{index_name}_matplotlib.png"
            plt.savefig(plt_path, bbox_inches='tight', pad_inches=0)
            plt.close()

            output_dir = f"si/{index_name}"
            os.makedirs(output_dir, exist_ok=True)
            combined_output = f"{output_dir}/{idx}_{capture_date}.png"

            with Image.open(plt_path) as si_img, Image.open(inset_path) as inset_img:
                new_width = si_img.width + int(inset_img.width * 1.5)
                new_height = max(si_img.height, int(inset_img.height * 1.5))
                combined = Image.new("RGB", (new_width, new_height))
                combined.paste(si_img, (0, 0))
                inset_img_resized = inset_img.resize((int(inset_img.width * 1.5), int(inset_img.height * 1.5)))
                combined.paste(inset_img_resized, (si_img.width, 0))
                combined.save(combined_output)
        else:
            continue
