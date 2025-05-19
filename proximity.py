"""This contins a single function to caluate the Euclidian
   distance from a value in a numpy ratser, using a rasterio
   object as a template. It matches GDAL's 'proximity' function."""

import math
import rasterio
from scipy import spatial
import numpy as np

def proximity(raster, rasterised, value):
    """Calculate distance to source pixel value in every
    cell of the raster.

    Calculates Euclidian distance. Matches GDAL's "proximity" function.

    Input: raster = rastioio raster object used as template
           rasterised = a numpy array
           value = the values in raster that are used as target 
                    (i.e. where distance will == 0)

    Output: A numpy array with dimensions of the input raster with shortest
            distance to any pixels in the input raster of value.

    Example usage:
        raster = rasterio.open("Rasterized_polygon.tif")
        distance = proximity(raster, 1)
    """

    # pylint: disable=too-many-locals
    geo_transform = raster.transform
    pixel_size_x = geo_transform[0]
    pixel_size_y =-geo_transform[4]
    pixel_distance = math.sqrt(pixel_size_x * pixel_size_y)

    height, width = rasterised.shape # Find the height and width of the array
    cols, rows = np.meshgrid(np.arange(width), np.arange(height))
    x_coordinates, y_coordinates = rasterio.transform.xy(raster.transform, rows, cols)
    #They are actually lists, convert them to arrays
    xcoords = np.array(x_coordinates)
    ycoords = np.array(y_coordinates)

    # find coords of points that have the target value in the rasterised raster
    source_coords = []
    where_result = np.where(rasterised == value)
    print(f"rasterised.shape: {rasterised.shape}")
    print(f"value: {value}")
    print(f"np.where(rasterised == value): {where_result}")
    if where_result[0].size > 0: # Check if any values were found
        for r, c in zip(*where_result):
            index = r * width + c
            print(f"r: {r}, c: {c}")  # Add this
            print(f"xcoords.shape: {xcoords.shape}, ycoords.shape: {ycoords.shape}")  # And this
            source_coords.append([xcoords[index], ycoords[index]])

    # now create all coords in the raster where we want distance
    target_coords = []
    for r in range (height):
        for c in range (width):
            index = r * width + c
            target_coords.append([xcoords[index], ycoords[index]])

    source_coords = np.array(source_coords)
    target_coords = np.array(target_coords)

    distance = np.ones((height,width))*float('inf')
    print(f"source_coords.shape: {source_coords.shape}")  # Add this
    print(f"target_coords.shape: {target_coords.shape}") 
    for coords in source_coords:
        dist = spatial.distance.cdist([coords], target_coords)
        print(f"dist.shape: {dist.shape}")
        dist = dist.reshape(height,width)
        distance = np.minimum(distance,dist)
    print(f"distance.shape: {distance.shape}") #add this
    print(f"distance: {distance}")

    distance = distance / pixel_distance
    print(f"pixel_distance: {pixel_distance}")
    return distance
