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
        self._begin = begin
        self._bearing = bearing
        self._distance = geodesic(nautical=distance)
        self._checkpoints = checkpoints

    def begin(self):
        return #self._begin

    def distance(self):
        return self._distance

    def bearing(self):
        return #self._bearing

    def end(self):
        endpos = self._distance.destination(self._begin, bearing=self._bearing)
        return endpos
        
    def geojson(self):
        end = self.end()
        lines = gj.LineString([
            (self._begin.longitude, self._begin.latitude),
            (end.longitude, end.latitude),
        ])
        feature = gj.Feature(geometry=lines)
        feature_collection = gj.FeatureCollection( [feature] )
        return gj.dumps(feature_collection, sort_keys=True)

def main():
    begin = (53.088, 6.0804,)
    leg1 = Leg(Point(begin), 212.0, 38.0)
    print(leg1.geojson())

if __name__ == "__main__":
    main()
