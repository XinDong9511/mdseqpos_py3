# Time-stamp: <2011-07-21 17:45:07 Tao Liu>

"""Module Description

Copyright (c) 2010,2011 Tao Liu <taoliu@jimmy.harvard.edu>

This code is free software; you can redistribute it and/or modify it
under the terms of the BSD License (see the file COPYING included with
the distribution).

@status:  experimental
@version: $Revision$
@author:  Tao Liu
@contact: taoliu@jimmy.harvard.edu
"""

# ------------------------------------
# python modules
# ------------------------------------
import sys
import os
import re
import logging
from subprocess import Popen, PIPE
from math import log
from MACS2.IO.cParser import BEDParser, ELANDResultParser, ELANDMultiParser, ELANDExportParser, SAMParser, BAMParser, BowtieParser,  guess_parser
# ------------------------------------
# constants
# ------------------------------------

efgsize = {"hs":2.7e9,
           "mm":1.87e9,
           "ce":9e7,
           "dm":1.2e8}

# ------------------------------------
# Misc functions
# ------------------------------------
def opt_validate ( optparser ):
    """Validate options from a OptParser object.

    Ret: Validated options object.
    """
    (options,args) = optparser.parse_args()

    # gsize
    try:
        options.gsize = efgsize[options.gsize]
    except:
        try:
            options.gsize = float(options.gsize)
        except:
            logging.error("Error when interpreting --gsize option: %s" % options.gsize)
            logging.error("Available shortcuts of effective genome sizes are %s" % ",".join(efgsize.keys()))
            sys.exit(1)


    # treatment file
    if not options.tfile:       # only required argument
        optparser.print_help()
        sys.exit(1)

    # format

    options.gzip_flag = False           # if the input is gzip file
    
    options.format = options.format.upper()
    if options.format == "ELAND":
        options.parser = ELANDResultParser
    elif options.format == "BED":
        options.parser = BEDParser
    elif options.format == "ELANDMULTI":
        options.parser = ELANDMultiParser
    elif options.format == "ELANDEXPORT":
        options.parser = ELANDExportParser
    elif options.format == "SAM":
        options.parser = SAMParser
    elif options.format == "BAM":
        options.parser = BAMParser
        options.gzip_flag = True
    elif options.format == "BOWTIE":
        options.parser = BowtieParser
    elif options.format == "AUTO":
        options.parser = guess_parser
    else:
        logging.error("Format \"%s\" cannot be recognized!" % (options.format))
        sys.exit(1)
    
    # duplicate reads
    if options.keepduplicates != "auto" and options.keepduplicates != "all":
        if not options.keepduplicates.isdigit():
            logging.error("--keep-dup should be 'auto', 'all' or an integer!")
            sys.exit(1)

    # shiftsize>0
    if options.shiftsize <=0 :
        logging.error("--shiftsize must > 0!")
        sys.exit(1)

    if options.qvalue:
        # if set, ignore pvalue cutoff
        options.log_qvalue = log(options.qvalue,10)*-1
        options.log_pvalue = None
    else:
        options.log_qvalue = None
        options.log_pvalue = log(options.pvalue,10)*-1
    
    # uppercase the format string 
    options.format = options.format.upper()

    # upper and lower mfold
    try:
        (options.lmfold,options.umfold) = map(int, options.mfold.split(","))
    except:
        logging.error("mfold format error! Your input is '%s'. It should be like '10,30'." % options.mfold)
        sys.exit(1)
    
    # output filenames
    options.peakxls = options.name+"_peaks.xls"
    options.peakbed = options.name+"_peaks.bed"
    options.peakNarrowPeak = options.name+"_peaks.encodePeak"    
    options.summitbed = options.name+"_summits.bed"
    options.zwig_tr = options.name+"_treat"
    options.zwig_ctl= options.name+"_control"
    #options.negxls  = options.name+"_negative_peaks.xls"
    #options.diagxls = options.name+"_diag.xls"
    options.modelR  = options.name+"_model.r"
    options.pqtable  = options.name+"_pq_table.txt"    

    # logging object
    logging.basicConfig(level=(4-options.verbose)*10,
                        format='%(levelname)-5s @ %(asctime)s: %(message)s ',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        stream=sys.stderr,
                        filemode="w"
                        )
	
    options.error   = logging.critical		# function alias
    options.warn    = logging.warning
    options.debug   = logging.debug
    options.info    = logging.info

    options.argtxt = "\n".join((
        "# ARGUMENTS LIST:",\
        "# name = %s" % (options.name),\
        "# format = %s" % (options.format),\
        "# ChIP-seq file = %s" % (options.tfile),\
        "# control file = %s" % (options.cfile),\
        "# effective genome size = %.2e" % (options.gsize),\
        #"# tag size = %d" % (options.tsize),\
        "# band width = %d" % (options.bw),\
        "# model fold = %s\n" % (options.mfold),\
        ))

    if options.qvalue:
        options.argtxt +=  "# qvalue cutoff = %.2e\n" % (options.qvalue)
    else:
        options.argtxt +=  "# pvalue cutoff = %.2e\n" % (options.pvalue)

    options.tocontrol = False
    if options.tocontrol:
        options.argtxt += "# ChIP dataset will be scaled towards Control dataset.\n"
    else:
        options.argtxt += "# Control dataset will be scaled towards ChIP dataset.\n"

    if options.cfile:
        options.argtxt += "# Range for calculating regional lambda is: %d bps and %d bps\n" % (options.smalllocal,options.largelocal)
    else:
        options.argtxt += "# Range for calculating regional lambda is: %d bps\n" % (options.largelocal)

    if options.halfext:
        options.argtxt += "# MACS will make 1/2d size fragments\n"

    return options
