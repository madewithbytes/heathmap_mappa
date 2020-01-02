#!/usr/bin/env python
import argparse

from mappa import engine


def main(state, file_path="data/PHLITL_2000/PHLITL_2000.shp"):
    if state.lower() == 'all':
        engine.render_all(file_path=file_path)
    else:
        engine.render(file_path=file_path, state=state)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("state")
    args = parser.parse_args()
    main(args.state)
