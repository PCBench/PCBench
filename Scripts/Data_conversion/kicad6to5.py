import json
import os
import sys
sys.path.append("..")
from Data_extraction.thirdparty.kicad_parser.sexp_parser import *

class Skip(SexpParser):
    def _export(self, out,prefix='', indent='  '):
        pass

class KicadPCB_gr_text(SexpParser):
    __slots__ = ()
    _default_bools = 'hide'
    _parse_tstamp = Skip

class KicadPCB_drill(SexpParser):
    __slots__ = ()
    _default_bools = 'oval'

class KicadPCB_pad(SexpParser):
    __slots__ = ()
    _parse1_drill = KicadPCB_drill

    def _parse1_layers(self,data):
        if not isinstance(data,list) or len(data)<3:
            raise ValueError('expects list of more than 2 element')
        return Sexp(data[1],data[2:],data[0])
    


class ExportSexpParser(SexpParser):
    def _export(self, out,prefix='', indent='  '):
        self._export_key(out, prefix, indent)
        self._export_value(out, prefix, indent)
    def _export_key(self, out, prefix='', indent='  ', ):
        out.write('\n{}({}'.format(prefix,"page"))
    def _export_value(self, out, prefix='', indent='  ', ):
        prefix += indent
        p = getattr(self._value,'_export',None)
        if p is not None:
            p(out,prefix,indent)
        elif isinstance(self._value,string_types) or \
                not hasattr(self._value,'__iter__'):
            out.write(' {}'.format(self._value))
        else:
            for v in (self._value if isinstance(self._value,list) \
                    else self._value.values()):
                self._exportValue(out,v,prefix,indent)
        out.write(')')


class Stroke(SexpParser):
    _defaults = ('width')
    def _export(self, out, prefix='', indent='  '):
        self.width._export(out, prefix, indent)

class FpText(SexpParser):
    _parse_tstamp = Skip
    _parse_locked = Skip

class FpLine(SexpParser):
    _parse_tstamp = Skip
    _parse_stroke = Stroke

class EndWithAngle(SexpParser):
    def _export(self, out, prefix='', indent='  '):
        super()._export(out, prefix, indent)
        out.write("(angle 0)")

class FpArc(SexpParser):
    _parse_tstamp = Skip
    _parse_stroke = Stroke
    _parse_end = EndWithAngle
    _parse_mid = Skip

class FpCircle(SexpParser):
    _parse_tstamp = Skip
    _parse_stroke = Stroke
    _parse_fill = Skip

class FpPoly(SexpParser):
    _parse_fill = Skip
    _parse_stroke = Stroke

class Pad(SexpParser):
    _parse_tstamp = Skip
    _parse_locked = Skip
    _parse_pinfunction = Skip
    _parse_pintype = Skip
    _parse_primitives = Skip
    _parse_thermal_bridge_angle = Skip

class Model(SexpParser):
    _parse_hide = Skip

class KicadPCB_footprint(ExportSexpParser):
    __slots__ = ()
    _default_bools = 'locked'
    _parse_fp_text = FpText
    _parse_fp_line = FpLine
    _parse_fp_arc = FpArc
    _parse_fp_circle = FpCircle
    _parse_fp_poly = FpPoly
    _parse_fp_rect = Skip
    _parse_pad = Pad
    _parse_attr = Skip
    _parse_property = Skip
    _parse_group = Skip
    _parse_model = Model
    _parse_zone = Skip

    def _export_key(self, out, prefix='', indent='  '):
        out.write('\n{}({}'.format(prefix, "module"))



class ProxySexpParser(SexpParser):
    _proxy = SexpParser(parseSexp('(not implemented)'))
    def _export(self, out, prefix='', indent='  '):
        self._proxy._export(out, prefix, indent)
class Paper(ProxySexpParser):
    # A5 is not a valid type in Kicad5
    _proxy = SexpParser(parseSexp('(page "A4")'))
    # def _export_key(self, out, prefix='', indent='  '):
    #     out.write('\n{}({}'.format(prefix,"page"))

class General(ExportSexpParser):
    def __init__(self, data):
        super().__init__(data)
        self._proxy = SexpParser(parseSexp("""
        (general
            (thickness 1.6)
            (drawings 15)
            (tracks 417)
            (zones 0)
            (modules 52)
            (nets 44)
          )
        """))
    def _export(self, out, prefix='', indent='  '):
        self._proxy._export(out, prefix, indent)


class Layers(ExportSexpParser):
    def __init__(self, data):
        super().__init__(data)
        self._proxy = SexpParser(parseSexp("""
        (layers
            (0 F.Cu signal)
            (31 B.Cu signal hide)
            (32 B.Adhes user)
            (33 F.Adhes user)
            (34 B.Paste user)
            (35 F.Paste user)
            (36 B.SilkS user)
            (37 F.SilkS user)
            (38 B.Mask user)
            (39 F.Mask user)
            (40 Dwgs.User user)
            (41 Cmts.User user)
            (42 Eco1.User user)
            (43 Eco2.User user)
            (44 Edge.Cuts user)
            (45 Margin user)
            (46 B.CrtYd user)
            (47 F.CrtYd user)
            (48 B.Fab user)
            (49 F.Fab user)
          )
          """))
    def _export(self, out, prefix='', indent='  '):
        self._proxy._export(out, prefix, indent)



class Generator(ExportSexpParser):
    def _export(self, out, prefix='', indent='  '):
        out.write('(host pcbnew "(5.1.4-0-10_14)")')
class Version(SexpParser):
    def _export(self, out, prefix='', indent='  '):
        out.write("(version 20171130)")


class FilledPolyGon(SexpParser):
    _parse_layer = Skip
    _parse_island = Skip

class Pts(SexpParser):
    _parse_arc = Skip

class Polygon(SexpParser):
    _parse_pts = Pts

class Zone(SexpParser):
    _parse_filled_areas_thickness = Skip
    _parse_filled_polygon = FilledPolyGon
    # skipping the fill instead
    _parse_fill = Skip
    _parse_polygon = Polygon
    _parse_locked = Skip
    _parse_name = Skip
    _parse_keepout = Skip

class Setup(SexpParser):
    _parse_stackup = Skip

class Via(SexpParser):
    _parse_free = Skip
    _parse_locked = Skip

class Segment(SexpParser):
    _parse_locked = Skip

class KicadPCB(SexpParser):
    """Read a kicad6 pcb file and export to kicad5."""
    _parse_footprint = KicadPCB_footprint
    _parse_paper = Paper
    _parse_generator = Generator
    _parse_general = General
    _parse_version = Version
    _parse1_layers = Layers
    _parse_gr_line = FpLine
    _parse_gr_arc = FpArc
    _parse_gr_text = FpText
    _parse_gr_circle = FpCircle
    _parse_gr_rect = Skip
    _parse_gr_poly = FpPoly
    _parse_zone = Zone
    _parse_dimension = Skip
    _parse_setup = Setup
    _parse_via = Via
    _parse_arc = Skip
    _parse_zone = Zone
    _parse_group = Skip
    _parse_segment = Segment

    def export(self, out, indent='  '):
        exportSexp(self,out,'',indent)

    def getError(self):
        return getSexpError(self)

    @staticmethod
    def load(filename):
        ret = None
        with open(filename,'r') as f:               # v5 or v6 
            ret = KicadPCB(parseSexp(f.read()))
            version = ret.version
        return ret

if __name__ == '__main__':
    KICAD6_DIR = "../../PCBs_KiCAD6"
    for dir in os.listdir(KICAD6_DIR):
        if not os.path.isdir(os.path.join(KICAD6_DIR, dir)):
            print("Not a directory", os.path.join(KICAD6_DIR, dir))
            continue
        fname = os.path.join(KICAD6_DIR, dir, "raw.kicad_pcb")
        out_fname = fname.split("raw")[0] + "export5.kicad_pcb"
        if True or not os.path.exists(out_fname):
            print("processing", fname)
            pcb = KicadPCB.load(fname)
            pcb.export(out_fname)