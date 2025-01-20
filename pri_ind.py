import ee
import geemap
import os

ee.Initialize(project='edge3-448100')

def get_closest_image_from_collection(collection):
    def get_closest_image(timestamp):
        date = ee.Date(timestamp)
        filtered = collection.filterDate(date, date.advance(90, 'day'))
        image = filtered.sort('system:time_start').first()
        image_time = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd HH:mm:ss')
        pri = image.normalizedDifference(['B4', 'B5']).rename('PRI')
        return pri.set({
            'system:time_start': date.millis(),
            'image_capture_time': image_time
        })
    return get_closest_image





def file_exists(site_file, si):
    find = f"{site_file}_{si}_ind"
    for file in os.listdir("out"):
        if file.startswith(find):
            return True
    return False

def get_site(site_file):
    out_file_normal = f"{site_file}_pri_ind_timelapse.gif"
    out_file_date = f"{site_file}_pri_ind_timelapse_date.gif"
    if file_exists(site_file, "pri"):
        print(f"{out_file_normal} exists. Skipping.")
        return

    out_file_normal = os.path.join("out", out_file_normal)
    out_file_date = os.path.join("out", out_file_date)

    roi = geemap.geojson_to_ee(site_file)

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(roi)
        .filterDate('2021-01-01', '2025-01-01')
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
    )

    dates = ee.List.sequence(
        ee.Date('2021-01-01').millis(),
        ee.Date('2025-01-01').millis(),
        3 * 30 * 24 * 60 * 60 * 1000
    )

    frames = dates.map(get_closest_image_from_collection(collection))
    composites_pri = ee.ImageCollection(frames)

    video_args = {
        'dimensions': 720,
        'region': roi.geometry(),
        'framesPerSecond': 0.5,
        'min': -1,
        'max': 1,
        'palette': ['brown', 'white', 'green']
    }

    gif_path = out_file_normal
    geemap.download_ee_video(composites_pri, video_args, gif_path)

    capture_times = composites_pri.aggregate_array('image_capture_time').getInfo()
    capture_times = [f"{i + 1}: {time}" for i, time in enumerate(capture_times)]

    geemap.add_text_to_gif(
        gif_path,
        out_file_date,
        xy=(10, 50),
        text_sequence=capture_times,
        font_size=30,
        font_color='white',
        duration=2000
    )

sites = ["site_1.geojson", "site_2.geojson", "site_3.geojson", "site_4.geojson"]

for site in sites:
    get_site(site)
