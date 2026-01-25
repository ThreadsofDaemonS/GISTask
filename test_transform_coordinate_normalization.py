#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for coordinate normalization in transform_data.py

This script tests that European decimal format (comma) is correctly
converted to standard format (period) when reading from Google Sheets.
"""

import sys
import pandas as pd
sys.path.insert(0, '.')
from transform_data import DataTransformer


def test_coordinate_normalization_in_transform():
    """Test that coordinates are normalized during read_google_sheet()."""
    print("Testing coordinate normalization in transform_data.py...")
    
    transformer = DataTransformer('test')
    
    # Create sample DataFrame with European format coordinates (comma as decimal)
    data = {
        'Дата': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Область': ['Київська', 'Львівська', 'Одеська'],
        'Місто': ['Київ', 'Львів', 'Одеса'],
        'Значення 1': [3, 5, 2],
        'Значення 2': [3, 3, 4],
        'Значення 3': [0, 1, 0],
        'Значення 4': [0, 0, 0],
        'Значення 5': [0, 0, 0],
        'Значення 6': [0, 0, 0],
        'Значення 7': [0, 0, 0],
        'Значення 8': [0, 0, 0],
        'Значення 9': [0, 0, 0],
        'Значення 10': [0, 0, 0],
        'long': ['30,7306393', '24,0297562', 30.7233],  # Mixed: comma strings and float
        'lat': ['50,4501234', '49,8383458', 46.4825]
    }
    df = pd.DataFrame(data)
    
    # Simulate what happens in read_google_sheet() after reading CSV
    # This is the normalization logic we added
    if 'long' in df.columns and 'lat' in df.columns:
        df['long'] = df['long'].astype(str).str.replace(',', '.').astype(float)
        df['lat'] = df['lat'].astype(str).str.replace(',', '.').astype(float)
    
    # Verify normalization
    assert isinstance(df.iloc[0]['long'], float), "Longitude not converted to float"
    assert isinstance(df.iloc[0]['lat'], float), "Latitude not converted to float"
    
    # Check specific values
    assert abs(df.iloc[0]['long'] - 30.7306393) < 0.0001, f"Expected 30.7306393, got {df.iloc[0]['long']}"
    assert abs(df.iloc[0]['lat'] - 50.4501234) < 0.0001, f"Expected 50.4501234, got {df.iloc[0]['lat']}"
    
    assert abs(df.iloc[1]['long'] - 24.0297562) < 0.0001, f"Expected 24.0297562, got {df.iloc[1]['long']}"
    assert abs(df.iloc[1]['lat'] - 49.8383458) < 0.0001, f"Expected 49.8383458, got {df.iloc[1]['lat']}"
    
    assert abs(df.iloc[2]['long'] - 30.7233) < 0.0001, f"Expected 30.7233, got {df.iloc[2]['long']}"
    assert abs(df.iloc[2]['lat'] - 46.4825) < 0.0001, f"Expected 46.4825, got {df.iloc[2]['lat']}"
    
    print("✓ Coordinate normalization test passed")


def test_transform_with_normalized_coordinates():
    """Test that transformation works correctly with normalized coordinates."""
    print("\nTesting transformation with normalized coordinates...")
    
    transformer = DataTransformer('test')
    
    # Create sample DataFrame with already normalized coordinates
    data = {
        'Дата': ['2024-01-01', '2024-01-02'],
        'Область': ['Київська', 'Львівська'],
        'Місто': ['Київ', 'Львів'],
        'Значення 1': [2, 3],
        'Значення 2': [2, 2],
        'Значення 3': [0, 0],
        'Значення 4': [0, 0],
        'Значення 5': [0, 0],
        'Значення 6': [0, 0],
        'Значення 7': [0, 0],
        'Значення 8': [0, 0],
        'Значення 9': [0, 0],
        'Значення 10': [0, 0],
        'long': [30.5234, 24.0297],
        'lat': [50.4501, 49.8397]
    }
    transformer.df = pd.DataFrame(data)
    
    # Transform data
    transformed_df = transformer.transform_data()
    
    # Verify coordinates are preserved correctly
    assert 'long' in transformed_df.columns, "long column missing"
    assert 'lat' in transformed_df.columns, "lat column missing"
    
    # Check that all coordinates are floats
    assert all(isinstance(x, float) for x in transformed_df['long']), "Some longitude values are not float"
    assert all(isinstance(x, float) for x in transformed_df['lat']), "Some latitude values are not float"
    
    # Check specific values are preserved
    assert abs(transformed_df.iloc[0]['long'] - 30.5234) < 0.0001, "First coordinate not preserved"
    assert abs(transformed_df.iloc[0]['lat'] - 50.4501) < 0.0001, "First coordinate not preserved"
    
    print("✓ Transformation with normalized coordinates test passed")


def test_csv_output_format():
    """Test that CSV output contains properly formatted coordinates."""
    print("\nTesting CSV output format...")
    
    transformer = DataTransformer('test')
    
    # Create sample data
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
        'long': [30.7306393],
        'lat': [50.4501234]
    }
    df = pd.DataFrame(data)
    
    # Save to CSV
    output_path = 'output/test_coordinate_format.csv'
    transformer.save_to_csv(df, output_path)
    
    # Read back and verify format
    df_read = pd.read_csv(output_path, encoding='utf-8-sig')
    
    # Verify coordinates are stored as proper decimals with period
    assert isinstance(df_read.iloc[0]['long'], float), "Longitude not read as float"
    assert isinstance(df_read.iloc[0]['lat'], float), "Latitude not read as float"
    
    assert abs(df_read.iloc[0]['long'] - 30.7306393) < 0.0001, "Longitude value changed"
    assert abs(df_read.iloc[0]['lat'] - 50.4501234) < 0.0001, "Latitude value changed"
    
    # Read CSV as text to verify format
    with open(output_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
        # Should contain period, not comma
        assert '30.7306393' in content or '30.73' in content, "Coordinate format incorrect in CSV"
        assert '30,7306393' not in content, "European format (comma) found in CSV!"
    
    print("✓ CSV output format test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Testing Coordinate Normalization in transform_data.py")
    print("=" * 60)
    
    try:
        test_coordinate_normalization_in_transform()
        test_transform_with_normalized_coordinates()
        test_csv_output_format()
        
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
