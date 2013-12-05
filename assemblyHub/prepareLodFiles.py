#!/usr/bin/env python

#Copyright (C) 2013 by Ngan Nguyen
#
#Released under the MIT license, see LICENSE.txt

"""Take care of Level-of-detail files
"""

import os
from sonLib.bioio import system  
from optparse import OptionGroup

def fixLodFilePath(lodtxtfile, localHalfile, outdir):
    #fix the path of the original hal file to point to the created
    #link relative to the output directory
    relPath = os.path.relpath(localHalfile, start=outdir)
    lodTxtBuf = ''
    for line in open(lodtxtfile):
        tokens = line.split()
        if len(tokens) == 2 and tokens[0] == '0':
            lodTxtBuf += '0 %s\n' % relPath
        else:
            lodTxtBuf += line
    with open(lodtxtfile, 'w') as lodFile:
        lodFile.write(lodTxtBuf)
    
def getLodFiles(localHalfile, options, outdir):
    lodtxtfile = os.path.join(outdir, "lod.txt") #outdir/lod.txt
    loddir = os.path.join(outdir, "lod") #outdir/lod
    if options.lodtxtfile and options.loddir: #if lod files were given, then just make soft links to them
        if os.path.exists(lodtxtfile):
            if os.path.abspath(lodtxtfile) != os.path.abspath(options.lodtxtfile):
                system("rm %s" %lodtxtfile)
                system("ln -s %s %s" %(os.path.abspath(options.lodtxtfile), lodtxtfile))
        else:
            system("ln -s %s %s" %(os.path.abspath(options.lodtxtfile), lodtxtfile))

        if os.path.exists(loddir):
            if os.path.abspath(loddir) != os.path.abspath(options.loddir):
                if os.path.islink(loddir):
                    system("rm %s" %loddir)
                else:
                    system("rm -Rf %s" %loddir)
                loddir = os.path.join(outdir, os.path.basename(options.loddir))
                system("ln -s %s %s" %(os.path.abspath(options.loddir), loddir))
        else:
            system("ln -s %s %s" %(os.path.abspath(options.loddir), loddir))
    else: #if lod files were not given, create them using halLodInterpolate.py
        system("halLodInterpolate.py %s %s --outHalDir %s %s" %(localHalfile, lodtxtfile, loddir, options.lodOpts))
        fixLodFilePath(lodtxtfile, localHalfile, outdir)
    return lodtxtfile, loddir

def getLod(options, localHalfile, outdir):
    #Create lod files if useLod is specified
    lodtxtfile = ''
    loddir = ''
    options.lodOpts = ''
    if options.lodMaxBlock is not None:
        options.lodOpts += '--maxBlock %d ' % options.lodMaxBlock
    if options.lodScale is not None:
        options.lodOpts += '--scale %f ' % options.lodScale
    if options.lodMaxDNA is not None:
        options.lodOpts += '--maxDNA %d ' % options.lodMaxDNA
    if options.lodInMemory is True:
        options.lodOpts += '--inMemory '
    if options.lodNumProc is not None:
        options.lodOpts += '--numProc %d ' % options.lodNumProc
    if options.lodMinSeqFrac is not None:
        options.lodOpts += '--minSeqFrac %f ' % options.lodMinSeqFrac
    if options.lodChunk is not None:
        options.lodOpts += '--chunk %d ' % options.lodChunk
    if len(options.lodOpts) > 0:
        options.lod = True
    if options.lod:
        lodtxtfile, loddir = getLodFiles(localHalfile, options, outdir)
    return lodtxtfile, loddir

def addLodOptions(parser):
    group = OptionGroup(parser, "LEVEL OF DETAILS", "Level-of-detail (LOD) options.")
    group.add_option('--lod', dest='lod', action="store_true", default=False, help='If specified, create "level of detail" (lod) hal files and will put the lod.txt at the bigUrl instead of the original hal file. Default=%default')
    group.add_option('--lodTxtFile', dest='lodtxtfile', help='"hal Level of detail" lod text file. If specified, will put this at the bigUrl instead of the hal file. Default=%default')
    group.add_option('--lodDir', dest='loddir', help='"hal Level of detail" lod dir. If specified, will put this at the bigUrl instead of the hal file. Default=%default')
    group.add_option('--lodMaxBlock', dest='lodMaxBlock', type='int', help='Maximum number of blocks to display in a hal level of detail. Default=%default', default=None)
    group.add_option('--lodScale', dest='lodScale', type='float', help='Scaling factor between two successive levels of detail. Default=%default.', default=None)
    group.add_option('--lodMaxDNA', dest='lodMaxDNA', type='int', help='Maximum query length that will such that its hal level of detail will contain nucleotide information. Default=%default.', default=None)
    group.add_option('--lodInMemory', dest='lodInMemory', action='store_true', help='Load entire hal file into memory when generating levels of detail instead of using hdf5 cache. Default=%default.', default=False)
    group.add_option('--lodNumProc', dest='lodNumProc', type='int', help='Number of levels of detail to generate concurrently in parallel processes', default=None)
    group.add_option('--lodMinSeqFrac', dest='lodMinSeqFrac', type='float', help='Minumum sequence length to sample as fraction of step size for level of detail generation: ie sequences with length <= floor(minSeqFrac * step) are ignored. Use default from halLodExtract if not set.', default=None)
    group.add_option('--lodChunk', dest='lodChunk', type='int', help='HDF5 chunk size for generated levels of detail.', default=None)
    parser.add_option_group(group)
