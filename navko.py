#!/usr/bin/env python

import argparse
import sys
import math

import yaml

from typing import Union, Annotated
from pydantic import BaseModel, Field, Discriminator, Tag
from pydantic import ValidationError
#PositiveInt, TypeAdapter

import geojson as gj

from geographiclib.geodesic import Geodesic

# from geopy.distance import geodesic
# import geopy.point


# class Point:
# Not to be confused with geopy.point.Point which is also used here
#
class Point(BaseModel):
    name: str
    latitude: float
    longitude: float
    altitude: int = Field(default=None)

    @staticmethod
    def DMS(coordinate):
        degrees = math.floor(coordinate)
        rest = abs(coordinate) - degrees
        minutes = math.floor(60 * rest)
        rest -= 60 * minutes
        seconds = round(3600 * rest)
        return (degrees, minutes, seconds)

    def get_vector(self, origin):
        geodict = Geodesic.WGS84.Inverse(
                origin.latitude,
                origin.longitude,
                self.latitude,
                self.longitude,
                )
        vector = Vector(
                self.name,
                geodict['azi1'],
                geodict['s12'],
                self.altitude,
                )
        return vector

    def __str__(self):
        deg_lat, min_lat, sec_lat = self.DMS(latitude)
        hemi_lat = 'N' if deg_lat > 0 else 'S'
        deg_lat = abs(deg_lat)

        deg_lon, min_lon, sec_lon = self.DMS(longitude)
        hemi_lon = 'E' if deg_lon > 0 else 'W'
        deg_lon = abs(deg_lon)

        return f'{deg_lat}\N{DEGREE SIGN}{min_lat}\N{PRIME}{sec_lat}\N{DOUBLE PRIME}{hemi_lat} {deg_lon}\N{DEGREE SIGN}{min_lon}\N{PRIME}{sec_lon}\N{DOUBLE PRIME}{hemi_lon}'


class Vector(BaseModel):
    name: str
    true_track: Annotated[int, Field(gt=0, lt=360, default=None)]
    distance: float
    altitude: int = Field(default=None)

    def get_point(self, origin):
        distance_meters = self.distance * 1.852
        geodict = Geodesic.WGS84.Direct(
                origin.latitude,
                origin.longitude,
                self.true_track,
                distance_meters,
                )
        point = Point(
                self.name,
                geodict['lat2'],
                geodict['lon2'],
                self.altitude,
                )
        return point


class Route(BaseModel):
    title: str
    start: Point
    checkpoints: list[
            Annotated[
                Union[
                    Annotated[Point, Tag('point')],
                    Annotated[Vector, Tag('vector')],
                ],
                Discriminator(lambda v: 'point' if v.get('latitude') else 'vector'),
            ]
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for checkpoint in self.checkpoints:
            print("DBG", checkpoint)
        print()

    @staticmethod
    def e6b(true_track, true_airspeed, wind_direction, wind_speed):   #FIXME
        tt = math.radians(true_track)
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


def main():
    parser = argparse.ArgumentParser(
                    prog = 'navko',
                    description = 'E6B deluxe',)
    parser.add_argument('route_filename')
    args = parser.parse_args()
    routes_data = yaml.load(open(args.route_filename), Loader=yaml.BaseLoader)
    routes = list()
    for route_data in routes_data:
        try:
            route = Route(**route_data)
            routes.append(route)
        except ValidationError as e:
            print(e)
    print(routes)

if __name__ == "__main__":
    main()
