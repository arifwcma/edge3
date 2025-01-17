import ee
import geemap

ee.Initialize(project='edge3-448100')
roi = geemap.geojson_to_ee("site_1.geojson")

def get_closest_image(timestamp):
    date = ee.Date(timestamp)
    filtered = collection.filterDate(date, date.advance(90, 'day'))
    image = filtered.sort('system:time_start').first()
    return image.select(['B4']).set('system:time_start', date.millis())

collection = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(roi)
    .filterDate('2020-01-01', '2024-01-01')
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
)

collection = collection.filter(ee.Filter.listContains('system:band_names', 'B4'))

dates = ee.List.sequence(
    ee.Date('2023-01-01').millis(),
    ee.Date('2024-01-01').millis(),
    3 * 30 * 24 * 60 * 60 * 1000
)

frames = dates.map(get_closest_image)
composites_b4 = ee.ImageCollection(frames)

video_args = {
    'dimensions': 720,
    'region': roi.geometry(),
    'framesPerSecond': 2,
    'min': 0,
    'max': 3000,
    'palette': ['black', 'white']
}

gif_path = 'ndvi_timelapse.gif'
geemap.download_ee_video(composites_b4, video_args, gif_path)

dates_info = dates.map(lambda d, i: ee.String(ee.Number(i).format('%d: ')).cat(ee.Date(d).format('YYYY-MM-dd'))).getInfo()

geemap.add_text_to_gif(
    gif_path,
    'ndvi_timelapse_with_date.gif',
    xy=(10, 50),
    text_sequence=dates_info,
    font_size=30,
    font_color='white',
)
