#!/usr/bin/python3

import math
import argparse
import subprocess
import time

import shapes
from shapes import Point, Region

FILL_MAX_VOLUME = 32768

def generate_regions(shape):
    '''
    how to make this better: 
        * work with even diameters
        * if there's layers that are identical (which can happen near y=0),
          then duplicate regions are generated ... could probably search
          for duplicate regions in the results
    '''
    z = 0
    regions = []
    # only do top half
    for y in range(shape.br, -1, -1):
        points = []
        x = shape.br

        #search for the x that brings the region into surface
        p = Point(x,y,z)
        while not shape._is_contained(p):
            p.x -= 1
            if p.x < 0:
                raise Exception("!")
        
        radius = p.x # x is now the radius of this layer

        while p.z < radius:
            # expand z until the point is no longer contained
            while shape._is_contained(p):
                p.z += 1
            p.z -= 1 # bring it back in

            points.append(p.copy())

            if p.z + 1 > radius:
                break

            while not shape._is_contained(Point(p.x, p.y, p.z+1)):
                p.x -= 1 # pull x down one

        
        # mirror the point across all 3 axis to create a region
        for p in points:
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

        # print("y: {}, points({}): {}".format(y, len(points), []))
    
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
            regions = generate_regions(s)
            print("Sphere     : {} : {} : {:.6f}".format(n, len(regions), time.time()-t0))

    if True:
        N = 512 + 2
        for i in range(17, N, 16):
            t0 = time.time()
            s = shapes.HemisphereSolid(i)
            regions = generate_regions(s)
            print("Hemisphere : {} : {} : {:.6f}".format(i, len(regions), time.time()-t0))

        for i in range(17, N, 16):
            t0 = time.time()
            s = shapes.SphereSolid(i)
            regions = generate_regions(s)
            print("Sphere     : {} : {} : {:.6f}".format(i, len(regions), time.time()-t0))


