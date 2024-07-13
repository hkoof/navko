#!/usr/bin/env python

import argparse
import sys
import math

import yaml

from typing import Union, Annotated, Optional
from pydantic import BaseModel, Field, Discriminator, Tag
from pydantic import ValidationError

import geojson as gj

from geographiclib.geodesic import Geodesic


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
        '''Convert float coordinate to DMS
           Args:
             coordinate: float
           Returns:
              tuple(int, int, float) for (Degrees, Minutes, Seconds).
        '''
        degrees = math.floor(coordinate)
        rest = abs(coordinate) - abs(degrees)
        minutes = math.floor(60 * rest)
        rest = 60 * rest - minutes
        seconds = 60 * rest
        return (degrees, minutes, seconds)

    def get_vector(self, origin):
        '''Get Vector object from origin to self
           Args:
             origin : Point
           Returns:
             Vector
        '''
        geodict = Geodesic.WGS84.Inverse(
                origin.latitude,
                origin.longitude,
                self.latitude,
                self.longitude,
                )
        azi = round(geodict['azi1'])
        if azi < 0 :
            azi = 360 -1
        vector = Vector(
                name=self.name,
                true_track=azi,
                distance=geodict['s12'],
                )
        return vector

    def __str__(self):
        deg_lat, min_lat, sec_lat = self.DMS(self.latitude)
        hemi_lat = 'N' if deg_lat > 0 else 'S'
        deg_lat = abs(deg_lat)

        deg_lon, min_lon, sec_lon = self.DMS(self.longitude)
        hemi_lon = 'E' if deg_lon > 0 else 'W'
        deg_lon = abs(deg_lon)

        return f'{self.name}: {deg_lat}\N{DEGREE SIGN}{min_lat}\N{PRIME}{sec_lat:.1f}\N{DOUBLE PRIME}{hemi_lat} {deg_lon}\N{DEGREE SIGN}{min_lon}\N{PRIME}{sec_lon:.1f}\N{DOUBLE PRIME}{hemi_lon}'


class Vector(BaseModel):
    name: str
    true_track: Annotated[int, Field(gt=0, lt=360, default=None)]
    distance: float
    altitude: int = Field(default=None)

    def get_point(self, origin):
        distance_meters = self.distance * 1852
        geodict = Geodesic.WGS84.Direct(
                origin.latitude,
                origin.longitude,
                self.true_track,
                distance_meters,
            )
        point = Point(
                name=self.name,
                latitude=geodict['lat2'],
                longitude=geodict['lon2'],
            )
        return point

    def __str__(self):
        if not self.true_track:
            return ''
        return f'{self.name}: {self.true_track}\N{DEGREE SIGN} {self.distance:.1f} NM'


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
        tt = self.checkpoints[0]  # assuming at least one, raising exception is correct
        for checkpoint in self.checkpoints:
            if isinstance(checkpoint, Vector):
                if checkpoint.true_track:
                    tt = checkpoint.true_track
                else:
                    checkpoint.true_track = tt

    @staticmethod
    def e6b(true_track, true_airspeed, wind_direction, wind_speed):
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

    def navigation_log(self, ias, wind_direction=0, wind_speed=0, variation=0):

        #route_altitude = self.altitude  # TODO
        tas = ias                       # TODO
        var = variation        # TODO

        leg_dist_acc = 0
        leg_time_acc = 0
        current_point = self.start

        for checkpoint in self.checkpoints:
            print ("DBG", checkpoint)
            if isinstance(checkpoint, Vector):
                leg_dist = checkpoint.distance
                tt = checkpoint.true_track
            else:
                leg_dist = checkpoint.get_vector(current_point).distance
                tt = checkpoint.get_vector(current_point).true_track
            leg_dist_acc += leg_dist

            name = checkpoint.name
            #altitude = checkpoint.altitude if checkpoint.altitiude else route_altitude # TODO

            wca, gs = self.e6b(tt, tas, wind_direction, wind_speed)
            th = tt + wca
            mh = th - var
            
            leg_time = math.floor(60 * leg_dist / tas)
            leg_time_acc += leg_time

            current_point = checkpoint




    def geojson(self):
        def append_line_feature(begin, end):
            line = gj.LineString([
                (begin.longitude, begin.latitude),
                (end.longitude, end.latitude),
            ])
            features.append(gj.Feature(geometry=line))

        points = list()
        features = list()
        current_point = leg_begin = self.start
        if isinstance(self.checkpoints[0], Vector):
            current_tt = self.checkpoints[0].true_track
        else:
            current_tt = self.checkpoints[0].get_vector(self.start).true_track

        for checkpoint in self.checkpoints:
            if isinstance(checkpoint, Vector):
                point = checkpoint.get_point(current_point)
                tt = checkpoint.true_track
            else:   # assumes instance is always Point instance from here
                point = checkpoint
                tt = checkpoint.get_vector(current_point).true_track

            points.append(point)

            if tt != current_tt:
                append_line_feature(leg_begin, current_point)
                current_tt = tt
                leg_begin = current_point

            current_point = point

        append_line_feature(leg_begin, current_point)
        features.append(gj.Feature(geometry=gj.Point( (self.start.longitude, self.start.latitude,) )))

        for point in points:
            feature = gj.Feature(
                    geometry=gj.Point((point.longitude, point.latitude,)),
                    properties = {
                        'name': point.name,
                    }
                )
            features.append(feature)

        feature_collection = gj.FeatureCollection( features )
        return gj.dumps(feature_collection)

def main():
    parser = argparse.ArgumentParser(
                    prog = 'navko',
                    description = 'E6B deluxe',
                    )
    parser.add_argument('route_filename')
    parser.add_argument(
            '--geojson',
            help='Dump route to geojson file',
            )
    parser.add_argument(
            '-n',
            '--navigation-log',
            action='store_true',
            help='Create navigation log',
            )
    parser.add_argument(
            '-s',
            '--ias',
            '--indicated-airspeed',
            type=int,
            default=100,
            help='Specify indicated air speed',
            )
    parser.add_argument(
            '-w',
            '--wind',
            nargs=2,
            type=int,
            default=(0, 0),
            metavar=('DIRECTION', 'SPEED'),
            help='Specify wind vector',
            )
    args = parser.parse_args()

    routes_data = yaml.load(open(args.route_filename), Loader=yaml.BaseLoader)
    routes = list()
    for route_data in routes_data:
        try:
            route = Route(**route_data)
            routes.append(route)
        except ValidationError as e:
            print(e)

    if args.geojson:
        with open(args.geojson, 'w') as output:
            for route in routes:
                print(route.geojson(), file=output)

    if args.navigation_log:
        for route in routes:
            wind_dir, wind_spd = args.wind if args.wind else (0, 0)
            navlog = route.navigation_log(args.ias, wind_dir, wind_spd)


if __name__ == "__main__":
    main()
