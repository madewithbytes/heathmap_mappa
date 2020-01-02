#!/usr/bin/env python

import pandas as pd
import shapefile as shp


def read_shape_file(*, file_path, encoding="ISO-8859-1"):
    return shp.Reader(file_path, encoding=encoding)


def prepare_data_frame(*, shape_file):
    column_names = [r[0] for r in shape_file.fields][1:]
    records = shape_file.records()
    shape_points = [s.points for s in shape_file.shapes()]
    data_frame = pd.DataFrame(columns=column_names, data=records)
    data_frame = data_frame.assign(coords=shape_points)
    return data_frame


def inspect_data_frame(*, data_frame):
    print("Available states: {}".format(set(data_frame.EDO_LEY)))
    print("Available values: {}".format(set(data_frame.DPHLIL_LEY)))


def main():
    shape_file = read_shape_file(file_path="./data/PHLITL_2000/PHLITL_2000.shp")
    data_frame = prepare_data_frame(shape_file=shape_file)
    inspect_data_frame(data_frame=data_frame)


if __name__ == "__main__":
    main()
