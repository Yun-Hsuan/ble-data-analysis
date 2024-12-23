import os
import json
from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd
from src.data_processing.loader import DataManager


class BaseCleaner(ABC):
    """
    Abstract base class for data cleaning.
    All custom cleaners should inherit from this class.
    """

    def __init__(self, file_path: Optional[str] = None, directory: Optional[str] = None):
        """
        Initialize the BaseCleaner with either a file path or a directory.
        :param file_path: Path to a single file.
        :param directory: Path to a folder containing multiple files.
        """
        self.data_manager = DataManager(file_path=file_path, directory=directory)
        self.data = None

    def load_data(self, pattern: str = None, sheet_name_column: str = None) -> pd.DataFrame:
        """
        Load data using DataManager.
        :param pattern: Optional regex pattern to filter files.
        :return: Loaded pandas DataFrame.
        """
        self.data = self.data_manager.load_files(pattern=pattern, sheet_name_column=sheet_name_column)
        return self.data
    

    @abstractmethod
    def clean(self) -> pd.DataFrame:
        """
        Abstract method to clean the data.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def validate(self) -> bool:
        """
        Abstract method to validate the data.
        Must be implemented by subclasses.
        """
        pass

    def drop_na(self, how: str = "any") -> None:
        """
        Drop rows with missing values.
        :param how: 'any' (default) or 'all'.
        """
        if self.data is not None:
            self.data.dropna(how=how, inplace=True)
        else:
            raise ValueError("No data loaded. Call 'load_data()' first.")

    def drop_duplicates(self, subset: Optional[list] = None) -> None:
        """
        Drop duplicate rows.
        :param subset: List of columns to consider for identifying duplicates.
        """
        if self.data is not None:
            self.data.drop_duplicates(subset=subset, inplace=True)
        else:
            raise ValueError("No data loaded. Call 'load_data()' first.")

    def rename_columns(self, column_mapping: dict) -> None:
        """
        Rename columns based on the provided mapping.
        :param column_mapping: Dictionary mapping old column names to new names.
        """
        if self.data is not None:
            self.data.rename(columns=column_mapping, inplace=True)
        else:
            raise ValueError("No data loaded. Call 'load_data()' first.")
        

    def sort(self, column: str, ascending: bool = True) -> None:
        """
        Sort the DataFrame by a specific column.
        :param column: Column name to sort by.
        :param ascending: Sort order (True for ascending, False for descending).
        """
        if self.data is not None:
            if column not in self.data.columns:
                raise ValueError(f"Column '{column}' not found in data.")
            self.data = self.data.sort_values(by=column, ascending=ascending)
        else:
            raise ValueError("No data loaded. Call 'load_data()' first.")


    def filter(self, column: str, condition: str, operation: str = "query") -> None:
        """
        Filter the DataFrame based on a specific condition.
        :param column: Column name to apply the filter on.
        :param condition: Condition as a string (e.g., "value == 'some_value'" or substring for 'contains').
        :param operation: The type of filtering operation ("query", "contains", or "startswith").
        """
        if self.data is None:
            raise ValueError("No data loaded. Call 'load_data()' first.")
        
        if column not in self.data.columns:
            raise ValueError(f"Column '{column}' not found in data.")

        try:
            if operation == "query":
                self.data = self.data.query(f"{column} {condition}")
            elif operation == "contains":
                self.data = self.data[self.data[column].str.contains(condition, na=False)]
            elif operation == "startswith":
                self.data = self.data[self.data[column].str.startswith(condition, na=False)]
            else:
                raise ValueError(f"Unsupported filter operation: {operation}")
        except Exception as e:
            raise ValueError(f"Invalid filter operation. Error: {e}")


    def execute_steps(self, cfg: str) -> None:
        """
        Execute a series of cleaning steps in the specified order.
        :param steps: List of cleaning steps in the format:
                      [{"operation": "sort", "params": {...}}, {"operation": "filter", "params": {...}}]
        """
        steps = []
        with open(cfg, "r") as f:
            steps = json.load(f).get("cleaning_steps", [])

        if self.data is None:
            raise ValueError("No data loaded. Call 'load_data()' first.")

        for step in steps:
            operation = step.get("operation")
            params = step.get("params", {})

            if operation == "sort":
                self.sort(**params)
            elif operation == "filter":
                self.filter(**params)
            else:
                raise ValueError(f"Unsupported operation: {operation}")    
            
    def save_to(self, output_path: str, encoding: str = "utf-8") -> None:
        """
        Save the cleaned data to a specified file with support for encoding.
        :param output_path: The path where the data should be saved.
                            Supports .csv and .xlsx formats.
        :param encoding: Encoding to use when saving the file (default: "utf-8-sig").
        """
        if self.data is None or self.data.empty:
            raise ValueError("No data to save. Ensure data is loaded and cleaned before saving.")
        
        # Check file extension
        _, ext = os.path.splitext(output_path)
        ext = ext.lower()

        if ext == ".csv":
            self.data.to_csv(output_path, index=False, encoding=encoding)
        elif ext == ".xlsx":
            # For Excel, pandas handles encoding internally
            self.data.to_excel(output_path, index=False)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Only .csv and .xlsx are supported.")

        print(f"Data saved to {output_path} with encoding {encoding}")


    def get_data(self):
        """
        Return a view of the data.
        """
        return self.data.copy(deep=False) if self.data is not None else None