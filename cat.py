spectral_indices = {
    "NDVI": {
        "function": lambda img: img.normalizedDifference(['B8', 'B4']),
        "vis_params": {"min": -0.1, "max": 0.9, "palette": ["white", "lightgreen", "darkgreen"]}
    },
    "EVI": {
        "function": lambda img: img.expression(
            '2.5 * ((B8 - B4) / (B8 + 6 * B4 - 7.5 * B2 + 1))',
            {'B2': img.select('B2'), 'B4': img.select('B4'), 'B8': img.select('B8')}
        ),
        "vis_params": {"min": -1, "max": 1, "palette": ["white", "lightgreen", "darkgreen"]}
    },
    "SAVI": {
        "function": lambda img: img.expression(
            '((B8 - B4) / (B8 + B4 + 0.5)) * (1.0 + 0.5)',
            {'B4': img.select('B4'), 'B8': img.select('B8')}
        ),
        "vis_params": {"min": 0, "max": 1, "palette": ["yellow", "lightgreen", "green"]}
    },
    "NDWI": {
        "function": lambda img: img.normalizedDifference(['B3', 'B8A']),
        "vis_params": {"min": -1, "max": 1, "palette": ["blue", "white", "lightblue"]}
    },
    "PRI": {
        "function": lambda img: img.expression(
            '((B3 - B4) / (B3 + B4))',
            {'B3': img.select('B3'), 'B4': img.select('B4')}
        ),
        "vis_params": {"min": -1, "max": 1, "palette": ["purple", "white", "green"]}
    },
    "MSAVI": {
        "function": lambda img: img.expression(
            '(2 * B8 + 1 - ((2 * B8 + 1) ** 2 - 8 * (B8 - B4)) ** 0.5) / 2',
            {'B4': img.select('B4'), 'B8': img.select('B8')}
        ),
        "vis_params": {"min": -1, "max": 1, "palette": ["brown", "white", "green"]}
    },
    "NDBI": {
        "function": lambda img: img.normalizedDifference(['B11', 'B8']),
        "vis_params": {"min": -0.5, "max": 0.5, "palette": ["purple", "white", "orange"]}
    },
    "NDII": {
        "function": lambda img: img.normalizedDifference(['B8', 'B11']),
        "vis_params": {"min": -0.5, "max": 1, "palette": ["blue", "white", "green"]}
    },
    "Chlorophyll_Index": {
        "function": lambda img: img.expression(
            'B8A / B5 - 1',
            {'B5': img.select('B5'), 'B8A': img.select('B8A')}
        ),
        "vis_params": {"min": 0, "max": 5, "palette": ["blue", "white", "darkgreen"]}
    }
}
