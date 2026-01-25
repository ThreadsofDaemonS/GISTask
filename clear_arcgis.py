#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArcGIS Online Feature Layer Clear Script

This script clears all records from an ArcGIS Online Feature Layer.
Useful for testing and fixing data upload errors.

⚠️ WARNING: This script deletes ALL records from the Feature Layer!
"""

import os
import sys
import logging
from dotenv import load_dotenv
from arcgis.gis import GIS
from arcgis.features import FeatureLayer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class FeatureLayerCleaner:
    """
    A class to handle clearing all records from an ArcGIS Online Feature Layer.

    Attributes:
        item_id (str): ArcGIS Online Item ID
        gis (GIS): Anonymous GIS connection
        feature_layer (FeatureLayer): Target feature layer
    """

    def __init__(self, item_id: str):
        """
        Initialize the FeatureLayerCleaner.

        Args:
            item_id (str): ArcGIS Online Item ID
        """
        self.item_id = item_id
        self.gis = None
        self.feature_layer = None

    def connect_anonymous(self) -> bool:
        """
        Connect to ArcGIS Online anonymously (public access).

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info("Підключення до ArcGIS Online...")
            self.gis = GIS()
            logger.info("✓ Підключення успішне")
            return True
        except Exception as e:
            logger.error(f"❌ Помилка підключення до ArcGIS Online: {str(e)}")
            return False

    def get_feature_layer(self) -> bool:
        """
        Get the Feature Layer from the Item ID.

        Returns:
            bool: True if feature layer retrieved successfully, False otherwise
        """
        try:
            logger.info(f"Отримання Feature Layer з Item ID: {self.item_id}")
            
            # Get the item
            item = self.gis.content.get(self.item_id)
            
            if item is None:
                logger.error(f"❌ Item з ID {self.item_id} не знайдено")
                return False
            
            logger.info(f"✓ Item знайдено: {item.title}")
            
            # Get the feature layer (first layer in the service)
            self.feature_layer = item.layers[0]
            logger.info(f"✓ Feature Layer отримано: {self.feature_layer.properties.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка при отриманні Feature Layer: {str(e)}")
            return False

    def count_features(self) -> int:
        """
        Count the number of features in the layer.

        Returns:
            int: Number of features, or -1 if error
        """
        try:
            # Query all features to count them
            result = self.feature_layer.query(where="1=1", return_count_only=True)
            return result
        except Exception as e:
            logger.error(f"❌ Помилка при підрахунку записів: {str(e)}")
            return -1

    def clear_all_features(self) -> dict:
        """
        Delete all features from the layer.

        Returns:
            dict: Dictionary with deletion results
        """
        try:
            logger.warning("Видалення всіх записів з Feature Layer...")
            
            # Delete all features using where="1=1"
            result = self.feature_layer.delete_features(where="1=1")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Помилка при видаленні записів: {str(e)}")
            return {'deleteResults': [], 'error': str(e)}

    def clear_feature_layer(self) -> bool:
        """
        Main method to clear the Feature Layer.

        Returns:
            bool: True if clearing successful, False otherwise
        """
        # Step 1: Count records before deletion
        count_before = self.count_features()
        
        if count_before < 0:
            logger.error("❌ Не вдалося підрахувати записи")
            return False
        
        logger.info(f"Знайдено записів: {count_before}")
        
        # Check if layer is already empty
        if count_before == 0:
            logger.info("ℹ️  Feature Layer вже порожній")
            return True
        
        # Step 2: Request confirmation
        print()
        print("⚠️  УВАГА! Це видалить ВСІ дані з Feature Layer!")
        confirmation = input("Ви впевнені? (введіть 'YES' для підтвердження): ")
        
        if confirmation != "YES":
            logger.info("❌ Операцію скасовано користувачем")
            return False
        
        print()
        logger.info(f"Видалення {count_before} записів...")
        
        # Step 3: Delete all records
        result = self.clear_all_features()
        
        # Step 4: Check results
        if 'error' in result:
            logger.error(f"❌ Помилка при видаленні: {result['error']}")
            return False
        
        if 'deleteResults' in result:
            delete_results = result['deleteResults']
            successful_deletes = sum(1 for r in delete_results if r.get('success', False))
            
            logger.info(f"✅ Успішно видалено: {successful_deletes} записів")
            
            # Check for failed deletions
            failed_deletes = len(delete_results) - successful_deletes
            if failed_deletes > 0:
                logger.warning(f"⚠️  Не вдалося видалити: {failed_deletes} записів")
        
        # Step 5: Count records after deletion
        count_after = self.count_features()
        
        if count_after >= 0:
            logger.info(f"Залишилось записів: {count_after}")
            
            if count_after > 0:
                logger.warning(f"⚠️  УВАГА: В Feature Layer залишилось {count_after} записів!")
                return False
        
        return True


def validate_environment() -> str:
    """
    Validate that required environment variables are set.

    Returns:
        str: ArcGIS Item ID

    Raises:
        ValueError: If ARCGIS_ITEM_ID is not set
    """
    item_id = os.getenv('ARCGIS_ITEM_ID', '').strip()

    if not item_id:
        logger.error("❌ Помилка: ARCGIS_ITEM_ID не знайдено в .env файлі")
        logger.info("\nБудь ласка, створіть .env файл на основі .env.sample:")
        logger.info("  1. cp .env.sample .env")
        logger.info("  2. Додайте ARCGIS_ITEM_ID в .env файл")
        raise ValueError("ARCGIS_ITEM_ID не налаштовано")

    return item_id


def main():
    """Main execution function."""
    print("=" * 60)
    print("🧹 ОЧИЩЕННЯ FEATURE LAYER")
    print("=" * 60)
    print()

    try:
        # Load environment variables
        load_dotenv()

        # Validate environment
        item_id = validate_environment()

        # Create cleaner instance
        cleaner = FeatureLayerCleaner(item_id)

        # Connect to ArcGIS Online
        if not cleaner.connect_anonymous():
            sys.exit(1)

        # Get feature layer
        if not cleaner.get_feature_layer():
            sys.exit(1)

        # Clear feature layer
        success = cleaner.clear_feature_layer()

        if success:
            print()
            print("=" * 60)
            print("✅ ОЧИЩЕННЯ ЗАВЕРШЕНО УСПІШНО")
            print("=" * 60)
            sys.exit(0)
        else:
            print()
            print("=" * 60)
            print("⚠️  ОЧИЩЕННЯ ЗАВЕРШЕНО З ПОМИЛКАМИ")
            print("=" * 60)
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Процес перервано користувачем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Критична помилка: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
