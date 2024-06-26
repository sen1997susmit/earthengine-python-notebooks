import ee 
from ee_plugin import Map 

# Image.ConnectedPixelCount example.

# Split pixels of band 01 into "bright" (arbitrarily defined as
# reflectance > 0.3) and "dim". Highlight small (<30 pixels)
# standalone islands of "bright" or "dim" type.
img = ee.Image('MODIS/006/MOD09GA/2012_03_09') \
              .select('sur_refl_b01') \
              .multiply(0.0001)

# Create a threshold image.
bright = img.gt(0.3)

# Compute connected pixel counts; stop searching for connected pixels
# once the size of the connected neightborhood reaches 30 pixels, and
# use 8-connected rules.
conn = bright.connectedPixelCount({
  'maxSize': 30,
  'eightConnected': True
})

# Make a binary image of small clusters.
smallClusters = conn.lt(30)

Map.setCenter(-107.24304, 35.78663, 8)
Map.addLayer(img, {'min': 0, 'max': 1}, 'original')
Map.addLayer(smallClusters.updateMask(smallClusters),
         {'min': 0, 'max': 1, 'palette': 'FF0000'}, 'cc')
