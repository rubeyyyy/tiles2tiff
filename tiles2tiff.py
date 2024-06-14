import os
import glob
import shutil
from osgeo import gdal
from conversion import bbox_to_xyz, tile_edges

temp_dir = os.path.join(os.getcwd(), "temp")

def fetch_tile(x, y, z, tile_dir):
    tile_path = os.path.join(tile_dir, str(z), str(x), f"{y}.png")
    if not os.path.exists(tile_path):
        return None
    return tile_path


def merge_tiles(input_pattern, output_path):
    vrt_path = temp_dir + "/tiles.vrt"
    gdal.BuildVRT(vrt_path, glob.glob(input_pattern))
    gdal.Translate(output_path, vrt_path)


def georeference_raster_tile(x, y, z, path, tms):
    bounds = tile_edges(x, y, z, tms)
    gdal.Translate(
        os.path.join(temp_dir, f"{temp_dir}/{x}_{y}_{z}.tif"),
        path,
        outputSRS="EPSG:4326",
        outputBounds=bounds,
        # rgbExpand="rgb",
    )


def convert(tile_dir, output_dir, bounding_box, zoom):
    lon_min, lat_min, lon_max, lat_max = bounding_box

    x_min, x_max, y_min, y_max = bbox_to_xyz(
        lon_min, lon_max, lat_min, lat_max, zoom, tms=False
    )

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Fetching & georeferencing {(x_max - x_min + 1) * (y_max - y_min + 1)} tiles")
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            try:
                png_path = fetch_tile(x, y, zoom, tile_dir)
                if png_path is None:
                    print(f"Error, tile {x},{y} not found")
                    continue
                print(f"{x},{y} fetched")
                georeference_raster_tile(x, y, zoom, png_path, tms=False)
            except OSError:
                print(f"Error, failed to process {x},{y}")
                pass

    print("Resolving and georeferencing of raster tiles complete")
    print("Merging tiles")
    merge_tiles(temp_dir + "/*.tif", output_dir + "/merged.tif")
    print("Merge complete")

    shutil.rmtree(temp_dir)

tile_dir= '/home/rubi/Desktop/DamageAssestment/tiles/20'
output= '/home/rubi/Desktop/NAXA/tiles2tiff/output'
bound= (82.27679590064035, 
    28.69555032008098, 
    82.28144880914303, 
    28.70131964736974)
zoom= 20

#usage
convert(tile_dir, output, bound, zoom)