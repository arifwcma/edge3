import ee
import geemap

ee.Initialize(project='edge3-448100')
roi = geemap.geojson_to_ee("site_1.geojson")

def add_date_to_image(image):
    date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd').getInfo()
    text = ee.Image.constant(1).visualize(
        palette=['black'], opacity=0.8
    ).set('label', date)
    annotated = image.visualize(min=0, max=3000, palette=['black', 'white'])
    return ee.Image.cat(annotated, text)

def select_b4(image):
    return image.select(['B4'])

def create_composite_b4(start):
    start_date = ee.Date(start)
    end_date = start_date.advance(3, 'month')
    filtered = collection.filterDate(start_date, end_date).map(select_b4)
    return filtered.median().set('system:time_start', start_date.millis())

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

composites_b4 = ee.ImageCollection(dates.map(create_composite_b4))
annotated_composites = composites_b4.map(add_date_to_image)

video_args = {
    'dimensions': 720,
    'region': roi.geometry(),
    'framesPerSecond': 2
}

video_url = annotated_composites.getVideoThumbURL(video_args)
print(video_url)
