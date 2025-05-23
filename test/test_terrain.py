import pytest
import sys
sys.path.insert(0,"../")
sys.path.insert(0,"./")
from terrain_analysis import *
from pylint.lint import Run
from pylint.reporters import CollectingReporter
from dataclasses import asdict
import numpy as np
import rasterio
import os 
from shapely.geometry import Point
import geopandas as gpd
import subprocess

class TestTerrainAnalysis():
    
    def test_convert_rasterio(self):

        import rasterio

        template = rasterio.open("test/data/raster_template.tif")
        data = np.zeros(template.shape)

        data_as_rasterio = convert_to_rasterio(data, template)

        assert type(data_as_rasterio) == rasterio.io.DatasetReader
        assert np.array_equal(data_as_rasterio.read(1), data)
        
    
    def test_extract_from_raster(self):

        import geopandas as gpd

        template = rasterio.open("test/data/raster_template.tif")
        point = gpd.read_file("test/data/test_point.shp")
        geom_sample = list(point.geometry)
        values = extract_values_from_raster(template, geom_sample)
        assert len(values) == 2
        assert values[0] == pytest.approx(2509.6870)
        assert values[1] == pytest.approx(2534.5088)

    def test_make_classifier(self):

        import sklearn
        
        test_data =  np.random.normal(size=20)
        data = {
            "x1": test_data,
            "x2": test_data * 2.45,
            "y": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        }
        df = pd.DataFrame(data)
        classifier = make_classifier(df.drop('y',axis=1),df['y'])
        assert type(classifier) == sklearn.ensemble._forest.RandomForestClassifier
        assert classifier.n_classes_ == 2

    def test_create_dataframe(self):
        
        import geopandas as gpd
       
        template = rasterio.open("test/data/raster_template.tif")
        point = gpd.read_file("test/data/test_point.shp")
        geom_sample = list(point.geometry)
        df = create_dataframe(template, template, template,
                              template, template, geom_sample,
                              0)
        assert type(df) == gpd.geodataframe.GeoDataFrame
        assert len(df) == 2
        assert np.array_equal(np.array(df.columns), np.array(['elev', 'fault', 'slope', 'LC', 'Geol', 'ls']))
        assert df['ls'].to_list() == [0,0]
        

    def test_lint(self):
        files =  ["terrain_analysis.py"]
        #pylint_options = ["--disable=line-too-long,import-error,fixme"]
        pylint_options = []

        report = CollectingReporter()
        result = Run(
                    files,
                    reporter=report,
                    exit=False,
                )
        score = result.linter.stats.global_note
        nErrors = len(report.messages)

        print("Score: " + str(score))
        line_format = "{path}:{line}:{column}: {msg_id}: {msg} ({symbol})"
        for error in report.messages:
            print(line_format.format(**asdict(error)))   

        assert score > 3
        assert score > 5
        assert score > 7
        assert score > 9
        assert nErrors < 500
        assert nErrors < 400
        assert nErrors < 250
        assert nErrors < 100
        assert nErrors < 50
        assert nErrors < 10
        assert nErrors == 0

class TestRegression():
    
    def test_regression(self):
        self.run_test(verbose=False)

    def test_regression_verbose(self):
        self.run_test(verbose=True)

    def run_test(self, verbose):
        # Construct absolute paths
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "terrain_analysis.py")
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

        # Check if the script exists
        if not os.path.exists(script_path):
            print(f"Error: Script not found at {script_path}")
            pytest.fail(f"Script not found: {script_path}")

        # Check if the data directory exists
        if not os.path.exists(data_dir):
            print(f"Error: Data directory not found at {data_dir}")
            pytest.fail(f"Data directory not found: {data_dir}")
            
        # Check if python is in path
        python_executable = shutil.which("python")
        if python_executable is None:
            python_executable = shutil.which("python3")
        if python_executable is None:
            print("Error: Python interpreter not found in PATH.")
            pytest.fail("Python interpreter not found in PATH.")
        print(f"Using python executable: {python_executable}")

        # Build command
        command = [
            python_executable,  # Use the found Python executable
            script_path,
            "--topography", os.path.join(data_dir, "AW3D30.tif"),
            "--geology", os.path.join(data_dir, "Geology.tif"),
            "--landcover", os.path.join(data_dir, "Landcover.tif"),
            "--faults", os.path.join(data_dir, "Confirmed_faults.shp"),
            os.path.join(data_dir, "landslides.shp"),  # Corrected path
            "test.tif",
        ]
        if verbose:
            command.append("--v")

        print(f"Running command: {command}")  # Print the command

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                check=True,
                text=True,  # Get output as text, not bytes
            )
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")

            if verbose:
                assert len(result.stdout) > 25
            else:
                assert len(result.stdout) < 25

            import rasterio
            with rasterio.open("test.tif") as raster:
                values = raster.read(1)
                assert values.max() <= 1
                assert values.min() >= 0
            os.remove("test.tif")

        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e}")
            print(f"stdout: {e.stdout}")  # Print the script's output
            print(f"stderr: {e.stderr}")  # Print the script's error output
            raise  # Re-raise the exception to fail the test

    def test_regression(self):
        
        try:
            subprocess.run([
               "python", "terrain_analysis.py",
               "--topography", "data/AW3D30.tif",
               "--geology", "data/Geology.tif",
               "--landcover", "data/Landcover.tif",
               "--faults", "data/Confirmed_faults.shp",
               "--landslides", "data/landslides.shp",
               "--output","test.tif"
               "--v"         
                          
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print("STDOUT:", e.stdout.decode())
            print("STDERR:", e.stderr.decode())
            raise
        
        from subprocess import run
        import os
        import rasterio
        import sys 
        print(os.path.exists('data/AW3D30.tif'))
        print(os.path.exists('data/Geology.tif'))

        terrain_analysis_path = "C:\\SEPwC_landslides_python\\terrain_analysis.py"
        result = run(["python ","terrain_analysis.py",
                                "--topography",
                                "data/AW3D30.tif",
                                "--geology",
                                "data/Geology.tif",
                                "--landcover",
                                "data/Landcover.tif",
                                "--faults",
                                "data/Confirmed_faults.shp",
                                "data/landslides.shp",
                                "--v",
                                "test.tif"], capture_output=True, check=True)
        assert len(result.stdout) < 25

        raster = rasterio.open("test.tif")
        values = raster.read(1)
        assert values.max() <= 1
        assert values.min() >= 0
        os.remove("test.tif")
        
        # Print full paths
        print(f"Python executable: {sys.executable}")
        print(f"Topography: {os.path.abspath('data/AW3D30.tif')}")
        print(f"Geology: {os.path.abspath('data/Geology.tif')}")
        print(f"Landcover: {os.path.abspath('data/Landcover.tif')}")
        print(f"Faults: {os.path.abspath('data/Confirmed_faults.shp')}")
        print(f"Landslides: {os.path.abspath('data/landslides.shp')}")
        output_path = os.path.abspath("test.tif")
        print(f"Output: {output_path}")

        # Run the script with the full python path and absolute paths
        result = subprocess.run(
            [sys.executable, "terrain_analysis.py",
             "--topography", os.path.abspath("data/AW3D30.tif"),
             "--geology", os.path.abspath("data/Geology.tif"),
             "--landcover", os.path.abspath("data/Landcover.tif"),
             "--faults", os.path.abspath("data/Confirmed_faults.shp"),
             os.path.abspath("data/landslides.shp"),
             output_path],
            capture_output=True,
            check=True,
            text=True
        )

    def test_regression_verbose(self):

        from subprocess import run
        import os
        import rasterio
        terrain_analysis_path = "C:\\SEPwC_landslides_python\\terrain_analysis.py"
        result = run(["python","terrain_analysis.py",
                                "--topography",
                                "data/AW3D30.tif",
                                "--geology",
                                "data/Geology.tif",
                                "--landcover",
                                "data/Landcover.tif",
                                "--faults",
                                "data/Confirmed_faults.shp",
                                "--landslides", "data/landslides.shp",
                                "--output","test.tif",
                                "--v"
                                ], capture_output=True, check=True)
        assert len(result.stdout) > 25

        raster = rasterio.open("test.tif")
        values = raster.read(1)
        assert values.max() <= 1
        assert values.min() >= 0
        os.remove("test.tif")



