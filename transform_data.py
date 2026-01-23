#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Sheets Data Transformation Script

This script reads data from a Google Sheets document and transforms it according to
specific business logic: expanding rows with multiple values into individual rows
with single values.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
import pandas as pd
import numpy as np
import gspread
from dotenv import load_dotenv


class DataTransformer:
    """
    A class to handle Google Sheets data transformation.
    
    Attributes:
        spreadsheet_id (str): Google Sheets document ID
        value_columns (List[str]): List of value column names (Значення 1-10)
        base_columns (List[str]): List of base columns to preserve (Дата, Область, Місто, long, lat)
    """
    
    def __init__(self, spreadsheet_id: str):
        """
        Initialize the DataTransformer.
        
        Args:
            spreadsheet_id (str): Google Sheets document ID
        """
        self.spreadsheet_id = spreadsheet_id
        self.value_columns = [f'Значення {i}' for i in range(1, 11)]
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
            
            # Create a gspread client (anonymous access for public sheets)
            gc = gspread.service_account_from_dict({
                "type": "service_account",
                "project_id": "dummy",
                "private_key_id": "dummy",
                "private_key": "-----BEGIN PRIVATE KEY-----\nMIIBVAIBADANBgkqhkiG9w0BAQEFAASCAT4wggE6AgEAAkEAwJbSK4pSVYO13H1I\nkU/7kCvIXqzOvR8W6FnJwKz3wRJkqFwvghQg5+OIFaULqZwbZ7mD15wPNKYxXo5D\nTgJuawIDAQABAkEAuWXA3b2FQND1TKMcYnxYJOkNfb8WFhxP2VfLq7zCM5lKGbxy\nvNNLAQR6YQJJ4VxIBWL8mGq7hPXCqGvXvDcKQQIhAO4a3m7x0RxE4U3K3ZlvTLkg\nULjWZ8Zw5J3qD3uUnNi5AiEAzf7TJVAiqCNGQU+9b2q9T/J0WyY6pVL3XsMHq9sZ\nLGsCIH5qVGYQHXjRUbQwNUJ6Kn/eDTM8B5VcGLVyH0HU3L8ZAiAQvN3Qkp3kGMmE\nsFHcFpVOQnLQP8mNkZyJ0zLXkPZU0QIgVlJr6L9KEPJCbDLZm2dJsHa/LW4Q0O8B\nV5UuGVTpZhk=\n-----END PRIVATE KEY-----\n",
                "client_email": "dummy@dummy.iam.gserviceaccount.com",
                "client_id": "dummy",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dummy%40dummy.iam.gserviceaccount.com"
            })
            
            # For public sheets, we can use the public URL
            url = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/export?format=csv&gid=0"
            self.df = pd.read_csv(url)
            
            print(f"✓ Завантажено {len(self.df)} рядків з Google Sheets")
            return self.df
            
        except Exception as e:
            print(f"❌ Помилка при читанні Google Sheets: {str(e)}")
            raise
    
    def transform_row(self, row: pd.Series) -> List[pd.Series]:
        """
        Transform a single row according to business logic.
        
        Logic:
        - Find maximum value across Значення 1-10
        - Create that many rows
        - For each output row, set value to 1 if original >= row number, else 0
        
        Args:
            row (pd.Series): Input row data
            
        Returns:
            List[pd.Series]: List of transformed rows
        """
        # Get values from Значення columns
        values = []
        for col in self.value_columns:
            if col in row.index:
                val = row[col]
                # Handle various data types
                if pd.isna(val):
                    values.append(0)
                else:
                    try:
                        values.append(int(float(val)))
                    except (ValueError, TypeError):
                        values.append(0)
            else:
                values.append(0)
        
        # Find maximum value (number of rows to create)
        max_value = max(values) if values else 0
        
        # If max_value is 0, create one row with all zeros
        if max_value == 0:
            max_value = 1
        
        # Create transformed rows
        transformed_rows = []
        for i in range(max_value):
            new_row = row.copy()
            
            # Set Значення columns
            for j, col in enumerate(self.value_columns):
                if col in row.index:
                    # Set to 1 if original value >= current row number + 1, else 0
                    new_row[col] = 1 if values[j] > i else 0
            
            transformed_rows.append(new_row)
        
        return transformed_rows
    
    def transform_data(self) -> pd.DataFrame:
        """
        Transform the entire DataFrame with progress reporting.
        
        Returns:
            pd.DataFrame: Transformed DataFrame
        """
        if self.df is None:
            raise ValueError("Дані не завантажено. Спочатку викличте read_google_sheet()")
        
        print("⚙ Початок трансформації даних...")
        
        total_rows = len(self.df)
        all_transformed_rows = []
        
        for idx, row in self.df.iterrows():
            # Transform the row
            transformed = self.transform_row(row)
            all_transformed_rows.extend(transformed)
            
            # Progress reporting every 50 rows
            if (idx + 1) % 50 == 0 or (idx + 1) == total_rows:
                print(f"  Оброблено {idx + 1}/{total_rows} рядків")
        
        # Create new DataFrame from transformed rows
        transformed_df = pd.DataFrame(all_transformed_rows)
        
        print(f"✓ Трансформація завершена: {total_rows} → {len(transformed_df)} рядків")
        
        return transformed_df
    
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
            
            # Save to CSV
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
    print("📈 Статистика трансформації:")
    print(f"  Вхідних рядків: {original_count}")
    print(f"  Вихідних рядків: {transformed_count}")
    print(f"  Коефіцієнт розширення: {expansion_factor:.2f}x")
    print("=" * 60)
    
    print("\n🔍 Приклад трансформованих даних (перші 5 рядків):")
    print(df.head().to_string())


def main():
    """Main execution function."""
    print("=" * 60)
    print("📊 Трансформація даних Google Sheets")
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
        
        # Transform data
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
