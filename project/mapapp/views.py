from django.shortcuts import render
import folium
import geemap
import ee
import os

# Initialize the Earth Engine API
ee.Initialize()


def index(request):
    # Create a map centered around a location of interest
    Map = geemap.Map(center=[30, 70], zoom=4)

    # Your forest cover analysis code here
    sf_bay_area = ee.Geometry.Rectangle([-123.0, 37.0, -121.0, 38.5])

    def maskS2clouds(image):
        qa = image.select("QA60")
        cloudBitMask = 1 << 10
        cirrusBitMask = 1 << 11
        mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0))
        return image.updateMask(mask).divide(10000)

    s2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterDate("2022-01-01", "2022-12-31")
        .filterBounds(sf_bay_area)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .map(maskS2clouds)
    )

    composite = s2.median()

    ndvi = composite.normalizedDifference(["B8", "B4"]).rename("NDVI")

    forest_threshold = 0.5
    sparse_threshold = 0.3

    forest_cover = (
        ee.Image(0)
        .where(ndvi.gte(forest_threshold), 3)
        .where(ndvi.lt(forest_threshold).And(ndvi.gte(sparse_threshold)), 2)
        .where(ndvi.lt(sparse_threshold), 1)
    )

    # For example, add a layer to the map
    vis_params = {"min": 1, "max": 3, "palette": ["red", "yellow", "green"]}

    Map = geemap.Map(center=[37.7, -122.0], zoom=9)
    Map.addLayer(
        forest_cover.clip(sf_bay_area), vis_params, "Forest Cover Classification"
    )
    Map.add_legend(
        title="Forest Cover",
        labels=["No Forest", "Medium Forest", "Dense Forest"],
        colors=[(255, 0, 0), (255, 255, 0), (0, 128, 0)],
    )

    # Define the path to save the HTML file
    map_path = os.path.join("mapapp", "templates", "mapapp", "map.html")

    # Save the map as an HTML file
    Map.save(map_path)

    return render(request, "mapapp/map.html")
