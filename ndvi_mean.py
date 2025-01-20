import ee
import geemap
import os

ee.Initialize(project='edge3-448100')


def get_mean_image_from_collection(collection):
    def get_mean_image(timestamp):
        date = ee.Date(timestamp)
        filtered = collection.filterDate(date, date.advance(90, 'day'))
        mean_image = filtered.mean()
        ndvi = mean_image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        return ndvi.set('system:time_start', date.millis())
    return get_mean_image



def file_exists(site_file,si):
    find = f"{site_file}_{si}_mean"
    for file in os.listdir("out"):
        if file.startswith(find):
            return True
    return False


def get_site(site_file):
    out_file_normal = f"{site_file}_ndvi_mean_timelapse.gif"
    out_file_date = f"{site_file}_ndvi_mean_timelapse_date.gif"
    if file_exists(site_file, "ndvi"):
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

    frames = dates.map(get_mean_image_from_collection(collection))
    composites_ndvi = ee.ImageCollection(frames)

    video_args = {
        'dimensions': 720,
        'region': roi.geometry(),
        'framesPerSecond': 0.5,
        'min': -1,
        'max': 1,
        'palette': ['blue', 'white', 'green']
    }

    gif_path = out_file_normal
    geemap.download_ee_video(composites_ndvi, video_args, gif_path)

    dates_info = dates.map(lambda d: ee.Date(d).format('YYYY-MM-dd')).getInfo()
    dates_info = [f"{i + 1}: {date}" for i, date in enumerate(dates_info)]

    geemap.add_text_to_gif(
        gif_path,
        out_file_date,
        xy=(10, 50),
        text_sequence=dates_info,
        font_size=30,
        font_color='white',
        duration=2000
    )

sites = ["site_1.geojson","site_2.geojson","site_3.geojson","site_4.geojson"]

for site in sites:
    get_site(site)