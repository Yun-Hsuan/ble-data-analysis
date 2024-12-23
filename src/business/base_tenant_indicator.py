from typing import Dict, Union
import json
import pandas as pd
from abc import ABC, abstractmethod
from data_processing.cleaners.ble_cleaner import BLECleaner
from data_processing.cleaners.transaction_cleaner import TransactionCleaner

class BaseTenantIndicator(ABC):
    """
    Abstract base class for tenant business indicators.
    Handles input from multiple cleaners and organizes data by terminal ID.
    """

    def __init__(self):
        """
        Initialize the BaseTenantIndicator with a predefined structure for cleaners.
        Each cleaner contributes its cleaned data, grouped by terminalId.
        """
        # Define expected cleaners and their classes
        self.cleaners: Dict[str, Union[BLECleaner, TransactionCleaner]] = {
            "ble_cleaner": None,
            "transaction_cleaner": None,
        }
        self.terminal_data: Dict[str, Dict[str, pd.DataFrame]] = {}
        self.tenant_mapping: Dict[str, str] = {}  # Map terminalId -> tenantName

        # Private parameters for RSSI thresholds
        self._pass_by_rssi_threshold: Dict[str, int] = {}
        self._entry_rssi_threshold: Dict[str, int] = {}
        self._transaction_rssi_threshold: int = -30

    def set_rssi_thresholds_from_file(self, file_path: str):
        """
        Set the RSSI thresholds for pass-by and entry calculations from an Excel file.
        The file must have columns 'terminalId', 'pass_by_rssi_threshold', and 'entry_rssi_threshold'.

        :param file_path: Path to the Excel file containing threshold data.
        """
        try:
            threshold_data = pd.read_excel(file_path)
            if not {'terminalId', 'pass_by_rssi_threshold', 'entry_rssi_threshold'}.issubset(threshold_data.columns):
                raise ValueError("The file must contain 'terminalId', 'pass_by_rssi_threshold', and 'entry_rssi_threshold' columns.")

            # Convert to dictionaries
            self._pass_by_rssi_threshold = threshold_data.set_index('terminalId')['pass_by_rssi_threshold'].to_dict()
            self._entry_rssi_threshold = threshold_data.set_index('terminalId')['entry_rssi_threshold'].to_dict()
            print("RSSI thresholds successfully loaded from file.")
        except Exception as e:
            print(f"Error loading RSSI thresholds from file: {e}")

    def set_tenant_mapping(self, mapping_table_path: str):
        """
        Load a tenantName-terminalId mapping table from an xlsx file and store it as a dictionary.
        :param mapping_table_path: Path to the xlsx file containing the mapping table.
        """
        if not mapping_table_path:
            raise FileNotFoundError(f"The file {mapping_table_path} does not exist.")

        # Load the mapping table
        mapping_table = pd.read_excel(mapping_table_path)

        # Validate the mapping table
        required_columns = {"tenantName", "terminalId"}
        if not required_columns.issubset(mapping_table.columns):
            raise ValueError(f"The mapping table must contain the columns: {required_columns}")

        # Convert mapping table to dictionary
        self.tenant_mapping = mapping_table.set_index("terminalId")["tenantName"].to_dict()
        print("TenantName mapping table has been successfully loaded.")


    def set_cleaner(self, cleaner_name: str, cleaner_instance: Union[BLECleaner, TransactionCleaner]):
        """
        Set the cleaner instance for the given cleaner name.
        :param cleaner_name: The name of the cleaner (e.g., "ble_cleaner").
        :param cleaner_instance: The instance of the cleaner.
        """
        if cleaner_name not in self.cleaners:
            raise ValueError(f"Cleaner '{cleaner_name}' is not recognized. Allowed cleaners: {list(self.cleaners.keys())}")

        self.cleaners[cleaner_name] = cleaner_instance

        # Organize data by terminalId for the cleaner
        data = cleaner_instance.get_data()
        if 'terminalId' not in data.columns:
            raise ValueError(f"The data from cleaner '{cleaner_name}' is missing the 'terminalId' column.")

        grouped_data = {
            terminal_id: group.reset_index(drop=True)
            for terminal_id, group in data.groupby('terminalId')
        }

        # Store grouped data
        self.terminal_data[cleaner_name] = grouped_data


    def get_mapping(self) -> Dict[str, str]:
        """
        Get the tenantName to terminalId mapping dictionary.
        :return: The mapping dictionary.
        """
        return self.tenant_mapping
    

    @abstractmethod
    def count(self, method: str = "default", *args, **kwargs):
        """
        Abstract method for calculating the indicator.
        Must be implemented by subclasses.
        """
        pass

    def profile(self) -> str:
        """
        Generate a profile for each cleaner and terminal:
        - Count of rows for each terminal.
        - Include tenantName in the profile if mapping exists.
        - Return the result in pretty JSON format.

        :return: A pretty JSON string with cleaner names as the first level keys,
                terminal IDs as the second level keys, and profiles as values.
        """
        profile_result = {}
        for cleaner_name, terminals in self.terminal_data.items():
            profile_result[cleaner_name] = {}
            for terminal_id, data in terminals.items():
                tenant_name = self.tenant_mapping.get(terminal_id, None)

                profile_result[cleaner_name][terminal_id] = {
                    "tenantName": tenant_name,
                    "row_count": len(data),
                    "unique_members": data['memberId'].nunique() if 'memberId' in data.columns else None
                }

        # Convert the result dictionary to a pretty JSON string
        pretty_json = json.dumps(profile_result, indent=4, ensure_ascii=False)
        return pretty_json

    def profile_legacy(self, rssi_threshold: int = -65, dwell_time_threshold: int = -60) -> str:
        """
        Generate a JSON profile for each terminal with:
        1. Unique memberId count
        2. Count of unique memberId with rssi > -70
        3. Count of memberId dwell_time > 60 seconds
        
        :return: JSON string with profile information.
        """
        import json

        result = {}
        for terminal_id, data in self.terminal_data.items():
            # Unique memberId count
            unique_members = data['memberId'].nunique()

            # Filter data by rssi > rssi_threshold
            filtered_data = data[data['rssi'] > rssi_threshold]

            # Ensure eventTime is datetime format
            filtered_data['eventTime'] = pd.to_datetime(filtered_data['eventTime'], errors='coerce')

            # Calculate dwell_time per memberId on filtered data
            dwell_times = filtered_data.groupby('memberId')['eventTime'].agg(['min', 'max'])
            dwell_times['dwell_time'] = (dwell_times['max'] - dwell_times['min']).dt.total_seconds()

            # Unique memberId with dwell_time > dwell_time_threshold
            dwell_filtered = dwell_times[dwell_times['dwell_time'] > dwell_time_threshold]

            # Store results for this terminal
            result[terminal_id] = {
                "unique_member_ids": unique_members,
                f"unique_member_ids_rssi_above_{rssi_threshold}": filtered_data['memberId'].nunique(),
                f"member_id_dwell_time_gt_{dwell_time_threshold}s": dwell_filtered.shape[0]
            }

        # Convert to JSON and return
        return json.dumps(result, indent=4)    