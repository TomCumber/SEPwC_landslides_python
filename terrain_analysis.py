import argparse
import numpy as np
import rasterio
import pandas as pd
import geopandas as pd
from proximity import proximity
from sklearn.ensemble import RandomForestClassifier


def convert_to_rasterio(raster_data, template_raster):
    """
    The function specifically targets and reads the data from the first band
    (layer) of the input template_raster dataset. This modifies the
    'raster_data' array rather than generating a new one

    """
    raster_data[:] = template_raster.read(1)
    
    return template_raster #I had to install rasterio as it wasnt installed


def extract_values_from_raster(raster, shape_object):
    """
    This extracts certain values from the raster file

    """
    
    #this is creating a list of coordinate pairs using the shape objects
    coord_pairs = [(shape.x, shape.y) for shape in shape_object]
    
    #this is samping the raster at certain coordinates
    values = raster.sample(coord_pairs)
    
    #converts the 'values' into a list
    value_list = []
    for value_sample in values:
        value_list.append(value_sample[0])
    

    return value_list

# dem (Digital Elevation model) used to calculate slope and espect of terrain.
def calculate_return_slope(dem, x_value, y_value):
    """This calculates the slope using pythagoras' theorem"""
    x_data, y_data = np.gradient(dem, x_value, y_value)
    #calculates gradient in direction of x and y
    
    h_slope_degrees = np.arctan(np.sqrt(x_data**2 + y_data**2) * (180 / np.pi))
    # calculates slope length and concerts to angle in degrees
    
    return h_slope_degrees

def distance_from_fault_raster(top,fault):
    """Generates the distance of faults from the slope raster using the
    proximity function"""
    dist_fault = proximity(topo, fault, 1)
    
    return dist_fault


def make_classifier(x, y, verbose=False):
    """ This generates a random forest classifier"""
    classifier = RandomForestClassifier(verbose=verbose)
    classifier.fit(x_values,y_values)
    
    return classifier

def make_prob_raster_data(topo, geo, lc, dist_fault, slope, classifier):

    return

def create_dataframe(topo, geo, lc, dist_fault, slope, shape, landslides):

    return


def main():


    parser = argparse.ArgumentParser(
                     prog="Landslide hazard using ML",
                     description="Calculate landslide hazards using simple ML",
                     epilog="Copyright 2024, Jon Hill"
                     )
    parser.add_argument('--topography',
                    required=True,
                    help="topographic raster file")
    parser.add_argument('--geology',
                    required=True,
                    help="geology raster file")
    parser.add_argument('--landcover',
                    required=True,
                    help="landcover raster file")
    parser.add_argument('--faults',
                    required=True,
                    help="fault location shapefile")
    parser.add_argument("landslides",
                    help="the landslide location shapefile")
    parser.add_argument("output",
                    help="the output raster file")
    parser.add_argument('-v', '--verbose',
                    action='store_true',
                    default=False,
                    help="Print progress")

    args = parser.parse_args()


if __name__ == '__main__':
    main()

