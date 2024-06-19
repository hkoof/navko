#!/usr/bin/env python

import argparse
import sys

import yaml

from typing import Union, Annotated 
from pydantic import BaseModel, Field, Discriminator, Tag
from pydantic import ValidationError 
#PositiveInt, TypeAdapter

class Point(BaseModel):
    name: str
    latitude: float
    longitude: float
    altitude: int = Field(default=None)

class Vector(BaseModel):
    name: str
    true_heading: Annotated[int, Field(gt=0, lt=360)]
    distance: float
    altitude: int = Field(default=None)

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
