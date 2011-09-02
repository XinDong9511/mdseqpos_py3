# Time-stamp: <2011-06-19 19:02:32 Tao Liu>

"""Module Description:  IO Module for bedGraph file

Copyright (c) 2011 Tao Liu <taoliu@jimmy.harvard.edu>

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
from MACS2.IO.cBedGraph import bedGraphTrackI

# ------------------------------------
# constants
# ------------------------------------

# ------------------------------------
# Misc functions
# ------------------------------------

# ------------------------------------
# Classes
# ------------------------------------

class bedGraphIO:
    """File Parser Class for bedGraph File.

    There are two assumptions in my bedGraphTrackI object:

    1. Continuous: the next region should be after the previous one
    unless they are on different chromosomes;
    
    2. Non-overlapping: the next region should never have overlaps
    with preceding region.

    If any of the above two criteria is violated, parsering will fail.
    """
    def __init__ (self,f):
        """f must be a filename or a file handler.
        
        """
        if type(f) == str:
            self.fhd = open(f,"r")
        elif type(f) == file:
            self.fhd = f
        else:
            raise Exception("f must be a filename or a file handler.")

    def build_bdgtrack (self, baseline_value=0):
        """Use this function to return a bedGraphTrackI object.

        baseline_value is the value to fill in the regions not defined
        in bedGraph. For example, if the bedGraph is like:

        chr1  100 200  1
        chr1  250 350  2

        Then the region chr1:200..250 should be filled with
        baseline_value. Default of baseline_value is 0.
        """
        data = bedGraphTrackI(baseline_value=baseline_value)
        add_func = data.add_loc
        for i in self.fhd:
            if i.startswith("track"):
                continue
            elif i.startswith("#"):
                continue
            elif i.startswith("browse"):
                continue
            else:
                (chrom,startpos,endpos,value)=i.split()
                add_func(chrom,int(startpos),int(endpos),float(value))
        self.fhd.seek(0)
        return data


