# %%
"""
<table class="ee-notebook-buttons" align="left">
    <td><a target="_blank"  href="https://github.com/giswqs/earthengine-py-notebooks/tree/master/Reducer/using_weights.ipynb"><img width=32px src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a></td>
    <td><a target="_blank"  href="https://nbviewer.jupyter.org/github/giswqs/earthengine-py-notebooks/blob/master/Reducer/using_weights.ipynb"><img width=26px src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/883px-Jupyter_logo.svg.png" />Notebook Viewer</a></td>
    <td><a target="_blank"  href="https://colab.research.google.com/github/giswqs/earthengine-py-notebooks/blob/master/Reducer/using_weights.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run in Google Colab</a></td>
</table>
"""

# %%
"""
## Install Earth Engine API and geemap
Install the [Earth Engine Python API](https://developers.google.com/earth-engine/python_install) and [geemap](https://geemap.org). The **geemap** Python package is built upon the [ipyleaflet](https://github.com/jupyter-widgets/ipyleaflet) and [folium](https://github.com/python-visualization/folium) packages and implements several methods for interacting with Earth Engine data layers, such as `Map.addLayer()`, `Map.setCenter()`, and `Map.centerObject()`.
The following script checks if the geemap package has been installed. If not, it will install geemap, which automatically installs its [dependencies](https://github.com/giswqs/geemap#dependencies), including earthengine-api, folium, and ipyleaflet.
"""

# %%
# Installs geemap package
import subprocess

try:
    import geemap
except ImportError:
    print('Installing geemap ...')
    subprocess.check_call(["python", '-m', 'pip', 'install', 'geemap'])

# %%
import ee
import geemap

# %%
"""
## Create an interactive map 
The default basemap is `Google Maps`. [Additional basemaps](https://github.com/giswqs/geemap/blob/master/geemap/basemaps.py) can be added using the `Map.add_basemap()` function. 
"""

# %%
Map = geemap.Map(center=[40,-100], zoom=4)
Map

# %%
"""
## Add Earth Engine Python script 
"""

# %%
# Add Earth Engine dataset
# Load an input Landsat 8 image.
image = ee.Image('LANDSAT/LC08/C01/T1_TOA/LC08_186059_20130419')

# Compute cloud score and reverse it such that the highest
# weight (100) is for the least cloudy pixels.
cloudWeight = ee.Image(100).subtract(
  ee.Algorithms.Landsat.simpleCloudScore(image).select(['cloud']))

# Compute NDVI and add the cloud weight band.
ndvi = image.normalizedDifference(['B5', 'B4']).addBands(cloudWeight)

# Define an arbitrary region in a cloudy area.
region = ee.Geometry.Rectangle(9.9069, 0.5981, 10.5, 0.9757)

# Use a mean reducer.
reducer = ee.Reducer.mean()

# Compute the unweighted mean.
unweighted = ndvi.select(['nd']).reduceRegion(reducer, region, 30)

# compute mean weighted by cloudiness.
weighted = ndvi.reduceRegion(reducer.splitWeights(), region, 30)

# Observe the difference as a result of weighting by cloudiness.
print('unweighted:', unweighted.getInfo())
print('weighted:', weighted.getInfo())



# %%
"""
## Display Earth Engine data layers 
"""

# %%
Map.addLayerControl() # This line is not needed for ipyleaflet-based Map.
Map