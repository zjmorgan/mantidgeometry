#! /usr/bin/python

from __future__ import print_function
from helper import MantidGeom
import h5py
import math
import numpy as np
import os
import sys

"""
Runs with 311 analyzer have "3.2750" as /entry/DASlogs/chopWL/value.
Runs with 111 analyzer have "6.2712" as /entry/DASlogs/chopWL/value
"""
nexus_file_111 = "/SNS/BSS/IPTS-5908/0/32264/NeXus/BSS_32264_event.nxs"
nexus_file_311 = "/SNS/BSS/IPTS-5908/0/40473/NeXus/BSS_40473_event.nxs"

reflections = {'generic': {'nexus': nexus_file_111,
                           'wavelength': 6.2712,
                           'ratio_to_irreducible_hkl': 1.0,
                           'efixed': False},
               '111': {'nexus': nexus_file_111,
                       'wavelength': 6.2712,
                       'ratio_to_irreducible_hkl': 1.0,
                       'efixed': True},
               '333': {'nexus': nexus_file_111,
                       'wavelength': 6.2712 / 3.0,
                       'ratio_to_irreducible_hkl': 1.0 / 3.0,
                       'efixed': True},
               '311': {'nexus': nexus_file_311,
                       'wavelength': 3.2750,
                       'ratio_to_irreducible_hkl': 1.0,
                       'efixed': True}
              }

n_inelastic_banks = 4

INCH_TO_METRE = 0.0254

TUBE_PRESSURE = ("tube_pressure", 0.0, "atm")
TUBE_THICKNESS = ("tube_thickness", 0.0008, "metre")
TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")

"""
INELASTIC
Tubes are positioned on the walls of the BASIS cylindrical container,
above and below the diffraction detectors.
Neighbor pixels are made to be separated by a small gap. This will
result in a black grid surrounding each pixel, facilitating identification
of each pixel when viewed in Mantid as 'cylindrical Y'
"""
INELASTIC_TUBES_PER_BANK = 64
# nghost tubes of each bank are not installed in the instrument
INELASTIC_TUBES_NGHOST = 8
INELASTIC_TUBE_NPIXEL = 64
# distance from sample to center of tube projection on XZ-plane
INELASTIC_TUBE_DISTANCE_TO_SAMPLE = 2.44365

# distance from the XZ-plane to the beginning of each tube
INELASTIC_TUBE_Y0 = 1.0 * INCH_TO_METRE
INELASTIC_TUBE_LENGTH = INELASTIC_TUBE_DISTANCE_TO_SAMPLE
INELASTIC_BANK_THETA_START = 11.5018 * (math.pi/180.0) #in radians
INELASTIC_BANK_THETA_END = 161.199 * (math.pi/180.0)
INELASTIC_BANK_THETA_SPREAD = (INELASTIC_BANK_THETA_END -INELASTIC_BANK_THETA_START)
INELASTIC_TUBE_WIDTH = INELASTIC_TUBE_DISTANCE_TO_SAMPLE * INELASTIC_BANK_THETA_SPREAD / (INELASTIC_TUBES_PER_BANK-INELASTIC_TUBES_NGHOST)
# neighbor pixels are separated by a gap
INELASTIC_PIXEL_RADIUS_GAP_RATIO = 0.1
INELASTIC_PIXEL_HEIGHT_GAP_RATIO = 0.1

# initial conditions for banks when calculating physical positions of pixels
Y_OFFSET = {0: INELASTIC_TUBE_Y0,
            1: -INELASTIC_TUBE_Y0 - INELASTIC_TUBE_LENGTH,
            2: INELASTIC_TUBE_Y0,
            3: -INELASTIC_TUBE_Y0 - INELASTIC_TUBE_LENGTH}
THETA_OFFSET = {0: INELASTIC_BANK_THETA_START,
                1: INELASTIC_BANK_THETA_START,
                2: math.pi+INELASTIC_BANK_THETA_START,
                3: math.pi+INELASTIC_BANK_THETA_START}

# DIFFRACTION
ELASTIC_BANK_START = 5
ELASTIC_BANK_END = 13
ELASTIC_DETECTORID_START = 16384
ELASTIC_TUBES_PER_BANK = 1
ELASTIC_TUBE_NPIXELS = 128
ELASTIC_TUBE_LENGTH = 25.24 * INCH_TO_METRE
ELASTIC_TUBE_WIDTH = 0.5 * INCH_TO_METRE   # 0.5" diameter tubes
ELASTIC_TUBE_PRESSURE = ("tube_pressure", 30.0, "atm")
ELASTIC_TUBE_THICKNESS = ("tube_thickness",  (0.01 * INCH_TO_METRE), "metre")
ELASTIC_TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")


def pixels_physical_xyz(bank_id):
    r"""
    Generate the cartesian positions of each pixel in a given bank

    Parameters
    ----------
    bank_id: int
        1: Top-left/South, 2:Botton-left/South, 3:Top-right/North, 4:Botton-right/North
    Returns
    -------
    tuple
        (x,y,z): items are a list of lists
    """
    xbank=list()
    ybank=list()
    zbank=list()
    ntubes = INELASTIC_TUBES_PER_BANK - INELASTIC_TUBES_NGHOST
    delta_theta = INELASTIC_BANK_THETA_SPREAD / ntubes
    pixel_length = INELASTIC_TUBE_LENGTH / INELASTIC_TUBE_NPIXEL
    for itube in range(ntubes):
        theta_tube = THETA_OFFSET[bank_id] + itube * delta_theta
        xtube = INELASTIC_TUBE_DISTANCE_TO_SAMPLE * math.sin(theta_tube)
        ztube = INELASTIC_TUBE_DISTANCE_TO_SAMPLE * math.cos(theta_tube)
        xbank.append( [xtube] * INELASTIC_TUBE_NPIXEL)
        zbank.append( [ztube] * INELASTIC_TUBE_NPIXEL)
        ytube = list()
        for ipixel in range(INELASTIC_TUBE_NPIXEL):
            ytube.append(Y_OFFSET[bank_id] + ipixel * pixel_length)
        ybank.append(ytube)
    return [np.array(component) for component in (xbank, ybank, zbank)]


def generate_reflection_file(reflection_key):
    r"""

    Parameters
    ----------
    reflection_key: str

    Returns
    -------

    """
    refl = reflections[reflection_key]
    if not os.path.exists(refl['nexus']):
        message = '{} not found. Not creating geometry'.format(refl['nexus'])
        raise FileExistsError(message)
    inst_name = "BASIS"
    # Set header information
    comment = "Created by Michael Reuter and Jose Borreguero"
    # Time needs to be in UTC?
    valid_from = "2014-01-01 00:00:00"

    xml_outfile = '{}_Definition_Si{}.xml'.format(inst_name, reflection_key)
    nfile = h5py.File(refl['nexus'], 'r')

    det = MantidGeom(inst_name, comment=comment, valid_from=valid_from)
    det.addSnsDefaults(indirect=True)
    det.addComment("SOURCE AND SAMPLE POSITION")
    det.addModerator(-84.0)
    det.addSamplePosition()
    det.addComment("MONITORS")
    det.addMonitors(names=["monitor1"], distance=["-0.23368"], neutronic=True)

    # Create the inelastic banks information
    det.addComment('INELASTIC DECTECTORS')
    det.addComponent('silicon')
    handle_silicon = det.makeTypeElement("silicon")
    # Slicer for removing ghosts. Due to the mapping, the ghost tubes sit
    # on the same sides of the arrays for all banks.
    remove_ghosts = slice(-INELASTIC_TUBES_NGHOST)

    for i in range(n_inelastic_banks):
        bank_id = "bank%d" % (i+1)
        pixel_id = nfile["/entry/instrument/bank%d/pixel_id" % (i+1)].value[remove_ghosts]
        distance = nfile["/entry/instrument/bank%d/distance" % (i+1)].value[remove_ghosts]
        # theta or polar_angle: angle from the Z-axis towards the X-axis
        polar_angle = nfile["/entry/instrument/bank%d/polar_angle" % (i+1)].value[remove_ghosts]
        polar_angle *= (180.0/math.pi)
        # phi or azimuthal_angle: angle in the XY-plane
        azimuthal_angle = nfile["/entry/instrument/bank%d/azimuthal_angle" % (i+1)].value[remove_ghosts]
        azimuthal_angle *= (180.0/math.pi)

        analyser_wavelength = nfile["/entry/instrument/analyzer%d/wavelength" % (i+1)].value[remove_ghosts]
        analyser_wavelength *= refl['ratio_to_irreducible_hkl']
        analyser_energy = 81.8042051/analyser_wavelength**2

        det.addComponent(bank_id, idlist=bank_id, root=handle_silicon)

        xbank, ybank, zbank = pixels_physical_xyz(i)
        det.addDetectorPixels(bank_id, x=xbank, y=ybank, z=zbank,
                              names=pixel_id, energy=analyser_energy,
                              nr=distance, ntheta=polar_angle,
                              nphi=azimuthal_angle,
                              output_efixed=refl['efixed'])

        det.addDetectorPixelsIdList(bank_id, r=distance, names=pixel_id,
                                    elg="multiple_ranges")


    # Create the diffraction bank information
    det.addComponent("elastic", "elastic")
    handle = det.makeTypeElement("elastic")

    idlist = []

    detector_z = [-2.1474825, -1.704594, -1.108373, -0.4135165, 0.3181,
                  1.0218315, 1.6330115, 2.0993535, 2.376999]
    detector_x = [1.1649855, 1.7484015, 2.175541, 2.408594, 2.422933,
                  2.216378, 1.8142005, 1.247867, 0.5687435]
    detector_y = [-0.001807, -0.001801, -0.0011845, -0.0006885, -0.0013145,
                  -0.001626, -0.001397, 0.0003465, -0.0001125]

    for i in range(ELASTIC_BANK_START, ELASTIC_BANK_END+1):
        bank_name = "bank%d" % i
        det.addComponent(bank_name, root=handle)

        k = i - ELASTIC_BANK_START

        x_coord = detector_x[k]
        y_coord = detector_y[k]
        z_coord = detector_z[k]

        det.addDetector(x_coord, y_coord, z_coord, 0.0, 0., 90.,
                        bank_name, "tube-elastic", facingSample=True)

        idlist.append(ELASTIC_DETECTORID_START +
                      ELASTIC_TUBE_NPIXELS*(i-ELASTIC_BANK_START))
        idlist.append(ELASTIC_DETECTORID_START +
                      ELASTIC_TUBE_NPIXELS*(i-ELASTIC_BANK_START) +
                      ELASTIC_TUBE_NPIXELS-1)
        idlist.append(None)

    # Diffraction tube information
    det.addComment("ELASTIC TUBE (90 degrees)")
    det.addPixelatedTube("tube-elastic", ELASTIC_TUBE_NPIXELS,
                         ELASTIC_TUBE_LENGTH, "pixel-elastic-tube",
                         neutronic=True, neutronicIsPhysical=True)

    # Set the diffraction pixel Ids
    det.addDetectorIds("elastic", idlist)

    # Creating diffraction pixel
    det.addComment("PIXEL FOR DIFFRACTION TUBES")
    det.addCylinderPixel("pixel-elastic-tube",
                         (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (ELASTIC_TUBE_WIDTH/2.0),
                         (ELASTIC_TUBE_LENGTH/ELASTIC_TUBE_NPIXELS))

    det.addComment("PIXEL FOR INELASTIC TUBES")
    det.addCylinderPixel("pixel", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                        INELASTIC_TUBE_WIDTH * (1.0-INELASTIC_PIXEL_RADIUS_GAP_RATIO) / 2.0,
                        INELASTIC_TUBE_LENGTH * (1.0-INELASTIC_PIXEL_HEIGHT_GAP_RATIO) / INELASTIC_TUBE_NPIXEL,
                        is_type="detector", algebra="cyl-approx")

    det.addComment("MONITOR SHAPE")
    det.addComment("FIXME: Do something real here.")
    det.addDummyMonitor(0.01, 0.03)

    det.addComment("MONITOR IDs")
    det.addMonitorIds(["-1"])

    det.writeGeom(xml_outfile)

    # Always clean after yourself
    nfile.close()


if __name__ == "__main__":
    for key in reflections:
        generate_reflection_file(key)
