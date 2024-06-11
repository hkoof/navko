#!/usr/bin/env python

import math

import geojson as gj

from geopy.distance import geodesic
import geopy.point


class Point(geopy.point.Point):
    def __init__(self, latitude=None, longitude=None, label=''):
        self.label = label
        super().__init__(altitude=None)

class Leg(list):
    def __init__(self, startpoint, bearing, distance, checkpoints=[]):
        # Leg: list of Points.
        #
        # The points parameter should be a sequence of tuples:
        #  ( <label>, <distance from begin> )
        # Internally these are converted to Points. 
        #
        self.bearing = bearing
        self.distance = geodesic(nautical=distance)
        end = self.distance.destination(self.begin, bearing=self.bearing)
        # FIXME: validate begin
        self._points = list(begin)
        for label, dist in checkpoints:




    def e6b(self, true_airspeed, wind_direction, wind_speed):
        tt = math.radians(self.bearing)  
        wd = math.radians(wind_direction + 180)

        wca = math.asin( (wind_speed / true_airspeed) * math.sin(wd - tt) )
        wind_correction_angle = math.degrees(wca)
        
        ground_speed = math.sqrt(
                true_airspeed**2 + wind_speed**2 -
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
        feature1 = gj.Feature(geometry=lines)
        feature2 = gj.Feature(geometry=gj.MultiPoint(self.checkpoints),
                              properties = {'name': 'QrQ', 'number': 7}
                              )
        feature_collection = gj.FeatureCollection( [feature1, feature2] )
        return gj.dumps(feature_collection) #, sort_keys=True)

def main():
    begin = (53.088, 6.0804,)
    leg1 = Leg(Point(begin), 212.0, 38.0, [ (6.08,53.08), (6.09,53.09,) ] )
    th, gs = leg1.e6b(100, 212, 20)
    #print("th =", th)
    #print("gs =", gs)
    print(leg1.geojson())

if __name__ == "__main__":
    main()
