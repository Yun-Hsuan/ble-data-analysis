from datetime import datetime
from typing import Optional, Dict, Tuple
import pandas as pd


class BaggingRateMethods:
    """
    Methods to calculate bagging rate metrics for tenants.
    """

    @staticmethod
    def simple(
        terminal_data: Dict[str, pd.DataFrame],
        tenant_mapping: Dict[str, str],
        rssi_threshold: Optional[int] = None,
        time_interval: Optional[Tuple[datetime, datetime]] = None
    ) -> pd.DataFrame:
        """
        Calculate bagging counts using a simple method.

        :param terminal_data: Terminal data grouped by terminal ID.
        :param tenant_mapping: Mapping of terminal IDs to tenant names.
        :param rssi_threshold: RSSI threshold for filtering (optional).
        :param time_interval: A tuple containing start and end times for filtering (optional).
        :return: A pandas DataFrame with bagging counts per tenant.
        """
        results = []

        for terminal_id, data in terminal_data.items():
            tenant_name = tenant_mapping.get(terminal_id, "Unknown")

            # Apply time interval filtering if specified
            if time_interval:
                data['eventTime'] = pd.to_datetime(data['eventTime'], errors='coerce')
                data = data.dropna(subset=['eventTime'])
                start_time, end_time = time_interval
                data = data[(data['eventTime'] >= start_time) & (data['eventTime'] <= end_time)]

            # Calculate bagging count
            bagging_count = data['eventTime'].nunique()  # Assuming unique transaction IDs represent bagging events

            results.append({
                "tenantName": tenant_name,
                "terminalId": terminal_id,
                "baggingCount": bagging_count
            })

        return pd.DataFrame(results)
