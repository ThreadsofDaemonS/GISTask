#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for upload_to_arcgis.py

This script tests the core functionality of the uploader without
requiring actual ArcGIS Online credentials.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Mock the arcgis module before importing upload_to_arcgis
sys.modules['arcgis'] = MagicMock()
sys.modules['arcgis.gis'] = MagicMock()
sys.modules['arcgis.features'] = MagicMock()

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from upload_to_arcgis import ArcGISUploader
import pandas as pd


def test_field_mapping():
    """Test that field mapping is correctly defined."""
    print("Testing field mapping...")
    
    uploader = ArcGISUploader(item_id="test_id")
    
    expected_fields = {
        'Дата': 'date_1',
        'Область': 'Область',
        'Місто': 'city',
        'Значення 1': 'value_1',
        'Значення 2': 'value_2',
        'Значення 3': 'value_3',
        'Значення 4': 'value_4',
        'Значення 5': 'value_5',
        'Значення 6': 'value_6',
        'Значення 7': 'value_7',
        'Значення 8': 'value_8',
        'Значення 9': 'value_9',
        'Значення 10': 'value_10',
        'long': 'long',
        'lat': 'lat'
    }
    
    assert uploader.FIELD_MAPPING == expected_fields, "Field mapping mismatch"
    print("✓ Field mapping test passed")


def test_read_csv():
    """Test reading CSV data."""
    print("\nTesting CSV reading...")
    
    uploader = ArcGISUploader(item_id="test_id")
    
    # Test with sample data
    csv_path = "data/transformed_data.csv"
    df = uploader.read_csv_data(csv_path)
    
    assert df is not None, "Failed to read CSV"
    assert len(df) > 0, "CSV is empty"
    assert 'Дата' in df.columns, "Missing 'Дата' column"
    assert 'long' in df.columns, "Missing 'long' column"
    assert 'lat' in df.columns, "Missing 'lat' column"
    
    print(f"✓ CSV reading test passed ({len(df)} rows)")


def test_create_features():
    """Test creating features from DataFrame."""
    print("\nTesting feature creation...")
    
    uploader = ArcGISUploader(item_id="test_id")
    
    # Create sample DataFrame
    data = {
        'Дата': ['2024-01-01'],
        'Область': ['Київська'],
        'Місто': ['Київ'],
        'Значення 1': [1],
        'Значення 2': [1],
        'Значення 3': [0],
        'Значення 4': [0],
        'Значення 5': [0],
        'Значення 6': [0],
        'Значення 7': [0],
        'Значення 8': [0],
        'Значення 9': [0],
        'Значення 10': [0],
        'long': [30.5234],
        'lat': [50.4501]
    }
    df = pd.DataFrame(data)
    
    features = uploader.create_features(df)
    
    assert len(features) == 1, "Wrong number of features created"
    
    feature = features[0]
    assert 'geometry' in feature, "Feature missing geometry"
    assert 'attributes' in feature, "Feature missing attributes"
    
    # Check geometry
    geometry = feature['geometry']
    assert geometry['x'] == 30.5234, "Wrong longitude"
    assert geometry['y'] == 50.4501, "Wrong latitude"
    assert geometry['spatialReference']['wkid'] == 4326, "Wrong spatial reference"
    
    # Check attributes
    attributes = feature['attributes']
    assert attributes['date_1'] == '2024-01-01', "Wrong date"
    assert attributes['Область'] == 'Київська', "Wrong region"
    assert attributes['city'] == 'Київ', "Wrong city"
    assert attributes['value_1'] == 1, "Wrong value_1"
    assert attributes['value_2'] == 1, "Wrong value_2"
    
    # IMPORTANT: Verify that long and lat ARE in attributes (stored as separate fields)
    assert 'long' in attributes, "Coordinate 'long' should be in attributes"
    assert 'lat' in attributes, "Coordinate 'lat' should be in attributes"
    assert attributes['long'] == 30.5234, "Wrong longitude in attributes"
    assert attributes['lat'] == 50.4501, "Wrong latitude in attributes"
    
    print("✓ Feature creation test passed")


def test_validation():
    """Test data validation (removing rows with empty coordinates)."""
    print("\nTesting data validation...")
    
    uploader = ArcGISUploader(item_id="test_id")
    
    # Create test CSV with missing coordinates
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("Дата,Область,Місто,Значення 1,Значення 2,Значення 3,Значення 4,Значення 5,Значення 6,Значення 7,Значення 8,Значення 9,Значення 10,long,lat\n")
        f.write("2024-01-01,Київська,Київ,1,0,0,0,0,0,0,0,0,0,30.5234,50.4501\n")
        f.write("2024-01-02,Львівська,Львів,1,0,0,0,0,0,0,0,0,0,,\n")  # Empty coordinates
        f.write("2024-01-03,Одеська,Одеса,1,0,0,0,0,0,0,0,0,0,30.7233,46.4825\n")
        temp_path = f.name
    
    df = uploader.read_csv_data(temp_path)
    
    # Clean up
    Path(temp_path).unlink()
    
    assert df is not None, "Failed to read CSV"
    assert len(df) == 2, f"Expected 2 rows after validation, got {len(df)}"
    
    print("✓ Data validation test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Testing upload_to_arcgis.py")
    print("=" * 60)
    
    try:
        test_field_mapping()
        test_read_csv()
        test_create_features()
        test_validation()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
