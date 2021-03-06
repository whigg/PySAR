#!/usr/bin/env python3
############################################################
# Program is part of PySAR                                 #
# Copyright(c) 2013-2018, Zhang Yunjun, Heresh Fattahi     #
# Author:  Zhang Yunjun, Heresh Fattahi                    #
############################################################

import os
import sys
import time
import argparse
import numpy as np
from pysar.objects import timeseries, giantTimeseries
from pysar.utils import readfile, writefile


#####################################################################################
EXAMPLE = """example:
  diff.py  velocity.h5    velocity_demErr.h5
  diff.py  timeseries.h5  ECMWF.h5  -o timeseries_ECMWF.h5
  diff.py  timeseries.h5  ECMWF.h5  -o timeseries_ECMWF.h5  --force
  diff.py  timeseries_ECMWF_demErr_ramp.h5  ../GIANT/Stack/LS-PARAMS.h5 -o pysar_giant.h5

  # multiple files
  diff.py  waterMask.h5  maskSantiago.h5  maskFernandina.h5  -o maskIsabela.h5
"""


def create_parser():
    parser = argparse.ArgumentParser(description='Generates the difference of two input files.',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=EXAMPLE)

    parser.add_argument('file1', help='file to be substracted.')
    parser.add_argument('file2', nargs='+', help='file used to substract')
    parser.add_argument('-o', '--output', dest='outfile',
                        help='output file name, default is file1_diff_file2.h5')
    parser.add_argument('--force', action='store_true',
                        help='Enforce the differencing for the shared dates only for time-series files')
    return parser


def cmd_line_parse(iargs=None):
    parser = create_parser()
    inps = parser.parse_args(args=iargs)
    return inps


#####################################################################################
def _check_reference(atr1, atr2):
    if atr1['REF_DATE'] == atr2['REF_DATE']:
        ref_date = None
    else:
        ref_date = atr1['REF_DATE']
        print('consider different reference date')

    ref_y = int(atr1['REF_Y'])
    ref_x = int(atr1['REF_X'])
    if ref_y == int(atr2['REF_Y']) and ref_x == int(atr2['REF_X']):
        ref_y = None
        ref_x = None
    else:
        print('consider different reference pixel')
    return ref_date, ref_y, ref_x


def diff_file(file1, file2, outFile=None, force=False):
    """Subtraction/difference of two input files"""
    if not outFile:
        fbase, fext = os.path.splitext(file1)
        if len(file2) > 1:
            raise ValueError('Output file name is needed for more than 2 files input.')
        outFile = '{}_diff_{}{}'.format(fbase, os.path.splitext(os.path.basename(file2[0]))[0], fext)
    print('{} - {} --> {}'.format(file1, file2, outFile))

    # Read basic info
    atr1 = readfile.read_attribute(file1)
    k1 = atr1['FILE_TYPE']
    atr2 = readfile.read_attribute(file2[0])
    k2 = atr2['FILE_TYPE']
    print('input files are: {} and {}'.format(k1, k2))

    if k1 == 'timeseries':
        if k2 not in ['timeseries', 'giantTimeseries']:
            raise Exception('Input multiple dataset files are not the same file type!')
        if len(file2) > 1:
            raise Exception(('Only 2 files substraction is supported for time series file,'
                             ' {} input.'.format(len(file2)+1)))

        obj1 = timeseries(file1)
        obj1.open()
        if k2 == 'timeseries':
            obj2 = timeseries(file2[0])
            unit_fac = 1.
        elif k2 == 'giantTimeseries':
            obj2 = giantTimeseries(file2[0])
            unit_fac = 0.001
        obj2.open()
        ref_date, ref_y, ref_x = _check_reference(obj1.metadata, obj2.metadata)

        # check dates shared by two timeseries files
        dateListShared = [i for i in obj1.dateList if i in obj2.dateList]
        dateShared = np.ones((obj1.numDate), dtype=np.bool_)
        if dateListShared != obj1.dateList:
            print('WARNING: {} does not contain all dates in {}'.format(file2, file1))
            if force:
                dateExcluded = list(set(obj1.dateList) - set(dateListShared))
                print('Continue and enforce the differencing for their shared dates only.')
                print('\twith following dates are ignored for differencing:\n{}'.format(dateExcluded))
                dateShared[np.array([obj1.dateList.index(i) for i in dateExcluded])] = 0
            else:
                raise Exception('To enforce the differencing anyway, use --force option.')

        # consider different reference_date/pixel
        data2 = readfile.read(file2[0], datasetName=dateListShared)[0] * unit_fac
        if ref_date:
            data2 -= np.tile(data2[obj2.dateList.index(ref_date), :, :],
                             (data2.shape[0], 1, 1))
        if ref_y and ref_x:
            data2 -= np.tile(data2[:, ref_y, ref_x].reshape(-1, 1, 1),
                             (1, data2.shape[1], data2.shape[2]))

        data = obj1.read()
        mask = data == 0.
        data[dateShared] -= data2
        data[mask] = 0.               # Do not change zero phase value
        writefile.write(data, out_file=outFile, ref_file=file1)

    # Sing dataset file
    else:
        data1 = readfile.read(file1)[0]
        data = np.array(data1, data1.dtype)
        for fname in file2:
            data2 = readfile.read(fname)[0]
            data = np.array(data, dtype=np.float32) - np.array(data2, dtype=np.float32)
            data = np.array(data, data1.dtype)
        print('writing >>> '+outFile)
        writefile.write(data, out_file=outFile, metadata=atr1)

    return outFile


def main(iargs=None):
    inps = cmd_line_parse(iargs)
    start_time = time.time()

    inps.outfile = diff_file(inps.file1, inps.file2, inps.outfile, force=inps.force)

    m, s = divmod(time.time()-start_time, 60)
    #print('time used: {:02.0f} mins {:02.1f} secs'.format(m, s))
    return inps.outfile


#####################################################################################
if __name__ == '__main__':
    main()
