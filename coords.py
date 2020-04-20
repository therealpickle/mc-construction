#!/usr/bin/python3

import math

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

    def __eq__(self, other):
        if (self.x == other.x) and (self.y == other.y) and (self.z == other.z):
            return True
        return False

    def copy(self):
        return Point(self.x, self.y, self.z)

    def xyz(self):
        return self.x, self.y, self.z


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

    def __eq__(self, other):
        if (self.p1 == other.p1) and (self.p2 == other.p2):
            return True

        if (self.p1 == other.p2) and (self.p2 == other.p1):
            return True

        return False

    def corner_points(self):
        x1, y1, z1 = self.p1.x, self.p1.y, self.p1.z
        x2, y2, z2 = self.p2.x, self.p2.y, self.p2.z
        return (Point(x1,y1,z1), Point(x2,y2,z2), Point(x2,y1,z1), 
            Point(x2,y1,z2), Point(x1,y1,z2), Point(x1,y2,z1), Point(x2,y2,z1), 
            Point(x1,y2,z2))

    def volume(self):
        x, y, z = self.size()
        return  x * y * z

    def size(self):
        return (abs(self.p2.x - self.p1.x) + 1, 
                abs(self.p2.y - self.p1.y) + 1, 
                abs(self.p2.z - self.p1.z) + 1)

    def split(self):
        '''
        Splits on the largest dimension, returns a tuple of the resulting
        Regions,
        '''
        x, y, z = self.size()

        if x == 1 and y == 1 and z ==1:
            raise Exception("Cannot split region: {}", self)

        r1 = Region(self.p1.copy(), self.p2.copy())
        r2 = Region(self.p1.copy(), self.p2.copy())
        
        if x >= y and x >= z:
            middle = (self.p1.x + self.p2.x) // 2
            if self.p2.x >= self.p1.x:
                r2.p1.x = middle + 1
                r1.p2.x = middle
            else:
                r2.p1.x = middle
                r1.p2.x = middle + 1
        elif y >= x and y >= z:
            middle = (self.p1.y + self.p2.y) // 2
            if self.p2.y >= self.p1.y:
                r2.p1.y = middle + 1
                r1.p2.y = middle
            else:
                r2.p1.y = middle
                r1.p2.y = middle + 1
        else:
            middle = (self.p1.z + self.p2.z) // 2
            if self.p2.z >= self.p1.z:
                r2.p1.z = middle + 1
                r1.p2.z = middle
            else:
                r2.p1.z = middle
                r1.p2.z = middle + 1

 
        # print("{} ->split-> {} : {}".format(self, r1, r2))
        return r1, r2

    def offset(self, point):
        self.p1 += point
        self.p2 += point

    def apply_limits(self, xmin=None, xmax=None, ymin=None, ymax=None, 
        zmin=None, zmax=None):
        ''' 
        '''
        if xmin is not None:
            self.p1.x = max(self.p1.x, xmin)
            self.p2.x = max(self.p2.x, xmin)
        if xmax is not None:
            self.p1.x = min(self.p1.x, xmax)
            self.p2.x = min(self.p2.x, xmax)
        if ymin is not None:
            # print(self.p1.y, ymin, max(self.p1.y, ymin))
            # print(self.p2.y, ymin, max(self.p2.y, ymin))
            self.p1.y = max(self.p1.y, ymin)
            self.p2.y = max(self.p2.y, ymin)
        if ymax is not None:
            self.p1.y = min(self.p1.y, ymax)
            self.p2.y = min(self.p2.y, ymax)
        if zmin is not None:
            self.p1.z = max(self.p1.z, zmin)
            self.p2.z = max(self.p2.z, zmin)
        if zmax is not None:
            self.p1.z = min(self.p1.z, zmax)
            self.p2.z = min(self.p2.z, zmax)
        

if __name__ == '__main__':
    REGIONS_TESTS       = True
    SPLIT_TEST          = REGIONS_TESTS and True
    CORNER_POINTS_TEST  = REGIONS_TESTS and True

    if CORNER_POINTS_TEST:
        x1, y1, z1 = (0, 1, 2)
        x2, y2, z2 = (3, 4, 5)
        r = Region(Point(x1, y1, z1), Point(x2, y2, z2))
        cps = r.corner_points()

        if len(cps) != 8:
            raise Exception("'Region.corner_points' did not return 8 Points: "
                "{} -> {}".format(r, cps))

        for p in (Point(x1,y1,z1), Point(x2,y2,z2), Point(x2,y1,z1), 
            Point(x2,y1,z2), Point(x1,y1,z2), Point(x1,y2,z1), Point(x2,y2,z1),
            Point(x1,y2,z2)):
            if p not in cps:
                raise Exception("{} not in corner_points: {}".format(p,cps))

    if SPLIT_TEST:
        for tr, tr1, tr2 in [
            (Region(Point(0, 0, 0), Point(0, 0, 9)), 
                Region(Point(0, 0, 0), Point(0, 0, 4)),
                Region(Point(0, 0, 5), Point(0, 0, 9))),
            (Region(Point(0, 0, 9), Point(0, 0, 0)), 
                Region(Point(0, 0, 0), Point(0, 0, 4)),
                Region(Point(0, 0, 5), Point(0, 0, 9))),
            (Region(Point(0, 0, 0), Point(0, 9, 0)), 
                Region(Point(0, 0, 0), Point(0, 4, 0)),
                Region(Point(0, 5, 0), Point(0, 9, 0))),
            (Region(Point(0, 9, 0), Point(0, 0, 0)), 
                Region(Point(0, 0, 0), Point(0, 4, 0)),
                Region(Point(0, 5, 0), Point(0, 9, 0))),
            (Region(Point(0, 0, 0), Point(9, 0, 0)), 
                Region(Point(0, 0, 0), Point(4, 0, 0)),
                Region(Point(5, 0, 0), Point(9, 0, 0))),
            (Region(Point(9, 0, 0), Point(0, 0, 0)), 
                Region(Point(0, 0, 0), Point(4, 0, 0)),
                Region(Point(5, 0, 0), Point(9, 0, 0))),
            ]:

            r1, r2 = tr.split()
            if not ((r1 == tr1 and r2 == tr2) or (r1 == tr2 and r2 == tr1)): 
                raise Exception(
                    "Split on {}:\nTarget: {}, {}:\nResult: {}, {}".format(
                        tr, tr1, tr2, r1, r2))

