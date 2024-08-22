from django.shortcuts import render
import folium
import geemap
import ee

# Initialize the Earth Engine API
ee.Initialize()


def index(request):
    # Create a map centered around a location of interest
    Map = geemap.Map(center=[30, 70], zoom=4)

    # Your forest cover analysis code here
    # For example, add a layer to the map
    forest = ee.Image(
        "projects/earthengine-legacy/assets/projects/wri-datalab/ATLAS/Forest/v4"
    )
    Map.addLayer(forest, {}, "Forest Cover")

    # Save the map as an HTML file
    map_html = Map._repr_html_()

    return render(request, "mapapp/map.html", {"map": map_html})
