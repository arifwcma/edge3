import ee
import geemap
import os

ee.Initialize(project='edge3-448100')

os.makedirs("temp", exist_ok=True)

def calculate_difference_image(collection, timestamp):
    date1 = ee.Date(timestamp)
    date2 = date1.advance(90, 'day')
    date3 = date2.advance(90, 'day')
    filtered1 = collection.filterDate(date1, date2).filter(ee.Filter.listContains('system:band_names', 'B11')).filter(ee.Filter.listContains('system:band_names', 'B8A'))
    filtered2 = collection.filterDate(date2, date3).filter(ee.Filter.listContains('system:band_names', 'B11')).filter(ee.Filter.listContains('system:band_names', 'B8A'))
    mean_image1 = filtered1.mean().normalizedDifference(['B11', 'B8A']).rename('NDBI')
    mean_image2 = filtered2.mean().normalizedDifference(['B11', 'B8A']).rename('NDBI')
    diff_image = mean_image2.subtract(mean_image1).rename('NDBI_DIFF')
    return diff_image.set('system:time_start', date2.millis())

def count_images_in_collection(collection, date, offset):
    start_date = ee.Date(date)
    end_date = start_date.advance(offset, 'day')
    filtered_collection = collection.filterDate(start_date, end_date)
    return filtered_collection.size().getInfo()

def generate_gif_for_site(site_file):
    name = site_file.split(".")[0]
    roi = geemap.geojson_to_ee(site_file)
    collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(roi).filterDate('2021-01-01', '2024-07-01')
    collection_size = collection.size().getInfo()
    if collection_size == 0:
        return
    dates = ee.List.sequence(
        ee.Date('2021-01-01').millis(),
        ee.Date('2024-07-01').millis(),
        3 * 30 * 24 * 60 * 60 * 1000
    )
    def map_function(timestamp):
        return calculate_difference_image(collection, timestamp)
    frames = dates.slice(0, dates.length().subtract(1)).map(map_function)
    composites_ndbi_diff = ee.ImageCollection(frames)
    video_args = {
        'dimensions': 720,
        'region': roi.geometry(),
        'framesPerSecond': 0.5,
        'min': -2,
        'max': 2,
        'palette': ['red', 'white', 'green']
    }
    os.makedirs("diff", exist_ok=True)
    gif_path = os.path.join("temp", f"{name}_NDBI_raw.gif")
    geemap.download_ee_video(composites_ndbi_diff, video_args, gif_path)
    dates_list = dates.slice(0, dates.length().subtract(1)).map(lambda d: ee.Date(d).advance(45, "day").format('YYYY-MM-dd')).getInfo()
    frames_size = ee.ImageCollection(frames).size().getInfo()
    dates_list = dates_list[:frames_size]
    dates_list = [f"{i+1}: {d}" for i, d in enumerate(dates_list)]
    output_path_with_text = os.path.join("diff", f"{name}_NDBI.gif")
    geemap.add_text_to_gif(
        gif_path,
        output_path_with_text,
        xy=(10, 50),
        text_sequence=dates_list,
        font_size=30,
        font_color='white',
        duration=2000
    )

geojson_files = ['site_1.geojson', 'site_2.geojson', 'site_3.geojson', 'site_4.geojson']
for gf in geojson_files:
    generate_gif_for_site(gf)