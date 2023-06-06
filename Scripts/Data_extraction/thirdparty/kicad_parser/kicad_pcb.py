'''
``kicad_pcb`` parser using `sexp_parser.SexpParser`

The parser `KicadPCB` demonstrates the usage of a more general S-expression
parser of class `sexp_parser.SexpParser`. Check out the source to see how easy
it is to implement a parser in an almost declarative way.

A usage demonstration is available in `test.py`
'''

import collections
import json
from .sexp_parser import *

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
                'segment',
                'arc',
                'via',
                ['module'] + _module,
                ['footprint'] + _module,
                ('zone',
                    'filled_polygon'))

    _alias_keys = {'footprint' : 'module'}
    _parse_module = KicadPCB_module
    _parse_footprint = KicadPCB_module
    _parse_gr_text = KicadPCB_gr_text

    def export(self, out, indent='  '):
        exportSexp(self,out,'',indent)

    def getError(self):
        return getSexpError(self)

    @staticmethod
    def load(filename):
        ret = None
        with open(filename,'r', encoding='utf-8') as f:               # v5 or v6 
            ret = KicadPCB(parseSexp(f.read()))
            version = ret.version
        if (version) > 20211000:  # if v6, extract net_class from project file. 
            circuitname = filename[0:len(filename)-10]   # assumes project file and pcb file have same name & in same dir
            try:
                with open(circuitname+'.kicad_pro') as f:
                    net_settings = json.load(f)['net_settings']
                    for net_class in net_settings['classes']:
                         net_class = V6ToV5Naming(net_class)
                         ret.net_class._value.append(Sexp('net_class', collections.OrderedDict(net_class)))
                    
                    # In v6, classes other than Default have lists of member nets in kicad_pro
                    # which we can convert to the add_net Sexp structure in V6ToV5Naming
                    # afterward, all remaining nets (found in ret.net) are put into the add_net Sexp structure for
                    # the Default net_class.
                    for nc in ret.net_class:
                        if nc[0] == "Default":
                            for net in ret.net:
                                if net[1] not in CLASSED_NETS:
                                    nc['add_net'].append(Sexp('add_net',net[1]))
            except FileNotFoundError:
                print(f"Warrning: kicad_pcb.py detected a kicad v6 file format, but\
                    \n could not find {circuitname}.kicad_pro in the directory of {circuitname}.kicad_pcb file\
                    Returning KicadPCB without getting .net_class attribute from project file")
            except KeyError:
                print(f"Warning: {circuitname}.kicad_pro did not contain key 'net_settings'\
                    \nand/or its subkey 'classes'\
                    Returning KicadPCB without getting .net_class attribute from project file")
        if len(ret.net_class) == 0:
            print(f"Warning: {filename} has been initialized with an empty net_class attribute")
        
        return ret

CLASSED_NETS = set()

def V6ToV5Naming(dict):
    dict = collections.OrderedDict(dict)
    dict[0] = dict['name']
    dict['via_dia'] = dict['via_diameter']
    dict['trace_width'] = dict['wire_width']
    del dict['wire_width']
    del dict['via_diameter']


    dict['add_net'] = list()    # The v5 net-to-class structure the Sexp: (net_class {name} {desc} (add_net {name})...)
                                # which converts to a List of add_net Sexp Objs with {name} values
    for k in dict.keys():
        if k == "nets":
            for item in dict[k]:
                dict["add_net"].append(Sexp("add_net", f'"{item}"'))    # Quotes preserved for Sexp
                CLASSED_NETS.add(item)
        dict[k] = Sexp(k, dict[k])
    return dict
