#!/usr/bin/env python3

import math
from coords import Point, Region

ADJ = 0.125

class Shape(object):
    def __init__(self, origin=Point(0,0,0)):
        self.origin = origin
        self.br = None # this must be set in subclass (brick range)
        self.limits_min = {'x':None, 'y':None, 'z':None}
        self.limits_max = {'x':None, 'y':None, 'z':None}

    def contains(self, point):
        ''' Returns True if the point is contained in the shape '''
        raise Exception("Subclasses MUST implement this")

    # def generate_regions(self):
    #     raise Exception("Subclasses MUST implement this")        

    def generate_regions_old(self, max_volume=32768):
        '''
        how to make this better: 
            * work with even diameters
        '''
        if self.br is None:
            raise Exception("Brick Range (br) must be defined in self!")

        z = 0
        regions = []
        # only do top half
        for y in range(self.br, -1, -1):
            points = []
            x = self.br

            #search for the x that brings the region into surface
            p = Point(x,y,z)
            while not self.contains(p):
                p.x -= 1
                if p.x < 0:
                    break
            if p.x < 0: # there's nothing in this layer
                continue
            
            radius = p.x # x is now the radius of this layer

            while p.z < radius:
                # expand z until the point is no longer contained
                while self.contains(p):
                    p.z += 1
                p.z -= 1 # bring it back in

                points.append(p.copy())

                if p.z + 1 > radius:
                    break

                while not self.contains(Point(p.x, p.y, p.z+1)):
                    p.x -= 1 # pull x down one

            
            # mirror the point across all 3 axis to create a region
            for p in points:
                r = Region(p, Point(-p.x, -p.y, -p.z))
                r.apply_limits(
                    xmin=self.limits_min['x'], xmax=self.limits_max['x'],
                    ymin=self.limits_min['y'], ymax=self.limits_max['y'],
                    zmin=self.limits_min['z'], zmax=self.limits_max['z'])
                if r.volume() <= max_volume:
                    regions.append(r)
                else:
                    r1, r2 = r.split()
                    regions.append(r1)
                    regions.append(r2)

            # print("y: {}, points({}): {}".format(y, len(points), []))
        
        return regions

    def generate_regions(self, max_volume=32768):
        '''
        * find all corners in y layer
        * for each cornerpoint that doesn't exist in layer above"
            * create regions by mirroring corner points about all 3 axis
            * apply limits
            * split
        * next y

        how to make this better: 
            * work with even diameters
        '''
        regions = []
        last_corner_points = []

        for y in range(self.br, -1, -1):
            corner_points = []

            x_start = self.br
            for z in range(0, self.br + 1):
                for x in range(x_start, -1, -1):
                    p = Point(x, y, z)
                    
                    if self.contains(p):
                        if not self.contains(Point(x, y, z + 1)):
                            corner_points.append(p)
                        x_start = p.x # start at this x for next z
                        break # next z

            # print("y: {}, n: {}, corners: {}".format(y, len(corner_points),
            #     corner_points))

            # mirror the point across all 3 axis to create a region
            for p in corner_points:
                plast = Point(p.x, p.y + 1, p.z)
                if plast not in last_corner_points:
                    r = Region(p, Point(-p.x, -p.y, -p.z))
                    r.apply_limits(
                        xmin=self.limits_min['x'], xmax=self.limits_max['x'],
                        ymin=self.limits_min['y'], ymax=self.limits_max['y'],
                        zmin=self.limits_min['z'], zmax=self.limits_max['z'])
                    for sr in r.split(max_volume=max_volume):
                        regions.append(sr)

            last_corner_points = corner_points

        return regions



# https://mathworld.wolfram.com/SphericalCap.html
class SphereSolid(Shape):
    def __init__(self, diameter, origin=Point(0,0,0)):
        super(SphereSolid, self).__init__(origin=origin)
       
        if diameter % 2 != 1:
            raise Exception("Cannot do even diameters: {}".format(diameter))
        if diameter <= 1:
            raise Exception("Cannot do diameter <= 1")
        
        self.d = diameter
        self.r = self.d / 2
        self.br = math.floor(self.r) # brick range

    def contains(self, point):
        mag = point.mag()
        res = False
        if mag <= (self.r + ADJ):
            res = True
        # print(point, mag, self.r-.02, res)
        return res



class HemisphereSolid(SphereSolid):
    def __init__(self, diameter, origin=None):
        super(HemisphereSolid,self).__init__(diameter, origin)
        self.limits_min['y'] = 0


class TubeSolid(Shape):
    def __init__(self, diameter, length, axis='z', origin=Point(0,0,0)):
        super(TubeSolid, self).__init__(origin = origin)
        if axis not in ('x', 'y', 'z'):
            raise Exception("Invalid axis: {}".format(axis))
        self.len = length
        self.d = diameter
        self.r = diameter / 2
        self.br = max(self.len // 2, self.d // 2)
        self.axis = axis

    def contains(self, point):
        res = False
        if self.axis == 'x':
            if abs(point.x) <= self.len // 2:
                r = math.sqrt(point.y**2 + point.z**2)
                if r <= self.r + ADJ:
                    res = True
        elif self.axis == 'y':
            if abs(point.y) <= self.len // 2:
                r = math.sqrt(point.x**2 + point.z**2)
                if r <= self.r + ADJ:
                    res = True
        else:
            if abs(point.z) <= self.len // 2:
                r = math.sqrt(point.x**2 + point.y**2)
                if r <= self.r + ADJ:
                    res = True
        return res

# class ArchSolid

if __name__ == '__main__':
    import time

    TEST_GENERATE_REGIONS = True

    DO_SPHERE_BENCHMARK     = True
    DO_HEMISPHERE_BENCHMARK = True

    if TEST_GENERATE_REGIONS:
        # these are based on current benchmark, if needed, adjust
        # test vector = diameter, #regions
        tv = ((9,12), (17, 36), (33, 102), (65, 582))
        for d, n in tv:
            s = SphereSolid(d)
            t0 = time.time()
            rs = s.generate_regions_old(max_volume=32768)
            t1 = time.time()
            rs = s.generate_regions(max_volume=32768)
            t2 = time.time()
            # print("SphereSolid({}) : {} : {} : {}".format(d, t1-t0, t2-t1,
            #     (t2-t1)/(t1-t0)))
            if len(rs) != n:
                print("SphereSolid({}) generated {} regions instead "
                    "of {}".format(d, len(rs), n))



    N = 256 + 2
    if DO_HEMISPHERE_BENCHMARK:
        print("Hemisphere : diameter : commands : time")
        for i in range(17, N, 16):
            t0 = time.time()
            s = HemisphereSolid(i)
            regions = s.generate_regions()
            t1 = time.time()
            print("Hemisphere : {:8} : {:8} : {:.6f}".format(i, len(regions), 
                t1-t0))

    if DO_SPHERE_BENCHMARK:
        print("Sphere : diameter : commands : time")
        for i in range(17, N, 16):
            t0 = time.time()
            s = SphereSolid(i)
            regions = s.generate_regions()
            t1 = time.time()
            print("Sphere : {:8} : {:8} : {:.6f}".format(i, len(regions), 
                t1-t0))


    if 0:
        from matplotlib import pyplot as plt

        def plot_point(ax, point):
            x, y, z = point.xyz()
            # if x >= 0 and y >= 0 and z >= 0:
            ax.scatter(x, z, y) #flip around to orient to minecraft

        def plot_region(ax, region):
            for p in region.corner_points():
                plot_point(ax, p)

        def plot_shape(ax, shape):
            for r in shape.generate_regions():
                plot_region(ax, r)

            # make a fake region and plot it to keep axis equal
            br = shape.br
            r = Region(Point(-br,-br,-br), Point(br, br, br))
            plot_region(ax, r)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlabel("X")
        ax.set_ylabel("Z")
        ax.set_zlabel("Y")

        s = TubeSolid(5, 17, axis = 'x')
        # s = SphereSolid(9)
        plot_shape(ax, s)


        plt.show()