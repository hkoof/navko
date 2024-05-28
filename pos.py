#!/usr/bin/env python

import math
import geojson as gj

from geopy.distance import geodesic
import geopy.point


class Point(geopy.point.Point):
    def __init__(self, latitude=None, longitude=None, altitude=None, label=''):
        self.label = label
        super().__init__()

class Leg:
    def __init__(self, begin, bearing, distance, checkpoints=[]):
        self.begin = begin
        self.bearing = bearing
        self.distance = geodesic(nautical=distance)
        self.checkpoints = checkpoints

    def end(self):
        endpos = self.distance.destination(self.begin, bearing=self.bearing)
        return endpos

    def e6b(self, true_airspeed, wind_direction, wind_speed):
        # Thanks: https://www.omnicalculator.com/physics/ground-speed
        #
        tt = math.radians(self.bearing)  
        wd = math.radians(wind_direction + 180)

        wca = math.asin( (wind_speed / true_airspeed) * math.sin(wd - tt) )
        wind_correction_angle = math.degrees(wca)
        
        ground_speed = math.sqrt(
                math.pow(true_airspeed, 2) + math.pow(wind_speed, 2) -
                (
                    2 * true_airspeed * wind_speed * math.cos(tt - wd + wca)
                )
             )

        return ( math.degrees(wca) % 360, ground_speed, )

    def geojson(self):
        end = self.end()
        lines = gj.LineString([
            (self.begin.longitude, self.begin.latitude),
            (end.longitude, end.latitude),
        ])
        feature = gj.Feature(geometry=lines)
        feature_collection = gj.FeatureCollection( [feature] )
        return gj.dumps(feature_collection, sort_keys=True)

def main():
    begin = (53.088, 6.0804,)
    leg1 = Leg(Point(begin), 212.0, 38.0)
    th, gs = leg1.e6b(100, 212, 20)
    print("th =", th)
    print("gs =", gs)
    #print(leg1.geojson())

if __name__ == "__main__":
    main()
