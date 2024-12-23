import os
import pandas as pd
from typing import List, Union, Callable

class DataManager:
    """
    A flexible data loading manager for handling single or multiple files.
    Supports directory-based loading, filtering by naming rules, and custom conditions.
    """

    def __init__(self, directory: str = None, file_path: str = None):
        """
        Initialize the DataManager.
        :param directory: Path to the folder containing files.
        :param file_path: Path to a single file.
        """
        print(f"Directory: {directory}")
        print(f"File Path: {file_path}")
        self.directory = directory
        self.file_path = file_path

    def load_files(self, pattern: str = None, filter_func: Callable[[str], bool] = None, sheet_name_column: str = None) -> pd.DataFrame:
        """
        Load data from a directory or a single file.
        :param pattern: Regex pattern to match filenames (optional).
        :param filter_func: Custom filter function for filenames (optional).
        :return: Combined pandas DataFrame.
        """
        if self.file_path:  # Single file mode
            return self._load_file(self.file_path, sheet_name_column=sheet_name_column)
        
        if self.directory:  # Directory mode
            all_files = [os.path.join(self.directory, f) for f in os.listdir(self.directory)]
            # Apply filtering if provided
            if pattern:
                import re
                all_files = [f for f in all_files if re.search(pattern, f)]
            if filter_func:
                all_files = [f for f in all_files if filter_func(f)]
            # Load and combine files
            return self._combine_files(all_files, sheet_name_column=sheet_name_column)

        raise ValueError("Either 'directory' or 'file_path' must be specified.")

    def _load_file(self, file_path: str, sheet_name_column: str = None) -> pd.DataFrame:
        """
        Load a single file into a pandas DataFrame.
        Supports .xlsx, .xls, and .csv files.
        """
        if file_path.endswith(('.xlsx', '.xls')):
            return self._load_and_merge_sheets(file_path, sheet_name_column=sheet_name_column)  # Handle multi-sheet logic
        elif file_path.endswith('.csv'):
            print(f"Loading CSV file: {file_path}")
            return pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")

    def _combine_files(self, file_paths: List[str], sheet_name_column: str = None) -> pd.DataFrame:
        """
        Combine multiple files into a single pandas DataFrame.
        :param file_paths: List of file paths to load.
        :return: Combined DataFrame.
        """
        dataframes = [self._load_file(file, sheet_name_column=sheet_name_column) for file in file_paths]
        return pd.concat(dataframes, ignore_index=True)

    def _load_and_merge_sheets(self, file_path: str, sheet_name_column: str = None) -> pd.DataFrame:
        """
        Load data from all sheets in an Excel file and merge them into a single DataFrame.
        Optionally adds a column to differentiate data from each sheet if there are multiple sheets.

        :param file_path: Path to the Excel file.
        :param sheet_name_column: Name of the column to store sheet names. If None, no column is added.
        :return: Merged DataFrame.
        """
        sheets = pd.read_excel(file_path, sheet_name=None)  # Read all sheets
        dataframes = []

        for sheet_name, df in sheets.items():
            if sheet_name_column:
                df[sheet_name_column] = sheet_name  # Add sheet name column
            dataframes.append(df)

        merged_data = pd.concat(dataframes, ignore_index=True)
        print(f"Merged data from {len(sheets)} sheets in file: {file_path}")
        return merged_data