import ee
import geemap

ee.Initialize(project='edge3-448100')

paddock1 = geemap.geojson_to_ee('site_1.geojson')
paddock2 = geemap.geojson_to_ee('site_2.geojson')
paddock3 = geemap.geojson_to_ee('site_3.geojson')
paddock4 = geemap.geojson_to_ee('site_4.geojson')

all_paddocks = paddock1.merge(paddock2).merge(paddock3).merge(paddock4)
bounding_box = all_paddocks.geometry().bounds().buffer(100).bounds()

sentinel2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
latest_image = sentinel2.filterBounds(bounding_box).sort('system:time_start', False).first()
rgb_image = latest_image.select(['B4', 'B3', 'B2']).visualize(min=0, max=3000)

empty_image = ee.Image().byte()

paddock_layer1 = empty_image.paint(paddock1, 1).visualize({'palette': 'red'})
paddock_layer2 = empty_image.paint(paddock2, 1).visualize({'palette': 'blue'})
paddock_layer3 = empty_image.paint(paddock3, 1).visualize({'palette': 'green'})
paddock_layer4 = empty_image.paint(paddock4, 1).visualize({'palette': 'yellow'})

map_layer = ee.ImageCollection([rgb_image, paddock_layer1, paddock_layer2, paddock_layer3, paddock_layer4]).mosaic()

print(map_layer)