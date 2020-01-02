#!/usr/bin/env python
from collections import namedtuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import shapefile as shp


def read_shape_file(*, file_path, encoding="ISO-8859-1"):
    return shp.Reader(file_path, encoding=encoding)


def prepare_data_frame(*, shape_file):
    """Transform the shapefile into a panda's DataFrame object."""
    column_names = [r[0] for r in shape_file.fields][1:]
    records = shape_file.records()
    shape_points = [s.points for s in shape_file.shapes()]
    data_frame = pd.DataFrame(columns=column_names, data=records)
    data_frame = data_frame.assign(coords=shape_points)
    return data_frame


# Use seaborn to generate colour palettes to be used in the heatmap:
PALETTE_STEPS = 6
PALETTE_PINK = sns.cubehelix_palette(PALETTE_STEPS)
PALETTE_NAVY = sns.light_palette("navy", PALETTE_STEPS)
PALETTES = [
    PALETTE_PINK,
    PALETTE_NAVY,
]

# Generate a configuration nomenclature indicating intensity and palette to be
# used by matplotlib to plot the figures:
NomConfig = namedtuple("NomConfig", ["intensity", "palette"])
NOMENCLATURE = [
    ("Sin poblacion hablante de lengua indigena", NomConfig(intensity=0, palette=0)),
    ("Menor de 2,500", NomConfig(intensity=1, palette=0)),
    ("De 2,500 a 4,999", NomConfig(intensity=2, palette=0)),
    ("De 5,000 a 14,999", NomConfig(intensity=3, palette=0)),
    ("De 15,000 y mas", NomConfig(intensity=0, palette=0)),
    ("Menor de 2,500 y de 2,500 a 4,999", NomConfig(intensity=2, palette=1)),
    ("Menor de 2,500 y de 5,000 a 14,999", NomConfig(intensity=3, palette=1)),
    ("De 2,500 a 4,999 y de 5,000 a 14,999", NomConfig(intensity=4, palette=1)),
    ("De 5,000 a 14,999 y de 15,000 y mas", NomConfig(intensity=5, palette=1)),
]


def plot_map_render_shape_file(*, shape_file):
    """Renders the full figure of the shape file"""
    figure = plt.figure()
    ax1 = figure.add_subplot()
    for shape in shape_file.shapeRecords():
        points = shape.shape.points[:]
        x = [i[0] for i in points]
        y = [i[1] for i in points]
        ax1.plot(x, y, linewidth=0.2, color="k")
    return ax1


def get_color_from_legend(legend):
    """Uses the legend and config to determine the colour for the heatmap."""
    config = dict(NOMENCLATURE).get(legend, 0)
    return PALETTES[config.palette][config.intensity]


def color_shape_by_intensity(*, shape_file, data_frame, ax):
    """Uses the shape legend to fill in the shape with the expected colour."""
    for i, (pk, legend) in enumerate(zip(data_frame.index.array, data_frame.DPHLIL_LEY)):
        shape_ex = shape_file.shape(pk)
        color = get_color_from_legend(legend)
        x_lon, y_lat = [], []
        for x, y in shape_ex.points:
            x_lon.append(x)
            y_lat.append(y)
        ax.fill(x_lon, y_lat, color=color)


FigurePoints = namedtuple("FigurePoints", ["left", "right", "top", "bottom"])


def zoom_plot(*, fp, padding=50000):
    """Zooms the image using the given points."""
    left = fp.left - padding
    right = fp.right + padding
    bottom = fp.bottom - padding
    top = fp.top + padding
    plt.xlim((left, right))
    plt.ylim((bottom, top))


def main():
    shape_file = read_shape_file(file_path="./data/PHLITL_2000/PHLITL_2000.shp")
    data_frame = prepare_data_frame(shape_file=shape_file)
    data_frame = data_frame.query('EDO_LEY == "{}"'.format('Oaxaca'))
    ax1 = plot_map_render_shape_file(shape_file=shape_file)
    color_shape_by_intensity(shape_file=shape_file, data_frame=data_frame, ax=ax1)
    # FigurePoint values were calculated manually using the x/y labels:
    figure_points = FigurePoints(left=2319225, right=2915448, top=2265814, bottom=1669590)
    zoom_plot(fp=figure_points)
    plt.show()


if __name__ == "__main__":
    main()
