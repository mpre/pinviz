#!/usr/bin/env python2.7

import sys
import argparse
import rbtree

def is_unique( interval_set ):
    """
    Analyze interval_set and return true if it represent a single, contiguous
    region.
    """
    uniq = True
    if len( interval_set ) == 0:
        return False
    elif len( interval_set ) == 1:
        return True
    else:
        for i in range( len( interval_set ) -1 ):
            if( interval_set[i].root[1] +1 != interval_set[i+1].root[0] ):
                uniq = False
        return uniq

def grow_right( interval_set ):
    """
    Compute the biggest contiguous region that starts from the first element of
    interval_set (if any).
    """
    if len( interval_set ) == 0:
        return [ ]
    elif len( interval_set ) == 1:
        return interval_set
    else:
        grown_interval = [ interval_set[ 0 ] ]
        for interval in interval_set[ 1 : ]:
            if interval.root[ 0 ] == grown_interval[ -1 ].root[ 1 ] +1:
                grown_interval.append( interval )
            else:
                return grown_interval
        return grown_interval

def grow_left( interval_set ):
    """
    Compute the biggest contiguous region that ends in the last element of 
    interval_set (if any).
    """
    if len( interval_set ) == 0:
        return [ ]
    elif len( interval_set ) == 1:
        return interval_set
    else:
        grown_interval = [ interval_set[ -1 ] ]
        for interval in interval_set[ 0:-1 ][::-1]:
            if grown_interval[ -1 ].root[ 0 ] == interval.root[ 1 ] +1 :
                grown_interval.append( interval )
            else:
                return grown_interval[::-1]
        return grown_interval[::-1]

def main( ):
    parser = argparse.ArgumentParser( prog = "cutfiller",
                                      description = "Rebuild exons from PIntron output." )
    parser.add_argument( '-p', '--pintron-output', help = "PIntron output file",
                         required = True, dest = 'pfile' )
    parser.add_argument( '-a', '--alignment-file', help = 'Alignment file (PIntron)',
                         required = True, dest = 'alfile')
    parser.add_argument( '-l', '--max-intron-length',
                         help = 'Max intron length accepted. Introns that exceed this value will be discarded',
                         required = False, dest = 'minIntron', type = int, default = 15000 )
    args = parser.parse_args(  )

    cutst = rbtree.RBIntervalTree( )

    print >> sys.stderr, "{0:<50}".format("==> OPENING ALIGNMENT FILE")

    # Open PIntron alignment file and build the tree
    align_index = 0
    with open( args.alfile, 'r' ) as inInts:
        for line in inInts.readlines( ):
            if not line.startswith( ">" ) and not line.startswith( "#" ):
                print >> sys.stderr, "{0:<50}\r".format( "==> PROCESSING ALIGNMENT NUMBER {0:<10}".format( align_index ) ),
                align_index += 1
                elements = line.split( ' ' )
                begin = int( elements[ 2 ] )
                end = int( elements[ 3 ] )
                cutst.rbinsert( [ begin, end ] )

    print >> sys.stderr # newline

    five_p_sites = []
    five_p_sites_no_exons = []
    three_p_sites = []
    three_p_sites_no_exons = []
    
    print >> sys.stderr, "{0:<50}".format("==> OPENING SPLICE SITE FILE: {0}".format( args.pfile) )
    with open( args.pfile, 'r' ) as inIntrons:
        for line in inIntrons.readlines( ):
            elements = line.split( "\t" )
            region_end = int( elements[ 0 ] ) -1
            region_begin = int( elements[ 1 ] ) +1
            if abs( region_begin - region_end ) <  args.minIntron:
                if region_end not in five_p_sites:
                    five_p_sites.append( region_end )
                    five_p_sites_no_exons.append ( region_end )
                if region_begin not in three_p_sites:
                    three_p_sites.append( region_begin )
                    three_p_sites_no_exons.append( region_begin )
            else:
                print >> sys.stderr, "{0:<50}".format( "==> INTRON TOO LARGE: [{0}, {1}]".format( region_begin, region_end ) )

    three_p_sites = sorted( list( set( three_p_sites ) ) )
    five_p_sites = sorted( list( set( five_p_sites ) ) )

    five_p_sites_no_exons = sorted( list( set( five_p_sites_no_exons ) ) )
    three_p_sites_no_exons = sorted( list( set( three_p_sites_no_exons ) ) )

    print >> sys.stderr, "{0:<50}".format("==> PROCESSING 3' SPLICE SITES")
    
    # Analyze complete regions for every splice site
    for site1 in three_p_sites:
        complete_regions_for_site1 = []
        should_continue = True
        for site2 in five_p_sites:
            if should_continue and site1 < site2:
                nodes = cutst.search( [ site1, site2 ] )
                if ( len( nodes ) > 0 and 
                     nodes[ 0 ].root[ 0 ] <= site1 and 
                     nodes[ -1 ].root[ 1 ] >= site2 and 
                     is_unique( nodes ) 
                 ):
                    if site1 in three_p_sites_no_exons:
                        three_p_sites_no_exons = filter( lambda x: x != site1, three_p_sites_no_exons )
                    if site2 in five_p_sites_no_exons:
                        five_p_sites_no_exons = filter( lambda x: x != site2, five_p_sites_no_exons )
                    complete_regions_for_site1.append( (site1, site2) )
                else:
                    should_continue = False
        print >> sys.stderr, "{0:<50}".format( "==> NUMBER OF COMPLETE REGIONS FOR STARTING SITE {0}: {1}".format( site1, len(complete_regions_for_site1)  ) )
        if len( complete_regions_for_site1 ) > 0:
            for region in complete_regions_for_site1:
                print "{0}\t{1}\t0".format(*region)

    print >> sys.stderr, "{0:<50}".format( "==> NUMBER OF 3' SPLICE SITES IN WHICH NO COMPLETE REGION STARTS: {0}".format( len( three_p_sites_no_exons ) ) )

    for position in three_p_sites_no_exons:
        nodes = cutst.search( [ position, cutst.get_max( ) ] )
        nodes = grow_right( nodes )
        if len( nodes ) >= 1:
            print "{0}\t{1}\t2".format( position, nodes[ -1 ].root[ 1 ] )

    print >> sys.stderr, "{0:<50}".format( "==> NUMBER OF 5' SPLICE SITES IN WHICH NO COMPLETE REGION ENDS: {0}".format( len( five_p_sites_no_exons ) ) )

    for position in five_p_sites_no_exons:
        nodes = cutst.search( [ 0, position ] )
        nodes = grow_left( nodes )
        if len( nodes ) >= 1:
            print "{0}\t{1}\t1".format( nodes[ 0 ].root[ 0 ], position )
        nodes = [ ]

    print >> sys.stderr, "{0:<50}".format( "==> PROCESS COMPLETE" )
        
if __name__ == "__main__":
    main( )
    
