#!/usr/bin/python3
from helper import MantidGeom
from SNS.SANS.utilities import (add_comment_section, kw, ag, make_filename,
                                add_basic_types, add_double_flat_panel_type,
                                add_double_flat_panel_component,
                                add_double_curved_panel_type,
                                add_double_curved_panel_component)

"""
Instrument requirements from meeting at HFIR on May 07, 2019
- One component for the front panel and one component for the back panel
- divide each bank into fourpacks
- Pixel ID's start at tube1 of bank1 and finish at last tube of the last bank
"""

iinfo = dict(valid_from='2019-01-01 00:00:00',
             valid_to='2100-12-31 23:59:59',
             comment='Created by Jose Borregero, borreguerojm@ornl.gov',
             instrument_name='BIOSANS',
             source_sample_distance=1.0,
             flat_array='detector1',  # name of the detector array
             flat_panel_types=dict(front='front-panel', back='back-panel'),
             bank_name='bank',
             tube_length=1.046,
             tube_diameter=0.00805,
             pixels_per_tube=256,
             tube_separation=0.0110,  # distance between consecutive tube axis
             fourpack_separation=0.0082,  # distance between front and back fourpacks
             fourpack_slip=0.0055,  # slip vector between the two fourpacks along X-axis
             number_eightpacks=24)  # number of eight-packs in the detector array

# Instrument handle
det = MantidGeom(iinfo['instrument_name'],
                 **kw(iinfo, 'comment', 'valid_from', 'valid_to'))
det.addSnsDefaults(default_view="3D", axis_view_3d="Z-")
fn = make_filename(*ag(iinfo, 'instrument_name', 'valid_from', 'valid_to'))
add_basic_types(det, iinfo)  # source, sample, pixel, tube, and fourpack
#
# Insert the flat panel
#
double_panel = add_double_flat_panel_type(det, iinfo)
add_comment_section(det, 'LIST OF PIXEL IDs in FLAT DETECTOR')
n_flat_pixels = iinfo['number_eightpacks'] * 8 * 256
det.addDetectorIds('flat_panel_ids', [0, n_flat_pixels - 1, 1])
add_double_flat_panel_component(double_panel, 'flat_panel_ids', det,
                                iinfo['flat_array'])
#
# Insert the curved panel
#
jinfo = dict(curved_array='wing_detector_arm',  # name of the wing detector
             curved_panel_types=dict(front='front-wing-panel',
                                     back='back-wing-panel'),
             bank_name='wing-bank',
             number_eightpacks=20,
             bank_radius=5.0,  # distance between focal-point and anchor point
             anchor_offset=0.0041,  # add this to bank_radius for distance between focal-point and eightpack midline
             eightpack_angle=0.5041)  # angle subtended by each eightpack, in degrees

iinfo.update(jinfo)
double_panel = add_double_curved_panel_type(det, iinfo)
add_comment_section(det, 'LIST OF PIXEL IDs in CURVED DETECTOR')
n_curved_pixels = iinfo['number_eightpacks'] * 8 * 256
det.addDetectorIds('curved_panel_ids',
                   [n_flat_pixels, n_flat_pixels + n_curved_pixels - 1, 1])
double_panel = add_double_curved_panel_component(double_panel,
                                                 'curved_panel_ids',
                                                 det, iinfo['curved_array'])
# Rotate the double panel away from the path of the Z-axis
rot_y = -iinfo['eightpack_angle'] * iinfo['number_eightpacks'] / 2
det.addLocation(double_panel, 0., 0., 0, rot_y=rot_y)
#
# Write to file
#
det.writeGeom(fn)