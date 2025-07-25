# Copyright (C) 2006-2010 Søren Roug, European Environment Agency
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Contributor(s):
#

import re

from polyglot.builtins import string_or_bytes, unicode_type

from .namespaces import (
    ANIMNS,
    CHARTNS,
    CONFIGNS,
    DR3DNS,
    DRAWNS,
    FONS,
    FORMNS,
    MANIFESTNS,
    METANS,
    NUMBERNS,
    OFFICENS,
    PRESENTATIONNS,
    SCRIPTNS,
    SMILNS,
    STYLENS,
    SVGNS,
    TABLENS,
    TEXTNS,
    XFORMSNS,
    XLINKNS,
)

pattern_color = re.compile(r'#[0-9a-fA-F]{6}')
pattern_vector3D = re.compile(r'\([ ]*-?([0-9]+(\.[0-9]*)?|\.[0-9]+)([ ]+-?([0-9]+(\.[0-9]*)?|\.[0-9]+)){2}[ ]*\)')


def make_NCName(arg):
    for c in (':',' '):
        arg = arg.replace(c, f'_{ord(c):x}_')
    return arg


def cnv_anyURI(attribute, arg, element):
    return str(arg)


def cnv_boolean(attribute, arg, element):
    if arg.lower() in ('false','no'):
        return 'false'
    if arg:
        return 'true'
    return 'false'


# Potentially accept color values

def cnv_color(attribute, arg, element):
    ''' A RGB color in conformance with §5.9.11 of [XSL], that is a RGB color in notation “#rrggbb”, where
        rr, gg and bb are 8-bit hexadecimal digits.
    '''
    return unicode_type(arg)


def cnv_configtype(attribute, arg, element):
    if unicode_type(arg) not in ('boolean', 'short', 'int', 'long',
    'double', 'string', 'datetime', 'base64Binary'):
        raise ValueError(f"'{unicode_type(arg)}' not allowed")
    return unicode_type(arg)


def cnv_data_source_has_labels(attribute, arg, element):
    if unicode_type(arg) not in ('none','row','column','both'):
        raise ValueError(f"'{unicode_type(arg)}' not allowed")
    return unicode_type(arg)


# Understand different date formats

def cnv_date(attribute, arg, element):
    ''' A dateOrDateTime value is either an [xmlschema-2] date value or an [xmlschema-2] dateTime
        value.
    '''
    return unicode_type(arg)


def cnv_dateTime(attribute, arg, element):
    ''' A dateOrDateTime value is either an [xmlschema-2] date value or an [xmlschema-2] dateTime
        value.
    '''
    return unicode_type(arg)


def cnv_double(attribute, arg, element):
    return unicode_type(arg)


def cnv_duration(attribute, arg, element):
    return unicode_type(arg)


def cnv_family(attribute, arg, element):
    ''' A style family '''
    if unicode_type(arg) not in ('text', 'paragraph', 'section', 'ruby', 'table', 'table-column', 'table-row', 'table-cell',
      'graphic', 'presentation', 'drawing-page', 'chart'):
        raise ValueError(f"'{unicode_type(arg)}' not allowed")
    return unicode_type(arg)


def __save_prefix(attribute, arg, element):
    prefix = arg.split(':',1)[0]
    if prefix == arg:
        return str(arg)
    namespace = element.get_knownns(prefix)
    if namespace is None:
        # raise ValueError(f"'{unicode_type(prefix)}' is an unknown prefix")
        return str(arg)
    return str(arg)


def cnv_formula(attribute, arg, element):
    ''' A string containing a formula. Formulas do not have a predefined syntax, but the string should
        begin with a namespace prefix, followed by a “:” (COLON, U+003A) separator, followed by the text
        of the formula. The namespace bound to the prefix determines the syntax and semantics of the
        formula.
    '''
    return __save_prefix(attribute, arg, element)


def cnv_ID(attribute, arg, element):
    return unicode_type(arg)


def cnv_IDREF(attribute, arg, element):
    return unicode_type(arg)


def cnv_integer(attribute, arg, element):
    return unicode_type(arg)


def cnv_legend_position(attribute, arg, element):
    if unicode_type(arg) not in ('start', 'end', 'top', 'bottom', 'top-start', 'bottom-start', 'top-end', 'bottom-end'):
        raise ValueError(f"'{unicode_type(arg)}' not allowed")
    return unicode_type(arg)


pattern_length = re.compile(r'-?([0-9]+(\.[0-9]*)?|\.[0-9]+)((cm)|(mm)|(in)|(pt)|(pc)|(px))')


def cnv_length(attribute, arg, element):
    ''' A (positive or negative) physical length, consisting of magnitude and unit, in conformance with the
        Units of Measure defined in §5.9.13 of [XSL].
    '''
    global pattern_length
    if not pattern_length.match(arg):
        raise ValueError(f"'{arg}' is not a valid length")
    return arg


def cnv_lengthorpercent(attribute, arg, element):
    failed = False
    try:
        return cnv_length(attribute, arg, element)
    except Exception:
        failed = True
    try:
        return cnv_percent(attribute, arg, element)
    except Exception:
        failed = True
    if failed:
        raise ValueError(f"'{arg}' is not a valid length or percent")
    return arg


def cnv_metavaluetype(attribute, arg, element):
    if unicode_type(arg) not in ('float', 'date', 'time', 'boolean', 'string'):
        raise ValueError(f"'{unicode_type(arg)}' not allowed")
    return unicode_type(arg)


def cnv_major_minor(attribute, arg, element):
    if arg not in ('major','minor'):
        raise ValueError(f"'{arg}' is not either 'minor' or 'major'")


pattern_namespacedToken = re.compile(r'[0-9a-zA-Z_]+:[0-9a-zA-Z._\-]+')


def cnv_namespacedToken(attribute, arg, element):
    global pattern_namespacedToken

    if not pattern_namespacedToken.match(arg):
        raise ValueError(f"'{arg}' is not a valid namespaced token")
    return __save_prefix(attribute, arg, element)


def cnv_NCName(attribute, arg, element):
    ''' NCName is defined in http://www.w3.org/TR/REC-xml-names/#NT-NCName
        Essentially an XML name minus ':'
    '''
    if isinstance(arg, string_or_bytes):
        return make_NCName(arg)
    else:
        return arg.getAttrNS(STYLENS, 'name')

# This function takes either an instance of a style (preferred)
# or a text string naming the style. If it is a text string, then it must
# already have been converted to an NCName
# The text-string argument is mainly for when we build a structure from XML


def cnv_StyleNameRef(attribute, arg, element):
    try:
        return arg.getAttrNS(STYLENS, 'name')
    except Exception:
        return arg

# This function takes either an instance of a style (preferred)
# or a text string naming the style. If it is a text string, then it must
# already have been converted to an NCName
# The text-string argument is mainly for when we build a structure from XML


def cnv_DrawNameRef(attribute, arg, element):
    try:
        return arg.getAttrNS(DRAWNS, 'name')
    except Exception:
        return arg


# Must accept list of Style objects

def cnv_NCNames(attribute, arg, element):
    return ' '.join(arg)


def cnv_nonNegativeInteger(attribute, arg, element):
    return unicode_type(arg)


pattern_percent = re.compile(r'-?([0-9]+(\.[0-9]*)?|\.[0-9]+)%')


def cnv_percent(attribute, arg, element):
    global pattern_percent
    if not pattern_percent.match(arg):
        raise ValueError(f"'{arg}' is not a valid length")
    return arg


# Real one doesn't allow floating point values
pattern_points = re.compile(r'-?[0-9]+,-?[0-9]+([ ]+-?[0-9]+,-?[0-9]+)*')
# pattern_points = re.compile(r'-?[0-9.]+,-?[0-9.]+([ ]+-?[0-9.]+,-?[0-9.]+)*')


def cnv_points(attribute, arg, element):
    global pattern_points
    if isinstance(arg, string_or_bytes):
        if not pattern_points.match(arg):
            raise ValueError('x,y are separated by a comma and the points are separated by white spaces')
        return arg
    else:
        try:
            strarg = ' '.join(['{},{}'.format(*p) for p in arg])
        except Exception:
            raise ValueError(f'Points must be string or [(0,0),(1,1)] - not {arg}')
        return strarg


def cnv_positiveInteger(attribute, arg, element):
    return unicode_type(arg)


def cnv_string(attribute, arg, element):
    return str(arg)


def cnv_textnoteclass(attribute, arg, element):
    if unicode_type(arg) not in ('footnote', 'endnote'):
        raise ValueError(f"'{unicode_type(arg)}' not allowed")
    return unicode_type(arg)


# Understand different time formats

def cnv_time(attribute, arg, element):
    return unicode_type(arg)


def cnv_token(attribute, arg, element):
    return unicode_type(arg)


pattern_viewbox = re.compile(r'-?[0-9]+([ ]+-?[0-9]+){3}$')


def cnv_viewbox(attribute, arg, element):
    global pattern_viewbox
    if not pattern_viewbox.match(arg):
        raise ValueError('viewBox must be four integers separated by whitespaces')
    return arg


def cnv_xlinkshow(attribute, arg, element):
    if unicode_type(arg) not in ('new', 'replace', 'embed'):
        raise ValueError(f"'{unicode_type(arg)}' not allowed")
    return unicode_type(arg)


attrconverters = {
        ((ANIMNS,'audio-level'), None): cnv_double,
        ((ANIMNS,'color-interpolation'), None): cnv_string,
        ((ANIMNS,'color-interpolation-direction'), None): cnv_string,
        ((ANIMNS,'command'), None): cnv_string,
        ((ANIMNS,'formula'), None): cnv_string,
        ((ANIMNS,'id'), None): cnv_ID,
        ((ANIMNS,'iterate-interval'), None): cnv_duration,
        ((ANIMNS,'iterate-type'), None): cnv_string,
        ((ANIMNS,'name'), None): cnv_string,
        ((ANIMNS,'sub-item'), None): cnv_string,
        ((ANIMNS,'value'), None): cnv_string,
        # ((DBNS,'type'), None): cnv_namespacedToken,
        ((CHARTNS,'attached-axis'), None): cnv_string,
        ((CHARTNS,'class'), (CHARTNS,'grid')): cnv_major_minor,
        ((CHARTNS,'class'), None): cnv_namespacedToken,
        ((CHARTNS,'column-mapping'), None): cnv_string,
        ((CHARTNS,'connect-bars'), None): cnv_boolean,
        ((CHARTNS,'data-label-number'), None): cnv_string,
        ((CHARTNS,'data-label-symbol'), None): cnv_boolean,
        ((CHARTNS,'data-label-text'), None): cnv_boolean,
        ((CHARTNS,'data-source-has-labels'), None): cnv_data_source_has_labels,
        ((CHARTNS,'deep'), None): cnv_boolean,
        ((CHARTNS,'dimension'), None): cnv_string,
        ((CHARTNS,'display-label'), None): cnv_boolean,
        ((CHARTNS,'error-category'), None): cnv_string,
        ((CHARTNS,'error-lower-indicator'), None): cnv_boolean,
        ((CHARTNS,'error-lower-limit'), None): cnv_string,
        ((CHARTNS,'error-margin'), None): cnv_string,
        ((CHARTNS,'error-percentage'), None): cnv_string,
        ((CHARTNS,'error-upper-indicator'), None): cnv_boolean,
        ((CHARTNS,'error-upper-limit'), None): cnv_string,
        ((CHARTNS,'gap-width'), None): cnv_string,
        ((CHARTNS,'interpolation'), None): cnv_string,
        ((CHARTNS,'interval-major'), None): cnv_string,
        ((CHARTNS,'interval-minor-divisor'), None): cnv_string,
        ((CHARTNS,'japanese-candle-stick'), None): cnv_boolean,
        ((CHARTNS,'label-arrangement'), None): cnv_string,
        ((CHARTNS,'label-cell-address'), None): cnv_string,
        ((CHARTNS,'legend-align'), None): cnv_string,
        ((CHARTNS,'legend-position'), None): cnv_legend_position,
        ((CHARTNS,'lines'), None): cnv_boolean,
        ((CHARTNS,'link-data-style-to-source'), None): cnv_boolean,
        ((CHARTNS,'logarithmic'), None): cnv_boolean,
        ((CHARTNS,'maximum'), None): cnv_string,
        ((CHARTNS,'mean-value'), None): cnv_boolean,
        ((CHARTNS,'minimum'), None): cnv_string,
        ((CHARTNS,'name'), None): cnv_string,
        ((CHARTNS,'origin'), None): cnv_string,
        ((CHARTNS,'overlap'), None): cnv_string,
        ((CHARTNS,'percentage'), None): cnv_boolean,
        ((CHARTNS,'pie-offset'), None): cnv_string,
        ((CHARTNS,'regression-type'), None): cnv_string,
        ((CHARTNS,'repeated'), None): cnv_nonNegativeInteger,
        ((CHARTNS,'row-mapping'), None): cnv_string,
        ((CHARTNS,'scale-text'), None): cnv_boolean,
        ((CHARTNS,'series-source'), None): cnv_string,
        ((CHARTNS,'solid-type'), None): cnv_string,
        ((CHARTNS,'spline-order'), None): cnv_string,
        ((CHARTNS,'spline-resolution'), None): cnv_string,
        ((CHARTNS,'stacked'), None): cnv_boolean,
        ((CHARTNS,'style-name'), None): cnv_StyleNameRef,
        ((CHARTNS,'symbol-height'), None): cnv_string,
        ((CHARTNS,'symbol-name'), None): cnv_string,
        ((CHARTNS,'symbol-type'), None): cnv_string,
        ((CHARTNS,'symbol-width'), None): cnv_string,
        ((CHARTNS,'text-overlap'), None): cnv_boolean,
        ((CHARTNS,'three-dimensional'), None): cnv_boolean,
        ((CHARTNS,'tick-marks-major-inner'), None): cnv_boolean,
        ((CHARTNS,'tick-marks-major-outer'), None): cnv_boolean,
        ((CHARTNS,'tick-marks-minor-inner'), None): cnv_boolean,
        ((CHARTNS,'tick-marks-minor-outer'), None): cnv_boolean,
        ((CHARTNS,'values-cell-range-address'), None): cnv_string,
        ((CHARTNS,'vertical'), None): cnv_boolean,
        ((CHARTNS,'visible'), None): cnv_boolean,
        ((CONFIGNS,'name'), None): cnv_formula,
        ((CONFIGNS,'type'), None): cnv_configtype,
        ((DR3DNS,'ambient-color'), None): cnv_string,
        ((DR3DNS,'back-scale'), None): cnv_string,
        ((DR3DNS,'backface-culling'), None): cnv_string,
        ((DR3DNS,'center'), None): cnv_string,
        ((DR3DNS,'close-back'), None): cnv_boolean,
        ((DR3DNS,'close-front'), None): cnv_boolean,
        ((DR3DNS,'depth'), None): cnv_length,
        ((DR3DNS,'diffuse-color'), None): cnv_string,
        ((DR3DNS,'direction'), None): cnv_string,
        ((DR3DNS,'distance'), None): cnv_length,
        ((DR3DNS,'edge-rounding'), None): cnv_string,
        ((DR3DNS,'edge-rounding-mode'), None): cnv_string,
        ((DR3DNS,'emissive-color'), None): cnv_string,
        ((DR3DNS,'enabled'), None): cnv_boolean,
        ((DR3DNS,'end-angle'), None): cnv_string,
        ((DR3DNS,'focal-length'), None): cnv_length,
        ((DR3DNS,'horizontal-segments'), None): cnv_string,
        ((DR3DNS,'lighting-mode'), None): cnv_boolean,
        ((DR3DNS,'max-edge'), None): cnv_string,
        ((DR3DNS,'min-edge'), None): cnv_string,
        ((DR3DNS,'normals-direction'), None): cnv_string,
        ((DR3DNS,'normals-kind'), None): cnv_string,
        ((DR3DNS,'projection'), None): cnv_string,
        ((DR3DNS,'shade-mode'), None): cnv_string,
        ((DR3DNS,'shadow'), None): cnv_string,
        ((DR3DNS,'shadow-slant'), None): cnv_nonNegativeInteger,
        ((DR3DNS,'shininess'), None): cnv_string,
        ((DR3DNS,'size'), None): cnv_string,
        ((DR3DNS,'specular'), None): cnv_boolean,
        ((DR3DNS,'specular-color'), None): cnv_string,
        ((DR3DNS,'texture-filter'), None): cnv_string,
        ((DR3DNS,'texture-generation-mode-x'), None): cnv_string,
        ((DR3DNS,'texture-generation-mode-y'), None): cnv_string,
        ((DR3DNS,'texture-kind'), None): cnv_string,
        ((DR3DNS,'texture-mode'), None): cnv_string,
        ((DR3DNS,'transform'), None): cnv_string,
        ((DR3DNS,'vertical-segments'), None): cnv_string,
        ((DR3DNS,'vpn'), None): cnv_string,
        ((DR3DNS,'vrp'), None): cnv_string,
        ((DR3DNS,'vup'), None): cnv_string,
        ((DRAWNS,'align'), None): cnv_string,
        ((DRAWNS,'angle'), None): cnv_integer,
        ((DRAWNS,'archive'), None): cnv_string,
        ((DRAWNS,'auto-grow-height'), None): cnv_boolean,
        ((DRAWNS,'auto-grow-width'), None): cnv_boolean,
        ((DRAWNS,'background-size'), None): cnv_string,
        ((DRAWNS,'blue'), None): cnv_string,
        ((DRAWNS,'border'), None): cnv_string,
        ((DRAWNS,'caption-angle'), None): cnv_string,
        ((DRAWNS,'caption-angle-type'), None): cnv_string,
        ((DRAWNS,'caption-escape'), None): cnv_string,
        ((DRAWNS,'caption-escape-direction'), None): cnv_string,
        ((DRAWNS,'caption-fit-line-length'), None): cnv_boolean,
        ((DRAWNS,'caption-gap'), None): cnv_string,
        ((DRAWNS,'caption-line-length'), None): cnv_length,
        ((DRAWNS,'caption-point-x'), None): cnv_string,
        ((DRAWNS,'caption-point-y'), None): cnv_string,
        ((DRAWNS,'caption-id'), None): cnv_IDREF,
        ((DRAWNS,'caption-type'), None): cnv_string,
        ((DRAWNS,'chain-next-name'), None): cnv_string,
        ((DRAWNS,'class-id'), None): cnv_string,
        ((DRAWNS,'class-names'), None): cnv_NCNames,
        ((DRAWNS,'code'), None): cnv_string,
        ((DRAWNS,'color'), None): cnv_string,
        ((DRAWNS,'color-inversion'), None): cnv_boolean,
        ((DRAWNS,'color-mode'), None): cnv_string,
        ((DRAWNS,'concave'), None): cnv_string,
        ((DRAWNS,'concentric-gradient-fill-allowed'), None): cnv_boolean,
        ((DRAWNS,'contrast'), None): cnv_string,
        ((DRAWNS,'control'), None): cnv_IDREF,
        ((DRAWNS,'copy-of'), None): cnv_string,
        ((DRAWNS,'corner-radius'), None): cnv_length,
        ((DRAWNS,'corners'), None): cnv_positiveInteger,
        ((DRAWNS,'cx'), None): cnv_string,
        ((DRAWNS,'cy'), None): cnv_string,
        ((DRAWNS,'data'), None): cnv_string,
        ((DRAWNS,'decimal-places'), None): cnv_string,
        ((DRAWNS,'display'), None): cnv_string,
        ((DRAWNS,'display-name'), None): cnv_string,
        ((DRAWNS,'distance'), None): cnv_lengthorpercent,
        ((DRAWNS,'dots1'), None): cnv_integer,
        ((DRAWNS,'dots1-length'), None): cnv_lengthorpercent,
        ((DRAWNS,'dots2'), None): cnv_integer,
        ((DRAWNS,'dots2-length'), None): cnv_lengthorpercent,
        ((DRAWNS,'end-angle'), None): cnv_double,
        ((DRAWNS,'end'), None): cnv_string,
        ((DRAWNS,'end-color'), None): cnv_string,
        ((DRAWNS,'end-glue-point'), None): cnv_nonNegativeInteger,
        ((DRAWNS,'end-guide'), None): cnv_length,
        ((DRAWNS,'end-intensity'), None): cnv_string,
        ((DRAWNS,'end-line-spacing-horizontal'), None): cnv_string,
        ((DRAWNS,'end-line-spacing-vertical'), None): cnv_string,
        ((DRAWNS,'end-shape'), None): cnv_IDREF,
        ((DRAWNS,'engine'), None): cnv_namespacedToken,
        ((DRAWNS,'enhanced-path'), None): cnv_string,
        ((DRAWNS,'escape-direction'), None): cnv_string,
        ((DRAWNS,'extrusion-allowed'), None): cnv_boolean,
        ((DRAWNS,'extrusion-brightness'), None): cnv_string,
        ((DRAWNS,'extrusion'), None): cnv_boolean,
        ((DRAWNS,'extrusion-color'), None): cnv_boolean,
        ((DRAWNS,'extrusion-depth'), None): cnv_double,
        ((DRAWNS,'extrusion-diffusion'), None): cnv_string,
        ((DRAWNS,'extrusion-first-light-direction'), None): cnv_string,
        ((DRAWNS,'extrusion-first-light-harsh'), None): cnv_boolean,
        ((DRAWNS,'extrusion-first-light-level'), None): cnv_string,
        ((DRAWNS,'extrusion-light-face'), None): cnv_boolean,
        ((DRAWNS,'extrusion-metal'), None): cnv_boolean,
        ((DRAWNS,'extrusion-number-of-line-segments'), None): cnv_integer,
        ((DRAWNS,'extrusion-origin'), None): cnv_double,
        ((DRAWNS,'extrusion-rotation-angle'), None): cnv_double,
        ((DRAWNS,'extrusion-rotation-center'), None): cnv_string,
        ((DRAWNS,'extrusion-second-light-direction'), None): cnv_string,
        ((DRAWNS,'extrusion-second-light-harsh'), None): cnv_boolean,
        ((DRAWNS,'extrusion-second-light-level'), None): cnv_string,
        ((DRAWNS,'extrusion-shininess'), None): cnv_string,
        ((DRAWNS,'extrusion-skew'), None): cnv_double,
        ((DRAWNS,'extrusion-specularity'), None): cnv_string,
        ((DRAWNS,'extrusion-viewpoint'), None): cnv_string,
        ((DRAWNS,'fill'), None): cnv_string,
        ((DRAWNS,'fill-color'), None): cnv_string,
        ((DRAWNS,'fill-gradient-name'), None): cnv_string,
        ((DRAWNS,'fill-hatch-name'), None): cnv_string,
        ((DRAWNS,'fill-hatch-solid'), None): cnv_boolean,
        ((DRAWNS,'fill-image-height'), None): cnv_lengthorpercent,
        ((DRAWNS,'fill-image-name'), None): cnv_DrawNameRef,
        ((DRAWNS,'fill-image-ref-point'), None): cnv_string,
        ((DRAWNS,'fill-image-ref-point-x'), None): cnv_string,
        ((DRAWNS,'fill-image-ref-point-y'), None): cnv_string,
        ((DRAWNS,'fill-image-width'), None): cnv_lengthorpercent,
        ((DRAWNS,'filter-name'), None): cnv_string,
        ((DRAWNS,'fit-to-contour'), None): cnv_boolean,
        ((DRAWNS,'fit-to-size'), None): cnv_boolean,
        ((DRAWNS,'formula'), None): cnv_string,
        ((DRAWNS,'frame-display-border'), None): cnv_boolean,
        ((DRAWNS,'frame-display-scrollbar'), None): cnv_boolean,
        ((DRAWNS,'frame-margin-horizontal'), None): cnv_string,
        ((DRAWNS,'frame-margin-vertical'), None): cnv_string,
        ((DRAWNS,'frame-name'), None): cnv_string,
        ((DRAWNS,'gamma'), None): cnv_string,
        ((DRAWNS,'glue-point-leaving-directions'), None): cnv_string,
        ((DRAWNS,'glue-point-type'), None): cnv_string,
        ((DRAWNS,'glue-points'), None): cnv_string,
        ((DRAWNS,'gradient-step-count'), None): cnv_string,
        ((DRAWNS,'green'), None): cnv_string,
        ((DRAWNS,'guide-distance'), None): cnv_string,
        ((DRAWNS,'guide-overhang'), None): cnv_length,
        ((DRAWNS,'handle-mirror-horizontal'), None): cnv_boolean,
        ((DRAWNS,'handle-mirror-vertical'), None): cnv_boolean,
        ((DRAWNS,'handle-polar'), None): cnv_string,
        ((DRAWNS,'handle-position'), None): cnv_string,
        ((DRAWNS,'handle-radius-range-maximum'), None): cnv_string,
        ((DRAWNS,'handle-radius-range-minimum'), None): cnv_string,
        ((DRAWNS,'handle-range-x-maximum'), None): cnv_string,
        ((DRAWNS,'handle-range-x-minimum'), None): cnv_string,
        ((DRAWNS,'handle-range-y-maximum'), None): cnv_string,
        ((DRAWNS,'handle-range-y-minimum'), None): cnv_string,
        ((DRAWNS,'handle-switched'), None): cnv_boolean,
        # ((DRAWNS,'id'), None): cnv_ID,
        # ((DRAWNS,'id'), None): cnv_nonNegativeInteger,   # ?? line 6581 in RNG
        ((DRAWNS,'id'), None): cnv_string,
        ((DRAWNS,'image-opacity'), None): cnv_string,
        ((DRAWNS,'kind'), None): cnv_string,
        ((DRAWNS,'layer'), None): cnv_string,
        ((DRAWNS,'line-distance'), None): cnv_string,
        ((DRAWNS,'line-skew'), None): cnv_string,
        ((DRAWNS,'luminance'), None): cnv_string,
        ((DRAWNS,'marker-end-center'), None): cnv_boolean,
        ((DRAWNS,'marker-end'), None): cnv_string,
        ((DRAWNS,'marker-end-width'), None): cnv_length,
        ((DRAWNS,'marker-start-center'), None): cnv_boolean,
        ((DRAWNS,'marker-start'), None): cnv_string,
        ((DRAWNS,'marker-start-width'), None): cnv_length,
        ((DRAWNS,'master-page-name'), None): cnv_StyleNameRef,
        ((DRAWNS,'may-script'), None): cnv_boolean,
        ((DRAWNS,'measure-align'), None): cnv_string,
        ((DRAWNS,'measure-vertical-align'), None): cnv_string,
        ((DRAWNS,'mime-type'), None): cnv_string,
        ((DRAWNS,'mirror-horizontal'), None): cnv_boolean,
        ((DRAWNS,'mirror-vertical'), None): cnv_boolean,
        ((DRAWNS,'modifiers'), None): cnv_string,
        ((DRAWNS,'name'), None): cnv_NCName,
        # ((DRAWNS,'name'), None): cnv_string,
        ((DRAWNS,'nav-order'), None): cnv_IDREF,
        ((DRAWNS,'nohref'), None): cnv_string,
        ((DRAWNS,'notify-on-update-of-ranges'), None): cnv_string,
        ((DRAWNS,'object'), None): cnv_string,
        ((DRAWNS,'ole-draw-aspect'), None): cnv_string,
        ((DRAWNS,'opacity'), None): cnv_string,
        ((DRAWNS,'opacity-name'), None): cnv_string,
        ((DRAWNS,'page-number'), None): cnv_positiveInteger,
        ((DRAWNS,'parallel'), None): cnv_boolean,
        ((DRAWNS,'path-stretchpoint-x'), None): cnv_double,
        ((DRAWNS,'path-stretchpoint-y'), None): cnv_double,
        ((DRAWNS,'placing'), None): cnv_string,
        ((DRAWNS,'points'), None): cnv_points,
        ((DRAWNS,'protected'), None): cnv_boolean,
        ((DRAWNS,'recreate-on-edit'), None): cnv_boolean,
        ((DRAWNS,'red'), None): cnv_string,
        ((DRAWNS,'rotation'), None): cnv_integer,
        ((DRAWNS,'secondary-fill-color'), None): cnv_string,
        ((DRAWNS,'shadow'), None): cnv_string,
        ((DRAWNS,'shadow-color'), None): cnv_string,
        ((DRAWNS,'shadow-offset-x'), None): cnv_length,
        ((DRAWNS,'shadow-offset-y'), None): cnv_length,
        ((DRAWNS,'shadow-opacity'), None): cnv_string,
        ((DRAWNS,'shape-id'), None): cnv_IDREF,
        ((DRAWNS,'sharpness'), None): cnv_string,
        ((DRAWNS,'show-unit'), None): cnv_boolean,
        ((DRAWNS,'start-angle'), None): cnv_double,
        ((DRAWNS,'start'), None): cnv_string,
        ((DRAWNS,'start-color'), None): cnv_string,
        ((DRAWNS,'start-glue-point'), None): cnv_nonNegativeInteger,
        ((DRAWNS,'start-guide'), None): cnv_length,
        ((DRAWNS,'start-intensity'), None): cnv_string,
        ((DRAWNS,'start-line-spacing-horizontal'), None): cnv_string,
        ((DRAWNS,'start-line-spacing-vertical'), None): cnv_string,
        ((DRAWNS,'start-shape'), None): cnv_IDREF,
        ((DRAWNS,'stroke'), None): cnv_string,
        ((DRAWNS,'stroke-dash'), None): cnv_string,
        ((DRAWNS,'stroke-dash-names'), None): cnv_string,
        ((DRAWNS,'stroke-linejoin'), None): cnv_string,
        ((DRAWNS,'style'), None): cnv_string,
        ((DRAWNS,'style-name'), None): cnv_StyleNameRef,
        ((DRAWNS,'symbol-color'), None): cnv_string,
        ((DRAWNS,'text-areas'), None): cnv_string,
        ((DRAWNS,'text-path-allowed'), None): cnv_boolean,
        ((DRAWNS,'text-path'), None): cnv_boolean,
        ((DRAWNS,'text-path-mode'), None): cnv_string,
        ((DRAWNS,'text-path-same-letter-heights'), None): cnv_boolean,
        ((DRAWNS,'text-path-scale'), None): cnv_string,
        ((DRAWNS,'text-rotate-angle'), None): cnv_double,
        ((DRAWNS,'text-style-name'), None): cnv_StyleNameRef,
        ((DRAWNS,'textarea-horizontal-align'), None): cnv_string,
        ((DRAWNS,'textarea-vertical-align'), None): cnv_string,
        ((DRAWNS,'tile-repeat-offset'), None): cnv_string,
        ((DRAWNS,'transform'), None): cnv_string,
        ((DRAWNS,'type'), None): cnv_string,
        ((DRAWNS,'unit'), None): cnv_string,
        ((DRAWNS,'value'), None): cnv_string,
        ((DRAWNS,'visible-area-height'), None): cnv_string,
        ((DRAWNS,'visible-area-left'), None): cnv_string,
        ((DRAWNS,'visible-area-top'), None): cnv_string,
        ((DRAWNS,'visible-area-width'), None): cnv_string,
        ((DRAWNS,'wrap-influence-on-position'), None): cnv_string,
        ((DRAWNS,'z-index'), None): cnv_nonNegativeInteger,
        ((FONS,'background-color'), None): cnv_string,
        ((FONS,'border-bottom'), None): cnv_string,
        ((FONS,'border'), None): cnv_string,
        ((FONS,'border-left'), None): cnv_string,
        ((FONS,'border-right'), None): cnv_string,
        ((FONS,'border-top'), None): cnv_string,
        ((FONS,'break-after'), None): cnv_string,
        ((FONS,'break-before'), None): cnv_string,
        ((FONS,'clip'), None): cnv_string,
        ((FONS,'color'), None): cnv_string,
        ((FONS,'column-count'), None): cnv_positiveInteger,
        ((FONS,'column-gap'), None): cnv_length,
        ((FONS,'country'), None): cnv_token,
        ((FONS,'end-indent'), None): cnv_length,
        ((FONS,'font-family'), None): cnv_string,
        ((FONS,'font-size'), None): cnv_string,
        ((FONS,'font-style'), None): cnv_string,
        ((FONS,'font-variant'), None): cnv_string,
        ((FONS,'font-weight'), None): cnv_string,
        ((FONS,'height'), None): cnv_string,
        ((FONS,'hyphenate'), None): cnv_boolean,
        ((FONS,'hyphenation-keep'), None): cnv_string,
        ((FONS,'hyphenation-ladder-count'), None): cnv_string,
        ((FONS,'hyphenation-push-char-count'), None): cnv_string,
        ((FONS,'hyphenation-remain-char-count'), None): cnv_string,
        ((FONS,'keep-together'), None): cnv_string,
        ((FONS,'keep-with-next'), None): cnv_string,
        ((FONS,'language'), None): cnv_token,
        ((FONS,'letter-spacing'), None): cnv_string,
        ((FONS,'line-height'), None): cnv_string,
        ((FONS,'margin-bottom'), None): cnv_string,
        ((FONS,'margin'), None): cnv_string,
        ((FONS,'margin-left'), None): cnv_string,
        ((FONS,'margin-right'), None): cnv_string,
        ((FONS,'margin-top'), None): cnv_string,
        ((FONS,'max-height'), None): cnv_string,
        ((FONS,'max-width'), None): cnv_string,
        ((FONS,'min-height'), None): cnv_lengthorpercent,
        ((FONS,'min-width'), None): cnv_string,
        ((FONS,'orphans'), None): cnv_string,
        ((FONS,'padding-bottom'), None): cnv_string,
        ((FONS,'padding'), None): cnv_string,
        ((FONS,'padding-left'), None): cnv_string,
        ((FONS,'padding-right'), None): cnv_string,
        ((FONS,'padding-top'), None): cnv_string,
        ((FONS,'page-height'), None): cnv_length,
        ((FONS,'page-width'), None): cnv_length,
        ((FONS,'space-after'), None): cnv_length,
        ((FONS,'space-before'), None): cnv_length,
        ((FONS,'start-indent'), None): cnv_length,
        ((FONS,'text-align'), None): cnv_string,
        ((FONS,'text-align-last'), None): cnv_string,
        ((FONS,'text-indent'), None): cnv_string,
        ((FONS,'text-shadow'), None): cnv_string,
        ((FONS,'text-transform'), None): cnv_string,
        ((FONS,'widows'), None): cnv_string,
        ((FONS,'width'), None): cnv_string,
        ((FONS,'wrap-option'), None): cnv_string,
        ((FORMNS,'allow-deletes'), None): cnv_boolean,
        ((FORMNS,'allow-inserts'), None): cnv_boolean,
        ((FORMNS,'allow-updates'), None): cnv_boolean,
        ((FORMNS,'apply-design-mode'), None): cnv_boolean,
        ((FORMNS,'apply-filter'), None): cnv_boolean,
        ((FORMNS,'auto-complete'), None): cnv_boolean,
        ((FORMNS,'automatic-focus'), None): cnv_boolean,
        ((FORMNS,'bound-column'), None): cnv_string,
        ((FORMNS,'button-type'), None): cnv_string,
        ((FORMNS,'command'), None): cnv_string,
        ((FORMNS,'command-type'), None): cnv_string,
        ((FORMNS,'control-implementation'), None): cnv_namespacedToken,
        ((FORMNS,'convert-empty-to-null'), None): cnv_boolean,
        ((FORMNS,'current-selected'), None): cnv_boolean,
        ((FORMNS,'current-state'), None): cnv_string,
        # ((FORMNS,'current-value'), None): cnv_date,
        # ((FORMNS,'current-value'), None): cnv_double,
        ((FORMNS,'current-value'), None): cnv_string,
        # ((FORMNS,'current-value'), None): cnv_time,
        ((FORMNS,'data-field'), None): cnv_string,
        ((FORMNS,'datasource'), None): cnv_string,
        ((FORMNS,'default-button'), None): cnv_boolean,
        ((FORMNS,'delay-for-repeat'), None): cnv_duration,
        ((FORMNS,'detail-fields'), None): cnv_string,
        ((FORMNS,'disabled'), None): cnv_boolean,
        ((FORMNS,'dropdown'), None): cnv_boolean,
        ((FORMNS,'echo-char'), None): cnv_string,
        ((FORMNS,'enctype'), None): cnv_string,
        ((FORMNS,'escape-processing'), None): cnv_boolean,
        ((FORMNS,'filter'), None): cnv_string,
        ((FORMNS,'focus-on-click'), None): cnv_boolean,
        ((FORMNS,'for'), None): cnv_string,
        ((FORMNS,'id'), None): cnv_ID,
        ((FORMNS,'ignore-result'), None): cnv_boolean,
        ((FORMNS,'image-align'), None): cnv_string,
        ((FORMNS,'image-data'), None): cnv_anyURI,
        ((FORMNS,'image-position'), None): cnv_string,
        ((FORMNS,'is-tristate'), None): cnv_boolean,
        ((FORMNS,'label'), None): cnv_string,
        ((FORMNS,'list-source'), None): cnv_string,
        ((FORMNS,'list-source-type'), None): cnv_string,
        ((FORMNS,'master-fields'), None): cnv_string,
        ((FORMNS,'max-length'), None): cnv_nonNegativeInteger,
        # ((FORMNS,'max-value'), None): cnv_date,
        # ((FORMNS,'max-value'), None): cnv_double,
        ((FORMNS,'max-value'), None): cnv_string,
        # ((FORMNS,'max-value'), None): cnv_time,
        ((FORMNS,'method'), None): cnv_string,
        # ((FORMNS,'min-value'), None): cnv_date,
        # ((FORMNS,'min-value'), None): cnv_double,
        ((FORMNS,'min-value'), None): cnv_string,
        # ((FORMNS,'min-value'), None): cnv_time,
        ((FORMNS,'multi-line'), None): cnv_boolean,
        ((FORMNS,'multiple'), None): cnv_boolean,
        ((FORMNS,'name'), None): cnv_string,
        ((FORMNS,'navigation-mode'), None): cnv_string,
        ((FORMNS,'order'), None): cnv_string,
        ((FORMNS,'orientation'), None): cnv_string,
        ((FORMNS,'page-step-size'), None): cnv_positiveInteger,
        ((FORMNS,'printable'), None): cnv_boolean,
        ((FORMNS,'property-name'), None): cnv_string,
        ((FORMNS,'readonly'), None): cnv_boolean,
        ((FORMNS,'selected'), None): cnv_boolean,
        ((FORMNS,'size'), None): cnv_nonNegativeInteger,
        ((FORMNS,'state'), None): cnv_string,
        ((FORMNS,'step-size'), None): cnv_positiveInteger,
        ((FORMNS,'tab-cycle'), None): cnv_string,
        ((FORMNS,'tab-index'), None): cnv_nonNegativeInteger,
        ((FORMNS,'tab-stop'), None): cnv_boolean,
        ((FORMNS,'text-style-name'), None): cnv_StyleNameRef,
        ((FORMNS,'title'), None): cnv_string,
        ((FORMNS,'toggle'), None): cnv_boolean,
        ((FORMNS,'validation'), None): cnv_boolean,
        # ((FORMNS,'value'), None): cnv_date,
        # ((FORMNS,'value'), None): cnv_double,
        ((FORMNS,'value'), None): cnv_string,
        # ((FORMNS,'value'), None): cnv_time,
        ((FORMNS,'visual-effect'), None): cnv_string,
        ((FORMNS,'xforms-list-source'), None): cnv_string,
        ((FORMNS,'xforms-submission'), None): cnv_string,
        ((MANIFESTNS,'algorithm-name'), None): cnv_string,
        ((MANIFESTNS,'checksum'), None): cnv_string,
        ((MANIFESTNS,'checksum-type'), None): cnv_string,
        ((MANIFESTNS,'full-path'), None): cnv_string,
        ((MANIFESTNS,'initialisation-vector'), None): cnv_string,
        ((MANIFESTNS,'iteration-count'), None): cnv_nonNegativeInteger,
        ((MANIFESTNS,'key-derivation-name'), None): cnv_string,
        ((MANIFESTNS,'media-type'), None): cnv_string,
        ((MANIFESTNS,'salt'), None): cnv_string,
        ((MANIFESTNS,'size'), None): cnv_nonNegativeInteger,
        ((METANS,'cell-count'), None): cnv_nonNegativeInteger,
        ((METANS,'character-count'), None): cnv_nonNegativeInteger,
        ((METANS,'date'), None): cnv_dateTime,
        ((METANS,'delay'), None): cnv_duration,
        ((METANS,'draw-count'), None): cnv_nonNegativeInteger,
        ((METANS,'frame-count'), None): cnv_nonNegativeInteger,
        ((METANS,'image-count'), None): cnv_nonNegativeInteger,
        ((METANS,'name'), None): cnv_string,
        ((METANS,'non-whitespace-character-count'), None): cnv_nonNegativeInteger,
        ((METANS,'object-count'), None): cnv_nonNegativeInteger,
        ((METANS,'ole-object-count'), None): cnv_nonNegativeInteger,
        ((METANS,'page-count'), None): cnv_nonNegativeInteger,
        ((METANS,'paragraph-count'), None): cnv_nonNegativeInteger,
        ((METANS,'row-count'), None): cnv_nonNegativeInteger,
        ((METANS,'sentence-count'), None): cnv_nonNegativeInteger,
        ((METANS,'syllable-count'), None): cnv_nonNegativeInteger,
        ((METANS,'table-count'), None): cnv_nonNegativeInteger,
        ((METANS,'value-type'), None): cnv_metavaluetype,
        ((METANS,'word-count'), None): cnv_nonNegativeInteger,
        ((NUMBERNS,'automatic-order'), None): cnv_boolean,
        ((NUMBERNS,'calendar'), None): cnv_string,
        ((NUMBERNS,'country'), None): cnv_token,
        ((NUMBERNS,'decimal-places'), None): cnv_integer,
        ((NUMBERNS,'decimal-replacement'), None): cnv_string,
        ((NUMBERNS,'denominator-value'), None): cnv_integer,
        ((NUMBERNS,'display-factor'), None): cnv_double,
        ((NUMBERNS,'format-source'), None): cnv_string,
        ((NUMBERNS,'grouping'), None): cnv_boolean,
        ((NUMBERNS,'language'), None): cnv_token,
        ((NUMBERNS,'min-denominator-digits'), None): cnv_integer,
        ((NUMBERNS,'min-exponent-digits'), None): cnv_integer,
        ((NUMBERNS,'min-integer-digits'), None): cnv_integer,
        ((NUMBERNS,'min-numerator-digits'), None): cnv_integer,
        ((NUMBERNS,'position'), None): cnv_integer,
        ((NUMBERNS,'possessive-form'), None): cnv_boolean,
        ((NUMBERNS,'style'), None): cnv_string,
        ((NUMBERNS,'textual'), None): cnv_boolean,
        ((NUMBERNS,'title'), None): cnv_string,
        ((NUMBERNS,'transliteration-country'), None): cnv_token,
        ((NUMBERNS,'transliteration-format'), None): cnv_string,
        ((NUMBERNS,'transliteration-language'), None): cnv_token,
        ((NUMBERNS,'transliteration-style'), None): cnv_string,
        ((NUMBERNS,'truncate-on-overflow'), None): cnv_boolean,
        ((OFFICENS,'automatic-update'), None): cnv_boolean,
        ((OFFICENS,'boolean-value'), None): cnv_boolean,
        ((OFFICENS,'conversion-mode'), None): cnv_string,
        ((OFFICENS,'currency'), None): cnv_string,
        ((OFFICENS,'date-value'), None): cnv_dateTime,
        ((OFFICENS,'dde-application'), None): cnv_string,
        ((OFFICENS,'dde-item'), None): cnv_string,
        ((OFFICENS,'dde-topic'), None): cnv_string,
        ((OFFICENS,'display'), None): cnv_boolean,
        ((OFFICENS,'mimetype'), None): cnv_string,
        ((OFFICENS,'name'), None): cnv_string,
        ((OFFICENS,'process-content'), None): cnv_boolean,
        ((OFFICENS,'server-map'), None): cnv_boolean,
        ((OFFICENS,'string-value'), None): cnv_string,
        ((OFFICENS,'target-frame'), None): cnv_string,
        ((OFFICENS,'target-frame-name'), None): cnv_string,
        ((OFFICENS,'time-value'), None): cnv_duration,
        ((OFFICENS,'title'), None): cnv_string,
        ((OFFICENS,'value'), None): cnv_double,
        ((OFFICENS,'value-type'), None): cnv_string,
        ((OFFICENS,'version'), None): cnv_string,
        ((PRESENTATIONNS,'action'), None): cnv_string,
        ((PRESENTATIONNS,'animations'), None): cnv_string,
        ((PRESENTATIONNS,'background-objects-visible'), None): cnv_boolean,
        ((PRESENTATIONNS,'background-visible'), None): cnv_boolean,
        ((PRESENTATIONNS,'class'), None): cnv_string,
        ((PRESENTATIONNS,'class-names'), None): cnv_NCNames,
        ((PRESENTATIONNS,'delay'), None): cnv_duration,
        ((PRESENTATIONNS,'direction'), None): cnv_string,
        ((PRESENTATIONNS,'display-date-time'), None): cnv_boolean,
        ((PRESENTATIONNS,'display-footer'), None): cnv_boolean,
        ((PRESENTATIONNS,'display-header'), None): cnv_boolean,
        ((PRESENTATIONNS,'display-page-number'), None): cnv_boolean,
        ((PRESENTATIONNS,'duration'), None): cnv_string,
        ((PRESENTATIONNS,'effect'), None): cnv_string,
        ((PRESENTATIONNS,'endless'), None): cnv_boolean,
        ((PRESENTATIONNS,'force-manual'), None): cnv_boolean,
        ((PRESENTATIONNS,'full-screen'), None): cnv_boolean,
        ((PRESENTATIONNS,'group-id'), None): cnv_string,
        ((PRESENTATIONNS,'master-element'), None): cnv_IDREF,
        ((PRESENTATIONNS,'mouse-as-pen'), None): cnv_boolean,
        ((PRESENTATIONNS,'mouse-visible'), None): cnv_boolean,
        ((PRESENTATIONNS,'name'), None): cnv_string,
        ((PRESENTATIONNS,'node-type'), None): cnv_string,
        ((PRESENTATIONNS,'object'), None): cnv_string,
        ((PRESENTATIONNS,'pages'), None): cnv_string,
        ((PRESENTATIONNS,'path-id'), None): cnv_string,
        ((PRESENTATIONNS,'pause'), None): cnv_duration,
        ((PRESENTATIONNS,'placeholder'), None): cnv_boolean,
        ((PRESENTATIONNS,'play-full'), None): cnv_boolean,
        ((PRESENTATIONNS,'presentation-page-layout-name'), None): cnv_StyleNameRef,
        ((PRESENTATIONNS,'preset-class'), None): cnv_string,
        ((PRESENTATIONNS,'preset-id'), None): cnv_string,
        ((PRESENTATIONNS,'preset-sub-type'), None): cnv_string,
        ((PRESENTATIONNS,'show'), None): cnv_string,
        ((PRESENTATIONNS,'show-end-of-presentation-slide'), None): cnv_boolean,
        ((PRESENTATIONNS,'show-logo'), None): cnv_boolean,
        ((PRESENTATIONNS,'source'), None): cnv_string,
        ((PRESENTATIONNS,'speed'), None): cnv_string,
        ((PRESENTATIONNS,'start-page'), None): cnv_string,
        ((PRESENTATIONNS,'start-scale'), None): cnv_string,
        ((PRESENTATIONNS,'start-with-navigator'), None): cnv_boolean,
        ((PRESENTATIONNS,'stay-on-top'), None): cnv_boolean,
        ((PRESENTATIONNS,'style-name'), None): cnv_StyleNameRef,
        ((PRESENTATIONNS,'transition-on-click'), None): cnv_string,
        ((PRESENTATIONNS,'transition-speed'), None): cnv_string,
        ((PRESENTATIONNS,'transition-style'), None): cnv_string,
        ((PRESENTATIONNS,'transition-type'), None): cnv_string,
        ((PRESENTATIONNS,'use-date-time-name'), None): cnv_string,
        ((PRESENTATIONNS,'use-footer-name'), None): cnv_string,
        ((PRESENTATIONNS,'use-header-name'), None): cnv_string,
        ((PRESENTATIONNS,'user-transformed'), None): cnv_boolean,
        ((PRESENTATIONNS,'verb'), None): cnv_nonNegativeInteger,
        ((PRESENTATIONNS,'visibility'), None): cnv_string,
        ((SCRIPTNS,'event-name'), None): cnv_formula,
        ((SCRIPTNS,'language'), None): cnv_formula,
        ((SCRIPTNS,'macro-name'), None): cnv_string,
        ((SMILNS,'accelerate'), None): cnv_double,
        ((SMILNS,'accumulate'), None): cnv_string,
        ((SMILNS,'additive'), None): cnv_string,
        ((SMILNS,'attributeName'), None): cnv_string,
        ((SMILNS,'autoReverse'), None): cnv_boolean,
        ((SMILNS,'begin'), None): cnv_string,
        ((SMILNS,'by'), None): cnv_string,
        ((SMILNS,'calcMode'), None): cnv_string,
        ((SMILNS,'decelerate'), None): cnv_double,
        ((SMILNS,'direction'), None): cnv_string,
        ((SMILNS,'dur'), None): cnv_string,
        ((SMILNS,'end'), None): cnv_string,
        ((SMILNS,'endsync'), None): cnv_string,
        ((SMILNS,'fadeColor'), None): cnv_string,
        ((SMILNS,'fill'), None): cnv_string,
        ((SMILNS,'fillDefault'), None): cnv_string,
        ((SMILNS,'from'), None): cnv_string,
        ((SMILNS,'keySplines'), None): cnv_string,
        ((SMILNS,'keyTimes'), None): cnv_string,
        ((SMILNS,'mode'), None): cnv_string,
        ((SMILNS,'repeatCount'), None): cnv_nonNegativeInteger,
        ((SMILNS,'repeatDur'), None): cnv_string,
        ((SMILNS,'restart'), None): cnv_string,
        ((SMILNS,'restartDefault'), None): cnv_string,
        ((SMILNS,'subtype'), None): cnv_string,
        ((SMILNS,'targetElement'), None): cnv_IDREF,
        ((SMILNS,'to'), None): cnv_string,
        ((SMILNS,'type'), None): cnv_string,
        ((SMILNS,'values'), None): cnv_string,
        ((STYLENS,'adjustment'), None): cnv_string,
        ((STYLENS,'apply-style-name'), None): cnv_StyleNameRef,
        ((STYLENS,'auto-text-indent'), None): cnv_boolean,
        ((STYLENS,'auto-update'), None): cnv_boolean,
        ((STYLENS,'background-transparency'), None): cnv_string,
        ((STYLENS,'base-cell-address'), None): cnv_string,
        ((STYLENS,'border-line-width-bottom'), None): cnv_string,
        ((STYLENS,'border-line-width'), None): cnv_string,
        ((STYLENS,'border-line-width-left'), None): cnv_string,
        ((STYLENS,'border-line-width-right'), None): cnv_string,
        ((STYLENS,'border-line-width-top'), None): cnv_string,
        ((STYLENS,'cell-protect'), None): cnv_string,
        ((STYLENS,'char'), None): cnv_string,
        ((STYLENS,'class'), None): cnv_string,
        ((STYLENS,'color'), None): cnv_string,
        ((STYLENS,'column-width'), None): cnv_string,
        ((STYLENS,'condition'), None): cnv_string,
        ((STYLENS,'country-asian'), None): cnv_string,
        ((STYLENS,'country-complex'), None): cnv_string,
        ((STYLENS,'data-style-name'), None): cnv_StyleNameRef,
        ((STYLENS,'decimal-places'), None): cnv_string,
        ((STYLENS,'default-outline-level'), None): cnv_positiveInteger,
        ((STYLENS,'diagonal-bl-tr'), None): cnv_string,
        ((STYLENS,'diagonal-bl-tr-widths'), None): cnv_string,
        ((STYLENS,'diagonal-tl-br'), None): cnv_string,
        ((STYLENS,'diagonal-tl-br-widths'), None): cnv_string,
        ((STYLENS,'direction'), None): cnv_string,
        ((STYLENS,'display'), None): cnv_boolean,
        ((STYLENS,'display-name'), None): cnv_string,
        ((STYLENS,'distance-after-sep'), None): cnv_length,
        ((STYLENS,'distance-before-sep'), None): cnv_length,
        ((STYLENS,'distance'), None): cnv_length,
        ((STYLENS,'dynamic-spacing'), None): cnv_boolean,
        ((STYLENS,'editable'), None): cnv_boolean,
        ((STYLENS,'family'), None): cnv_family,
        ((STYLENS,'filter-name'), None): cnv_string,
        ((STYLENS,'first-page-number'), None): cnv_string,
        ((STYLENS,'flow-with-text'), None): cnv_boolean,
        ((STYLENS,'font-adornments'), None): cnv_string,
        ((STYLENS,'font-charset'), None): cnv_string,
        ((STYLENS,'font-charset-asian'), None): cnv_string,
        ((STYLENS,'font-charset-complex'), None): cnv_string,
        ((STYLENS,'font-family-asian'), None): cnv_string,
        ((STYLENS,'font-family-complex'), None): cnv_string,
        ((STYLENS,'font-family-generic-asian'), None): cnv_string,
        ((STYLENS,'font-family-generic'), None): cnv_string,
        ((STYLENS,'font-family-generic-complex'), None): cnv_string,
        ((STYLENS,'font-independent-line-spacing'), None): cnv_boolean,
        ((STYLENS,'font-name-asian'), None): cnv_string,
        ((STYLENS,'font-name'), None): cnv_string,
        ((STYLENS,'font-name-complex'), None): cnv_string,
        ((STYLENS,'font-pitch-asian'), None): cnv_string,
        ((STYLENS,'font-pitch'), None): cnv_string,
        ((STYLENS,'font-pitch-complex'), None): cnv_string,
        ((STYLENS,'font-relief'), None): cnv_string,
        ((STYLENS,'font-size-asian'), None): cnv_string,
        ((STYLENS,'font-size-complex'), None): cnv_string,
        ((STYLENS,'font-size-rel-asian'), None): cnv_length,
        ((STYLENS,'font-size-rel'), None): cnv_length,
        ((STYLENS,'font-size-rel-complex'), None): cnv_length,
        ((STYLENS,'font-style-asian'), None): cnv_string,
        ((STYLENS,'font-style-complex'), None): cnv_string,
        ((STYLENS,'font-style-name-asian'), None): cnv_string,
        ((STYLENS,'font-style-name'), None): cnv_string,
        ((STYLENS,'font-style-name-complex'), None): cnv_string,
        ((STYLENS,'font-weight-asian'), None): cnv_string,
        ((STYLENS,'font-weight-complex'), None): cnv_string,
        ((STYLENS,'footnote-max-height'), None): cnv_length,
        ((STYLENS,'glyph-orientation-vertical'), None): cnv_string,
        ((STYLENS,'height'), None): cnv_string,
        ((STYLENS,'horizontal-pos'), None): cnv_string,
        ((STYLENS,'horizontal-rel'), None): cnv_string,
        ((STYLENS,'justify-single-word'), None): cnv_boolean,
        ((STYLENS,'language-asian'), None): cnv_string,
        ((STYLENS,'language-complex'), None): cnv_string,
        ((STYLENS,'layout-grid-base-height'), None): cnv_length,
        ((STYLENS,'layout-grid-color'), None): cnv_string,
        ((STYLENS,'layout-grid-display'), None): cnv_boolean,
        ((STYLENS,'layout-grid-lines'), None): cnv_string,
        ((STYLENS,'layout-grid-mode'), None): cnv_string,
        ((STYLENS,'layout-grid-print'), None): cnv_boolean,
        ((STYLENS,'layout-grid-ruby-below'), None): cnv_boolean,
        ((STYLENS,'layout-grid-ruby-height'), None): cnv_length,
        ((STYLENS,'leader-char'), None): cnv_string,
        ((STYLENS,'leader-color'), None): cnv_string,
        ((STYLENS,'leader-style'), None): cnv_string,
        ((STYLENS,'leader-text'), None): cnv_string,
        ((STYLENS,'leader-text-style'), None): cnv_StyleNameRef,
        ((STYLENS,'leader-type'), None): cnv_string,
        ((STYLENS,'leader-width'), None): cnv_string,
        ((STYLENS,'legend-expansion-aspect-ratio'), None): cnv_double,
        ((STYLENS,'legend-expansion'), None): cnv_string,
        ((STYLENS,'length'), None): cnv_positiveInteger,
        ((STYLENS,'letter-kerning'), None): cnv_boolean,
        ((STYLENS,'line-break'), None): cnv_string,
        ((STYLENS,'line-height-at-least'), None): cnv_string,
        ((STYLENS,'line-spacing'), None): cnv_length,
        ((STYLENS,'line-style'), None): cnv_string,
        ((STYLENS,'lines'), None): cnv_positiveInteger,
        ((STYLENS,'list-style-name'), None): cnv_StyleNameRef,
        ((STYLENS,'master-page-name'), None): cnv_StyleNameRef,
        ((STYLENS,'may-break-between-rows'), None): cnv_boolean,
        ((STYLENS,'min-row-height'), None): cnv_string,
        ((STYLENS,'mirror'), None): cnv_string,
        ((STYLENS,'name'), None): cnv_NCName,
        ((STYLENS,'name'), (STYLENS,'font-face')): cnv_string,
        ((STYLENS,'next-style-name'), None): cnv_StyleNameRef,
        ((STYLENS,'num-format'), None): cnv_string,
        ((STYLENS,'num-letter-sync'), None): cnv_boolean,
        ((STYLENS,'num-prefix'), None): cnv_string,
        ((STYLENS,'num-suffix'), None): cnv_string,
        ((STYLENS,'number-wrapped-paragraphs'), None): cnv_string,
        ((STYLENS,'overflow-behavior'), None): cnv_string,
        ((STYLENS,'page-layout-name'), None): cnv_StyleNameRef,
        ((STYLENS,'page-number'), None): cnv_string,
        ((STYLENS,'page-usage'), None): cnv_string,
        ((STYLENS,'paper-tray-name'), None): cnv_string,
        ((STYLENS,'parent-style-name'), None): cnv_StyleNameRef,
        ((STYLENS,'position'), (STYLENS,'tab-stop')): cnv_length,
        ((STYLENS,'position'), None): cnv_string,
        ((STYLENS,'print'), None): cnv_string,
        ((STYLENS,'print-content'), None): cnv_boolean,
        ((STYLENS,'print-orientation'), None): cnv_string,
        ((STYLENS,'print-page-order'), None): cnv_string,
        ((STYLENS,'protect'), None): cnv_boolean,
        ((STYLENS,'punctuation-wrap'), None): cnv_string,
        ((STYLENS,'register-true'), None): cnv_boolean,
        ((STYLENS,'register-truth-ref-style-name'), None): cnv_string,
        ((STYLENS,'rel-column-width'), None): cnv_string,
        ((STYLENS,'rel-height'), None): cnv_string,
        ((STYLENS,'rel-width'), None): cnv_string,
        ((STYLENS,'repeat'), None): cnv_string,
        ((STYLENS,'repeat-content'), None): cnv_boolean,
        ((STYLENS,'rotation-align'), None): cnv_string,
        ((STYLENS,'rotation-angle'), None): cnv_string,
        ((STYLENS,'row-height'), None): cnv_string,
        ((STYLENS,'ruby-align'), None): cnv_string,
        ((STYLENS,'ruby-position'), None): cnv_string,
        ((STYLENS,'run-through'), None): cnv_string,
        ((STYLENS,'scale-to'), None): cnv_string,
        ((STYLENS,'scale-to-pages'), None): cnv_string,
        ((STYLENS,'script-type'), None): cnv_string,
        ((STYLENS,'shadow'), None): cnv_string,
        ((STYLENS,'shrink-to-fit'), None): cnv_boolean,
        ((STYLENS,'snap-to-layout-grid'), None): cnv_boolean,
        ((STYLENS,'style'), None): cnv_string,
        ((STYLENS,'style-name'), None): cnv_StyleNameRef,
        ((STYLENS,'tab-stop-distance'), None): cnv_string,
        ((STYLENS,'table-centering'), None): cnv_string,
        ((STYLENS,'text-align-source'), None): cnv_string,
        ((STYLENS,'text-autospace'), None): cnv_string,
        ((STYLENS,'text-blinking'), None): cnv_boolean,
        ((STYLENS,'text-combine'), None): cnv_string,
        ((STYLENS,'text-combine-end-char'), None): cnv_string,
        ((STYLENS,'text-combine-start-char'), None): cnv_string,
        ((STYLENS,'text-emphasize'), None): cnv_string,
        ((STYLENS,'text-line-through-color'), None): cnv_string,
        ((STYLENS,'text-line-through-mode'), None): cnv_string,
        ((STYLENS,'text-line-through-style'), None): cnv_string,
        ((STYLENS,'text-line-through-text'), None): cnv_string,
        ((STYLENS,'text-line-through-text-style'), None): cnv_string,
        ((STYLENS,'text-line-through-type'), None): cnv_string,
        ((STYLENS,'text-line-through-width'), None): cnv_string,
        ((STYLENS,'text-outline'), None): cnv_boolean,
        ((STYLENS,'text-position'), None): cnv_string,
        ((STYLENS,'text-rotation-angle'), None): cnv_string,
        ((STYLENS,'text-rotation-scale'), None): cnv_string,
        ((STYLENS,'text-scale'), None): cnv_string,
        ((STYLENS,'text-underline-color'), None): cnv_string,
        ((STYLENS,'text-underline-mode'), None): cnv_string,
        ((STYLENS,'text-underline-style'), None): cnv_string,
        ((STYLENS,'text-underline-type'), None): cnv_string,
        ((STYLENS,'text-underline-width'), None): cnv_string,
        ((STYLENS,'type'), None): cnv_string,
        ((STYLENS,'use-optimal-column-width'), None): cnv_boolean,
        ((STYLENS,'use-optimal-row-height'), None): cnv_boolean,
        ((STYLENS,'use-window-font-color'), None): cnv_boolean,
        ((STYLENS,'vertical-align'), None): cnv_string,
        ((STYLENS,'vertical-pos'), None): cnv_string,
        ((STYLENS,'vertical-rel'), None): cnv_string,
        ((STYLENS,'volatile'), None): cnv_boolean,
        ((STYLENS,'width'), None): cnv_string,
        ((STYLENS,'wrap'), None): cnv_string,
        ((STYLENS,'wrap-contour'), None): cnv_boolean,
        ((STYLENS,'wrap-contour-mode'), None): cnv_string,
        ((STYLENS,'wrap-dynamic-threshold'), None): cnv_length,
        ((STYLENS,'writing-mode-automatic'), None): cnv_boolean,
        ((STYLENS,'writing-mode'), None): cnv_string,
        ((SVGNS,'accent-height'), None): cnv_integer,
        ((SVGNS,'alphabetic'), None): cnv_integer,
        ((SVGNS,'ascent'), None): cnv_integer,
        ((SVGNS,'bbox'), None): cnv_string,
        ((SVGNS,'cap-height'), None): cnv_integer,
        ((SVGNS,'cx'), None): cnv_string,
        ((SVGNS,'cy'), None): cnv_string,
        ((SVGNS,'d'), None): cnv_string,
        ((SVGNS,'descent'), None): cnv_integer,
        ((SVGNS,'fill-rule'), None): cnv_string,
        ((SVGNS,'font-family'), None): cnv_string,
        ((SVGNS,'font-size'), None): cnv_string,
        ((SVGNS,'font-stretch'), None): cnv_string,
        ((SVGNS,'font-style'), None): cnv_string,
        ((SVGNS,'font-variant'), None): cnv_string,
        ((SVGNS,'font-weight'), None): cnv_string,
        ((SVGNS,'fx'), None): cnv_string,
        ((SVGNS,'fy'), None): cnv_string,
        ((SVGNS,'gradientTransform'), None): cnv_string,
        ((SVGNS,'gradientUnits'), None): cnv_string,
        ((SVGNS,'hanging'), None): cnv_integer,
        ((SVGNS,'height'), None): cnv_length,
        ((SVGNS,'ideographic'), None): cnv_integer,
        ((SVGNS,'mathematical'), None): cnv_integer,
        ((SVGNS,'name'), None): cnv_string,
        ((SVGNS,'offset'), None): cnv_string,
        ((SVGNS,'origin'), None): cnv_string,
        ((SVGNS,'overline-position'), None): cnv_integer,
        ((SVGNS,'overline-thickness'), None): cnv_integer,
        ((SVGNS,'panose-1'), None): cnv_string,
        ((SVGNS,'path'), None): cnv_string,
        ((SVGNS,'r'), None): cnv_length,
        ((SVGNS,'rx'), None): cnv_length,
        ((SVGNS,'ry'), None): cnv_length,
        ((SVGNS,'slope'), None): cnv_integer,
        ((SVGNS,'spreadMethod'), None): cnv_string,
        ((SVGNS,'stemh'), None): cnv_integer,
        ((SVGNS,'stemv'), None): cnv_integer,
        ((SVGNS,'stop-color'), None): cnv_string,
        ((SVGNS,'stop-opacity'), None): cnv_double,
        ((SVGNS,'strikethrough-position'), None): cnv_integer,
        ((SVGNS,'strikethrough-thickness'), None): cnv_integer,
        ((SVGNS,'string'), None): cnv_string,
        ((SVGNS,'stroke-color'), None): cnv_string,
        ((SVGNS,'stroke-opacity'), None): cnv_string,
        ((SVGNS,'stroke-width'), None): cnv_length,
        ((SVGNS,'type'), None): cnv_string,
        ((SVGNS,'underline-position'), None): cnv_integer,
        ((SVGNS,'underline-thickness'), None): cnv_integer,
        ((SVGNS,'unicode-range'), None): cnv_string,
        ((SVGNS,'units-per-em'), None): cnv_integer,
        ((SVGNS,'v-alphabetic'), None): cnv_integer,
        ((SVGNS,'v-hanging'), None): cnv_integer,
        ((SVGNS,'v-ideographic'), None): cnv_integer,
        ((SVGNS,'v-mathematical'), None): cnv_integer,
        ((SVGNS,'viewBox'), None): cnv_viewbox,
        ((SVGNS,'width'), None): cnv_length,
        ((SVGNS,'widths'), None): cnv_string,
        ((SVGNS,'x'), None): cnv_length,
        ((SVGNS,'x-height'), None): cnv_integer,
        ((SVGNS,'x1'), None): cnv_lengthorpercent,
        ((SVGNS,'x2'), None): cnv_lengthorpercent,
        ((SVGNS,'y'), None): cnv_length,
        ((SVGNS,'y1'), None): cnv_lengthorpercent,
        ((SVGNS,'y2'), None): cnv_lengthorpercent,
        ((TABLENS,'acceptance-state'), None): cnv_string,
        ((TABLENS,'add-empty-lines'), None): cnv_boolean,
        ((TABLENS,'algorithm'), None): cnv_formula,
        ((TABLENS,'align'), None): cnv_string,
        ((TABLENS,'allow-empty-cell'), None): cnv_boolean,
        ((TABLENS,'application-data'), None): cnv_string,
        ((TABLENS,'automatic-find-labels'), None): cnv_boolean,
        ((TABLENS,'base-cell-address'), None): cnv_string,
        ((TABLENS,'bind-styles-to-content'), None): cnv_boolean,
        ((TABLENS,'border-color'), None): cnv_string,
        ((TABLENS,'border-model'), None): cnv_string,
        ((TABLENS,'buttons'), None): cnv_string,
        # ((TABLENS,'case-sensitive'), None): cnv_boolean,
        ((TABLENS,'case-sensitive'), None): cnv_string,
        ((TABLENS,'cell-address'), None): cnv_string,
        ((TABLENS,'cell-range-address'), None): cnv_string,
        ((TABLENS,'cell-range'), None): cnv_string,
        ((TABLENS,'column'), None): cnv_integer,
        ((TABLENS,'comment'), None): cnv_string,
        ((TABLENS,'condition'), None): cnv_formula,
        ((TABLENS,'condition-source'), None): cnv_string,
        ((TABLENS,'condition-source-range-address'), None): cnv_string,
        ((TABLENS,'contains-error'), None): cnv_boolean,
        ((TABLENS,'contains-header'), None): cnv_boolean,
        ((TABLENS,'content-validation-name'), None): cnv_string,
        ((TABLENS,'copy-back'), None): cnv_boolean,
        ((TABLENS,'copy-formulas'), None): cnv_boolean,
        ((TABLENS,'copy-styles'), None): cnv_boolean,
        ((TABLENS,'count'), None): cnv_positiveInteger,
        ((TABLENS,'country'), None): cnv_token,
        ((TABLENS,'data-cell-range-address'), None): cnv_string,
        ((TABLENS,'data-field'), None): cnv_string,
        ((TABLENS,'data-type'), None): cnv_string,
        ((TABLENS,'database-name'), None): cnv_string,
        ((TABLENS,'database-table-name'), None): cnv_string,
        ((TABLENS,'date-end'), None): cnv_string,
        ((TABLENS,'date-start'), None): cnv_string,
        ((TABLENS,'date-value'), None): cnv_date,
        ((TABLENS,'default-cell-style-name'), None): cnv_StyleNameRef,
        ((TABLENS,'direction'), None): cnv_string,
        ((TABLENS,'display-border'), None): cnv_boolean,
        ((TABLENS,'display'), None): cnv_boolean,
        ((TABLENS,'display-duplicates'), None): cnv_boolean,
        ((TABLENS,'display-filter-buttons'), None): cnv_boolean,
        ((TABLENS,'display-list'), None): cnv_string,
        ((TABLENS,'display-member-mode'), None): cnv_string,
        ((TABLENS,'drill-down-on-double-click'), None): cnv_boolean,
        ((TABLENS,'enabled'), None): cnv_boolean,
        ((TABLENS,'end-cell-address'), None): cnv_string,
        ((TABLENS,'end'), None): cnv_string,
        ((TABLENS,'end-column'), None): cnv_integer,
        ((TABLENS,'end-position'), None): cnv_integer,
        ((TABLENS,'end-row'), None): cnv_integer,
        ((TABLENS,'end-table'), None): cnv_integer,
        ((TABLENS,'end-x'), None): cnv_length,
        ((TABLENS,'end-y'), None): cnv_length,
        ((TABLENS,'execute'), None): cnv_boolean,
        ((TABLENS,'expression'), None): cnv_formula,
        ((TABLENS,'field-name'), None): cnv_string,
        # ((TABLENS,'field-number'), None): cnv_nonNegativeInteger,
        ((TABLENS,'field-number'), None): cnv_string,
        ((TABLENS,'filter-name'), None): cnv_string,
        ((TABLENS,'filter-options'), None): cnv_string,
        ((TABLENS,'formula'), None): cnv_formula,
        ((TABLENS,'function'), None): cnv_string,
        ((TABLENS,'grand-total'), None): cnv_string,
        ((TABLENS,'group-by-field-number'), None): cnv_nonNegativeInteger,
        ((TABLENS,'grouped-by'), None): cnv_string,
        ((TABLENS,'has-persistent-data'), None): cnv_boolean,
        ((TABLENS,'id'), None): cnv_string,
        ((TABLENS,'identify-categories'), None): cnv_boolean,
        ((TABLENS,'ignore-empty-rows'), None): cnv_boolean,
        ((TABLENS,'index'), None): cnv_nonNegativeInteger,
        ((TABLENS,'is-active'), None): cnv_boolean,
        ((TABLENS,'is-data-layout-field'), None): cnv_string,
        ((TABLENS,'is-selection'), None): cnv_boolean,
        ((TABLENS,'is-sub-table'), None): cnv_boolean,
        ((TABLENS,'label-cell-range-address'), None): cnv_string,
        ((TABLENS,'language'), None): cnv_token,
        ((TABLENS,'last-column-spanned'), None): cnv_positiveInteger,
        ((TABLENS,'last-row-spanned'), None): cnv_positiveInteger,
        ((TABLENS,'layout-mode'), None): cnv_string,
        ((TABLENS,'link-to-source-data'), None): cnv_boolean,
        ((TABLENS,'marked-invalid'), None): cnv_boolean,
        ((TABLENS,'matrix-covered'), None): cnv_boolean,
        ((TABLENS,'maximum-difference'), None): cnv_double,
        ((TABLENS,'member-count'), None): cnv_nonNegativeInteger,
        ((TABLENS,'member-name'), None): cnv_string,
        ((TABLENS,'member-type'), None): cnv_string,
        ((TABLENS,'message-type'), None): cnv_string,
        ((TABLENS,'mode'), None): cnv_string,
        ((TABLENS,'multi-deletion-spanned'), None): cnv_integer,
        ((TABLENS,'name'), None): cnv_string,
        ((TABLENS,'null-year'), None): cnv_positiveInteger,
        ((TABLENS,'number-columns-repeated'), None): cnv_positiveInteger,
        ((TABLENS,'number-columns-spanned'), None): cnv_positiveInteger,
        ((TABLENS,'number-matrix-columns-spanned'), None): cnv_positiveInteger,
        ((TABLENS,'number-matrix-rows-spanned'), None): cnv_positiveInteger,
        ((TABLENS,'number-rows-repeated'), None): cnv_positiveInteger,
        ((TABLENS,'number-rows-spanned'), None): cnv_positiveInteger,
        ((TABLENS,'object-name'), None): cnv_string,
        ((TABLENS,'on-update-keep-size'), None): cnv_boolean,
        ((TABLENS,'on-update-keep-styles'), None): cnv_boolean,
        ((TABLENS,'operator'), None): cnv_string,
        ((TABLENS,'order'), None): cnv_string,
        ((TABLENS,'orientation'), None): cnv_string,
        ((TABLENS,'page-breaks-on-group-change'), None): cnv_boolean,
        ((TABLENS,'parse-sql-statement'), None): cnv_boolean,
        ((TABLENS,'password'), None): cnv_string,
        ((TABLENS,'position'), None): cnv_integer,
        ((TABLENS,'precision-as-shown'), None): cnv_boolean,
        ((TABLENS,'print'), None): cnv_boolean,
        ((TABLENS,'print-ranges'), None): cnv_string,
        ((TABLENS,'protect'), None): cnv_boolean,
        ((TABLENS,'protected'), None): cnv_boolean,
        ((TABLENS,'protection-key'), None): cnv_string,
        ((TABLENS,'query-name'), None): cnv_string,
        ((TABLENS,'range-usable-as'), None): cnv_string,
        # ((TABLENS,'refresh-delay'), None): cnv_boolean,
        ((TABLENS,'refresh-delay'), None): cnv_duration,
        ((TABLENS,'rejecting-change-id'), None): cnv_string,
        ((TABLENS,'row'), None): cnv_integer,
        ((TABLENS,'scenario-ranges'), None): cnv_string,
        ((TABLENS,'search-criteria-must-apply-to-whole-cell'), None): cnv_boolean,
        ((TABLENS,'selected-page'), None): cnv_string,
        ((TABLENS,'show-details'), None): cnv_boolean,
        # ((TABLENS,'show-empty'), None): cnv_boolean,
        ((TABLENS,'show-empty'), None): cnv_string,
        ((TABLENS,'show-filter-button'), None): cnv_boolean,
        ((TABLENS,'sort-mode'), None): cnv_string,
        ((TABLENS,'source-cell-range-addresses'), None): cnv_string,
        ((TABLENS,'source-field-name'), None): cnv_string,
        ((TABLENS,'source-name'), None): cnv_string,
        ((TABLENS,'sql-statement'), None): cnv_string,
        ((TABLENS,'start'), None): cnv_string,
        ((TABLENS,'start-column'), None): cnv_integer,
        ((TABLENS,'start-position'), None): cnv_integer,
        ((TABLENS,'start-row'), None): cnv_integer,
        ((TABLENS,'start-table'), None): cnv_integer,
        ((TABLENS,'status'), None): cnv_string,
        ((TABLENS,'step'), None): cnv_double,
        ((TABLENS,'steps'), None): cnv_positiveInteger,
        ((TABLENS,'structure-protected'), None): cnv_boolean,
        ((TABLENS,'style-name'), None): cnv_StyleNameRef,
        ((TABLENS,'table-background'), None): cnv_boolean,
        ((TABLENS,'table'), None): cnv_integer,
        ((TABLENS,'table-name'), None): cnv_string,
        ((TABLENS,'target-cell-address'), None): cnv_string,
        ((TABLENS,'target-range-address'), None): cnv_string,
        ((TABLENS,'title'), None): cnv_string,
        ((TABLENS,'track-changes'), None): cnv_boolean,
        ((TABLENS,'type'), None): cnv_string,
        ((TABLENS,'use-labels'), None): cnv_string,
        ((TABLENS,'use-regular-expressions'), None): cnv_boolean,
        ((TABLENS,'used-hierarchy'), None): cnv_integer,
        ((TABLENS,'user-name'), None): cnv_string,
        ((TABLENS,'value'), None): cnv_string,
        ((TABLENS,'value-type'), None): cnv_string,
        ((TABLENS,'visibility'), None): cnv_string,
        ((TEXTNS,'active'), None): cnv_boolean,
        ((TEXTNS,'address'), None): cnv_string,
        ((TEXTNS,'alphabetical-separators'), None): cnv_boolean,
        ((TEXTNS,'anchor-page-number'), None): cnv_positiveInteger,
        ((TEXTNS,'anchor-type'), None): cnv_string,
        ((TEXTNS,'animation'), None): cnv_string,
        ((TEXTNS,'animation-delay'), None): cnv_string,
        ((TEXTNS,'animation-direction'), None): cnv_string,
        ((TEXTNS,'animation-repeat'), None): cnv_string,
        ((TEXTNS,'animation-start-inside'), None): cnv_boolean,
        ((TEXTNS,'animation-steps'), None): cnv_length,
        ((TEXTNS,'animation-stop-inside'), None): cnv_boolean,
        ((TEXTNS,'annote'), None): cnv_string,
        ((TEXTNS,'author'), None): cnv_string,
        ((TEXTNS,'bibliography-data-field'), None): cnv_string,
        ((TEXTNS,'bibliography-type'), None): cnv_string,
        ((TEXTNS,'booktitle'), None): cnv_string,
        ((TEXTNS,'bullet-char'), None): cnv_string,
        ((TEXTNS,'bullet-relative-size'), None): cnv_string,
        ((TEXTNS,'c'), None): cnv_nonNegativeInteger,
        ((TEXTNS,'capitalize-entries'), None): cnv_boolean,
        ((TEXTNS,'caption-sequence-format'), None): cnv_string,
        ((TEXTNS,'caption-sequence-name'), None): cnv_string,
        ((TEXTNS,'change-id'), None): cnv_IDREF,
        ((TEXTNS,'chapter'), None): cnv_string,
        ((TEXTNS,'citation-body-style-name'), None): cnv_StyleNameRef,
        ((TEXTNS,'citation-style-name'), None): cnv_StyleNameRef,
        ((TEXTNS,'class-names'), None): cnv_NCNames,
        ((TEXTNS,'column-name'), None): cnv_string,
        ((TEXTNS,'combine-entries'), None): cnv_boolean,
        ((TEXTNS,'combine-entries-with-dash'), None): cnv_boolean,
        ((TEXTNS,'combine-entries-with-pp'), None): cnv_boolean,
        ((TEXTNS,'comma-separated'), None): cnv_boolean,
        ((TEXTNS,'cond-style-name'), None): cnv_StyleNameRef,
        ((TEXTNS,'condition'), None): cnv_formula,
        ((TEXTNS,'connection-name'), None): cnv_string,
        ((TEXTNS,'consecutive-numbering'), None): cnv_boolean,
        ((TEXTNS,'continue-numbering'), None): cnv_boolean,
        ((TEXTNS,'copy-outline-levels'), None): cnv_boolean,
        ((TEXTNS,'count-empty-lines'), None): cnv_boolean,
        ((TEXTNS,'count-in-text-boxes'), None): cnv_boolean,
        ((TEXTNS,'current-value'), None): cnv_boolean,
        ((TEXTNS,'custom1'), None): cnv_string,
        ((TEXTNS,'custom2'), None): cnv_string,
        ((TEXTNS,'custom3'), None): cnv_string,
        ((TEXTNS,'custom4'), None): cnv_string,
        ((TEXTNS,'custom5'), None): cnv_string,
        ((TEXTNS,'database-name'), None): cnv_string,
        ((TEXTNS,'date-adjust'), None): cnv_duration,
        ((TEXTNS,'date-value'), None): cnv_date,
        # ((TEXTNS,'date-value'), None): cnv_dateTime,
        ((TEXTNS,'default-style-name'), None): cnv_StyleNameRef,
        ((TEXTNS,'description'), None): cnv_string,
        ((TEXTNS,'display'), None): cnv_string,
        ((TEXTNS,'display-levels'), None): cnv_positiveInteger,
        ((TEXTNS,'display-outline-level'), None): cnv_nonNegativeInteger,
        ((TEXTNS,'dont-balance-text-columns'), None): cnv_boolean,
        ((TEXTNS,'duration'), None): cnv_duration,
        ((TEXTNS,'edition'), None): cnv_string,
        ((TEXTNS,'editor'), None): cnv_string,
        ((TEXTNS,'filter-name'), None): cnv_string,
        ((TEXTNS,'first-row-end-column'), None): cnv_string,
        ((TEXTNS,'first-row-start-column'), None): cnv_string,
        ((TEXTNS,'fixed'), None): cnv_boolean,
        ((TEXTNS,'footnotes-position'), None): cnv_string,
        ((TEXTNS,'formula'), None): cnv_formula,
        ((TEXTNS,'global'), None): cnv_boolean,
        ((TEXTNS,'howpublished'), None): cnv_string,
        ((TEXTNS,'id'), None): cnv_ID,
        # ((TEXTNS,'id'), None): cnv_string,
        ((TEXTNS,'identifier'), None): cnv_string,
        ((TEXTNS,'ignore-case'), None): cnv_boolean,
        ((TEXTNS,'increment'), None): cnv_nonNegativeInteger,
        ((TEXTNS,'index-name'), None): cnv_string,
        ((TEXTNS,'index-scope'), None): cnv_string,
        ((TEXTNS,'institution'), None): cnv_string,
        ((TEXTNS,'is-hidden'), None): cnv_boolean,
        ((TEXTNS,'is-list-header'), None): cnv_boolean,
        ((TEXTNS,'isbn'), None): cnv_string,
        ((TEXTNS,'issn'), None): cnv_string,
        ((TEXTNS,'journal'), None): cnv_string,
        ((TEXTNS,'key'), None): cnv_string,
        ((TEXTNS,'key1'), None): cnv_string,
        ((TEXTNS,'key1-phonetic'), None): cnv_string,
        ((TEXTNS,'key2'), None): cnv_string,
        ((TEXTNS,'key2-phonetic'), None): cnv_string,
        ((TEXTNS,'kind'), None): cnv_string,
        ((TEXTNS,'label'), None): cnv_string,
        ((TEXTNS,'last-row-end-column'), None): cnv_string,
        ((TEXTNS,'last-row-start-column'), None): cnv_string,
        ((TEXTNS,'level'), None): cnv_positiveInteger,
        ((TEXTNS,'line-break'), None): cnv_boolean,
        ((TEXTNS,'line-number'), None): cnv_string,
        ((TEXTNS,'main-entry'), None): cnv_boolean,
        ((TEXTNS,'main-entry-style-name'), None): cnv_StyleNameRef,
        ((TEXTNS,'master-page-name'), None): cnv_StyleNameRef,
        ((TEXTNS,'min-label-distance'), None): cnv_string,
        ((TEXTNS,'min-label-width'), None): cnv_string,
        ((TEXTNS,'month'), None): cnv_string,
        ((TEXTNS,'name'), None): cnv_string,
        ((TEXTNS,'note-class'), None): cnv_textnoteclass,
        ((TEXTNS,'note'), None): cnv_string,
        ((TEXTNS,'number'), None): cnv_string,
        ((TEXTNS,'number-lines'), None): cnv_boolean,
        ((TEXTNS,'number-position'), None): cnv_string,
        ((TEXTNS,'numbered-entries'), None): cnv_boolean,
        ((TEXTNS,'offset'), None): cnv_string,
        ((TEXTNS,'organizations'), None): cnv_string,
        ((TEXTNS,'outline-level'), None): cnv_string,
        ((TEXTNS,'page-adjust'), None): cnv_integer,
        ((TEXTNS,'pages'), None): cnv_string,
        ((TEXTNS,'paragraph-style-name'), None): cnv_StyleNameRef,
        ((TEXTNS,'placeholder-type'), None): cnv_string,
        ((TEXTNS,'prefix'), None): cnv_string,
        ((TEXTNS,'protected'), None): cnv_boolean,
        ((TEXTNS,'protection-key'), None): cnv_string,
        ((TEXTNS,'publisher'), None): cnv_string,
        ((TEXTNS,'ref-name'), None): cnv_string,
        ((TEXTNS,'reference-format'), None): cnv_string,
        ((TEXTNS,'relative-tab-stop-position'), None): cnv_boolean,
        ((TEXTNS,'report-type'), None): cnv_string,
        ((TEXTNS,'restart-numbering'), None): cnv_boolean,
        ((TEXTNS,'restart-on-page'), None): cnv_boolean,
        ((TEXTNS,'row-number'), None): cnv_nonNegativeInteger,
        ((TEXTNS,'school'), None): cnv_string,
        ((TEXTNS,'section-name'), None): cnv_string,
        ((TEXTNS,'select-page'), None): cnv_string,
        ((TEXTNS,'separation-character'), None): cnv_string,
        ((TEXTNS,'series'), None): cnv_string,
        ((TEXTNS,'sort-algorithm'), None): cnv_string,
        ((TEXTNS,'sort-ascending'), None): cnv_boolean,
        ((TEXTNS,'sort-by-position'), None): cnv_boolean,
        ((TEXTNS,'space-before'), None): cnv_string,
        ((TEXTNS,'start-numbering-at'), None): cnv_string,
        # ((TEXTNS,'start-value'), None): cnv_nonNegativeInteger,
        ((TEXTNS,'start-value'), None): cnv_positiveInteger,
        ((TEXTNS,'string-value'), None): cnv_string,
        ((TEXTNS,'string-value-if-false'), None): cnv_string,
        ((TEXTNS,'string-value-if-true'), None): cnv_string,
        ((TEXTNS,'string-value-phonetic'), None): cnv_string,
        ((TEXTNS,'style-name'), None): cnv_StyleNameRef,
        ((TEXTNS,'suffix'), None): cnv_string,
        ((TEXTNS,'tab-ref'), None): cnv_nonNegativeInteger,
        ((TEXTNS,'table-name'), None): cnv_string,
        ((TEXTNS,'table-type'), None): cnv_string,
        ((TEXTNS,'time-adjust'), None): cnv_duration,
        # ((TEXTNS,'time-value'), None): cnv_dateTime,
        ((TEXTNS,'time-value'), None): cnv_time,
        ((TEXTNS,'title'), None): cnv_string,
        ((TEXTNS,'track-changes'), None): cnv_boolean,
        ((TEXTNS,'url'), None): cnv_string,
        ((TEXTNS,'use-caption'), None): cnv_boolean,
        ((TEXTNS,'use-chart-objects'), None): cnv_boolean,
        ((TEXTNS,'use-draw-objects'), None): cnv_boolean,
        ((TEXTNS,'use-floating-frames'), None): cnv_boolean,
        ((TEXTNS,'use-graphics'), None): cnv_boolean,
        ((TEXTNS,'use-index-marks'), None): cnv_boolean,
        ((TEXTNS,'use-index-source-styles'), None): cnv_boolean,
        ((TEXTNS,'use-keys-as-entries'), None): cnv_boolean,
        ((TEXTNS,'use-math-objects'), None): cnv_boolean,
        ((TEXTNS,'use-objects'), None): cnv_boolean,
        ((TEXTNS,'use-other-objects'), None): cnv_boolean,
        ((TEXTNS,'use-outline-level'), None): cnv_boolean,
        ((TEXTNS,'use-soft-page-breaks'), None): cnv_boolean,
        ((TEXTNS,'use-spreadsheet-objects'), None): cnv_boolean,
        ((TEXTNS,'use-tables'), None): cnv_boolean,
        ((TEXTNS,'value'), None): cnv_nonNegativeInteger,
        ((TEXTNS,'visited-style-name'), None): cnv_StyleNameRef,
        ((TEXTNS,'volume'), None): cnv_string,
        ((TEXTNS,'year'), None): cnv_string,
        ((XFORMSNS,'bind'), None): cnv_string,
        ((XLINKNS,'actuate'), None): cnv_string,
        ((XLINKNS,'href'), None): cnv_anyURI,
        ((XLINKNS,'show'), None): cnv_xlinkshow,
        ((XLINKNS,'title'), None): cnv_string,
        ((XLINKNS,'type'), None): cnv_string,
}


class AttrConverters:
    def convert(self, attribute, value, element):
        ''' Based on the element, figures out how to check/convert the attribute value
            All values are converted to string
        '''
        conversion = attrconverters.get((attribute, element.qname), None)
        if conversion is not None:
            return conversion(attribute, value, element)
        else:
            conversion = attrconverters.get((attribute, None), None)
            if conversion is not None:
                return conversion(attribute, value, element)
        return str(value)
