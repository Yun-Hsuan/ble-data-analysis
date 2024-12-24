from business.base_tenant_indicator import BaseTenantIndicator
from business.tenant_indicators.analytic_methods.visit_rate_methods import VisitRateMethods
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import pandas as pd

class VisitRateIndicator(BaseTenantIndicator):
    """
    Visit Rate Indicator: Calculates the visit rate for tenants.
    """

    def __init__(self):
        super().__init__()
        self.visit_data = None

    def count(
        self,
        method: str = "simple",
        time_interval: Optional[Tuple[datetime, datetime]] = None
    ) -> pd.DataFrame:
        """
        Calculate the visit rate for each tenant using the specified method.

        :param method: Method to calculate visit rate ('simple' or 'advanced').
        :param time_interval: A tuple containing start and end times for filtering (optional, for 'simple').
        :return: A pandas DataFrame with visit rates per tenant.
        """
        if method == "simple":
            self.visit_data = VisitRateMethods.simple(
                terminal_data=self.terminal_data["ble_cleaner"],
                tenant_mapping=self.tenant_mapping,
                rssi_thresholds=self._entry_rssi_threshold,
                time_interval=time_interval
            )
        elif method == "advanced":
            self.visit_data = VisitRateMethods.advanced(
                terminal_data=self.terminal_data["ble_cleaner"],
                tenant_mapping=self.tenant_mapping
            )
        else:
            raise ValueError(f"Unsupported method: {method}")

        return self.visit_data
        
    def rate(
        self,
        pass_by_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate the visit rate for each tenant by comparing visit count to pass-by count.

        :param pass_by_df: DataFrame containing pass-by counts with columns 'tenantName', 'terminalId', and 'passByCount'.
        :return: A pandas DataFrame with calculated visit rates.
        """
        if self.visit_data is None:
            raise ValueError("Visit data is not calculated. Call 'count()' before 'rate()'.")

        # Merge visit count with pass-by count
        merged_df = pd.merge(
            self.visit_data,
            pass_by_df,
            on=["tenantName", "terminalId"],
            how="inner"
        )

        # Calculate visit rate
        merged_df["visitRate"] = merged_df["visitCount"] / merged_df["passByCount"]

        return merged_df
    

    def average_dwell_time(
        self, time_interval: Optional[Tuple[datetime, datetime]]
    ) -> pd.DataFrame:
        """
        Calculate the average dwell time for unique members in a given time interval for all terminals.

        :param time_interval: A tuple containing start and end times for filtering.
        :return: A pandas DataFrame with terminalId, tenantName, and average dwell time for each tenant.
        """
        results = []

        for terminal_id, terminal_data in self.terminal_data["ble_cleaner"].items():
            tenant_name = self.tenant_mapping.get(terminal_id, "Unknown")

            terminal_data['eventTime'] = pd.to_datetime(terminal_data['eventTime'], errors='coerce')
            terminal_data = terminal_data.dropna(subset=['eventTime'])

            if terminal_data.empty:
                results.append({"terminalId": terminal_id, "tenantName": tenant_name, "averageDwellTime": 0.0})
                continue

            # Filter data for the specified time interval
            if time_interval:
                start_time, end_time = time_interval
                terminal_data = terminal_data[(terminal_data["eventTime"] >= start_time) & (terminal_data["eventTime"] <= end_time)]

            if terminal_data.empty:
                results.append({"terminalId": terminal_id, "tenantName": tenant_name, "averageDwellTime": 0.0})
                continue

            # Group by memberId and calculate first and last event times
            member_dwell_times = terminal_data.groupby("memberId").agg(
                first_time=("eventTime", "min"),
                last_time=("eventTime", "max")
            ).reset_index()

            # Calculate dwell duration and filter positive durations
            member_dwell_times["dwellDuration"] = (
                member_dwell_times["last_time"] - member_dwell_times["first_time"]
            ).dt.total_seconds()
            member_dwell_times = member_dwell_times[member_dwell_times["dwellDuration"] > 0]

            if member_dwell_times.empty:
                results.append({"terminalId": terminal_id, "tenantName": tenant_name, "averageDwellTime": 0.0})
                continue

            # Calculate average dwell time
            average_dwell_time = member_dwell_times["dwellDuration"].mean()
            results.append({"terminalId": terminal_id, "tenantName": tenant_name, "averageDwellTime": average_dwell_time})

        return pd.DataFrame(results)