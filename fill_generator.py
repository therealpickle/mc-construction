#!/usr/bin/python3

import math
import argparse
import subprocess
import time

import shapes
from shapes import Point, Region


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
