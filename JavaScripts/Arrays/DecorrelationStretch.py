# %%
"""
<table class="ee-notebook-buttons" align="left">
    <td><a target="_blank"  href="https://github.com/giswqs/earthengine-py-notebooks/tree/master/JavaScripts/Arrays/DecorrelationStretch.ipynb"><img width=32px src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a></td>
    <td><a target="_blank"  href="https://nbviewer.jupyter.org/github/giswqs/earthengine-py-notebooks/blob/master/JavaScripts/Arrays/DecorrelationStretch.ipynb"><img width=26px src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/883px-Jupyter_logo.svg.png" />Notebook Viewer</a></td>
    <td><a target="_blank"  href="https://colab.research.google.com/github/giswqs/earthengine-py-notebooks/blob/master/JavaScripts/Arrays/DecorrelationStretch.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run in Google Colab</a></td>
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
# Decorrelation Stretch

def dcs(image, region, scale):
  bandNames = image.bandNames()

  # The axes are numbered, so to make the following code more
  # readable, give the axes names.
  imageAxis = 0
  bandAxis = 1

  # Compute the mean of each band in the region.
  means = image.reduceRegion(ee.Reducer.mean(), region, scale)

  # Create a constant array image from the mean of each band.
  meansArray = ee.Image(means.toArray())

  # Collapse the bands of the image into a 1D array per pixel,
  # with images along the first axis and bands along the second.
  arrays = image.toArray()

  # Perform element-by-element subtraction, which centers the
  # distribution of each band within the region.
  centered = arrays.subtract(meansArray)

  # Compute the covariance of the bands within the region.
  covar = centered.reduceRegion({
    'reducer': ee.Reducer.centeredCovariance(),
    'geometry': region,
    'scale': scale
  })

  # Get the 'array' result and cast to an array. Note this is a
  # single array, not one array per pixel, and represents the
  # band-to-band covariance within the region.
  covarArray = ee.Array(covar.get('array'))

  # Perform an eigen analysis and slice apart the values and vectors.
  eigens = covarArray.eigen()
  eigenValues = eigens.slice(bandAxis, 0, 1)
  eigenVectors = eigens.slice(bandAxis, 1)

  # Rotate by the eigenvectors, scale to a variance of 30, and rotate back.
  i = ee.Array.identity(bandNames.length())
  variance = eigenValues.sqrt().matrixToDiag()
  scaled = i.multiply(30).divide(variance)
  rotation = eigenVectors.transpose() \
    .matrixMultiply(scaled) \
    .matrixMultiply(eigenVectors)

  # Reshape the 1-D 'normalized' array, so we can left matrix multiply
  # with the rotation. This requires embedding it in 2-D space and
  # transposing.
  transposed = centered.arrayRepeat(bandAxis, 1).arrayTranspose()

  # Convert rotated results to 3 RGB bands, and shift the mean to 127.
  return transposed.matrixMultiply(ee.Image(rotation)) \
    .arrayProject([bandAxis]) \
    .arrayFlatten([bandNames]) \
    .add(127).byte()


image = ee.Image('MODIS/006/MCD43A4/2002_07_04')

Map.setCenter(-52.09717, -7.03548, 7)

# View the original bland image.
rgb = [0, 3, 2]
Map.addLayer(image.select(rgb), {'min': -100, 'max': 2000}, 'Original Image')

# Stretch the values within an interesting region.
region = ee.Geometry.Rectangle(-57.04651, -8.91823, -47.24121, -5.13531)
Map.addLayer(dcs(image, region, 1000).select(rgb), {}, 'DCS Image')

# Display the region in which covariance stats were computed.
Map.addLayer(ee.Image().paint(region, 0, 2), {}, 'Region')



# %%
"""
## Display Earth Engine data layers 
"""

# %%
Map.addLayerControl() # This line is not needed for ipyleaflet-based Map.
Map