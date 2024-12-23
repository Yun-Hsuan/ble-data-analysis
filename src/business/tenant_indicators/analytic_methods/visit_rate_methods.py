from typing import Dict, Optional, Tuple
import pandas as pd
from datetime import datetime, timedelta

class VisitRateMethods:
    """
    Methods to calculate visit rate metrics for tenants.
    """

    @staticmethod
    def simple(
        terminal_data: Dict[str, pd.DataFrame],
        tenant_mapping: Dict[str, str],
        rssi_thresholds: Optional[Dict[str, int]] = None,
        time_interval: Optional[Tuple[datetime, datetime]] = None
    ) -> pd.DataFrame:
        """
        Calculate visit rates using a simple method.

        :param terminal_data: Terminal data grouped by terminal ID.
        :param tenant_mapping: Mapping of terminal IDs to tenant names.
        :param rssi_thresholds: Dictionary of terminal-specific RSSI thresholds (optional).
        :param time_interval: A tuple containing start and end times for filtering (optional).
        :return: A pandas DataFrame with visit rates per tenant.
        """
        results = []

        for terminal_id, data in terminal_data.items():
            tenant_name = tenant_mapping.get(terminal_id, "Unknown")

            # Apply RSSI filtering if thresholds are provided
            if rssi_thresholds and terminal_id in rssi_thresholds:
                threshold = rssi_thresholds[terminal_id]
                data = data[data['rssi'] > threshold]
            
            # data.loc[:, 'eventTime'] = pd.to_datetime(data['eventTime'], errors='coerce')
            # data = data.dropna(subset=['eventTime'])
            # data['eventTime'] = pd.to_datetime(data['eventTime'])  

            # Apply time interval filtering if specified
            data.loc[:, 'eventTime'] = pd.to_datetime(data['eventTime'], errors='coerce')
            data = data.dropna(subset=['eventTime'])
            data['eventTime'] = pd.to_datetime(data['eventTime'])
            if time_interval and 'eventTime' in data.columns:
                start_time, end_time = time_interval
                data = data[(data['eventTime'] >= start_time) & (data['eventTime'] <= end_time)]

            # Calculate visit count
            visit_count = len(data['memberId'].unique())
            results.append({
                "tenantName": tenant_name,
                "terminalId": terminal_id,
                "visitCount": visit_count
            })

        return pd.DataFrame(results)

    @staticmethod
    def advanced(
        terminal_data: Dict[str, pd.DataFrame],
        tenant_mapping: Dict[str, str]
    ) -> pd.DataFrame:
        """
        Advanced method to calculate visit rates.
        :param terminal_data: Terminal data grouped by terminal ID.
        :param tenant_mapping: Mapping of terminal IDs to tenant names.
        :return: A pandas DataFrame with advanced visit rates per tenant.
        """
        # Placeholder for advanced calculations
        # Add more detailed logic if required
        results = [
            {
                "tenantName": tenant_mapping.get(terminal_id, "Unknown"),
                "terminalId": terminal_id,
                "visitRate": len(data['memberId'].unique())  # Example: Unique visits
            }
            for terminal_id, data in terminal_data.items()
        ]

        return pd.DataFrame(results)