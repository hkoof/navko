#!/usr/bin/env python

import sys
import re

import argparse

pattern_lat = '([0-9]{2})([0-9]{2})([0-9]{2}){0,1}([NS])'
pattern_lon = '([0-9][0-9]{2})([0-9]{2})([0-9]{2}){0,1}([EW])'
pattern_coord = pattern_lat + ' ' + pattern_lon

re_coord = re.compile(pattern_coord)

def notam2dec(notam_coordinates):

    print("DBG: coord: ", notam_coordinates)

    m_coord = re.match(re_coord, notam_coordinates)
    if m_coord == None:
        print(f'notam format error: {notam_coordinates}')
        sys.exit(2)

    grp_coord = m_coord.groups()
    lat_dec = (1 if grp_coord[3] == 'N' else -1) * (
                  int(grp_coord[0]) +
                  int(grp_coord[1]) / 60.0 +
                  int(grp_coord[2]) / 3600.0
                )
    lon_dec = (1 if grp_coord[7] == 'E' else -1) * (
                  int(grp_coord[4]) +
                  int(grp_coord[5]) / 60.0 +
                  int(grp_coord[6]) / 3600.0
                )
    return f'{lat_dec:.5f} {lon_dec:.5f}'


def main():
    parser = argparse.ArgumentParser(
        prog='notam_coordinates',
        description='Convert notam coordinates',
    )
    parser.add_argument('-c', '--coordinates', nargs=2)
    parser.add_argument('-f', '--file')
    parser.add_argument(
        '--geojson',
        help='Write to geojson file',
    )
    args = parser.parse_args()

    if args.coordinates:
        dec_coords = notam2dec(args.coordinates[0] + ' ' + args.coordinates[1])
        print(dec_coords)
        sys.exit(0)

    if args.geojson:
        with open(args.geojson, 'w') as output:
            for route in routes:
                print(route.geojson(), file=output)

    notam_coordinates = list()


if __name__ == "__main__":
    main()
