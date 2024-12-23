import os
import pandas as pd
from data_processing.base_cleaner import BaseCleaner

class TransactionCleaner(BaseCleaner):
    """
    Cleaner for transaction data.
    """

    def clean(self) -> pd.DataFrame:
        """
        Clean the intermediate transaction data:
        1. Retain only required columns.
        2. Standardize column names.
        3. Parse specific fields (e.g., timestamps).
        """
        if self.data is None:
            raise ValueError("No data loaded. Call 'load_data()' first.")

        # Define column name mapping (new column names -> old column names)
        column_mapping = {
            "店別": "storeId",
            "櫃位": "tenantName",
            "機號": "terminalId",
            "序號": "serialNumber",
            "交易日期": "transDate",
            "交易時間": "transTime"
        }

        # Rename columns to standard names
        self.data.rename(columns=column_mapping, inplace=True)

        # Retain only required columns
        required_columns = ["tenantName", "terminalId", "transDate", "transTime"]
        if not set(required_columns).issubset(self.data.columns):
            raise ValueError(f"Missing required columns: {set(required_columns) - set(self.data.columns)}")

        self.data = self.data[required_columns]
       
         # Combine 'eventDate' and 'eventTime' into a single 'timestamp' column
        self.data["eventTime"] = pd.to_datetime(
            self.data["transDate"].astype(str) + " " + self.data["transTime"].astype(str),
            format="%Y-%m-%d %H%M",
            errors="coerce"
        )

        # Drop original 'eventDate' and 'eventTime' columns
        self.data.drop(columns=["transDate", "transTime"], inplace=True)

        # Log invalid rows with missing timestamps
        invalid_rows = self.data[self.data["eventTime"].isna()]
        if not invalid_rows.empty:
            print("Warning: The following rows have invalid 'timestamp' values and were set to NaT:")
            print(invalid_rows)

        print("Cleaning process completed successfully.")
        return self.data

    def validate(self) -> bool:
        """
        Validate the transaction data structure.
        :return: True if valid, False otherwise.
        """
        required_columns = ["tenantName", "terminalId", "eventTime"]
        return all(column in self.data.columns for column in required_columns)

    def profile(self) -> dict:
        """
        Provide a profile of the transaction data, including key statistics.
        :return: A dictionary containing data profiling information.
        """
        if self.data is None:
            raise ValueError("No data loaded. Call 'load_data()' first.")

        total_rows = len(self.data)
        unique_users = self.data["user_id"].nunique()
        max_amount_row = self.data.loc[self.data["amount"].idxmax()].to_dict()
        min_amount_row = self.data.loc[self.data["amount"].idxmin()].to_dict()

        profile = {
            "total_rows": total_rows,
            "unique_users": unique_users,
            "max_amount_row": max_amount_row,
            "min_amount_row": min_amount_row
        }

        return profile

    def filter_invalid_transactions(self) -> None:
        """
        Filter out transactions with invalid or missing values.
        """
        if self.data is None:
            raise ValueError("No data loaded. Call 'load_data()' first.")

        before_count = len(self.data)

        # Filter out rows with missing or invalid 'amount' values
        self.data = self.data[self.data["amount"].notna() & (self.data["amount"] > 0)]

        after_count = len(self.data)
        removed_count = before_count - after_count

        print(f"Filtered invalid transactions. Rows before: {before_count}, after: {after_count}, removed: {removed_count}")
