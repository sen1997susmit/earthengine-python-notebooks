# %%
"""
<table class="ee-notebook-buttons" align="left">
    <td><a target="_blank"  href="https://github.com/giswqs/earthengine-py-notebooks/tree/master/Image/hillshade.ipynb"><img width=32px src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a></td>
    <td><a target="_blank"  href="https://nbviewer.jupyter.org/github/giswqs/earthengine-py-notebooks/blob/master/Image/hillshade.ipynb"><img width=26px src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/883px-Jupyter_logo.svg.png" />Notebook Viewer</a></td>
    <td><a target="_blank"  href="https://colab.research.google.com/github/giswqs/earthengine-py-notebooks/blob/master/Image/hillshade.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run in Google Colab</a></td>
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
import math

Map.setCenter(-121.767, 46.852, 11)

def Radians(img):
  return img.toFloat().multiply(math.pi).divide(180)


def Hillshade(az, ze, slope, aspect):
  """Compute hillshade for the given illumination az, el."""
  azimuth = Radians(ee.Image(az))
  zenith = Radians(ee.Image(ze))
  # Hillshade = cos(Azimuth - Aspect) * sin(Slope) * sin(Zenith) +
  #     cos(Zenith) * cos(Slope)
  return (azimuth.subtract(aspect).cos()
          .multiply(slope.sin())
          .multiply(zenith.sin())
          .add(
              zenith.cos().multiply(slope.cos())))

terrain = ee.Algorithms.Terrain(ee.Image('srtm90_v4'))
slope_img = Radians(terrain.select('slope'))
aspect_img = Radians(terrain.select('aspect'))

# Add 1 hillshade at az=0, el=60.
Map.addLayer(Hillshade(0, 60, slope_img, aspect_img), {}, 'Hillshade')


# %%
"""
## Display Earth Engine data layers 
"""

# %%
Map.addLayerControl() # This line is not needed for ipyleaflet-based Map.
Map