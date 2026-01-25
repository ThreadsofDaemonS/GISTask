#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstration of coordinate normalization fix

This script demonstrates the fix for coordinate normalization that follows
the "Clean Data Early" principle.
"""

import pandas as pd
import sys
sys.path.insert(0, '.')
from transform_data import DataTransformer


def main():
    print("=" * 70)
    print("📊 ДЕМОНСТРАЦІЯ ВИПРАВЛЕННЯ НОРМАЛІЗАЦІЇ КООРДИНАТ")
    print("=" * 70)
    
    print("\n### ПРОБЛЕМА: Європейський формат координат з комою ###\n")
    
    # Simulate data from Google Sheets with European format (comma as decimal)
    print("Дані з Google Sheets (європейський формат):")
    data_european = {
        'Дата': ['2024-01-15'],
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
        'long': ['30,73'],  # ❌ Кома - європейський формат
        'lat': ['46,47']    # ❌ Кома - європейський формат
    }
    df = pd.DataFrame(data_european)
    print(f"  long: {df.iloc[0]['long']} (тип: {type(df.iloc[0]['long']).__name__})")
    print(f"  lat:  {df.iloc[0]['lat']} (тип: {type(df.iloc[0]['lat']).__name__})")
    
    print("\n" + "=" * 70)
    print("### РІШЕННЯ: Нормалізація в transform_data.py ###\n")
    
    # Apply normalization (as done in transform_data.py)
    print("🔄 Нормалізація координат (кома → крапка)...")
    if 'long' in df.columns and 'lat' in df.columns:
        df['long'] = df['long'].astype(str).str.replace(',', '.').astype(float)
        df['lat'] = df['lat'].astype(str).str.replace(',', '.').astype(float)
    print("✓ Координати нормалізовано\n")
    
    print("Після нормалізації:")
    print(f"  long: {df.iloc[0]['long']} (тип: {type(df.iloc[0]['long']).__name__})")
    print(f"  lat:  {df.iloc[0]['lat']} (тип: {type(df.iloc[0]['lat']).__name__})")
    
    # Save to CSV to demonstrate format in file
    transformer = DataTransformer('demo')
    output_path = 'output/demo_normalized_coordinates.csv'
    transformer.save_to_csv(df, output_path)
    
    print("\n" + "=" * 70)
    print("### РЕЗУЛЬТАТ: CSV з правильним форматом ###\n")
    
    # Read back and show what's in the CSV
    with open(output_path, 'r', encoding='utf-8-sig') as f:
        csv_content = f.read()
        # Show coordinate line
        lines = csv_content.strip().split('\n')
        if len(lines) > 1:
            print("Вміст CSV файлу:")
            print(f"  Header: {lines[0]}")
            print(f"  Data:   {lines[1]}")
    
    print("\n" + "=" * 70)
    print("### ПЕРЕВАГИ РІШЕННЯ ###\n")
    print("✅ Координати нормалізуються ОДИН РАЗ при читанні з Google Sheets")
    print("✅ CSV файл містить правильний формат (30.73, не 30,73)")
    print("✅ upload_to_arcgis.py тільки валідує, не конвертує")
    print("✅ Дотримання принципу 'Clean Data Early'")
    print("✅ Простіше тестувати та відлагоджувати")
    
    print("\n" + "=" * 70)
    print("### ПОРІВНЯННЯ: До і Після ###\n")
    
    comparison = """
    ┌─────────────────────────┬──────────────────┬──────────────────┐
    │ Етап                    │ До виправлення   │ Після виправлення│
    ├─────────────────────────┼──────────────────┼──────────────────┤
    │ Google Sheets           │ 30,73            │ 30,73            │
    │ transform_data.py       │ 30,73 (без змін) │ 30.73 ✅         │
    │ CSV файл                │ 30,73 ❌         │ 30.73 ✅         │
    │ upload_to_arcgis.py     │ 30.73 (конверт.) │ 30.73 (валідац.)│
    │ ArcGIS атрибути         │ 30,73 ❌         │ 30.73 ✅         │
    │ ArcGIS геометрія        │ 30.73 ✅         │ 30.73 ✅         │
    └─────────────────────────┴──────────────────┴──────────────────┘
    """
    print(comparison)
    
    print("\n" + "=" * 70)
    print("✅ ДЕМОНСТРАЦІЯ ЗАВЕРШЕНА")
    print("=" * 70)
    print(f"\nРезультат збережено в: {output_path}")


if __name__ == "__main__":
    main()
