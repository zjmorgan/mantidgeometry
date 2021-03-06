#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

BIOSANS

Generates only the wing detector

File is accepted by mantid.

@author: ferrazlealrm@ornl.gov
```
./generate_all_detectors.py > /tmp/biosans.xml
LoadEmptyInstrument(Filename='/tmp/biosans.xml', OutputWorkspace='tmp')
```


"""
from django.template import Template, Context
from django.conf import settings
from django import setup

from datetime import datetime
import numpy as np

# INIT
settings.configure()
setup()

# Variables
radius = 1.13
n_tubes = 20*8
n_pixels_tube = 256
n_total_pixels = n_tubes * n_pixels_tube

biosans_tube_step_meters = 0.0055
tube_step_angle_radians = np.arcsin(biosans_tube_step_meters/2.0/radius)
tube_step_angle_degrees = np.degrees(tube_step_angle_radians)

# copied from biosans
pixel_positions = np.linspace(-0.54825, 0.54825, 256)

# Values to replace in the template
values = {
    "last_modified" : str(datetime.now()),
    "first_id" : 2000000,
    "last_id" : 2000000 + n_total_pixels -1,
    "radius" : radius,
    "tube_pos_angle" : [ -tube_step_angle_degrees * x for x in range(n_tubes) ] ,
    "pixel_positions" : pixel_positions,
}


# Template
template = """<?xml version='1.0' encoding='ASCII'?>
<instrument xmlns="http://www.mantidproject.org/IDF/1.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0 http://schema.mantidproject.org/IDF/1.0/IDFSchema.xsd"
            name="BIOSANSWING"
            valid-from="2016-04-22 00:00:00"
            valid-to="2100-01-31 23:59:59"
		    last-modified="{{ last_modified }}">

<defaults>
    <length unit="meter"/>
    <angle unit="degree"/>
    <reference-frame>
        <along-beam axis="z"/>
        <pointing-up axis="y"/>
        <handedness val="right"/>
    </reference-frame>
</defaults>

<!--SOURCE AND SAMPLE POSITION-->
<component type="moderator">
    <location z="-13.601"/>
</component>
<type name="moderator" is="Source"/>

<component type="sample-position">
    <location y="0.0" x="0.0" z="0.0"/>
</component>
<type name="sample-position" is="SamplePos"/>

<!--MONITOR 1 -->
<component type="monitor1" idlist="monitor1">
    <location z="-10.5" />
</component>
<type name="monitor1" is="monitor" />
<idlist idname="monitor1">
    <id val="1" />
</idlist>

<!--MONITOR 2 -->
<component type="timer1" idlist="timer1">
    <location z="-10.5" />
</component>
<type name="timer1" is="monitor" />
<idlist idname="timer1">
    <id val="2" />
</idlist>

<!-- Wing Detector -->
<component type="wing_detector" idlist="wing_detector_ids">
    <location />
</component>

<idlist idname="wing_detector_ids">
    <id start="{{ first_id }}" end="{{ last_id }}" />
</idlist>

<type name="wing_detector">
    <component type="wing_tube">
        {% for angle in tube_pos_angle %}
        <location r="{{ radius }}" t="{{ angle }}" name="wing_tube_{{ forloop.counter0 }}" />{% endfor %}
    </component>
</type>

<type name="wing_tube" outline="yes">
    <component type="wing_pixel">
        {% for pos_y in pixel_positions %}
        <location y="{{pos_y}}" name="wing_pixel_{{ forloop.counter0 }}" />{% endfor %}
    </component>
</type>

<type name="wing_pixel" is="detector">
    <cylinder id="cyl-approx">
        <centre-of-bottom-base p="0.0" r="0.0" t="0.0"/>
        <axis y="1.0" x="0.0" z="0.0"/>
        <radius val="0.00275"/>
        <height val="0.0043"/>
    </cylinder>
    <algebra val="cyl-approx"/>
</type>

</instrument>
"""

def to_string():
    """
    Render the template
    """
    t = Template(template)
    c = Context(values)
    content = t.render(c)
    return content



if __name__ == '__main__':
    print to_string()
