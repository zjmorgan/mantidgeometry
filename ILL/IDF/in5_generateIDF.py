from __future__ import (absolute_import, division, print_function)

from helper import MantidGeom
from lxml import etree as le
import numpy as np


# # Global variables
instrumentName = 'IN5'
numberOfPixelsPerTube = 256
firstDetectorId = 1
radius = 4 # meters

# Tubes In 5: 2.95m / 241 positions = 256 - 7 pixel top - 8 pixels bottom
tubeHeight = 2.95
removedPixelsTop = 8
removedPixelsBottom = 7
# One inch diameter, 0.5mm thick walls
pixelRadius = (0.0254 - 0.001) / 2.
tubePixelStep =  tubeHeight / float(numberOfPixelsPerTube - removedPixelsTop - removedPixelsBottom)
totalTubeHeight = tubePixelStep * numberOfPixelsPerTube

# Don't touch!
azimuthalAngle = [ -11.9175,     -11.5451,     -11.1727,     -10.8003,     -10.4279,     -10.0554,     -9.68300,     -9.31058,     -8.93816,     -8.56573,     -8.19331,     -7.82089,     -7.44846,     -7.07604,     -6.70362,     -6.33119,     -5.95877,     -5.58635,     -5.21393,     -4.84150,     -4.46908,     -4.09666,     -3.72423,     -3.35181,     -2.97939,     -2.60696,     -2.23454,     -1.86212,     -1.48969,     -1.11727,    -0.744846,    -0.372423,    0.372423,     0.744847,      1.11727,      1.48969,      1.86212,      2.23454,      2.60696,      2.97939,      3.35181,      3.72423,      4.09666,      4.46908,      4.84150,      5.21393,      5.58635,      5.95877,     6.33119,      6.70362,      7.07604,      7.44846,      7.82089,      8.19331,      8.56573,      8.93816,      9.31058,      9.68300,      10.0554,      10.4279,      10.8003,      11.1727,      11.5451,      11.9175,     12.6624,      13.0348,      13.4072,      13.7797,      14.1521,      14.5245,      14.8969,      15.2694,      15.6418,      16.0142,      16.3866,      16.7590,      17.1315,      17.5039,      17.8763,      18.2487,     18.6212,      18.9936,      19.3660,      19.7384,      20.1109,      20.4833,      20.8557,      21.2281,      21.6005,      21.9730,      22.3454,      22.7178,      23.0902,      23.4627,      23.8351,      24.2075,     24.9524,      25.3248,      25.6972,      26.0696,      26.4420,      26.8145,      27.1869,      27.5593,      27.9317,      28.3042,      28.6766,      29.0490,      29.4214,      29.7939,      30.1663,      30.5387,     30.9111,      31.2836,      31.6560,      32.0284,      32.4008,      32.7732,      33.1457,      33.5181,      33.8905,      34.2629,      34.6354,      35.0078,      35.3802,      35.7526,      36.1251,      36.4975,     37.2423,      37.6147,      37.9872,      38.3596,      38.7320,      39.1044,      39.4769,      39.8493,      40.2217,      40.5941,      40.9666,      41.3390,      41.7114,      42.0838,      42.4562,      42.8287,     43.2011,      43.5735,      43.9459,      44.3184,      44.6908,      45.0632,      45.4356,      45.8081,      46.1805,      46.5529,      46.9253,      47.2978,      47.6702,      48.0426,      48.4150,      48.7874,     49.5323,      49.9047,      50.2771,      50.6496,      51.0220,      51.3944,      51.7668,      52.1393,      52.5117,      52.8841,      53.2565,      53.6289,      54.0014,      54.3738,      54.7462,      55.1186,     55.4911,      55.8635,      56.2359,      56.6083,      56.9808,      57.3532,      57.7256,      58.0980,      58.4704,      58.8429,      59.2153,      59.5877,      59.9601,      60.3326,      60.7050,      61.0774,     61.8223,      62.1947,      62.5671,      62.9395,      63.3120,      63.6844,      64.0568,      64.4292,      64.8017,      65.1741,      65.5465,      65.9189,      66.2913,      66.6638,      67.0362,      67.4086,     67.7810,      68.1535,      68.5259,      68.8983,      69.2707,      69.6432,      70.0156,      70.3880,      70.7604,      71.1328,      71.5053,      71.8777,      72.2501,      72.6225,      72.9950,      73.3674,     74.1122,      74.4846,      74.8571,      75.2295,      75.6019,      75.9743,      76.3468,      76.7192,      77.0916,      77.4640,      77.8365,      78.2089,      78.5813,      78.9537,      79.3262,      79.6986,     80.0710,      80.4434,      80.8158,      81.1883,      81.5607,      81.9331,      82.3055,      82.6780,      83.0504,      83.4228,      83.7952,      84.1677,      84.5401,      84.9125,      85.2849,      85.6573,     86.4022,      86.7746,      87.1470,      87.5195,      87.8919,      88.2643,      88.6367,      89.0092,      89.3816,      89.7540,      90.1264,      90.4989,      90.8713,      91.2437,      91.6161,      91.9885,     92.3610,      92.7334,      93.1058,      93.4782,      93.8507,      94.2231,      94.5955,      94.9679,      95.3404,      95.7128,      96.0852,      96.4576,      96.8300,      97.2025,      97.5749,      97.9473,     98.6922,      99.0646,      99.4370,      99.8094,      100.182,      100.554,      100.927,      101.299,      101.672,      102.044,      102.416,      102.789,      103.161,      103.534,      103.906,      104.279,     104.651,      105.023,      105.396,      105.768,      106.141,      106.513,      106.885,      107.258,      107.630,      108.003,      108.375,      108.748,      109.120,      109.492,      109.865,      110.237,     110.982,      111.355,      111.727,      112.099,      112.472,      112.844,      113.217,      113.589,      113.962,      114.334,      114.706,      115.079,      115.451,      115.824,      116.196,      116.568,     116.941,      117.313,      117.686,      118.058,      118.431,      118.803,      119.175,      119.548,      119.920,      120.293,      120.665,      121.038,      121.410,      121.782,      122.155,      122.527,     123.272,      123.645,      124.017,      124.389,      124.762,      125.134,      125.507,      125.879,      126.251,      126.624,      126.996,      127.369,      127.741,      128.114,      128.486,      128.858,     129.231,      129.603,      129.976,      130.348,      130.721,      131.093,      131.465,      131.838,      132.210,      132.583,      132.955,      133.328,      133.700,      134.072,      134.445,      134.817]
azimuthalAngle.reverse()
numberOfTubes = len(azimuthalAngle)     
numberOfDetectors = numberOfPixelsPerTube * numberOfTubes

frameOverlapChopperZ = -2.10945
monitorZ = -0.5

comment = """ This is the instrument definition file of the IN5 spectrometer at the ILL.
       This file was automatically generated by mantidgeometry/ILL/IDF/in5_generateIDF.py
       """
validFrom = '1900-01-31 23:59:59'
geometry = MantidGeom(instrumentName, comment=comment, valid_from=validFrom)
geometry.addSnsDefaults(theta_sign_axis='x')
geometry.addComponentILL('frame-overlap_chopper', 0.0, 0.0, frameOverlapChopperZ, 'Source')
geometry.addComponentILL('sample-position', 0.0, 0.0, 0.0, 'SamplePos')
geometry.addMonitors(names=['monitor'], distance=[monitorZ])
geometry.addDummyMonitor(0.01, 0.03)
geometry.addMonitorIds(['100000'])
pixelBase = {'x': 0., 'y': -tubePixelStep / 2., 'z': 0.}
geometry.addCylinderPixelAdvanced(
    'standard_pixel', center_bottom_base=pixelBase,
    axis={'x': 0., 'y': 1., 'z': 0.}, pixel_radius=pixelRadius,
    pixel_height=tubePixelStep,
    algebra='pixel_shape')
root = geometry.getRoot()
bank = le.SubElement(root, 'type', name='bank_uniq')
tubes = le.SubElement(bank, 'component', type='standard_tube')
for index, angle in enumerate(azimuthalAngle):
    attributes = {
        'r': str(radius),
        't': str(angle),
        'rot': str(angle),
        'axis-x': str(0.),
        'axis-y': str(1.),
        'axis-z': str(0.),
        'name': 'tube_{}'.format(index+1)
    }
    le.SubElement(tubes, 'location', **attributes)
tubeType = le.SubElement(root, 'type', name='standard_tube', outline='yes')
tube = le.SubElement(tubeType, 'component', type='standard_pixel')
pixelPositions = np.linspace(-totalTubeHeight/2., totalTubeHeight/2., numberOfPixelsPerTube)
for pos in pixelPositions:
    le.SubElement(tube, 'location', y=str(pos))
geometry.addComponent('detectors', idlist='detectors')
detectorType = le.SubElement(root, 'type', name='detectors')
bankComponent = le.SubElement(detectorType, 'component', type='bank_uniq')
le.SubElement(bankComponent, 'location')
geometry.addDetectorIds('detectors', [1, 98304, None])
geometry.writeGeom("./ILL/IDF/" + instrumentName + "_Definition.xml")
