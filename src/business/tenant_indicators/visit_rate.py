from business.base_tenant_indicator import BaseTenantIndicator
from business.tenant_indicators.analytic_methods.visit_rate_methods import VisitRateMethods
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import seaborn as sns


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

            # Apply RSSI filtering if thresholds are provided
            if self._entry_rssi_threshold and terminal_id in self._entry_rssi_threshold:
                threshold = self._entry_rssi_threshold[terminal_id]
                terminal_data = terminal_data[terminal_data['rssi'] > threshold]
            
            # terminal_data['eventTime'] = pd.to_datetime(terminal_data['eventTime'], errors='coerce')
            # terminal_data = terminal_data.dropna(subset=['eventTime'])

            terminal_data.loc[:, 'eventTime'] = pd.to_datetime(terminal_data['eventTime'], errors='coerce')
            terminal_data = terminal_data.dropna(subset=['eventTime'])
            terminal_data['eventTime'] = pd.to_datetime(terminal_data['eventTime'])

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
    
    def dwell_time_distribution(
            self, time_interval: Optional[Tuple[datetime, datetime]], 
            output_dir: str = "./dwell_time_distributions"):
        
        tenant_mapping=self.tenant_mapping
        """
        Generate and save dwell time distribution plots for each terminal.

        :param output_dir: Directory to save the distribution plots.
        """
        os.makedirs(output_dir, exist_ok=True)

         # Extract date from time_interval
        date_str = time_interval[0].strftime("%Y-%m-%d") if time_interval else "unknown_date"
        date_dir = os.path.join(output_dir, date_str)
        os.makedirs(date_dir, exist_ok=True)

        for terminal_id, terminal_data in self.terminal_data["ble_cleaner"].items():

            tenant_name = tenant_mapping.get(terminal_id, "Unknown Tenant")

            if terminal_data.empty:
                print(f"Skipping terminalId {terminal_id}: No data available.")
                continue

            # Apply RSSI filtering if thresholds are provided
            if self._entry_rssi_threshold and terminal_id in self._entry_rssi_threshold:
                threshold = self._entry_rssi_threshold[terminal_id]
                terminal_data = terminal_data[terminal_data['rssi'] > threshold]
            
            terminal_data.loc[:, 'eventTime'] = pd.to_datetime(terminal_data['eventTime'], errors='coerce')
            terminal_data = terminal_data.dropna(subset=['eventTime'])
            terminal_data['eventTime'] = pd.to_datetime(terminal_data['eventTime'])

            # Filter data for the specified time interval
            if time_interval:
                start_time, end_time = time_interval
                terminal_data = terminal_data[(terminal_data["eventTime"] >= start_time) & (terminal_data["eventTime"] <= end_time)]

            # Group by memberId to calculate dwell times
            member_dwell_times = terminal_data.groupby("memberId").agg(
                start_time=("eventTime", "min"),
                end_time=("eventTime", "max")
            ).reset_index()

            # Calculate dwell durations and filter by >10 seconds
            member_dwell_times["dwellDuration"] = (
                member_dwell_times["end_time"] - member_dwell_times["start_time"]
            ).dt.total_seconds()

            
            valid_dwell_times = member_dwell_times[member_dwell_times["dwellDuration"] > 30]["dwellDuration"]

            if valid_dwell_times.empty:
                print(f"Skipping terminalId {terminal_id}: No valid dwell times > 10s.")
                continue

            # Create the histogram with 10-second bins
            plt.figure(figsize=(10, 6))
            bins = np.arange(0, max(valid_dwell_times) + 10, 10)  # Bin size of 10 seconds
            sns.histplot(
                valid_dwell_times,
                bins=bins,
                kde=True,
                color=sns.color_palette("coolwarm", n_colors=10)[5],  # Use a coolwarm color palette
                edgecolor='black'
            )

            # Set plot details
            plt.title(f"Dwell Time Distribution for Tenant {tenant_name} ({date_str})")
            plt.xlabel("Dwell Time (seconds)")
            plt.ylabel("Visitor Count")
            plt.grid(axis='y', alpha=0.75)
            plt.xlim(0, 1200)

            # Save the plot
            plot_path = os.path.join(date_dir, f"dwell_time_distribution_{tenant_name.replace(' ', '_')}.png")
            plt.savefig(plot_path)
            plt.close()

            print(f"Plot saved for tenant {tenant_name} at {plot_path}")

            print(f"Saved dwell time distribution plot for terminalId {tenant_name} at {plot_path}")