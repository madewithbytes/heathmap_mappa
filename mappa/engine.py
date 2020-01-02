import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import shapefile as shp

from structlog import get_logger
from collections import namedtuple

from mappa import config

logger = get_logger()


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

PALETTE_STEPS = 6
PALETTE_PINK = sns.cubehelix_palette(PALETTE_STEPS)
PALETTE_NAVY = sns.light_palette("navy", PALETTE_STEPS)
PALETTES = [
    PALETTE_PINK,
    PALETTE_NAVY,
]
FigurePoints = namedtuple("FigurePoints", ["min_x", "max_x", "min_y", "max_y"])


def read_shape_file(*, file_path, encoding="ISO-8859-1"):
    logger.info("shp.reading", file_path=file_path, encoding=encoding)
    return shp.Reader(file_path, encoding=encoding)


def zoom_plot(*, figure_points, padding=50000):
    fp = figure_points
    dx = fp.max_x - fp.min_x
    dy = fp.max_y - fp.min_y
    if dx > dy:
        adjustment = int(dx - dy) / 2
        left = fp.min_x - padding
        right = fp.min_x + padding + dx
        bottom = fp.min_y - padding - adjustment
        top = fp.min_y + padding + dx - adjustment
    else:
        adjustment = int(dy - dx) / 2
        left = fp.min_x - padding - adjustment
        right = fp.min_x + padding + dy - adjustment
        bottom = fp.min_y - padding
        top = fp.min_y + padding + dy
    logger.info("plot.zooming", left=left, right=right, bottom=bottom, top=top)
    plt.xlim((left, right))
    plt.ylim((bottom, top))


def split_points(points):
    x = [i[0] for i in points]
    y = [i[1] for i in points]
    return x, y


def get_color_from_legend(legend):
    config = dict(NOMENCLATURE).get(legend, 0)
    return PALETTES[config.palette][config.intensity]


def plot_shape_file(*, shape_file, figure):
    logger.info("plt.rendering", shape_file=shape_file.shapeName)
    figure = plt.figure()
    ax1 = figure.add_subplot()
    # Remove axis values:
    if not config.DEBUG:
        ax1.get_xaxis().set_visible(False)
        ax1.get_yaxis().set_visible(False)
    # Plot all shapes:
    for shape in shape_file.shapeRecords():
        x, y = split_points(shape.shape.points[:])
        ax1.plot(x, y, linewidth=0.2, color="k")
    return ax1


def highlight_dataframe_by_intensity(*, data_frame, shape_file, ax):
    """Colours data frame by intensity.
    Returns top, right, left, and bottom points by DataFrame."""
    for i, (pk, legend) in enumerate(
        zip(data_frame.index.array, data_frame.DPHLIL_LEY)
    ):
        shape_ex = shape_file.shape(pk)
        x_lon, y_lat = [], []
        for x, y in shape_ex.points:
            if i == 0:
                min_x, max_x = x, x
                min_y, max_y = y, y
            # Calculate min/max points:
            if x < min_x:
                min_x = x
            if x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y
            x_lon.append(x)
            y_lat.append(y)
        color = get_color_from_legend(legend)
        ax.fill(x_lon, y_lat, color=color)
    return FigurePoints(min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y)


def transform_shape_file_to_data_frame(*, shape_file):
    logger.info("shp.dataframing", shape_file=shape_file.shapeName)
    column_names = [r[0] for r in shape_file.fields][1:]
    records = shape_file.records()
    shape_points = [s.points for s in shape_file.shapes()]
    data_frame = pd.DataFrame(columns=column_names, data=records)
    data_frame = data_frame.assign(coords=shape_points)
    return data_frame


def get_data_frame_by_state(*, shape_file, state):
    data_frame = transform_shape_file_to_data_frame(shape_file=shape_file)
    data_frame = data_frame.query('EDO_LEY == "{}"'.format(state))
    return data_frame


def configure_plot(params=None, figsize=(10, 9)):
    config = {
        "style": "whitegrid",
        "palette": "pastel",
        "color_codes": True,
    }
    if params is not None:
        config.update(params)
    logger.info("seaborn.configuring", **config)
    sns.set(**config)
    sns.set_style("whitegrid", {"axes.grid": False, "font.family": "DejaVu Sans",})
    sns.mpl.rc("figure", figsize=figsize)
    sns.palplot(PALETTE_PINK)
    sns.set_palette(PALETTE_PINK)


def render(*, file_path, state):
    state = config.normalize_state_name(state)
    configure_plot()
    shape_file = read_shape_file(file_path=file_path)
    data_frame = get_data_frame_by_state(shape_file=shape_file, state=state)
    figure = plt.figure()
    ax = plot_shape_file(shape_file=shape_file, figure=figure)
    figure_points = highlight_dataframe_by_intensity(
        data_frame=data_frame, shape_file=shape_file, ax=ax
    )
    zoom_plot(figure_points=figure_points)
    export_plot(name=state)


def render_all(*, file_path):
    for state in config.STATES:
        render(file_path=file_path, state=state)


def export_plot(*, name, file_format="png"):
    file_name = "{}.{}".format(name, file_format)
    plt.savefig(fname=file_name, format=file_format)
    logger.info("image.saved", file_name=file_name)
