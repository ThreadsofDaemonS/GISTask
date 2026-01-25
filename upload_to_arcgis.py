#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArcGIS Online Data Upload Script

This script reads transformed data from CSV and uploads it to an ArcGIS Online 
Feature Layer using anonymous access to a public feature service.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
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


class ArcGISUploader:
    """
    A class to handle uploading transformed data to ArcGIS Online Feature Layer.

    Attributes:
        item_id (str): ArcGIS Online Item ID
        gis (GIS): Anonymous GIS connection
        feature_layer (FeatureLayer): Target feature layer
        batch_size (int): Number of records to upload per batch (default: 100)
    """

    # Field mapping: CSV column -> ArcGIS field
    FIELD_MAPPING = {
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

    def __init__(self, item_id: str, batch_size: int = 100):
        """
        Initialize the ArcGISUploader.

        Args:
            item_id (str): ArcGIS Online Item ID
            batch_size (int): Number of records per batch (default: 100)
        """
        self.item_id = item_id
        self.batch_size = batch_size
        self.gis = None
        self.feature_layer = None

    def connect_anonymous(self) -> bool:
        """
        Connect to ArcGIS Online anonymously (public access).

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info("🔄 Підключення до ArcGIS Online (анонімно)...")
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
            logger.info(f"🔄 Отримання Feature Layer з Item ID: {self.item_id}")
            
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

    def read_csv_data(self, csv_path: str) -> Optional[pd.DataFrame]:
        """
        Read and validate CSV data.

        Args:
            csv_path (str): Path to the CSV file

        Returns:
            Optional[pd.DataFrame]: DataFrame with validated data, or None if error
        """
        try:
            logger.info(f"🔄 Читання даних з {csv_path}...")
            
            # Check if file exists
            if not Path(csv_path).exists():
                logger.error(f"❌ Файл {csv_path} не знайдено")
                return None
            
            # Read CSV
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            logger.info(f"✓ Завантажено {len(df)} рядків з CSV")
            
            # Validate required columns (from FIELD_MAPPING + coordinates)
            required_columns = list(self.FIELD_MAPPING.keys()) + ['long', 'lat']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.error(f"❌ Відсутні обов'язкові колонки: {missing_columns}")
                return None
            
            logger.info("✓ Всі обов'язкові поля присутні")
            
            # Нормалізація координат: заміна коми на крапку (європейський формат → стандартний формат)
            logger.info("🔄 Нормалізація формату координат (кома → крапка)...")
            try:
                df['long'] = df['long'].astype(str).str.replace(',', '.').astype(float)
                df['lat'] = df['lat'].astype(str).str.replace(',', '.').astype(float)
                logger.info("✓ Координати успішно нормалізовано")
            except Exception as e:
                logger.error(f"❌ Помилка при нормалізації координат: {str(e)}")
                return None
            
            # Remove rows with empty coordinates
            initial_count = len(df)
            df = df.dropna(subset=['long', 'lat'])
            removed_count = initial_count - len(df)
            
            if removed_count > 0:
                logger.info(f"⚠️  Видалено {removed_count} рядків з порожніми координатами")
            
            logger.info(f"✓ Валідація даних завершена: {len(df)} рядків готові до завантаження")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Помилка при читанні CSV: {str(e)}")
            return None

    def create_features(self, df: pd.DataFrame) -> List[Dict]:
        """
        Create ArcGIS features from DataFrame.

        Args:
            df (pd.DataFrame): DataFrame with transformed data

        Returns:
            List[Dict]: List of feature dictionaries
        """
        logger.info("🔄 Створення features з геометрією...")
        
        features = []
        
        for idx, row in df.iterrows():
            try:
                # Create geometry (Point with WGS84 coordinates)
                geometry = {
                    'x': float(row['long']),
                    'y': float(row['lat']),
                    'spatialReference': {'wkid': 4326}  # WGS84
                }
                
                # Create attributes with field mapping
                attributes = {}
                for csv_field, arcgis_field in self.FIELD_MAPPING.items():
                    value = row[csv_field]
                    
                    # Handle different data types
                    if pd.isna(value):
                        attributes[arcgis_field] = None
                    elif csv_field in ['long', 'lat']:
                        # Store coordinates as floats in attributes
                        try:
                            attributes[arcgis_field] = float(value)
                        except (ValueError, TypeError):
                            logger.warning(f"⚠️  Не вдалося конвертувати {csv_field}='{value}' в float, використано None")
                            attributes[arcgis_field] = None
                    elif csv_field.startswith('Значення'):
                        # Safely convert to integer, handling potential errors
                        try:
                            attributes[arcgis_field] = int(float(value)) if not pd.isna(value) else 0
                        except (ValueError, TypeError):
                            logger.warning(f"⚠️  Не вдалося конвертувати {csv_field}='{value}' в integer, використано 0")
                            attributes[arcgis_field] = 0
                    else:
                        attributes[arcgis_field] = str(value)
                
                # Create feature
                feature = {
                    'geometry': geometry,
                    'attributes': attributes
                }
                
                features.append(feature)
                
            except Exception as e:
                logger.warning(f"⚠️  Помилка при створенні feature для рядка {idx}: {str(e)}")
                continue
        
        logger.info(f"✓ Створено {len(features)} features")
        return features

    def upload_features(self, features: List[Dict]) -> Dict[str, int]:
        """
        Upload features to ArcGIS Online in batches.

        Args:
            features (List[Dict]): List of features to upload

        Returns:
            Dict[str, int]: Dictionary with 'success' and 'failed' counts
        """
        logger.info(f"🔄 Завантаження {len(features)} features пакетами по {self.batch_size}...")
        
        total_features = len(features)
        successful = 0
        failed = 0
        
        # Upload in batches
        for i in range(0, total_features, self.batch_size):
            batch = features[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (total_features + self.batch_size - 1) // self.batch_size
            
            try:
                logger.info(f"  Пакет {batch_num}/{total_batches}: завантаження {len(batch)} features...")
                
                # Add features to the layer
                result = self.feature_layer.edit_features(adds=batch)
                
                # Check results
                if result['addResults']:
                    for add_result in result['addResults']:
                        if add_result['success']:
                            successful += 1
                        else:
                            failed += 1
                            logger.warning(f"    ⚠️  Feature не завантажено: {add_result.get('error', 'Unknown error')}")
                
                logger.info(f"  ✓ Пакет {batch_num}/{total_batches} завершено")
                
            except Exception as e:
                logger.error(f"  ❌ Помилка при завантаженні пакету {batch_num}: {str(e)}")
                failed += len(batch)
        
        return {
            'success': successful,
            'failed': failed
        }

    def upload_csv_data(self, csv_path: str) -> bool:
        """
        Main method to upload CSV data to ArcGIS Online.

        Args:
            csv_path (str): Path to the CSV file

        Returns:
            bool: True if upload successful, False otherwise
        """
        # Step 1: Read and validate CSV data
        df = self.read_csv_data(csv_path)
        if df is None or len(df) == 0:
            logger.error("❌ Немає даних для завантаження")
            return False
        
        # Step 2: Create features
        features = self.create_features(df)
        if not features:
            logger.error("❌ Не вдалося створити features")
            return False
        
        # Step 3: Upload features
        results = self.upload_features(features)
        
        # Step 4: Print summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 Підсумки завантаження:")
        logger.info(f"  Всього записів: {len(df)}")
        logger.info(f"  Створено features: {len(features)}")
        logger.info(f"  ✅ Успішно завантажено: {results['success']}")
        logger.info(f"  ❌ Не вдалося завантажити: {results['failed']}")
        logger.info("=" * 60)
        
        return results['failed'] == 0


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
    logger.info("=" * 60)
    logger.info("📤 Завантаження даних в ArcGIS Online")
    logger.info("=" * 60)

    try:
        # Load environment variables
        load_dotenv()

        # Validate environment
        item_id = validate_environment()

        # Get CSV path from environment or use default
        csv_path = os.getenv('CSV_PATH', 'output/transformed_data.csv')
        logger.info(f"CSV шлях: {csv_path}")

        # Create uploader instance
        uploader = ArcGISUploader(item_id)

        # Connect to ArcGIS Online
        if not uploader.connect_anonymous():
            sys.exit(1)

        # Get feature layer
        if not uploader.get_feature_layer():
            sys.exit(1)

        # Upload data
        success = uploader.upload_csv_data(csv_path)

        if success:
            logger.info("\n✅ Процес успішно завершено!")
            sys.exit(0)
        else:
            logger.error("\n⚠️  Процес завершено з помилками")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Процес перервано користувачем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Критична помилка: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
