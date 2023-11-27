'''
``kicad_pcb`` parser using `sexp_parser.SexpParser`

The parser `KicadPCB` demonstrates the usage of a more general S-expression
parser of class `sexp_parser.SexpParser`. Check out the source to see how easy
it is to implement a parser in an almost declarative way.

A usage demonstration is available in `test.py`
'''
import json
import collections

try:
    from .sexp_parser import *
except ImportError:
    from sexp_parser.sexp_parser import *

__author__ = "Zheng, Lei"
__copyright__ = "Copyright 2016, Zheng, Lei"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "realthunder.dev@gmail.com"
__status__ = "Prototype"


class KicadPCB_gr_text(SexpParser):
    __slots__ = ()
    _default_bools = 'hide'


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


class KicadPCB_module(SexpParser):
    __slots__ = ()
    _default_bools = 'locked'
    _parse_fp_text = KicadPCB_gr_text
    _parse_pad = KicadPCB_pad


class KicadPCB(SexpParser):

    # To make sure the following key exists, and is of type SexpList
    _module = ['fp_text',
               'fp_circle',
               'fp_arc',
               'pad',
               'model']

    _defaults =('net',
                ('net_class',
                    'add_net'),
                'dimension',
                'gr_text',
                'gr_line',
                'gr_circle',
                'gr_arc',
                'gr_curve',
                'gr_poly',
                'segment',
                'arc',
                'via',
                'module',
                'footprint',
                ['module'] + _module,
                ['footprint'] + _module,
                ('zone',
                    'filled_polygon'))

    # _alias_keys = {'footprint' : 'module'}
    _parse_module = KicadPCB_module
    _parse_footprint = KicadPCB_module
    _parse_gr_text = KicadPCB_gr_text

    def export(self, out, indent='  '):
        exportSexp(self,out,'',indent)

    def getError(self):
        return getSexpError(self)

    # @staticmethod
    # def load(filename, quote_no_parse=None):
    #     with open(filename,'r') as f:
    #         return KicadPCB(parseSexp(f.read(), quote_no_parse))
    
    @staticmethod
    def load(filename):
        ret = None
        with open(filename,'r', encoding='utf-8') as f:               # v5 or v6 
            ret = KicadPCB(parseSexp(f.read()))
            version = ret.version
        if (version) > 20211000:  # if v6, extract net_class from project file. 
            circuitname = filename[0:len(filename)-10]   # assumes project file and pcb file have same name & in same dir
            net_classes = None
            try:
                with open(circuitname+'.kicad_pro') as f:
                    net_settings = json.load(f)['net_settings']
                    net_classes = get_netclass(net_settings, "v7")
                    
            except FileNotFoundError:
                print(f"Warrning: kicad_pcb.py detected a kicad v6 file format, but\
                    \n could not find {circuitname}.kicad_pro in the directory of {circuitname}.kicad_pcb file\
                    Returning KicadPCB without getting .net_class attribute from project file")

            return ret, net_classes
        return ret, get_netclass(ret["net_class"], "v5")

def get_netclass(classes, kicad_version="v5"):
    net_classes = {}
    if kicad_version == "v5":
        for net_class in classes:
            nc_dict = {}
            nc_dict['width'] = net_class.trace_width
            nc_dict['clearance'] = net_class.clearance
            nc_dict['via_diameter'] = net_class.via_dia
            nc_dict['net_names'] = list()
            for i in range(len(net_class.add_net)):
                nc_dict["net_names"].append(net_class.add_net[i])
            net_classes[net_class[0]] = nc_dict
    elif kicad_version == "v7":
        for net_class in classes["classes"]:
            nc_dict = {}
            nc_dict['width'] = net_class["track_width"]
            nc_dict['clearance'] = net_class["clearance"]
            nc_dict['via_diameter'] = net_class["via_diameter"]
            nc_dict['net_names'] = list()
            net_classes[net_class["name"]] = nc_dict
        if "netclass_patterns" in classes:
            for pattern in classes["netclass_patterns"]:
                net_classes[pattern["netclass"]]["net_names"].append(f'"{pattern["pattern"]}"')
    return net_classes