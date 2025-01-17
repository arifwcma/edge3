import ee
import geemap
ee.Initialize(project='edge3-448100')
roi = geemap.geojson_to_ee("site_1.geojson")

def calculate_ndvi(image):
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return image.addBands(ndvi)

def create_composite(start):
    start_date = ee.Date(start)
    end_date = start_date.advance(3, 'month')
    filtered = ndvi_collection.filterDate(start_date, end_date)
    return filtered.median().set('system:time_start', start_date.millis())

collection = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(roi)
    .filterDate('2020-01-01', '2024-01-01')
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
)

valid_bands_filter = ee.Filter.listContains('system:band_names', 'B8').And(
    ee.Filter.listContains('system:band_names', 'B4')
)

filtered_collection = collection.filter(valid_bands_filter)

ndvi_collection = filtered_collection.map(calculate_ndvi)

first_image = ndvi_collection.first()
print(first_image.bandNames().getInfo())

dates = ee.List.sequence(
    ee.Date('2020-01-01').millis(),
    ee.Date('2024-01-01').millis(),
    3 * 30 * 24 * 60 * 60 * 1000
)

composites = ee.ImageCollection(dates.map(create_composite))

video_args = {
    'dimensions': 720,
    'region': roi.geometry(),
    'framesPerSecond': 2,
    'min': 0,
    'max': 1,
    'palette': ['blue', 'white', 'green']
}

composites_size = composites.size().getInfo()
print(f"Number of images in composites: {composites_size}")


video_url = composites.select('NDVI').getVideoThumbURL(video_args)
print(video_url)
