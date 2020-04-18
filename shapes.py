import math
import argparse
import subprocess
import time

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
        self.p1 = point1
        self.p2 = point2
        
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

    def size(self):
        return (abs(self.p2.x - self.p1.x + 1), 
                abs(self.p2.y - self.p1.y + 1), 
                abs(self.p2.z - self.p1.z + 1))

    def split(self):
        '''
        Splits on the largest dimension, returns a tuple of the resulting
        Regions,
        '''
        x, y, z = self.size()

        if x == 1 and y == 1 and z ==1:
            raise Exception("Cannot split region: {}", self)

        # print(self, ":", (x,y,z))

        sec1_p1 = self.p1.copy()
        sec1_p2 = self.p2.copy()
        sec2_p1 = self.p1.copy()
        sec2_p2 = self.p2.copy()
        
        if x >= y and x >= z:
            sec1_p2.x = sec1_p1.x + x//2
            sec2_p1.x = sec1_p1.x + x//2 + 1 
        elif y >= x and y >= z:
            sec1_p2.y = sec1_p1.y + y//2
            sec2_p1.y = sec1_p1.y + y//2 + 1
        else:
            sec1_p2.z = sec1_p1.z + z//2
            sec2_p1.z = sec1_p1.z + z//2 + 1
 
        # print(Region(sec1_p1, sec1_p2), ":",Region(sec2_p1, sec2_p2))
        return Region(sec1_p1, sec1_p2), Region(sec2_p1, sec2_p2)

    def offset(self, point):
        self.p1 += point
        self.p2 += point

class Shape(object):
    def __init__(self, origin=Point(0,0,0)):
        self.origin = origin

    def _is_contained(self, point):
        ''' Returns True if the point is contained in the shape '''
        raise Exception("Subclasses MUST implement this")

# https://mathworld.wolfram.com/SphericalCap.html
class SphereSolid(Shape):
    def __init__(self, diameter, origin=Point(0,0,0)):
        super(SphereSolid, self).__init__(origin=origin)
        
        if diameter % 2 != 1:
            raise Exception("Cannot do even diameters: {}".format(diameter))
        if diameter <= 1:
            raise Exception("Cannot do diameter <= 1")
        
        self.d = diameter
        self.r = self.d/2
        self.br = math.floor(self.r) # brick range

        self.limit_y_min = None

    def _is_contained(self, point):
        mag = point.mag()
        res = False
        if mag < self.r-.01:
            res = True
        # print(point, mag, self.r-.01, res)
        return res

class HemisphereSolid(SphereSolid):
    def __init__(self, diameter, origin=None):
        super(HemisphereSolid,self).__init__(diameter, origin)
        self.limit_y_min = 0


if __name__ == '__main__':
    
    for a, b in [(0, 150), (0, -150), (-100, 100)]:
        rstx = Region(Point(a, 0, 0), Point(b, 100, 100)) 
        rstx.split()

        rsty = Region(Point(0, a, 0), Point(100, b, 100)) 
        rsty.split()

        rstz = Region(Point(0, 0, a), Point(100, 100, b)) 
        rstz.split()

        print()