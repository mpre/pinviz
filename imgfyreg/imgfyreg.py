#!/usr/bin/env python2.7

import sys
import argparse
import numpy
from PIL import Image
from PIL import ImageDraw
from PIL import ImageChops
from PIL import ImageFont
from PIL import ImageOps

YSIZE   = 80
XOFFSET = 20
YOFFSET = 10
START   = 0

class Region( object ):
    
    def __init__( self, start, end, t, annot=False ):
        self.start = start
        self.end   = end
        self.t     = t

def is_white( region ):
    for line in region:
        for pixel in line:
            if pixel[ 0 ] == 255 and pixel[ 1 ] == 255 and pixel[ 2 ] == 255:
                pass
            else:
                return False
    return True

def get_overlapping_exons( region, annotExons ):
    overlappingExons = [ ]
    for exon in annotExons:
        if exon[ 1 ] < region.start:
            continue
        elif exon[ 0 ] > region.end:
            break
        else:
            overlappingExons.append( exon )
    return overlappingExons

def draw_full_rect( draw, position, annot, scale, start, origin_im ):
    # Draw a full rectangle from position[ 0 ] to position [ 1 ].
    # A full rectangle is something similar to
    #
    #  ###################################
    #  ###################################
    #  ###################################
    #  ###################################
    #
    print >> sys.stderr, "====> draw_full_rect:\t{0}\t{1}".format( position,
                                                                   [(x-start) * scale for x in position] )
    if annot == False:
        color = (200, 0, 0)
    else:
        color = (0, 0, 0)
    draw.rectangle( [ ( (position[ 0 ] - start) * scale + XOFFSET, 0 + YOFFSET),
                      ( (position[ 1 ] - start) * scale + XOFFSET, YSIZE + YOFFSET) ],
                    color, (0, 0, 0) )

    f = ImageFont.truetype( "DejaVuSansMono.ttf", size=12 )
    txt=Image.new("RGBA", (60, 30), (256, 256, 256))
    d = ImageDraw.Draw(txt)
    d.text( (0, 0), str( position[ 0 ] ), font=f, fill=0 )
    w = txt.rotate( 90 )

    # Find where we want to draw the text
    
    ydist = int(YSIZE * 3.5)
    pixels = numpy.asarray( origin_im )

    xstart = int( (position[ 0 ] -start -2 ) * scale + XOFFSET )
    xend = int( (position[ 0 ] - start -2) * scale + XOFFSET +30)

    # print len( pixels )
    # print len( pixels[ 0 ] )
    # print xstart
    # print xend
    # sys.exit( )

    print xstart, xend

    a = [y[xstart:xend+1] for y in pixels[ ydist:ydist+61] ]
    # print is_white(a)
    
    # sys.exit( )

    while not is_white( a ):
        ydist += 20
        a = [y[xstart:xend+1] for y in pixels[ ydist:ydist+61] ]
#        a = [y[ ydist:ydist+20 ] for y in pixels[ xstart-1: xend+1 ] ]

    print ydist

    draw.line( [ ( (position[ 0 ] - start) * scale + XOFFSET, 0 + YOFFSET + YSIZE ),
                 ( (position[ 0 ] - start) * scale + XOFFSET, ydist + 60) ],
               (0, 200, 0 ), 1 )


    origin_im.paste( w, (int( (position[ 0 ] - start -2) * scale +
                              XOFFSET) , ydist ) )

    ydist = int(YSIZE * 3.5)

    xstart = int( (position[ 1 ] -start -2 ) * scale + XOFFSET )
    xend = int( (position[ 1 ] - start -2) * scale + XOFFSET +30)

    a = [y[xstart:xend+1] for y in pixels[ ydist:ydist+61] ]
#    a = [y[ ydist:ydist+20 ] for y in pixels[ xstart-1: xend+1 ] ]
    while not is_white( a ):
        ydist += 20
        a = [y[xstart:xend+1] for y in pixels[ ydist:ydist+61] ]
        #a = [y[ ydist:ydist+20 ] for y in pixels[ xstart-1: xend+1 ] ]

    print ydist

    txt=Image.new("RGBA", (60, 30), (256, 256, 256))
    d = ImageDraw.Draw(txt)
    d.text( (0, 0), str( position[ 1 ] ), font=f, fill=0 )
    w = txt.rotate( 90 )

    draw.line( [ ( (position[ 1 ] - start) * scale + XOFFSET, 0 + YOFFSET + YSIZE ),
                 ( (position[ 1 ] - start) * scale + XOFFSET, ydist +60) ],
               (0, 200, 0 ), 1 )

    origin_im.paste( w, (int( (position[ 1 ] - start -2) * scale +
                              XOFFSET) , ydist) )
        
    return draw
    
def draw_striped_rect( draw, position, annot, scale, start, origin_im ):
    # Draw a striped rectangle from position[ 0 ] to position [ 1 ].
    # A striped rectangle is something similar to
    #
    #  ###################################
    #  ########################          #
    #  ######                            #
    #  ###################################
    #
    if annot == False:
        color = (200, 0, 0)
    else:
        color = (0, 0, 0)
    print >> sys.stderr, "====> draw_striped_rect:\t{0}\t{1}".format( position,
                                                                      [(x-start) * scale for x in position] )
    draw.polygon( [ ((position[ 0 ] - start) * scale + XOFFSET, 0 + YOFFSET),
                    ((position[ 1 ] - start) * scale + XOFFSET, 0 + YOFFSET),
                    ((position[ 0 ] - start) * scale + XOFFSET, YSIZE + YOFFSET) ],
                  color, (0, 0, 0) )
    draw.polygon( [ ((position[ 1 ] - start) * scale + XOFFSET, 0 + YOFFSET),
                    ((position[ 1 ] - start) * scale + XOFFSET, YSIZE + YOFFSET),
                    ((position[ 0 ] - start) * scale + XOFFSET, YSIZE + YOFFSET) ],
                  outline = (0, 0, 0) )
    f = ImageFont.truetype( "DejaVuSansMono.ttf", size=12 )
    txt=Image.new("RGBA", (60, 30), (256, 256, 256))
    d = ImageDraw.Draw(txt)
    d.text( (0, 0), str( position[ 0 ] ), font=f, fill=0 )
    w = txt.rotate( 90 )

    ydist = int(YSIZE * 3.5)
    pixels = numpy.asarray( origin_im )

    xstart = int( (position[ 0 ] -start -2 ) * scale + XOFFSET )
    xend = int( (position[ 0 ] - start -2) * scale + XOFFSET +30)

    a = [y[xstart:xend+1] for y in pixels[ ydist:ydist+61] ]
#    a = [y[ ydist:ydist+20 ] for y in pixels[ xstart-1: xend+1 ] ]
    while not is_white( a ):
        ydist += 20
        a = [y[xstart:xend+1] for y in pixels[ ydist:ydist+61] ]
#        a = [y[ ydist:ydist+20 ] for y in pixels[ xstart-1: xend+1 ] ]
    print ydist

    draw.line( [ ( (position[ 0 ] - start) * scale + XOFFSET, 0 + YOFFSET + YSIZE ),
                 ( (position[ 0 ] - start) * scale + XOFFSET, ydist) ],
               (0, 200, 0 ), 1 )


    origin_im.paste( w, (int( (position[ 0 ] - start -2) * scale +
                              XOFFSET) , ydist) )

    ydist = int(YSIZE * 3.5)

    xstart = int( (position[ 1 ] -start -2 ) * scale + XOFFSET )
    xend = int( (position[ 1 ] - start -2) * scale + XOFFSET +30)

    a = [y[xstart:xend+1] for y in pixels[ ydist:ydist+61] ]
#    a = [y[ ydist:ydist+20 ] for y in pixels[ xstart-1: xend+1 ] ]
    while not is_white( a ):
        ydist += 20
        a = [y[xstart:xend+1] for y in pixels[ ydist:ydist+61] ]
#        a = [y[ ydist:ydist+20 ] for y in pixels[ xstart-1: xend+1 ] ]

    print ydist

    txt=Image.new("RGBA", (60, 30), (256, 256, 256))
    d = ImageDraw.Draw(txt)
    d.text( (0, 0), str( position[ 1 ] ), font=f, fill=0 )
    w = txt.rotate( 90 )

    draw.line( [ ( (position[ 1 ] - start) * scale + XOFFSET, 0 + YOFFSET + YSIZE ),
                 ( (position[ 1 ] - start) * scale + XOFFSET, ydist ) ],
               (0, 200, 0 ), 1 )

    origin_im.paste( w, (int( (position[ 1 ] - start -2) * scale +
                              XOFFSET) , ydist) )
    # draw.line( [ ( (position[ 0 ] - start) * scale + XOFFSET, 0 + YOFFSET + YSIZE ),
    #              ( (position[ 0 ] - start) * scale + XOFFSET, YSIZE * 4.5) ],
    #            (0, 200, 0 ), 1 )


    # origin_im.paste( w, (int( (position[ 0 ] - start -2) * scale +
    #                           XOFFSET) , int( YSIZE * 4.5 ) ) )

    # txt=Image.new("RGBA", (60, 30), (256, 256, 256))
    # d = ImageDraw.Draw(txt)
    # d.text( (0, 0), str( position[ 1 ] ), font=f, fill=0 )
    # w = txt.rotate( 90 )

    # draw.line( [ ( (position[ 1 ] - start) * scale + XOFFSET, 0 + YOFFSET + YSIZE ),
    #              ( (position[ 1 ] - start) * scale + XOFFSET, YSIZE * 3.5) ],
    #            (0, 200, 0 ), 1 )

    # origin_im.paste( w, (int( (position[ 1 ] - start -2) * scale +
    #                           XOFFSET) , int( YSIZE * 3.5 ) ) )
        
    return draw

def draw_line( draw, position, scale, start ):
    print >> sys.stderr, "====> draw_line:\t{0}\t{1}".format( position,
                                                                   [(x-start) * scale for x in position] )
    draw.line( [ ( (position[ 0 ] - start) * scale + XOFFSET, YSIZE/2 + YOFFSET ),
                 ( (position[ 1 ] - start) * scale + XOFFSET, YSIZE/2 + YOFFSET) ],
               (0, 200, 0 ), 2 )
    return draw

def main( ):
    parser = argparse.ArgumentParser( prog = "imgfyreg", description = "Produce image representation of regreb output.",
                                      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument( '-r', '--regreb-output', help = "regreb.py output file",
                         required = True, dest = 'regionsFile' )
    parser.add_argument( '-g', '--gtf-file', help = 'annotation file',
                         required = True, dest = 'annotationFile')
    parser.add_argument( '-W', '--width', help = 'image width', default = 800,
                         type = int, dest = 'imgw' )
    parser.add_argument( '-H', '--height', help = 'image height',
                         default = 4*YSIZE, type = int, dest = 'imgh' )
    parser.add_argument( '-o', '--output-file', help = 'output filename',
                         default = 'output.png', dest = 'oFile' )
    args = parser.parse_args( )

    regions = [ ]
    with open( args.regionsFile ) as regionsIn:
        for line in regionsIn.readlines( ):
            elements = line.replace("\n", '').split( "\t" )
            start, end, t = int( elements[ 0 ] ), int( elements[ 1 ] ), elements[ 2 ]
            regions.append( Region( start, end, t ) )
    
    annotExons = set( )
    with open( args.annotationFile ) as annotIn:
        for line in annotIn.readlines( ):
            elements = line.replace("\n", '').split( "\t" )
            t, start, end = elements[ 2 ], 1338447 + int( elements[ 3 ] ), 1338447 + int( elements[ 4 ] )
            if t == "exon":
                annotExons.add( ( start, end ) )

    annotExons = sorted( list( annotExons ) )

    region_start = regions[ 0 ].start

    GEN_TO_PIX = (args.imgw - XOFFSET * 2 )/ float( regions[ -1 ].end - regions[ 0 ].start )
    
    im   = Image.new( "RGBA", (args.imgw, args.imgh), (256, 256, 256) )
    draw = ImageDraw.Draw( im )

    draw.rectangle( [ XOFFSET, YSIZE * 2, args.imgw - XOFFSET, YSIZE * 2.5 ],
                    (0, 0, 200, 80), (0, 0, 0, 80) )


    #### RIVEDERE UN PO' QUI SOTTO
    for r in regions:
        print >> sys.stderr, "REGION {0} {1} {2}".format( r.start, r.end, r.t )
        if r.t == "BLANK":
            continue
        else:
            overlappingExons = get_overlapping_exons( r, annotExons )
            current_start = r.start
            current_end   = r.end
            t             = r.t
            if overlappingExons:
                for exon in overlappingExons[:]:
                    if current_start >= current_end:
                        break
                    elif current_start <= exon[ 0 ]:
                        #draw
                        if t == "EXON":
                            draw = draw_full_rect( draw, [current_start, exon[ 0 ] +1 ], False, GEN_TO_PIX, region_start, im)
                            draw = draw_full_rect( draw, [exon[ 0 ], min( exon[ 1 ], current_end ) +1],
                                                   True, GEN_TO_PIX, region_start, im)
                            current_start = min( exon[ 1 ], current_end )
                        elif t == "INTRON":
                            draw =  draw_line( draw, [current_start, current_end +1], GEN_TO_PIX, region_start )
                            current_start = current_end
                        elif t == "BOTH":
                            draw = draw_striped_rect( draw, [current_start, exon[ 0 ] +1], False, GEN_TO_PIX, region_start, im)
                            draw = draw_striped_rect( draw, [exon[ 0 ], min( exon[ 1 ],
                                                                             current_end ) +1 ],
                                                      True, GEN_TO_PIX, region_start, im )
                            current_start = min( exon[ 1 ], current_end )
                    elif current_start > exon[ 0 ]:
                        if t == "EXON":
                            draw = draw_full_rect( draw, [current_start, min( exon[ 1 ],
                                                                              current_end) +1 ], 
                                                   True, GEN_TO_PIX, region_start, im)
                            current_start = min( exon[ 1 ], current_end )
                        elif t == "INTRON":
                            draw = draw_line( draw, [current_start, current_end +1 ], GEN_TO_PIX, region_start )
                            current_start = current_end
                        elif t == "BOTH":
                            draw = draw_striped_rect( draw, [current_start, min( exon[ 1 ],
                                                                                 current_end ) +1 ],
                                                      True, GEN_TO_PIX, region_start, im)
                            current_start = min( exon[ 1 ], current_end )
                if current_start != current_end:
                    if t == "EXON":
                        draw = draw_full_rect( draw, [current_start, current_end +1], False, GEN_TO_PIX, region_start, im)
                    elif t == "INTRON":
                        draw = draw_line( draw, [current_start, current_end +1], GEN_TO_PIX, region_start )
                    elif t == "BOTH":
                        draw = draw_striped_rect( draw, [current_start, current_end +1], False, GEN_TO_PIX, region_start, im )
                    else:
                        pass
            else:
                if t == "EXON":
                    draw = draw_full_rect( draw, [current_start, current_end +1], False, GEN_TO_PIX, region_start, im)
                elif t == "INTRON":
                    draw = draw_line( draw, [current_start, current_end +1], GEN_TO_PIX, region_start )
                elif t == "BOTH":
                    draw = draw_striped_rect( draw, [current_start, current_end +1], False, GEN_TO_PIX, region_start, im )
                else:
                    pass

    im.save( args.oFile )

if __name__ == "__main__":
    main( )
