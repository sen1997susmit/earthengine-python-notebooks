# %%
"""
<table class="ee-notebook-buttons" align="left">
    <td><a target="_blank"  href="https://github.com/giswqs/earthengine-py-notebooks/tree/master/JavaScripts/Arrays/SpectralUnmixing.ipynb"><img width=32px src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a></td>
    <td><a target="_blank"  href="https://nbviewer.jupyter.org/github/giswqs/earthengine-py-notebooks/blob/master/JavaScripts/Arrays/SpectralUnmixing.ipynb"><img width=26px src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/883px-Jupyter_logo.svg.png" />Notebook Viewer</a></td>
    <td><a target="_blank"  href="https://colab.research.google.com/github/giswqs/earthengine-py-notebooks/blob/master/JavaScripts/Arrays/SpectralUnmixing.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run in Google Colab</a></td>
</table>
"""

# %%
"""
## Install Earth Engine API and geemap
Install the [Earth Engine Python API](https://developers.google.com/earth-engine/python_install) and [geemap](https://github.com/giswqs/geemap). The **geemap** Python package is built upon the [ipyleaflet](https://github.com/jupyter-widgets/ipyleaflet) and [folium](https://github.com/python-visualization/folium) packages and implements several methods for interacting with Earth Engine data layers, such as `Map.addLayer()`, `Map.setCenter()`, and `Map.centerObject()`.
The following script checks if the geemap package has been installed. If not, it will install geemap, which automatically installs its [dependencies](https://github.com/giswqs/geemap#dependencies), including earthengine-api, folium, and ipyleaflet.

**Important note**: A key difference between folium and ipyleaflet is that ipyleaflet is built upon ipywidgets and allows bidirectional communication between the front-end and the backend enabling the use of the map to capture user input, while folium is meant for displaying static data only ([source](https://blog.jupyter.org/interactive-gis-in-jupyter-with-ipyleaflet-52f9657fa7a)). Note that [Google Colab](https://colab.research.google.com/) currently does not support ipyleaflet ([source](https://github.com/googlecolab/colabtools/issues/60#issuecomment-596225619)). Therefore, if you are using geemap with Google Colab, you should use [`import geemap.eefolium`](https://github.com/giswqs/geemap/blob/master/geemap/eefolium.py). If you are using geemap with [binder](https://mybinder.org/) or a local Jupyter notebook server, you can use [`import geemap`](https://github.com/giswqs/geemap/blob/master/geemap/geemap.py), which provides more functionalities for capturing user input (e.g., mouse-clicking and moving).
"""

# %%
# Installs geemap package
import subprocess

try:
    import geemap
except ImportError:
    print('geemap package not installed. Installing ...')
    subprocess.check_call(["python", '-m', 'pip', 'install', 'geemap'])

# Checks whether this notebook is running on Google Colab
try:
    import google.colab
    import geemap.eefolium as geemap
except:
    import geemap

# Authenticates and initializes Earth Engine
import ee

try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()  

# %%
"""
## Create an interactive map 
The default basemap is `Google MapS`. [Additional basemaps](https://github.com/giswqs/geemap/blob/master/geemap/basemaps.py) can be added using the `Map.add_basemap()` function. 
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
# Array-based spectral unmixing.

# Create a mosaic of Landsat 5 images from June through September, 2007.
allBandMosaic = ee.ImageCollection('LANDSAT/LT05/C01/T1') \
  .filterDate('2007-06-01', '2007-09-30') \
  .select('B[0-7]') \
  .median()

# Create some representative endmembers computed previously by sampling
# the Landsat 5 mosaic.
urbanEndmember = [88, 42, 48, 38, 86, 115, 59]
vegEndmember = [50, 21, 20, 35, 50, 110, 23]
waterEndmember = [51, 20, 14, 9, 7, 116, 4]

# Compute the 3x7 pseudo inverse.
endmembers = ee.Array([urbanEndmember, vegEndmember, waterEndmember])
inverse = ee.Image(endmembers.matrixPseudoInverse().transpose())

# Convert the bands to a 2D 7x1 array. The toArray() call concatenates
# pixels from each band along the default axis 0 into a 1D vector per
# pixel, and the toArray(1) call concatenates each band (in this case
# just the one band of 1D vectors) along axis 1, forming a 2D array.
inputValues = allBandMosaic.toArray().toArray(1)

# Matrix multiply the pseudo inverse of the endmembers by the pixels to
# get a 3x1 set of endmembers fractions from 0 to 1.
unmixed = inverse.matrixMultiply(inputValues)

# Create and show a colored image of the endmember fractions. Since we know
# the result has size 3x1, project down to 1D vectors at each pixel (since the
# second axis is pointless now), and then flatten back to a regular scalar
# image.
colored = unmixed \
  .arrayProject([0]) \
  .arrayFlatten([['urban', 'veg', 'water']])
Map.setCenter(-98.4, 19, 11)

# Load a hillshade to use as a backdrop.
Map.addLayer(ee.Algorithms.Terrain(ee.Image('CGIAR/SRTM90_V4')).select('hillshade'))
Map.addLayer(colored, {'min': 0, 'max': 1},
  'Unmixed (red=urban, green=veg, blue=water)')


# %%
"""
## Display Earth Engine data layers 
"""

# %%
Map.addLayerControl() # This line is not needed for ipyleaflet-based Map.
Map