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

# Base class for different kind of checkpoints
#


class CheckPoint(BaseModel):
    name: str
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

    @staticmethod
    def true_airspeed(ias, alt):
        # Rule of thumb:
        # Add about 2% to IAS for every 1000 ft altitude
        #
        return round(ias + 0.02 * alt * ias / 1000)


# class Point:
#
class Point(CheckPoint):
    latitude: float
    longitude: float

    def get_vector(self, origin):
        '''Get Vector object from origin to self
           Args:
             origin : Point
           Returns:
             Vector
        '''
        geodict = Geodesic.WGS84.Inverse(
            origin.get_latitude(),
            origin.get_longitude(),
            self.latitude,
            self.longitude,
        )
        azi = round(geodict['azi1']) % 360
        if azi < 0:
            azi = 360 - azi
        vector = Vector(
            name=self.name,
            true_track=azi,
            distance=geodict['s12'] / 1852,
        )
        return vector

    def get_latitude(self): return self.latitude
    def get_longitude(self): return self.longitude
    def get_true_track(self): return self._true_track
    def get_distance(self): return self._distance

    def __str__(self):
        deg_lat, min_lat, sec_lat = self.DMS(self.latitude)
        hemi_lat = 'N' if deg_lat > 0 else 'S'
        deg_lat = abs(deg_lat)

        deg_lon, min_lon, sec_lon = self.DMS(self.longitude)
        hemi_lon = 'E' if deg_lon > 0 else 'W'
        deg_lon = abs(deg_lon)

        return f'{self.name}: {deg_lat}\N{DEGREE SIGN}{min_lat}\N{PRIME}{sec_lat:.1f}\N{DOUBLE PRIME}{hemi_lat} {deg_lon}\N{DEGREE SIGN}{min_lon}\N{PRIME}{sec_lon:.1f}\N{DOUBLE PRIME}{hemi_lon}'


class Vector(CheckPoint):
    true_track: Annotated[int, Field(gt=0, le=360, default=None)]
    distance: float

    def get_point(self, origin):
        distance_meters = self.distance * 1852
        geodict = Geodesic.WGS84.Direct(
            origin.get_latitude(),
            origin.get_longitude(),
            self.true_track,
            distance_meters,
        )
        point = Point(
            name=self.name,
            latitude=geodict['lat2'],
            longitude=geodict['lon2'],
        )
        return point

    def get_latitude(self): return self._latitude
    def get_longitude(self): return self._longitude
    def get_true_track(self): return self.true_track
    def get_distance(self): return self.distance

    def __str__(self):
        if not self.true_track:
            return ''
        return (f'{self.name}: {self.true_track}\N{DEGREE SIGN}'
                '{self.distance:.1f} NM'
                )


class NavigationLog:
    def make_sparse(self):
        '''Set selected values that are not different from the previous leg to None'''

        last_vals = {
            'tt': None,
            'alt': None,
            'tas': None,
            'wca': None,
            'th': None,
            'mh': None,
            'gs': None,
        }

        for leg in self.legs:
            if leg.__dict__['tt'] == last_vals['tt']:
                for attr in ('tt', 'wca', 'th', 'mh', 'gs'):
                    leg.__dict__[attr] = None
            else:
                for attr in ('tt', 'wca', 'th', 'mh', 'gs'):
                    last_vals[attr] = leg.__dict__[attr]

            for attr in ('alt', 'tas'):
                if leg.__dict__[attr] == last_vals[attr]:
                    leg.__dict__[attr] = None
                else:
                    last_vals[attr] = leg.__dict__[attr]

    def __str__(self):
        title = (
            f'{self.title:<14}\n'
            f'IAS: {self.ias:<14}'
            f'Wind: {self.wind_direction}/{self.wind_speed} kt {"":<14}'
            f'Variation: {self.var:<+14}'
            '\n'
        )
        header = f'Leg Acc {"Checkpoint":<30} Alt  MH  TH  WCA TT  TAS  GS Leg Acc\n'

        start = f'  0   0 {self.start_name:<30}   -   -   -   -   -   -   -    0   0\n'

        line = '-' * (len(header) - 1) + '\n'
        s = title + line + header + line + start

        for leg in self.legs:
            s = s + str(leg)

        s += line
        return s


class Leg:
    def __str__(self):
        s = str()

        s += f'{self.time:>3}'
        s += f'{self.time_acc:>4}'
        s += f' {self.name:<30}'

        s += f'{self.alt:>5}' if self.alt else f'{"":>5}'
        s += f'{self.mh:>4}' if self.mh else f'{"":>4}'
        s += f'{self.th:>4}' if self.th else f'{"":>4}'
        s += f'{self.wca:>+4d}' if self.wca else f'{"":>4}'
        s += f'{self.tt:>4}' if self.tt else f'{"":>4}'
        s += f'{self.tas:>4}' if self.tas else f'{"":>4}'
        s += f'{self.gs:>4}' if self.gs else f'{"":>4}'

        s += f'{self.dist:>4.0f}'
        s += f'{self.dist_acc:>4.0f}'
        s += '\n'

        return s


class Route(BaseModel):
    title: str
    start: Point
    checkpoints: list[
        Annotated[
            Union[
                Annotated[Point, Tag('point')],
                Annotated[Vector, Tag('vector')],
            ],
            Discriminator(lambda v: 'point' if v.get(
                'latitude') else 'vector'),
        ]
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # assuming at least one, raising exception is correct
        tt = self.checkpoints[0]
        alt = self.checkpoints[0].altitude
        if alt == None:
            alt = 1500

        # Resolve Vector attributes for Points and the other way around.
        #
        current_point = self.start
        for checkpoint in self.checkpoints:
            if isinstance(checkpoint, Vector):
                if checkpoint.true_track:
                    tt = checkpoint.true_track
                else:
                    checkpoint.true_track = tt

                point = checkpoint.get_point(current_point)
                checkpoint._latitude = point.latitude
                checkpoint._longitude = point.longitude
            else:
                vector = checkpoint.get_vector(current_point)
                checkpoint._true_track = vector.true_track
                checkpoint._distance = vector.distance

            if checkpoint.altitude:
                alt = checkpoint.altitude
            else:
                checkpoint.altitude = alt

            current_point = checkpoint

    @staticmethod
    def e6b(true_track, true_airspeed, wind_direction, wind_speed):
        tt = math.radians(true_track)
        wd = math.radians(wind_direction)

        wca = math.asin((wind_speed / true_airspeed) * math.sin(wd - tt))
        wind_correction_angle = math.degrees(wca)

        ground_speed = math.sqrt(
            true_airspeed**2 + wind_speed**2 -
            (
                2 * true_airspeed * wind_speed * math.cos(tt - wd + wca)
            )
        )

        wca_deg = round(math.degrees(wca))
        if wca_deg > 180:
            wca_deg = 360 - wca_deg

        return (wca_deg, round(ground_speed), )

    def navigation_log(self, ias, wind_direction=0, wind_speed=0, variation=0):
        navlog = NavigationLog()

        # navlog global:
        #
        navlog.title = self.title
        navlog.wind_direction = wind_direction
        navlog.wind_speed = wind_speed
        navlog.var = variation
        navlog.ias = ias

        navlog.start_name = self.start.name

        navlog.legs = list()
        navlog.leg_dist_acc = 0
        navlog.leg_time_acc = 0

        dist_acc = 0
        time_acc = 0
        current_point = self.start
        previous_leg = None
        for checkpoint in self.checkpoints:
            leg = Leg()

            leg.dist = checkpoint.get_distance()
            leg.tt = checkpoint.get_true_track()
            dist_acc += leg.dist
            leg.dist_acc = dist_acc

            leg.name = checkpoint.name

            leg.alt = checkpoint.altitude
            leg.tas = checkpoint.true_airspeed(ias, leg.alt)

            leg.wca, leg.gs = self.e6b(
                leg.tt, leg.tas, wind_direction, wind_speed)
            leg.th = leg.tt + leg.wca
            leg.mh = leg.th - navlog.var

            leg.time = math.floor(60 * leg.dist / leg.gs)
            time_acc += leg.time
            leg.time_acc = time_acc

            navlog.legs.append(leg)
            current_point = checkpoint
            previous_leg = leg

        return navlog

    def geojson(self):
        def append_line_feature(begin, end):
            line = gj.LineString([
                (begin.get_longitude(), begin.get_latitude()),
                (end.get_longitude(), end.get_latitude()),
            ])
            features.append(gj.Feature(geometry=line))

        points = list()
        features = list()
        current_point = leg_begin = self.start
        current_tt = self.checkpoints[0].get_true_track()

        for checkpoint in self.checkpoints:
            tt = checkpoint.get_true_track()
            if tt != current_tt:
                append_line_feature(leg_begin, current_point)
                current_tt = tt
                leg_begin = current_point

            points.append(checkpoint)
            current_point = checkpoint

        append_line_feature(leg_begin, current_point)
        features.append(gj.Feature(geometry=gj.Point(
            (self.start.longitude, self.start.latitude,))))

        for point in points:
            feature = gj.Feature(
                geometry=gj.Point(
                    (point.get_longitude(), point.get_latitude(),)),
                properties={
                    'name': point.name,
                }
            )
            features.append(feature)

        feature_collection = gj.FeatureCollection(features)
        return gj.dumps(feature_collection)


def main():
    parser = argparse.ArgumentParser(
        prog='navko',
        description='E6B deluxe',
    )
    parser.add_argument('route_filename')
    parser.add_argument(
        '--geojson',
        help='Dump route to geojson file',
    )
    parser.add_argument(
        '-a',
        '--navlog-stdout',
        action='store_true',
        help='Print navigation log to stdout',
    )
    parser.add_argument(
        '-p',
        '---navlog-pdf',
        help='Write navigation log to PDF file',
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
    parser.add_argument(
        '-r',
        '--sparse',
        action='store_true',
        help='Skip leg attribute values that are the same as the previous leg',
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

    if args.navlog_stdout or args.navlog_pdf:
        for route in routes:
            wind_dir, wind_spd = args.wind if args.wind else (0, 0)
            navlog = route.navigation_log(args.ias, wind_dir, wind_spd, 2)
            if args.sparse:
                navlog.make_sparse()
            if args.navlog_stdout:
                print(navlog)
            if args.navlog_pdf:
                from navkopdf import navlog2pdf
                navlog2pdf(navlog, args.navlog_pdf)


if __name__ == "__main__":
    main()
