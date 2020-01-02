#!/usr/bin/env python
import shapefile as shp


def read_shape_file(*, file_path, encoding="ISO-8859-1"):
    return shp.Reader(file_path, encoding=encoding)


def inspect_shape_file(*, shape_file):
    column_names = [r[0] for r in shape_file.fields][1:]
    print("Columns available: `{}`".format(column_names))
    print("Total records: {}".format(len(shape_file)))


def inspect_record(*, record, shape):
    print("Municipality: {}".format(record.MPO_LEY))
    print("State: {}".format(record.EDO_LEY))
    print("Total native speakers: {}".format(record.DPHLIL_LEY))
    print("Shape points (sample): `{}`".format(shape.points[:3]))


def main():
    shape_file = read_shape_file(file_path="./data/PHLITL_2000/PHLITL_2000.shp")
    inspect_shape_file(shape_file=shape_file)
    # Fetch the first record for inspection:
    record = shape_file.records()[0]
    shape = shape_file.shapes()[0]
    inspect_record(record=record, shape=shape)


if __name__ == "__main__":
    main()
