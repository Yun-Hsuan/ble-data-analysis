import os
import pandas as pd
import json
from data_processing.base_cleaner import BaseCleaner

class BLECleaner(BaseCleaner):
    """
    Cleaner for BLE scan data.
    """

    def clean(self) -> pd.DataFrame:
        """
        Clean the intermediate BLE data:
        1. Retain only required columns.
        2. Parse 'rawData' (JSON format) to extract 'accessAddress' and 'rssi'.
        3. Add parsed values as new columns.
        """
        if self.data is None:
            raise ValueError("No data loaded. Call 'load_data()' first.")

        # Define column name mapping (new column names -> old column names)
        column_mapping = {
            "POSCode": "terminalId",
            "UserId": "memberId",
            "PLICd": "eventSource",
            "PLIEventCd": "eventType",
            "PLIEventTimestamp": "eventTime",
            "Distance": "distance",
            "RawData": "rawData"
        }
        
        # Rename columns to old names for compatibility
        self.data.rename(columns=column_mapping, inplace=True)
        
        # Retain only required columns
        required_columns = [
            "terminalId", "memberId", "eventSource", "eventType", "eventTime", "distance", "rawData"
        ]
        if not set(required_columns).issubset(self.data.columns):
            raise ValueError(f"Missing required columns: {set(required_columns) - set(self.data.columns)}")
        
        self.data = self.data[required_columns]

        # Parse 'rawData' and add 'accessAddress' and 'rssi'
        def parse_raw_data(raw_data):
            try:
                parsed = json.loads(raw_data)
                return parsed.get("AD3"), parsed.get("rssi")
            except (json.JSONDecodeError, TypeError):
                return None, None

        self.data["accessAddress"], self.data["rssi"] = zip(*self.data["rawData"].map(parse_raw_data))

        # Drop the original 'rawData' column and any unused columns
        self.data.drop(columns=["rawData", "distance", "eventSource"], inplace=True)

        # Add a unique 'id' column (optional)
        self.data.reset_index(drop=True, inplace=True)
        self.data.insert(0, "id", self.data.index + 1)

        def convert_to_24_hour_format(value):
            """
            Convert Chinese AM/PM time format to 24-hour format and return valid datetime strings.
            Handle invalid or empty values gracefully.
            """
            if not isinstance(value, str) or value.strip() == "":
                # Handle empty or non-string values
                return None

            value = value.strip()  # Remove leading/trailing whitespace

            try:
                if "上午" in value:
                    # Remove '上午' and return cleaned time
                    return value.replace("上午", "").strip()
                elif "下午" in value:
                    # Process '下午' and convert to 24-hour format
                    date_part, time_part = value.replace("下午", "").strip().split("  ")
                    hour, minute, second = map(int, time_part.split(":"))
                    if hour != 12:  # Avoid converting 12 PM to 24
                        hour += 12
                    time_part = f"{hour}:{minute:02}:{second:02}"
                    return f"{date_part} {time_part}"
                else:
                    # Assume already valid format
                    return value
            except (ValueError, IndexError) as e:
                # Log invalid values and return None
                print(f"Invalid time format encountered: {value}. Error: {e}")
                return None

        # Apply the conversion function and extract only the date
        print("Standardizing 'eventTime' column to date format...")
        self.data["eventTime"] = self.data["eventTime"].map(convert_to_24_hour_format)
        self.data["eventTime"] = pd.to_datetime(self.data["eventTime"], format="%Y/%m/%d %H:%M:%S", errors="coerce")

        # Log invalid rows
        invalid_rows = self.data[self.data["eventTime"].isna()]
        if not invalid_rows.empty:
            print("Warning: The following rows have invalid 'eventTime' values and were set to NaT:")
            print(invalid_rows)

        print("Cleaning process completed successfully.")
        return self.data


    def validate(self) -> bool:
        """
        Implement validation logic for BLE data.
        """
        # Example: Ensure required columns are present
        required_columns = ["rssi", "timestamp", "device_id"]
        return all(column in self.data.columns for column in required_columns)
    
    def profile(self) -> dict:
        """
        Provide a profile of the data, including key statistics.
        :return: A dictionary containing data profiling information.
        """
        if self.data is None:
            raise ValueError("No data loaded. Call 'load_data()' first.")

        # 1. Total number of rows
        total_rows = len(self.data)

        # 2. Number of unique memberID values
        unique_members = self.data["memberId"].nunique()

        # 3. Row with maximum rssi value
        max_rssi_row = self.data.loc[self.data["rssi"].idxmax()].to_dict()

        # 4. Row with minimum rssi value
        min_rssi_row = self.data.loc[self.data["rssi"].idxmin()].to_dict()

        # Construct profile dictionary
        profile = {
            "total_rows": total_rows,
            "unique_member_ids": unique_members,
            "max_rssi_row": max_rssi_row,
            "min_rssi_row": min_rssi_row,
        }

        return profile

    def filter_invalid_member_ids(self) -> None:
        """
        Filter out member_ids that are only detected on a single terminalId.
        Log the total count of member_ids before and after filtering, and rows removed.
        """
        if self.data is None:
            raise ValueError("No data loaded. Call 'load_data()' first.")

        # 計算剔除前的 memberId 總數
        member_ids_before = self.data['memberId'].nunique()

        # Group by memberId and count the number of unique terminalIds for each memberId
        member_terminal_counts = self.data.groupby('memberId')['terminalId'].nunique()

        # 找出只出現在單一 terminalId 的 memberId
        invalid_member_ids = member_terminal_counts[member_terminal_counts == 1].index

        # 計算要剔除的 rows 數量
        rows_to_remove = self.data[self.data['memberId'].isin(invalid_member_ids)].shape[0]

        # 剔除無效的 memberId
        self.data = self.data[~self.data['memberId'].isin(invalid_member_ids)]

        # 計算剔除後的 memberId 總數
        member_ids_after = self.data['memberId'].nunique()

        # 計算被剔除的 memberId 總數
        total_removed_member_ids = member_ids_before - member_ids_after

        # Log filtering results
        print(f"Filtering invalid member_ids...")
        print(f"Total member_ids before filtering: {member_ids_before}")
        print(f"Total member_ids after filtering: {member_ids_after}")
        print(f"Total removed member_ids: {total_removed_member_ids}")
        print(f"Rows removed: {rows_to_remove}")
        