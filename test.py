import ee

d = ee.Date("2021-01-01")
e = d.advance(90, "day")
print(e)