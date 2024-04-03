import ee 
from ee_plugin import Map 

# Upsample MODIS landcover classification (250m) to Landsat
# resolution (30m) using a supervised classifier.

geometry = ee.Geometry.Polygon(
        [[[29.972731783841393, 31.609824974226175],
          [29.972731783841393, 30.110383818311096],
          [32.56550522134139, 30.110383818311096],
          [32.56550522134139, 31.609824974226175]]], {}, False)

# Use the MCD12 land-cover as training data.
collection = ee.ImageCollection('MODIS/006/MCD12Q1')
# See the collection docs to get details on classification system.
modisLandcover = collection \
    .filterDate('2001-01-01', '2001-12-31') \
    .first() \
    .select('LC_Type1') \
    .subtract(1)

# A pallete to use for visualizing landcover images.  You can get this
# from the properties of the collection.
landcoverPalette = '05450a,086a10,54a708,78d203,009900,c6b044,dcd159,' + \
    'dade48,fbff13,b6ff05,27ff87,c24f44,a5a5a5,ff6d4c,69fff8,f9ffa4,1c0dff'
# A set of visualization parameters using the landcover palette.
landcoverVisualization = {'palette': landcoverPalette, 'min': 0, 'max': 16, 'format': 'png'}
# Center over our region of interest.
Map.centerObject(geometry, 11)
# Draw the MODIS landcover image.
Map.addLayer(modisLandcover, landcoverVisualization, 'MODIS landcover')

# Load and filter Landsat data.
l7 = ee.ImageCollection('LANDSAT/LE07/C01/T1') \
    .filterBounds(geometry) \
    .filterDate('2000-01-01', '2001-01-01')

# Draw the Landsat composite, visualizing True color bands.
landsatComposite = ee.Algorithms.Landsat.simpleComposite({
  'collection': l7,
  'asFloat': True
})
Map.addLayer(landsatComposite, {'min': 0, 'max': 0.3, 'bands': ['B3','B2','B1']}, 'Landsat composite')

# Make a training dataset by sampling the stacked images.
training = modisLandcover.addBands(landsatComposite).sample({
  'region': geometry,
  'scale': 30,
  'numPixels': 1000
})

# Train a classifier using the training data.
classifier = ee.Classifier.smileCart().train({
  'features': training,
  'classProperty': 'LC_Type1',
})

# Apply the classifier to the original composite.
upsampled = landsatComposite.classify(classifier)

# Draw the upsampled landcover image.
Map.addLayer(upsampled, landcoverVisualization, 'Upsampled landcover')

# Show the training area.
Map.addLayer(geometry, {}, 'Training region', False)
