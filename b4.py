import ee
import geemap

ee.Initialize(project='edge3-448100')
roi = geemap.geojson_to_ee("site_1.geojson")

def get_closest_image(timestamp):
    date = ee.Date(timestamp)
    filtered = collection.filterDate(date, date.advance(90, 'day'))
    image = filtered.sort('system:time_start').first()
    image = image.select(['B4']).set('system:time_start', date.millis())
    label = ee.Image.constant(1).visualize(
        opacity=0.7, palette=['black']
    ).set('label', date.format('YYYY-MM-dd'))
    return image.visualize(min=0, max=3000, palette=['black', 'white']).blend(label)

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
frames_size = composites_b4.size().getInfo()
print(frames_size)

video_args = {
    'dimensions': 720,
    'region': roi.geometry(),
    'framesPerSecond': 2,
}

video_url = composites_b4.getVideoThumbURL(video_args)
print(video_url)
