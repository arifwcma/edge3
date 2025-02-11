import ee
import json
import os
import pandas as pd
import numpy as np


def restart_gee_session():
    ee.Reset()
    ee.Initialize(project='edge3-448100')


sites = [
    {'name': 'site_1', 'geojson_path': 'site_1.geojson'},
    {'name': 'site_2', 'geojson_path': 'site_2.geojson'},
    {'name': 'site_3', 'geojson_path': 'site_3.geojson'},
    {'name': 'site_4', 'geojson_path': 'site_4.geojson'}
]

output_folder = "central"
os.makedirs(output_folder, exist_ok=True)

for site in sites:
    restart_gee_session()
    name = site['name']
    geojson_path = site['geojson_path']

    with open(geojson_path) as f:
        geojson = json.load(f)

    polygon = ee.Geometry.Polygon(geojson['features'][0]['geometry']['coordinates'])
    center = polygon.centroid()
    highlight_square = center.buffer(50).bounds()

    collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(polygon)

    start_date = ee.Date('2021-01-01')
    end_date = ee.Date('2024-12-31')

    data = []

    while start_date.millis().getInfo() < end_date.millis().getInfo():
        restart_gee_session()
        print(start_date.millis().getInfo())
        print(end_date.millis().getInfo())
        next_month = start_date.advance(1, 'month')
        images = collection.filterDate(start_date, next_month)
        pri_stats = images.map(lambda img: img.normalizedDifference(['B3', 'B5'])).mean().reduceRegion(
            reducer=ee.Reducer.mean().combine(
                ee.Reducer.stdDev(), sharedInputs=True).combine(
                ee.Reducer.count(), sharedInputs=True
            ),
            geometry=highlight_square,
            scale=10
        ).getInfo()

        if pri_stats:
            avg_si = pri_stats.get('nd_mean', None)
            std = pri_stats.get('nd_stdDev', None)
            num = pri_stats.get('nd_count', None)
            data.append({
                'year': start_date.get('year').getInfo(),
                'month': start_date.get('month').getInfo(),
                'avg_si': avg_si,
                'num': num,
                'std': std
            })

        start_date = next_month

    df = pd.DataFrame(data)
    csv_path = os.path.join(output_folder, f"{name}_pri_stats2.csv")
    df.to_csv(csv_path, index=False)
    print(f"CSV for {name} saved to {csv_path}")
