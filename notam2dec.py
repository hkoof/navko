#!/usr/bin/env python

import sys
import re

def main():
    nargs = len(sys.argv)
    if nargs == 3:
        lat_notam = sys.argv[1]
        lon_notam = sys.argv[2]
    else:
        print(f'Usage: {sys.argv[0]} <coordinates in notam format>', file=sys.stderr)
        sys.exit(1)

    #print("lat: ", lat_notam)
    #print("lon: ", lon_notam)

    re_lat = re.compile('([0-9]{2})([0-9]{2})([0-9]{2}){0,1}([NS])')
    re_lon = re.compile('([0-9][0-9]{2})([0-9]{2})([0-9]{2}){0,1}([EW])')

    m_lat = re.match(re_lat, lat_notam)
    if m_lat == None:
        print(f'notam format error in latitude part: {lat_notam}')
        sys.exit(2)

    m_lon = re.match(re_lon, lon_notam)
    if m_lon == None:
        print(f'notam format error in longitude part: {lon_notam}')
        sys.exit(2)

    grp_lat = m_lat.groups()
    lat_dec = (1 if grp_lat[3] == 'N' else -1) * (
                  int(grp_lat[0]) +
                  int(grp_lat[1]) / 60.0 +
                  int(grp_lat[2]) / 3600.0
                )

    grp_lon = m_lon.groups()
    lon_dec = (1 if grp_lon[3] == 'E' else -1) * (
                  int(grp_lon[0]) +
                  int(grp_lon[1]) / 60.0 +
                  int(grp_lon[2]) / 3600.0
                )

    print(f'{lat_dec:.5f} {lon_dec:.5f}')

if __name__ == "__main__":
    main()
