#!/usr/bin/env python2.7

import sys
import argparse
import rbtree

NAMES = { rbtree.BLANK  : "BLANK",
          rbtree.EXON   : "EXON",
          rbtree.INTRON : "INTRON",
          rbtree.BOTH   : "BOTH" }

def main( ):
    parser = argparse.ArgumentParser( prog = "regreb",
                                      description = "Rebuil gene structure from PIntron and cutfiller output." )
    parser.add_argument( '-p', '--pintron-output', help = "PIntron output file.",
                         required = True, dest = 'pfile' )
    parser.add_argument( '-c', '--cutfiller-output', help = "cutfiller output file.",
                         required = True, dest = 'cfile' )
    
    args = parser.parse_args( )
    itree = rbtree.RBIntervalTree( )

    print >> sys.stderr, "{0:<50}".format("==> OPENING PINTRON OUTPUT FILE: {0}".format( args.pfile ) )
    with open( args.pfile, 'r' ) as inIntrons:
        for line in inIntrons.readlines( ):
            elements     = line.split( "\t" )
            intron_begin = int( elements[ 0 ] )
            intron_end   = int( elements[ 1 ] )
            # print >> sys.stderr, intron_begin, "\t", intron_end
            itree.rbinsert( [ intron_begin, intron_end ], rbtree.INTRON )

    print >> sys.stderr, "{0:<50}".format("==> OPENING CUTFILLER OUTPUT FILE: {0}".format( args.cfile )) 
    with open( args.cfile, 'r' ) as inExons:
        for line in inExons.readlines( ):
            elements   = line.split( "\t" )
            exon_begin = int( elements[ 0 ] )
            exon_end   = int( elements[ 1 ] )
            itree.rbinsert( [ exon_begin, exon_end ], rbtree.EXON )

    nodes = itree.search( [ itree.get_min( ), itree.get_max( ) ] )
    start = 0
    end = 0
    t = rbtree.BLANK
    # Join consecutive regions that have the same "type"
    for position, regtype in [ [ x.root , x.regtype ] for x in nodes ]:
        if end == position[ 0 ] -1 and t == regtype:
            end = position[ 1 ]
        else:
            if end == position[ 0 ] -1:
                print "{0}\t{1}\t{2}".format( start, end, NAMES[ t ] )
                start = position[ 0 ]
                end   = position[ 1 ]
                t     = regtype
            else:
                if t == rbtree.BLANK:
                    print "{0}\t{1}\t{2}".format( start, position[ 0 ] -1, NAMES[ t ] )
                else:
                    print "{0}\t{1}\t{2}".format( start, end, NAMES[ t ] )
                    print "{0}\t{1}\t{2}".format( end+1, position[ 0 ] -1, NAMES[ rbtree.BLANK ] )
                start = position[ 0 ]
                end   = position[ 1 ]
                t     = regtype

    print "{0}\t{1}\t{2}".format( start, end, NAMES[ t ] )
    print >> sys.stderr, "{0:<50}".format( "==> PROCESS COMPLETE" )

if __name__ == "__main__":
    main( )
    

    
