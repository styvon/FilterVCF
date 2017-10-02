import sys
import os.path
import itertools
import gzip

def _getHeader(filename):
	# Get header (variable name line) in vcf file
    out = []
    start = -1 # row id where seq data starts
    with gzip.open(filename,'rt') as f:
        for i, line in enumerate(f):
            if line.startswith( '#CHROM' ):
                out = str.split(line)
                start = i
                break           
    return start, out

def _getFilter(filename):
	# get effective sample ids from .ped file
    out = ['#CHROM','POS','ID','REF','ALT','QUAL','FILTER','INFO','FORMAT']
    with open(filename) as f:
        for line in f:
            if line.startswith( '#' ):
                continue
            else:
                out.append(str.split(line)[0])
    #filter.extend(('#CHROM','POS','ID','REF','ALT','QUAL','FILTER','INFO','FORMAT'))
    return out

def _getColumnId(filename_d, filename_f):
	# Get column ids (of required vcf variables + of sample ids that exist in Filter) that will remain
    start, header = _getHeader(filename_d)
    filter = _getFilter(filename_f)

    idx = []
    
    for i,var in enumerate(header):
        if var in filter:
            idx.append(i)

    return start, idx

def filterVCF(filename_d, filename_f, dir_output):
	# Filter vcf file columns so that only sample ids existing in Filter remain
    if not os.path.isfile(filename_d):
        raise ValueError('{} is not a valid directory'.format(filename_d))
    if not os.path.isfile(filename_f):
        raise ValueError('{} is not a valid directory'.format(filename_f))

    start, idx = _getColumnId(filename_d, filename_f)
    
    print('writing data to {}...'.format(dir_output))
    if os.path.isdir(dir_output)==False:
        raise ValueError('{} is not a directory'.format(dir_output))
    if dir_output.endswith('/')==False:
        dir_output = dir_output+'//'
    
    outfilename = 'filtered_'+str.split(filename_d,'/')[-1]
    with gzip.open(filename_d,'rt') as i, gzip.open(dir_output+outfilename,'wt') as o:
        for it, line in enumerate(i):
            if it < start:
                o.writelines(line + '\n')
                #o.write(line + '\n')
            else:
                contents = []
                for id in idx:
                    contents.append(str.split(line)[id])
                o.writelines('\t'.join(str(c) for c in contents) + '\n')
                #o.writelines('\t'.join(str(l) for l in str.split(line)[idx]) + '\n')
                #o.write('\t'.join(str(l) for l in str.split(line)[idx]) + '\n')

    print('file created:{}{}'.format(dir_output,outfilename))