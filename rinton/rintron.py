#! /usr/bin/env python2.7

import sys
import argparse

def main( ):
    parser = argparse.ArgumentParser( prog = "rintron",
                                      description = "Analyze PIntron output and extract reads that\
                                                     align in an intron" )

    parser.add_argument( '-a', '--alignment-file', help = 'Alignment file (PIntron)',
                         required = True, dest = 'alfile' )
    parser.add_argument( '-b', '--region-begin', help = 'Intron start position',
                         required = True, dest = 'rbegin', type = int )
    parser.add_argument( '-e', '--region-end', help = 'Intron end position',
                         required = True, dest = 'rend', type = int )

    args = parser.parse_args( )

    print >> sys.stderr, "{0:<50}".format("==> OPENING ALIGNMENT FILE")

    align_index = 0
    with open( args.alfile, 'r' ) as inInts:
        align_entry = ""
        for line in inInts.xreadlines( ):
            align_entry += line
            if not line.startswith( '>' ) and not line.startswith( '#' ):
                align_index += 1
                elements = line.split( ' ' )
                align_begin = int( elements[ 2 ] )
                align_end = int( elements[ 3 ] )
                if args.rbegin <= align_begin <= args.rend or args.rbegin <= align_end <= args.rend:
                    print align_entry
                align_entry = ""

    print >> sys.stderr, "{0:<50}".format( "==> PROCESS COMPLETE" )

if __name__ == "__main__":
    main( )
