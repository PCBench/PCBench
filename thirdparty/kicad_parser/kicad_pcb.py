'''
``kicad_pcb`` parser using `sexp_parser.SexpParser`

The parser `KicadPCB` demonstrates the usage of a more general S-expression
parser of class `sexp_parser.SexpParser`. Check out the source to see how easy
it is to implement a parser in an almost declarative way.

A usage demonstration is available in `test.py`
'''

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
        with open(filename,'r') as f:               # v5 or v6 
            ret = KicadPCB(parseSexp(f.read()))
            version = ret.version
        if (version) > 20211000:  # if v6, extract net_class from project file. 
            circuitname = filename[0:len(filename)-10]   # assumes project file and pcb file have same name & in same dir
            try:
                with open(circuitname+'.kicad_pro') as f:
                    ret.net_class = json.load(f)['net_settings']['classes']
                    ret.V6ToV5Naming()
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

    def V6ToV5Naming(self):
        for net_class in self.net_class[0]:     # TODO: net_class is currently singular instead of plural. Why?
                                                # Also, is it just me or is the KicadPCB class miserable?
            net_class['via_dia'] = net_class['via_diameter']
            net_class['trace_width'] = net_class['wire_width']
            net_class['uvia_dia'] = net_class['microvia_diameter']
            net_class['uvia_drill'] = net_class['microvia_drill']
            if "nets" in net_class:
                net_class['add_net'] = net_class['nets']
                del net_class['nets']
            del net_class['wire_width']
            del net_class['via_diameter']
            del net_class['microvia_diameter']
            del net_class['microvia_drill']
        tmp = self.net_class[0]
        del self.net_class[0]
        for net_class in tmp:
            self.net_class = net_class