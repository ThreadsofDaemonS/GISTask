#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for clear_arcgis.py

This script tests the core functionality of the cleaner without
requiring actual ArcGIS Online credentials.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock the arcgis module before importing clear_arcgis
sys.modules['arcgis'] = MagicMock()
sys.modules['arcgis.gis'] = MagicMock()
sys.modules['arcgis.features'] = MagicMock()

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from clear_arcgis import FeatureLayerCleaner


def test_initialization():
    """Test that FeatureLayerCleaner initializes correctly."""
    print("Testing initialization...")
    
    cleaner = FeatureLayerCleaner(item_id="test_item_id")
    
    assert cleaner.item_id == "test_item_id", "Item ID not set correctly"
    assert cleaner.gis is None, "GIS should be None initially"
    assert cleaner.feature_layer is None, "Feature layer should be None initially"
    
    print("✓ Initialization test passed")


def test_connect_anonymous():
    """Test anonymous connection."""
    print("\nTesting anonymous connection...")
    
    cleaner = FeatureLayerCleaner(item_id="test_item_id")
    
    # Mock GIS
    with patch('clear_arcgis.GIS') as mock_gis:
        mock_gis.return_value = MagicMock()
        result = cleaner.connect_anonymous()
        
        assert result is True, "Connection should succeed"
        assert cleaner.gis is not None, "GIS should be set"
        mock_gis.assert_called_once()
    
    print("✓ Anonymous connection test passed")


def test_get_feature_layer():
    """Test getting feature layer."""
    print("\nTesting get feature layer...")
    
    cleaner = FeatureLayerCleaner(item_id="test_item_id")
    
    # Mock GIS and item
    mock_gis = MagicMock()
    mock_item = MagicMock()
    mock_item.title = "Test Layer"
    mock_layer = MagicMock()
    mock_layer.properties.name = "Test Feature Layer"
    mock_item.layers = [mock_layer]
    
    mock_gis.content.get.return_value = mock_item
    cleaner.gis = mock_gis
    
    result = cleaner.get_feature_layer()
    
    assert result is True, "Should successfully get feature layer"
    assert cleaner.feature_layer is not None, "Feature layer should be set"
    mock_gis.content.get.assert_called_once_with("test_item_id")
    
    print("✓ Get feature layer test passed")


def test_count_features():
    """Test counting features."""
    print("\nTesting count features...")
    
    cleaner = FeatureLayerCleaner(item_id="test_item_id")
    
    # Mock feature layer
    mock_layer = MagicMock()
    mock_layer.query.return_value = 150
    cleaner.feature_layer = mock_layer
    
    count = cleaner.count_features()
    
    assert count == 150, f"Expected 150 features, got {count}"
    mock_layer.query.assert_called_once_with(where="1=1", return_count_only=True)
    
    print("✓ Count features test passed")


def test_clear_all_features():
    """Test clearing all features."""
    print("\nTesting clear all features...")
    
    cleaner = FeatureLayerCleaner(item_id="test_item_id")
    
    # Mock feature layer with successful deletion
    mock_layer = MagicMock()
    mock_layer.delete_features.return_value = {
        'deleteResults': [
            {'objectId': 1, 'success': True},
            {'objectId': 2, 'success': True},
            {'objectId': 3, 'success': True}
        ]
    }
    cleaner.feature_layer = mock_layer
    
    result = cleaner.clear_all_features()
    
    assert 'deleteResults' in result, "Result should contain deleteResults"
    assert len(result['deleteResults']) == 3, "Should have 3 delete results"
    mock_layer.delete_features.assert_called_once_with(where="1=1")
    
    print("✓ Clear all features test passed")


def test_clear_feature_layer_empty():
    """Test clearing when layer is already empty."""
    print("\nTesting clear when layer is empty...")
    
    cleaner = FeatureLayerCleaner(item_id="test_item_id")
    
    # Mock feature layer with 0 records
    mock_layer = MagicMock()
    mock_layer.query.return_value = 0
    cleaner.feature_layer = mock_layer
    
    result = cleaner.clear_feature_layer()
    
    assert result is True, "Should return True when layer is already empty"
    # delete_features should not be called
    mock_layer.delete_features.assert_not_called()
    
    print("✓ Clear empty layer test passed")


def test_clear_feature_layer_with_confirmation():
    """Test clearing with user confirmation."""
    print("\nTesting clear with confirmation...")
    
    cleaner = FeatureLayerCleaner(item_id="test_item_id")
    
    # Mock feature layer
    mock_layer = MagicMock()
    mock_layer.query.side_effect = [100, 0]  # Before: 100, After: 0
    mock_layer.delete_features.return_value = {
        'deleteResults': [{'success': True}] * 100
    }
    cleaner.feature_layer = mock_layer
    
    # Mock user input to confirm
    with patch('builtins.input', return_value='YES'):
        result = cleaner.clear_feature_layer()
    
    assert result is True, "Should successfully clear layer"
    mock_layer.delete_features.assert_called_once_with(where="1=1")
    
    print("✓ Clear with confirmation test passed")


def test_clear_feature_layer_cancelled():
    """Test cancelling the clear operation."""
    print("\nTesting clear cancellation...")
    
    cleaner = FeatureLayerCleaner(item_id="test_item_id")
    
    # Mock feature layer with records
    mock_layer = MagicMock()
    mock_layer.query.return_value = 100
    cleaner.feature_layer = mock_layer
    
    # Mock user input to cancel
    with patch('builtins.input', return_value='NO'):
        result = cleaner.clear_feature_layer()
    
    assert result is False, "Should return False when cancelled"
    # delete_features should not be called
    mock_layer.delete_features.assert_not_called()
    
    print("✓ Clear cancellation test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Testing clear_arcgis.py")
    print("=" * 60)
    
    try:
        test_initialization()
        test_connect_anonymous()
        test_get_feature_layer()
        test_count_features()
        test_clear_all_features()
        test_clear_feature_layer_empty()
        test_clear_feature_layer_with_confirmation()
        test_clear_feature_layer_cancelled()
        
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
