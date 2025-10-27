#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract voxel count, volume and cluster count for the segmented brainstem and its subregions from (multiple) NIfTI files, corresponding to
differnt patients and containing MARS segmentation label-maps, and aggregate these statistics across files into a single table.
"""

import sys, os, glob, argparse, re, time
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import ndimage
import datetime

def isDir(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError("File path for directory has to be an existing directory. Please check: %s"%(path))
    else:
        return path
    
def extNii(path):
    if not path.endswith('.nii.gz') and not path.endswith('.nii'):
        raise argparse.ArgumentTypeError("File path for filename has to end with '.nii' or 'nii.gz'. Please check: %s"%(path))
    else:
        return path

def plausiblePath(path):
    if os.path.isdir(path):
        return path
    else:
        directory = os.path.dirname(path)
        base = os.path.basename(path)
        if len(base)>4 and base[-4:]=='.csv' and (len(directory)==0 or (len(directory)>1 and os.path.isdir(directory))):
            return path
        else:
            raise argparse.ArgumentTypeError("File path has to be an existing directory or a filename. If filename, it must end with '.csv' and can be optionally prepended by the path to an existing directory. Please check: %s"%(path))

license = 'https://github.com/miac-research/MARS-brainstem'
region = 'brainstem'
defaultFnOut = f"MARS-{region}_volumes_aggregated.csv"
defaultLabels = [1,2,3]
defaultNames = ['mesencephalon','pons','medulla oblongata']

def iniParser():
    parser = argparse.ArgumentParser(description="Extract voxel count, volume and cluster count for segmented regions from (multiple) NIfTI files containing MARS label-maps and aggregate these statistics across files into a single table. MARS label-maps will be globbed in the specified DIRECTORY using the specified FILENAME and DEPTH.",
                                     add_help=False,
                                     epilog=f'Notice: By using MARS, you agree to the software license terms described at "{license}"')
    group0 = parser.add_argument_group()
    group0.add_argument(dest="directory", metavar='DIRECTORY', type=isDir, help="path to directory containing MARS label-maps (NIfTI files). Will be used for globbing.")
    group0.add_argument("-f", dest="filename", type=extNii, default=f"*_{region}.nii.gz", help="name of MARS label-maps (default: '%(default)s'). Will be used for globbing and can contain wildcards ('*'). Requires extension '.nii[.gz]'.")
    group0.add_argument("-d", dest="depth", type=int, default=-1, help="depth for globbing (default: %(default)s, which means any depth).")
    group0.add_argument("-o", dest="output", metavar="OUTPUT-PATH", type=plausiblePath, default=defaultFnOut, help="path to write aggregated table to (default: %(default)s). If left at default or only a filename is provided, it will be saved into the DIRECTORY provided for globbing. If only a directory is provided, the default output-filename will be used.")    
    group0.add_argument("-l", metavar='LABEL', dest='labels', type=int, action="extend", nargs="+", default=None, help=f"labels; i.e., integer values used to label voxels in the label map corresponding to the regions of interest (default: {defaultLabels}).")
    group0.add_argument("-n", metavar='NAME', dest='names', type=str, action="extend", nargs="+", default=None, help=f"names of regions of interest, corresponding to the labels chosen with option '-l' (default: {defaultNames}; can be 'None' to exclude names from table).")
    group0.add_argument("-c", dest='connectivity', type=int, default=1, help="Connectivity criterium for determining connected voxels belonging to the same cluster (default: %(default)s); possible values 1 (voxels must touch via surfaces; produces the most clusters), 2 (touching edge is sufficient), and 3 (touching vertex is sufficient; produces the fewest clusers).")
    group0.add_argument("-x", dest="overwrite", action='store_true', help="allow overwriting output if existing. By default, already existing output will raise an error.")
    group0.add_argument("-t", dest="appendDate", choices=['date', 'time', 'datetime'], default=None, help="append output filename with current date, time, or datetime (default: %(default)s), formated as '*[_YYYY-MM-DD][_HHMMSS].csv'")
    group0.add_argument("-q", dest="verbose", action='store_false', help="quiet mode; only warnings and errors are displayed.")
    group0.add_argument("-h", action="help", help="show this help message and exit")
    group0.add_argument("-help","--help", action="help", help=argparse.SUPPRESS)
    return parser      


if __name__ == "__main__":
    
    start = time.time()
    parser = iniParser()
    if len(sys.argv)==1:
        parser.print_usage()
        print(f'\nRun "{os.path.basename(__file__)} -h" for detailed help\n'
              f'Notice: By using MARS, you agree to the software license terms described at "{license}"\n')
        parser.exit()
    
    args = parser.parse_args()


    if args.verbose:
        print("Running: " + " ".join([os.path.basename(sys.argv[0])]+sys.argv[1::]))
    
    # construct output filename path
    if os.path.isdir(args.output):
        fnOut = os.path.join(args.output, defaultFnOut)
    elif os.path.dirname(args.output)=='':
        fnOut = os.path.join(args.directory, args.output)
    else:
        fnOut = args.output
    
    # append date
    if args.appendDate:
        if args.appendDate == 'date':
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        elif args.appendDate == 'time':
            date = datetime.datetime.now().strftime("%H%M%S")
        elif args.appendDate == 'datetime': 
            date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        fnOut = re.sub(r'\.csv$', f'_{date}.csv', fnOut)

    
    # check existence of output file
    if os.path.isfile(fnOut):
        if not args.overwrite:
            print(f'\nERROR: Output file already exists:\n {fnOut}')
            print(" Use option '-x' to overwrite existing file or change output filepath with option '-o' or '-t datetime'.\n")
            sys.exit(1)
        else:
            print(f'\nWARNING: Output file already exists and will be overwritten:\n {fnOut}')
    
    # check correspondance of labels and names
    background = 0
    if args.labels is None:
        args.labels = defaultLabels
    else:
        assert len(set(args.labels)) == len(args.labels), 'ERROR: requested labels have to be unique! Please check: ' + str(args.labels)
        assert all([x!=background for x in args.labels]), f'ERROR: label {background} is reserved for background! Please check: ' + str(args.labels)
        assert all([x>=0 for x in args.labels]), f'ERROR: negative labels are not supported! Please check: ' + str(args.labels)
    if args.names is None:
        args.names = defaultNames
    if args.names[0] == 'None':
        args.names = None
    elif len(args.labels) != len(args.names):
        print('ERROR: number of labels and of names (options "-l" and "-n") has to be equal!\nPlease check:')
        print('  Labels:', args.labels)
        print('  Names:', args.names)
        sys.exit(1)

    # find all MARS label-maps
    if args.depth == -1:
        depth = '**'
        depthStr = 'any depth'
    else:
        depth = '/'.join(['*'] * args.depth)
        depthStr = f'search depth = {args.depth}'
    
    if args.verbose: print(f'\nSearching for MARS label-maps in "{args.directory}" at {depthStr} and with pattern "{args.filename}":')
    fnames = sorted(glob.glob(os.path.join(args.directory, depth, args.filename), recursive=True))
    fnamesRel = [re.sub('^'+re.escape(args.directory),'',fname) for fname in fnames]

    if len(fnames) == 0:
        print(f'\nNo MARS label-maps found in "{args.directory}" at {depthStr} and with pattern "{args.filename}"')
        sys.exit(1)

    # display found label-maps
    if args.verbose:
        nShow = min(10, len(fnames))
        if nShow == len(fnames):
            print(f'\nFound {len(fnames)} label-maps:')
            for i in range(nShow):
                print(' '+fnamesRel[i])
        else:
            cc = 5
            print(f'\nFound {len(fnames)} label-maps')
            print(f'Showing first and last {cc} files:')
            for i in range(cc):
                print(' '+fnamesRel[i])
            print(' ...')
            for i in range(cc):
                print(' '+fnamesRel[len(fnames)-cc+i])

    # prepare to extract stats for all labels, if multiple labels are requested
    if args.verbose: print()
    if len(args.labels)>1:
        insertTotal = True
        labelsOut = args.labels + [-1]
        if args.names is not None:
            if set(args.names) == set(defaultNames):
                namesOut = args.names + ['brainstem']
            else:
                namesOut = args.names + ['merged regions'] #-- there is a small chance that there is a conflict with names chosen by user, but the labels will always be unique
    else:
        insertTotal = False
        labelsOut = args.labels
        if args.names is not None:
            namesOut = args.names
    
    # loop over label map files and extract stats
    stats = list()
    warnings = list()
    addNewLine='\n' if args.verbose else ''
    for i, file in enumerate(fnames):
        
        if args.verbose: print(f"\rReading {i+1}. out of {len(fnames)} files ...", end='')

        try:
            nii = nib.load(file)
        except:
            # print(addNewLine+'  Error reading file:', fnamesRel[i])
            warnings.append([i+1, fnamesRel[i], 'error', 'file reading error', ''])
            continue
        
        if not np.issubdtype(nii.get_data_dtype(), np.integer):
            warnings.append([i+1, fnamesRel[i], 'warning', 'non-integer data type', nii.get_data_dtype()])

        # find unique labels and voxel counts
        map = nii.get_fdata()
        labels, voxels = np.unique(map, return_counts=True)
        if not np.all(labels == labels.astype('uint64')):
            # print(addNewLine+'  Error: not all detected labels are positiv whole numbers:', fnamesRel[i])
            warnings.append([i+1, fnamesRel[i], 'error', 'not all detected labels are positiv whole numbers', labels[labels != labels.astype('uint64')]])
            continue
        if len(labels)==0:
            # print(addNewLine+'  Error: no valid labels in:', fnamesRel[i])
            warnings.append([i+1, fnamesRel[i], 'error', 'no valid labels', setdiff])
            continue
        setdiff = list(set(labels[labels!=0]) - set(args.labels))
        if len(setdiff)>0:
            warnings.append([i+1, fnamesRel[i], 'warning', 'unexpected labels detected', setdiff])


        # for each requested label, keep the corresponding voxel count, and insert 0 if the label was not found
        voxels = np.asarray([voxels[label==labels][0] if label in labels else 0 for label in args.labels])
        
        # calculate volumes
        volumes = voxels * np.prod(nii.header.get_zooms()[0:3])
        
        # dtermine number of voxel clusters per label
        struct = ndimage.generate_binary_structure(map.ndim, args.connectivity)
        clusters = [0] * len(args.labels)
        for j, label in enumerate(args.labels):
            if voxels[j] > 0:
                _, clusters[j] = ndimage.label(map == label, struct)

        if insertTotal:
            voxels = np.append(voxels, np.sum(voxels))
            volumes = np.append(volumes, np.sum(volumes))
            if len(set(labels[labels!=0]) & set(args.labels)) > 1:
                _, clustersT = ndimage.label(np.isin(map, args.labels), struct)
                clusters = np.append(clusters, clustersT)
            else:
                clusters = np.append(clusters, np.sum(clusters))

        # append extracted stats to list
        if args.names is None:
            stats.append(pd.DataFrame({'file_index': i+1, 'file_path_relative': fnamesRel[i], 'file_path': file, 'label': labelsOut, 'voxels': voxels, 'volume': volumes, 'clusters': clusters}))
        else:
            stats.append(pd.DataFrame({'file_index': i+1, 'file_path_relative': fnamesRel[i], 'file_path': file, 'label': labelsOut, 'region': namesOut, 'voxels': voxels, 'volume': volumes, 'clusters': clusters}))
    
    
    if args.verbose: print('\nDone reading files!                                  ')

    # check warnings
    if len(warnings)>0:
        dfWarnings = pd.DataFrame(warnings, columns=['file_index','file_path_relative','code','description','additional_info'])

        # error if not any file could be read
        nErrors = sum(dfWarnings['code']=='error')
        if nErrors == len(fnames):
            print('\nERROR: none of the globbed files could be read!')
            sys.exit(1)

    # concat stats and display
    df = pd.concat(stats)
    df.reset_index(drop=True,inplace=True)
    if args.verbose:
        pd.set_option('display.max_rows', 20)
        print("\nResults table:")
        print(df.drop('file_path', axis=1))
    
    # Save table
    if args.verbose:
        print(f'\nWriting results table to:\n {fnOut}\n')
    df.replace(np.nan, '', inplace=True)
    df.drop('file_path_relative', axis=1).to_csv(fnOut, index=False)

    # display errors and warning
    if len(warnings)>0:
        if any(dfWarnings['code']=='warning') and nErrors>0:
            print('\nERRORS and WARNINGS per file:')
        elif nErrors>0:
            print('\nERRORS per file:')
        else:
            print('\nWARNINGS per file:')
        
        print(dfWarnings)
        
        if nErrors>0:
            print(f'\nWARNING: {nErrors} files were excluded due to error!')
    
    if args.verbose:
        elapsed = time.time() - start
        print('Total duration: {:02.0f}:{:02.0f}\n'.format(elapsed//60, elapsed%60))
