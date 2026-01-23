#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for data transformation with sample data.
This script demonstrates the transformation logic without requiring network access.
"""

import pandas as pd
import sys
sys.path.insert(0, '.')
from transform_data import DataTransformer


def create_sample_data():
    """Create sample data that matches Google Sheets structure."""
    data = {
        'Дата': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
        'Область': ['Київська', 'Львівська', 'Одеська', 'Харківська'],
        'Місто': ['Київ', 'Львів', 'Одеса', 'Харків'],
        'Значення 1': [3, 5, 2, 4],
        'Значення 2': [3, 3, 4, 2],
        'Значення 3': [0, 1, 0, 3],
        'Значення 4': [0, 0, 0, 0],
        'Значення 5': [0, 0, 0, 0],
        'Значення 6': [0, 0, 0, 0],
        'Значення 7': [0, 0, 0, 0],
        'Значення 8': [0, 0, 0, 0],
        'Значення 9': [0, 0, 0, 0],
        'Значення 10': [0, 0, 0, 0],
        'long': [30.5233, 24.0232, 30.7233, 36.2304],
        'lat': [50.4501, 49.8397, 46.4825, 49.9935]
    }
    return pd.DataFrame(data)


def main():
    """Main test function."""
    print("=" * 60)
    print("📊 Тестування трансформації даних (Sample Data)")
    print("=" * 60)
    
    # Create sample data
    print("🔄 Створення тестових даних...")
    df = create_sample_data()
    print(f"✓ Створено {len(df)} рядків тестових даних")
    
    print("\n📋 Оригінальні дані:")
    print(df[['Дата', 'Область', 'Місто', 'Значення 1', 'Значення 2', 'Значення 3']].to_string())
    
    # Initialize transformer
    transformer = DataTransformer('sample')
    transformer.df = df
    
    # Transform data
    print()
    transformed_df = transformer.transform_data()
    
    # Save results
    output_path = 'output/test_transformed_data.csv'
    transformer.save_to_csv(transformed_df, output_path)
    
    # Print statistics
    print("\n" + "=" * 60)
    print("📈 Статистика трансформації:")
    print(f"  Вхідних рядків: {len(df)}")
    print(f"  Вихідних рядків: {len(transformed_df)}")
    print(f"  Коефіцієнт розширення: {len(transformed_df) / len(df):.2f}x")
    print("=" * 60)
    
    print("\n🔍 Приклад трансформованих даних (перші 10 рядків):")
    print(transformed_df[['Дата', 'Область', 'Місто', 'Значення 1', 'Значення 2', 'Значення 3', 'long', 'lat']].head(10).to_string())
    
    print("\n✅ Тест успішно завершено!")
    print(f"📁 Результати збережено в: {output_path}")


if __name__ == "__main__":
    main()
