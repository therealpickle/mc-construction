#!/usr/bin/python3

import math
import argparse
import subprocess
import time

import shapes
from shapes import Point, Region


#Sphere     : 17 : 39 : 0.015627
def generate_regions_2(shape):
    regions = []
    last_corner_points = []
    for y in range(shape.br, -1, -1):
        corner_points = []

        #search for the x that brings the region into surface
        p_range = shape.br
        while not shape.contains(Point(p_range, y, 0)):
            p_range -= 1
            if p_range < 0:
                break
        if p_range < 0:
            print("Nothing on y = {}".format(y))
            continue

        # search quadrant for corner points
        for x in range(0,p_range + 1):
            for z in range(0,p_range + 1):
                p = Point(x, y, z)
                pn = Point(x + 1, y, z)
                pe = Point(x, y, z + 1)

                if shape.contains(p):
                    if not shape.contains(pn) and not shape.contains(pe):
                        corner_points.append(p)

        # mirror the point across all 3 axis to create a region
        for p in corner_points:
            # if p in last_corner_points:
            #     print("{} in {}".format(p, last_corner_points))
            #     continue

            if (shape.limit_y_min is not None) and (-p.y < shape.limit_y_min):
                r = Region(p, Point(-p.x, shape.limit_y_min, -p.z))
            else:
               r = Region(p, Point(-p.x, -p.y, -p.z))
            
            if r.volume() <= FILL_MAX_VOLUME:
                regions.append(r)
            else:
                r1, r2 = r.split()
                regions.append(r1)
                regions.append(r2)


        # print("y: {}, corners: {}".format(y, corner_points))
        last_corner_points = corner_points

    return regions

def cmd_fill(regions, block):
    commands = []
    for r in regions:
        cmd = "fill ~{} ~{} ~{} ~{} ~{} ~{} {}".format(
            r.p1.x, r.p1.y, r.p1.z, r.p2.x, r.p2.y, r.p2.z, block)
        commands.append(cmd)
    return commands

if __name__ == '__main__':
    print("Shape      : size : commands : seconds to generate")

    if None: # large object generation
        for n in range(1024, 8196+1, 1024):
            t0 = time.time()
            s = shapes.SphereSolid(n + 1)
            regions = s.generate_regions()
            print("Sphere     : {} : {} : {:.6f}".format(n, len(regions), 
                time.time()-t0))

    N = 192 + 2
    if True:
        for i in range(17, N, 16):
            t0 = time.time()
            s = shapes.HemisphereSolid(i)
            regions = s.generate_regions()
            print("Hemisphere : {} : {} : {:.6f}".format(i, len(regions), 
                time.time()-t0))

    if True:
        for i in range(17, N, 16):
            t0 = time.time()
            s = shapes.SphereSolid(i)
            regions = s.generate_regions()
            print("Sphere     : {} : {} : {:.6f}".format(i, len(regions), 
                time.time()-t0))
            

    if False:
        for d, l in ((5,17),):
            t0 = time.time()
            s = shapes.TubeSolid(d, l, axis='z')
            regions = generate_regions_2(s)
            print("Tube       : {}d, {}l : {} : {}".format(d, l, len(regions), 
                time.time()-t0))
