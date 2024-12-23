from typing import Dict, Optional, Tuple, List
import pandas as pd
from datetime import datetime, timedelta

class DwellRateMethods:
    """
    Methods to calculate dwell rate metrics for tenants.
    """

    @staticmethod
    def simple(
        terminal_data: Dict[str, pd.DataFrame],
        tenant_mapping: Dict[str, str],
        rssi_thresholds: Optional[Dict[str, int]] = None,
        time_interval: Optional[Tuple[datetime, datetime]] = None,
        dwell_time_thresholds: Optional[List[int]] = None
    ) -> pd.DataFrame:
        """
        Calculate dwell rates using a simple method, including dwell counts for thresholds.

        :param terminal_data: Terminal data grouped by terminal ID.
        :param tenant_mapping: Mapping of terminal IDs to tenant names.
        :param rssi_thresholds: Dictionary of terminal-specific RSSI thresholds (optional).
        :param time_interval: A tuple containing start and end times for filtering (optional).
        :param dwell_time_thresholds: List of thresholds for calculating dwell counts.
        :return: A pandas DataFrame with dwell rates and dwell counts per tenant.
        """
        results = []
        for terminal_id, data in terminal_data.items():
            tenant_name = tenant_mapping.get(terminal_id, "Unknown")

            # Apply RSSI filtering if thresholds are provided
            if rssi_thresholds and terminal_id in rssi_thresholds:
                threshold = rssi_thresholds[terminal_id]
                data = data[data['rssi'] > threshold]
            
            data.loc[:, 'eventTime'] = pd.to_datetime(data['eventTime'], errors='coerce')
            data = data.dropna(subset=['eventTime'])
            data['eventTime'] = pd.to_datetime(data['eventTime']) 
            # Apply time interval filtering if specified
            if time_interval and 'eventTime' in data.columns:    
                start_time, end_time = time_interval
                data = data[(data['eventTime'] >= start_time) & (data['eventTime'] <= end_time)]

            visit_count = len(data['memberId'].unique())
            # Calculate first and last times for each member
            member_dwell_times = data.groupby('memberId')['eventTime'].agg(
                first_time='min', last_time='max'
            )
            member_dwell_times['dwellDuration'] = (
                member_dwell_times['last_time'] - member_dwell_times['first_time']
            ).dt.total_seconds()
            
            # Calculate dwell counts for each threshold
            dwell_counts = {}
            for threshold in dwell_time_thresholds:
                dwell_counts[f"dwellCount_{threshold}"] = (member_dwell_times['dwellDuration'] >= threshold).sum()

            # Append results
            results.append({
                "tenantName": tenant_name,
                "terminalId": terminal_id,
                **dwell_counts
            })

        return pd.DataFrame(results)

    @staticmethod
    def advanced(
        terminal_data: Dict[str, pd.DataFrame],
        tenant_mapping: Dict[str, str]
    ) -> pd.DataFrame:
        """
        Advanced method to calculate dwell rates.
        :param terminal_data: Terminal data grouped by terminal ID.
        :param tenant_mapping: Mapping of terminal IDs to tenant names.
        :return: A pandas DataFrame with advanced dwell rates per tenant.
        """
        results = []

        for terminal_id, data in terminal_data.items():
            tenant_name = tenant_mapping.get(terminal_id, "Unknown")

            # Calculate dwell time per member
            data['eventTime'] = pd.to_datetime(data['eventTime'], errors='coerce')
            data['dwellTime'] = data.groupby('memberId')['eventTime'].transform(
                lambda x: (x.max() - x.min()).total_seconds()
            )

            # Advanced aggregation logic
            dwell_rate = data['dwellTime'].median() if not data.empty else 0

            results.append({
                "tenantName": tenant_name,
                "terminalId": terminal_id,
                "dwellRate": dwell_rate
            })

        return pd.DataFrame(results)