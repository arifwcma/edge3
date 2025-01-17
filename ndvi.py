import ee
import geemap

ee.Initialize(project='edge3-448100')
roi = geemap.geojson_to_ee("site_1.geojson")

def get_closest_image(timestamp):
    date = ee.Date(timestamp)
    filtered = collection.filterDate(date, date.advance(90, 'day'))
    image = filtered.sort('system:time_start').first()
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return ndvi.set('system:time_start', date.millis())

collection = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(roi)
    .filterDate('2021-01-01', '2025-01-01')
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
)

collection = collection.filter(ee.Filter.listContains('system:band_names', 'B4'))
collection = collection.filter(ee.Filter.listContains('system:band_names', 'B8'))

dates = ee.List.sequence(
    ee.Date('2021-01-01').millis(),
    ee.Date('2025-01-01').millis(),
    3 * 30 * 24 * 60 * 60 * 1000
)

frames = dates.map(get_closest_image)
composites_ndvi = ee.ImageCollection(frames)

video_args = {
    'dimensions': 720,
    'region': roi.geometry(),
    'framesPerSecond': 0.5,
    'min': -1,
    'max': 1,
    'palette': ['blue', 'white', 'green']
}

gif_path = 'ndvi_timelapse.gif'
geemap.download_ee_video(composites_ndvi, video_args, gif_path)

dates_info = dates.map(lambda d: ee.Date(d).format('YYYY-MM-dd')).getInfo()
dates_info = [f"{i + 1}: {date}" for i, date in enumerate(dates_info)]

geemap.add_text_to_gif(
    gif_path,
    'ndvi_timelapse_with_date.gif',
    xy=(10, 50),
    text_sequence=dates_info,
    font_size=30,
    font_color='white',
    duration=2000
)
