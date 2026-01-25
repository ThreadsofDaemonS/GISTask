#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for coordinate normalization in upload_to_arcgis.py

This script tests that European decimal format (comma) is correctly
converted to standard format (period) for coordinates.
"""

import sys
import tempfile
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


def test_european_format_coordinates():
    """Test that European format coordinates (comma as decimal) are normalized."""
    print("Testing European format coordinate normalization...")
    
    uploader = ArcGISUploader(item_id="test_id")
    
    # Create test CSV with European format coordinates (comma as decimal separator)
    # Note: In CSV, we need to quote values that contain commas to avoid CSV parsing issues
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8-sig') as f:
        f.write("Дата,Область,Місто,Значення 1,Значення 2,Значення 3,Значення 4,Значення 5,Значення 6,Значення 7,Значення 8,Значення 9,Значення 10,long,lat\n")
        f.write('2024-01-01,Київська,Київ,1,0,0,0,0,0,0,0,0,0,"30,7306393","50,4501234"\n')  # European format with comma (quoted)
        f.write('2024-01-02,Львівська,Львів,1,0,0,0,0,0,0,0,0,0,"24,0297562","49,8383458"\n')  # European format with comma (quoted)
        f.write("2024-01-03,Одеська,Одеса,1,0,0,0,0,0,0,0,0,0,30.7233,46.4825\n")  # Standard format with period
        temp_path = f.name
    
    try:
        # Read and normalize data
        df = uploader.read_csv_data(temp_path)
        
        assert df is not None, "Failed to read CSV"
        assert len(df) == 3, f"Expected 3 rows, got {len(df)}"
        
        # Check that coordinates are properly converted to float
        assert isinstance(df.iloc[0]['long'], float), "Longitude not converted to float"
        assert isinstance(df.iloc[0]['lat'], float), "Latitude not converted to float"
        
        # Check specific values are correctly parsed
        # First row: "30,7306393" should become 30.7306393
        assert abs(df.iloc[0]['long'] - 30.7306393) < 0.0001, f"Expected 30.7306393, got {df.iloc[0]['long']}"
        assert abs(df.iloc[0]['lat'] - 50.4501234) < 0.0001, f"Expected 50.4501234, got {df.iloc[0]['lat']}"
        
        # Second row: "24,0297562" should become 24.0297562
        assert abs(df.iloc[1]['long'] - 24.0297562) < 0.0001, f"Expected 24.0297562, got {df.iloc[1]['long']}"
        assert abs(df.iloc[1]['lat'] - 49.8383458) < 0.0001, f"Expected 49.8383458, got {df.iloc[1]['lat']}"
        
        # Third row: "30.7233" should remain 30.7233
        assert abs(df.iloc[2]['long'] - 30.7233) < 0.0001, f"Expected 30.7233, got {df.iloc[2]['long']}"
        assert abs(df.iloc[2]['lat'] - 46.4825) < 0.0001, f"Expected 46.4825, got {df.iloc[2]['lat']}"
        
        print("✓ European format coordinate normalization test passed")
        
    finally:
        # Clean up
        Path(temp_path).unlink()


def test_create_features_with_normalized_coordinates():
    """Test that features are created successfully with normalized coordinates."""
    print("\nTesting feature creation with normalized coordinates...")
    
    uploader = ArcGISUploader(item_id="test_id")
    
    # Create DataFrame with already normalized coordinates
    data = {
        'Дата': ['2024-01-01'],
        'Область': ['Київська'],
        'Місто': ['Київ'],
        'Значення 1': [1],
        'Значення 2': [0],
        'Значення 3': [0],
        'Значення 4': [0],
        'Значення 5': [0],
        'Значення 6': [0],
        'Значення 7': [0],
        'Значення 8': [0],
        'Значення 9': [0],
        'Значення 10': [0],
        'long': [30.7306393],  # Already normalized
        'lat': [50.4501234]    # Already normalized
    }
    df = pd.DataFrame(data)
    
    # Create features
    features = uploader.create_features(df)
    
    assert len(features) == 1, "Expected 1 feature"
    
    feature = features[0]
    geometry = feature['geometry']
    
    # Check that geometry has correct coordinates
    assert abs(geometry['x'] - 30.7306393) < 0.0001, f"Expected x=30.7306393, got {geometry['x']}"
    assert abs(geometry['y'] - 50.4501234) < 0.0001, f"Expected y=50.4501234, got {geometry['y']}"
    
    print("✓ Feature creation with normalized coordinates test passed")


def test_mixed_format_csv():
    """Test CSV with mixed format (some rows with comma, some with period)."""
    print("\nTesting mixed format CSV...")
    
    uploader = ArcGISUploader(item_id="test_id")
    
    # Create test CSV with mixed format
    # Note: Values with commas need to be quoted in CSV
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8-sig') as f:
        f.write("Дата,Область,Місто,Значення 1,Значення 2,Значення 3,Значення 4,Значення 5,Значення 6,Значення 7,Значення 8,Значення 9,Значення 10,long,lat\n")
        f.write('2024-01-01,Київська,Київ,1,0,0,0,0,0,0,0,0,0,"30,5234","50,4501"\n')    # Comma format (quoted)
        f.write("2024-01-02,Львівська,Львів,1,0,0,0,0,0,0,0,0,0,24.0297,49.8383\n")  # Period format
        temp_path = f.name
    
    try:
        df = uploader.read_csv_data(temp_path)
        
        assert df is not None, "Failed to read CSV"
        assert len(df) == 2, f"Expected 2 rows, got {len(df)}"
        
        # Both should be correctly parsed as floats
        assert isinstance(df.iloc[0]['long'], float), "First row longitude not float"
        assert isinstance(df.iloc[1]['long'], float), "Second row longitude not float"
        
        # Check values
        assert abs(df.iloc[0]['long'] - 30.5234) < 0.0001, f"Expected 30.5234, got {df.iloc[0]['long']}"
        assert abs(df.iloc[1]['long'] - 24.0297) < 0.0001, f"Expected 24.0297, got {df.iloc[1]['long']}"
        
        print("✓ Mixed format CSV test passed")
        
    finally:
        Path(temp_path).unlink()


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Testing Coordinate Normalization")
    print("=" * 60)
    
    try:
        test_european_format_coordinates()
        test_create_features_with_normalized_coordinates()
        test_mixed_format_csv()
        
        print("\n" + "=" * 60)
        print("✅ All coordinate normalization tests passed!")
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
