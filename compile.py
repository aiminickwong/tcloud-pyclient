import os
import py_compile
import sys
from twindow.common import utils
import datetime

ROOT = os.path.dirname(os.path.realpath(__file__))

def compile_src(version):
    build_version(version)
    if os.path.exists(ROOT):
        for path,_,f in os.walk(ROOT):
            for f_name in f:
                if f_name.endswith('py'):
                    py_compile.compile(path+'/'+f_name)
        

def build_version(version):
    filename = os.path.join(ROOT,'twindow','__init__.py')
    utils.dict_updating(filename,dict(BUILD_VERSION='\"build %s\"' % version ))

if __name__ == '__main__':
    version = sys.argv[1]
    compile_src(version)
