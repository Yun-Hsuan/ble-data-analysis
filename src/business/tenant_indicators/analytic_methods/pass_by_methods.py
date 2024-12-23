import pandas as pd
from typing import Dict, Optional, Tuple
from datetime import datetime

class PassByMethods:
    """
    Methods to calculate pass-by metrics for tenants.
    """

    @staticmethod
    def simple(
        terminal_data: Dict[str, pd.DataFrame],
        tenant_mapping: Dict[str, str],
        rssi_thresholds: Optional[Dict[str, int]] = None,
        time_interval: Optional[Tuple[datetime, datetime]] = None
    ) -> pd.DataFrame:
        """
        Calculate pass-by counts using a simple method, with optional RSSI filtering and time interval grouping.

        :param terminal_data: Terminal data grouped by terminal ID.
        :param tenant_mapping: Mapping of terminal IDs to tenant names.
        :param rssi_thresholds: Dictionary of terminal-specific RSSI thresholds (optional).
        :param time_interval: A tuple containing start and end times for filtering (optional).
        :return: A pandas DataFrame with pass-by counts per tenant.
        """
        results = []
        
        for terminal_id, data in terminal_data.items():
            tenant_name = tenant_mapping.get(terminal_id, "Unknown")
            
            # Apply RSSI filtering if a threshold is provided for this terminal
            if terminal_id in rssi_thresholds:
                threshold = rssi_thresholds[terminal_id]
                data = data[data['rssi'] > threshold]

            # Apply time interval filtering if specified
            data.loc[:, 'eventTime'] = pd.to_datetime(data['eventTime'], errors='coerce')
            data = data.dropna(subset=['eventTime'])
            data['eventTime'] = pd.to_datetime(data['eventTime'])
            if time_interval and 'eventTime' in data.columns:
                start_time, end_time = time_interval
                data = data[(data['eventTime'] >= start_time) & (data['eventTime'] <= end_time)]

            pass_by_count = data['memberId'].nunique() if 'memberId' in data.columns else 0

            results.append({
                "tenantName": tenant_name,
                "terminalId": terminal_id,
                "passByCount": pass_by_count
            })

        return pd.DataFrame(results)

    @staticmethod
    def advanced(
        terminal_data: Dict[str, pd.DataFrame],
        tenant_mapping: Dict[str, str]
    ) -> pd.DataFrame:
        """
        Calculate pass-by counts using an advanced method, considering additional metrics like RSSI or dwell time.

        :param terminal_data: Terminal data grouped by terminal ID.
        :param tenant_mapping: Mapping of terminal IDs to tenant names.
        :return: A pandas DataFrame with pass-by counts per tenant.
        """
        results = []

        for terminal_id, data in terminal_data.items():
            tenant_name = tenant_mapping.get(terminal_id, "Unknown")

            # Filter data by RSSI > -75 as an example of advanced filtering
            filtered_data = data[data['rssi'] > -75]
            pass_by_count = len(filtered_data)

            results.append({
                "tenantName": tenant_name,
                "terminalId": terminal_id,
                "passByCount": pass_by_count
            })

        return pd.DataFrame(results)