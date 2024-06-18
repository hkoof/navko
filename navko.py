#!/usr/bin/env python

import argparse
import sys

import yaml

from pydantic import BaseModel

class Route(BaseModel):
    title: str
    altitude: int | None


def main():
    parser = argparse.ArgumentParser(
                    prog = 'navko',
                    description = 'E6B deluxe',)
    parser.add_argument('route_filename')
    args = parser.parse_args()
    routes_data = yaml.safe_load(open(args.route_filename))
    routes = list()
    for route_data in routes_data:
       route = Route(**route_data)
       routes.append(route)
    print(routes)

if __name__ == "__main__":
    main()
