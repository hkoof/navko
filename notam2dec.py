#!/usr/bin/env python

import sys
import re

import argparse

pattern_lat = '([0-9]{2})([0-9]{2})([0-9]{2}){0,1}([NS])'
pattern_lon = '([0-9][0-9]{2})([0-9]{2})([0-9]{2}){0,1}([EW])'
pattern_coord = pattern_lat + ' ' + pattern_lon

re_coord = re.compile(pattern_coord)

def notam2dec(notam_coordinate_re_match):
    grp_coord = notam_coordinate_re_match.groups()
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
        description='Convert notam coordinates to decimal coordinates',
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', nargs=2, metavar=('LONGITUDE', 'LATITUDE'))
    group.add_argument('-f', metavar='INPUT_FILE')

    parser.add_argument(
        '--geojson',
        action='store_true',
        help='Write to geojson file (default stdout)',
    )
    args = parser.parse_args()

    notam_coords = list()
    if args.c:
        m_coord = re.match(re_coord, args.c[0] + ' ' + args.c[1])
        if m_coord == None:
            print(f'notam format error: {notam_coordinates}')
            sys.exit(2)

        dec_coords = notam2dec(m_coord)
        notam_coords.append(dec_coords)
    else: # required mutual exclusive args
        with open(args.file) as fd:
            content = fd.read().replace('\n', ' ')
        #for match in findall() # fixme

    if args.geojson:
        pass

    notam_coordinates = list()
    print(notam_coords)


if __name__ == "__main__":
    main()
