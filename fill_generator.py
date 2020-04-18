#!/usr/bin/python3

import math
import argparse
import subprocess
import time

CUBE_SIZE = 1
FILL_MAX_VOLUME = 32768
MAX_CMDS = 10000

class Point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def mag(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def __str__(self):
        return "P({}, {}, {})".format(self.x, self.y, self.z)

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def copy(self):
        return Point(self.x, self.y, self.z)

class Region(object):
    def __init__(self, point1, point2):
        if point1.mag() < point2.mag():
            self.p1 = point1
            self.p2 = point2
        else:
            self.p1 = point2
            self.p2 = point1

    @classmethod
    def from_coords(cls, x1, y1, z1, x2, y2, z2):
        return cls(Point(x1, y1, z1), Point(x2, y2, z2))

    def __str__(self):
        return "R({} - {})".format(self.p1, self.p2)

    def __repr__(self):
        return self.__str__()

    def volume(self):
        return  (self.p2.x - self.p1.x + 1) * \
                (self.p2.y - self.p1.y + 1) * \
                (self.p2.z - self.p1.z + 1)

    def split(self):
        '''
        to make this better, split on the largest dimension
        to make it even better, make it recursive until all 
            regions under max fill volume
        '''
        if self.p1.y == self.p2.y:
            raise Exception("Cannot split region: {}", self)
        top_p1 = self.p1.copy()
        top_p2 = self.p2.copy()
        bot_p1 = self.p1.copy()
        bot_p2 = self.p2.copy()

        top_p2.y = 0
        bot_p1.y = -1
        

        return Region(top_p1, top_p2), Region(bot_p1, bot_p2)

# https://mathworld.wolfram.com/SphericalCap.html
class SphereSolid(object):
    def __init__(self, diameter, origin=None):
        if diameter % 2 != 1:
            raise Exception("Cannot do even diameters: {}".format(diameter))
        if diameter <= 1:
            raise Exception("Cannot do diameter <= 1")
        self.o = origin
        self.d = diameter
        self.r = self.d/2
        self.br = math.floor(self.r) # brick range
        # print("D: {}, R: {}, BR: {}".format(self.d, self.r, self.br))
        self.limit_y_min = None

        

    def _is_contained(self, point):
        mag = point.mag()
        res = False
        if mag < self.r-.01:
            res = True
        # print(point, mag, self.r-.01, res)
        return res


    def generate_regions(self):
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
        for y in range(self.br, -1, -1):
            points = []
            x = self.br

            #search for the x that brings the region into surface
            p = Point(x,y,z)
            while not self._is_contained(p):
                p.x -= 1
                if p.x < 0:
                    raise Exception("!")
            
            radius = p.x # x is now the radius of this layer

            while p.z < radius:
                # expand z until the point is no longer contained
                while self._is_contained(p):
                    p.z += 1
                p.z -= 1 # bring it back in

                points.append(p.copy())

                if p.z + 1 > radius:
                    break

                while not self._is_contained(Point(p.x, p.y, p.z+1)):
                    p.x -= 1 # pull x down one

            
            # mirror the point across all 3 axis to create a region
            for p in points:
                if (self.limit_y_min is not None) and (-p.y < self.limit_y_min):
                    r = Region(p, Point(-p.x, self.limit_y_min, -p.z))
                else:
                   r = Region(p, Point(-p.x, -p.y, -p.z))
                
                if r.volume() <= FILL_MAX_VOLUME:
                    regions.append(r)
                else:
                    r1, r2 = r.split()
                    regions.append(r1)
                    regions.append(r2)

            # print("y: {}, points({}): {}".format(y, len(points), []))
        
        self.regions = regions
        return self.regions

class HemisphereSolid(SphereSolid):
    def __init__(self, diameter, origin=None):
        super(HemisphereSolid,self).__init__(diameter, origin)
        self.limit_y_min = 0

def cmd_fill(regions, block):
    commands = []
    for r in regions:
        cmd = "fill ~{} ~{} ~{} ~{} ~{} ~{} {}".format(
            r.p1.x, r.p1.y, r.p1.z, r.p2.x, r.p2.y, r.p2.z, block)
        commands.append(cmd)
    return commands

if __name__ == '__main__':
    print("Shape: size : commands : seconds to generate")

    for i in range(17, 255, 16):
        t0 = time.time()
        s = HemisphereSolid(i)
        s.generate_regions()
        print("Hemisphere: {} : {} : {:.6f}".format(i, len(s.regions), time.time()-t0))

    for i in range(17, 255, 16):
        t0 = time.time()
        s = SphereSolid(i)
        s.generate_regions()
        print("Sphere:     {} : {} : {:.6f}".format(i, len(s.regions), time.time()-t0))


