############################################################
# Program is part of PySAR                                 #
# Copyright(c) 2013-2018, Zhang Yunjun, Heresh Fattahi     #
# Author:  Zhang Yunjun, Heresh Fattahi, 2018 Mar          #
############################################################


from __future__ import print_function


import sys
import os
pysar_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, pysar_path)
sys.path.insert(1, os.path.join(pysar_path, 'defaults'))
sys.path.insert(1, os.path.join(pysar_path, 'objects'))
sys.path.insert(1, os.path.join(pysar_path, 'simulation'))
sys.path.insert(1, os.path.join(pysar_path, 'utils'))

from pysar.version import *
__version__ = release_version

try:
    os.environ['PYSAR_HOME']
except KeyError:
    print('Using default PySAR Path: %s' % (pysar_path))
    os.environ['PYSAR_HOME'] = pysar_path


# PySAR modules listed by relative dependecies:
# 0. Independent modules:
# pysar.objects.pysarobj
# pysar.objects.sensor
# pysar.defaults.auto_path
# pysar.utils.writefile
# pysar.utils.datetime
#
# Level 1 dependent modules (depends on Level 0):
# pysar.utils.readfile
# pysar.utils.network
#
# Level 2 dependent modules (depends on Level 0,1):
# pysar.utils.utils
#
# Level 3 dependent modules (depends on Level 0,1,2):
# pysar.objects.insarobj
# pysar.utils.plot
#
