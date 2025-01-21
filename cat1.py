import ee
import geemap
import requests
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.colors import LinearSegmentedColormap

ee.Initialize(project='edge3-448100')

geojson_files = ['site_1.geojson']
spectral_indices = {
    "NDII": lambda img: img.normalizedDifference(['B8', 'B11'])
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

    for index_name, index_function in spectral_indices.items():
        index_image = index_function(latest_image)
        palette = ['blue', 'white', 'green']
        cmap = LinearSegmentedColormap.from_list('custom', palette)
        vis_params = {'min': -1, 'max': 1, 'palette': palette}
        thumb = index_image.visualize(**vis_params).getThumbURL({'region': roi.getInfo(), 'scale': 10})

        response = requests.get(thumb, stream=True)
        si_path = f"temp/site_{idx}_{index_name}.png"

        if response.status_code == 200:
            with open(si_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            si_img_array = np.array(Image.open(si_path).convert('RGB'))
            fig, ax = plt.subplots(figsize=(10, 8))
            cax = ax.imshow(si_img_array)
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=-1, vmax=1))
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