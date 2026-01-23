#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Sheets Data Transformation Script (NumPy Optimized)

This script reads data from a Google Sheets document and transforms it using
vectorized NumPy operations for maximum performance.
"""

import os
import sys
from pathlib import Path
from typing import Optional
import pandas as pd
import numpy as np
from dotenv import load_dotenv


class DataTransformer:
    """
    A class to handle Google Sheets data transformation with NumPy optimization.

    Attributes:
        spreadsheet_id (str): Google Sheets document ID
        value_columns (List[str]): List of value column names (Значення 1-10)
        base_columns (List[str]): List of base columns to preserve
        num_value_columns (int): Number of value columns (default: 10)
    """

    def __init__(self, spreadsheet_id: str, num_value_columns: int = 10):
        """
        Initialize the DataTransformer.

        Args:
            spreadsheet_id (str): Google Sheets document ID
            num_value_columns (int): Number of value columns to process (default: 10)
        """
        self.spreadsheet_id = spreadsheet_id
        self.num_value_columns = num_value_columns
        self.value_columns = [f'Значення {i}' for i in range(1, num_value_columns + 1)]
        self.base_columns = ['Дата', 'Область', 'Місто', 'long', 'lat']
        self.df = None

    def read_google_sheet(self) -> pd.DataFrame:
        """
        Read data from a public Google Sheets document.

        Returns:
            pd.DataFrame: DataFrame containing the sheet data

        Raises:
            Exception: If unable to read the Google Sheet
        """
        try:
            print("🔄 Підключення до Google Sheets...")

            # For public sheets, we can use the public CSV export URL
            url = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/export?format=csv&gid=0"
            self.df = pd.read_csv(url)

            print(f"✓ Завантажено {len(self.df)} рядків з Google Sheets")
            return self.df

        except Exception as e:
            print(f"❌ Помилка при читанні Google Sheets: {str(e)}")
            raise

    def transform_data(self) -> pd.DataFrame:
        """
        Transform the DataFrame using vectorized NumPy operations for optimal performance.

        Logic:
        - Extract max value from each row across Значення 1-10 columns
        - Expand each row by max_value times
        - Set binary values: 1 if original_value > row_number, else 0

        Returns:
            pd.DataFrame: Transformed DataFrame

        Performance: O(n*m) where n=rows, m=max_value
        Memory-efficient with NumPy vectorization
        """
        if self.df is None:
            raise ValueError("Дані не завантажено. Спочатку викличте read_google_sheet()")

        print("⚙ NumPy векторизована трансформація даних...")

        total_rows = len(self.df)

        # Step 1: Extract value columns as NumPy array
        # Fill NaN with 0 and convert to integers
        value_data = self.df[self.value_columns].fillna(0).astype(int).values

        # Step 2: Find max value for each row (determines expansion factor)
        max_values = value_data.max(axis=1)

        # Handle edge case: if all values are 0, set max to 1
        max_values = np.maximum(max_values, 1)

        # Step 3: Create indices for row expansion
        # repeat_indices: which original row each expanded row comes from
        repeat_indices = np.repeat(np.arange(len(self.df)), max_values)

        # row_numbers: the position (0, 1, 2...) within each expanded group
        row_numbers = np.concatenate([np.arange(mv) for mv in max_values])

        print(f"  Розгортання: {total_rows} → {len(repeat_indices)} рядків")

        # Step 4: Expand base DataFrame
        expanded_df = self.df.iloc[repeat_indices].reset_index(drop=True)

        # Step 5: Vectorized binary value assignment
        # expanded_values[i, j] = original value for row i, column j
        expanded_values = value_data[repeat_indices]

        # mask[i, j] = True if expanded_values[i, j] > row_numbers[i]
        # Broadcasting: row_numbers[:, None] creates column vector for comparison
        mask = expanded_values > row_numbers[:, None]

        # Assign binary values (1 or 0) based on mask
        expanded_df[self.value_columns] = mask.astype(int)

        print(f"✓ Трансформація завершена: {total_rows} → {len(expanded_df)} рядків")

        return expanded_df

    def save_to_csv(self, df: pd.DataFrame, output_path: str = "output/transformed_data.csv") -> None:
        """
        Save the transformed DataFrame to a CSV file.

        Args:
            df (pd.DataFrame): DataFrame to save
            output_path (str): Output file path
        """
        try:
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save to CSV with UTF-8 BOM for Excel compatibility
            df.to_csv(output_path, index=False, encoding='utf-8-sig')

            # Get file size
            file_size = Path(output_path).stat().st_size / 1024  # KB

            print(f"✓ Дані збережено у {output_path}")
            print(f"  Розмір файлу: {file_size:.2f} KB")

        except Exception as e:
            print(f"❌ Помилка при збереженні файлу: {str(e)}")
            raise


def validate_environment() -> str:
    """
    Validate that required environment variables are set.

    Returns:
        str: Spreadsheet ID

    Raises:
        ValueError: If SPREADSHEET_ID is not set
    """
    spreadsheet_id = os.getenv('SPREADSHEET_ID', '').strip()

    if not spreadsheet_id:
        print("❌ Помилка: SPREADSHEET_ID не знайдено в .env файлі")
        print("\nБудь ласка, створіть .env файл на основі .env.sample:")
        print("  1. cp .env.sample .env")
        print("  2. Додайте SPREADSHEET_ID в .env файл")
        raise ValueError("SPREADSHEET_ID не налаштовано")

    return spreadsheet_id


def print_statistics(original_count: int, transformed_count: int, df: pd.DataFrame) -> None:
    """
    Print transformation statistics.

    Args:
        original_count (int): Number of original rows
        transformed_count (int): Number of transformed rows
        df (pd.DataFrame): Transformed DataFrame for preview
    """
    expansion_factor = transformed_count / original_count if original_count > 0 else 0

    print("\n" + "=" * 60)
    print("��� Статистика трансформації:")
    print(f"  Вхідних рядків: {original_count}")
    print(f"  Вихідних рядків: {transformed_count}")
    print(f"  Коефіцієнт розширення: {expansion_factor:.2f}x")
    print("=" * 60)

    print("\n🔍 Приклад трансформованих даних (перші 5 рядків):")
    print(df.head().to_string())


def main():
    """Main execution function."""
    print("=" * 60)
    print("📊 Трансформація даних Google Sheets (NumPy Optimized)")
    print("=" * 60)

    try:
        # Load environment variables
        load_dotenv()

        # Validate environment
        spreadsheet_id = validate_environment()

        # Create transformer instance
        transformer = DataTransformer(spreadsheet_id)

        # Read data from Google Sheets
        original_df = transformer.read_google_sheet()
        original_count = len(original_df)

        # Transform data (NumPy vectorized)
        transformed_df = transformer.transform_data()
        transformed_count = len(transformed_df)

        # Save to CSV
        transformer.save_to_csv(transformed_df)

        # Print statistics
        print_statistics(original_count, transformed_count, transformed_df)

        print("\n✅ Процес успішно завершено!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Процес перервано користувачем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критична помилка: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()