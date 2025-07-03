from src.business.base_tenant_indicator import BaseTenantIndicator
from src.business.tenant_indicators.analytic_methods.dwell_rate_methods import DwellRateMethods
from datetime import datetime
from typing import Optional, Dict, Tuple, List
import pandas as pd

class DwellRateIndicator(BaseTenantIndicator):
    """
    Dwell Rate Indicator: Calculates the dwell rate for tenants.
    """

    def __init__(self, dwell_time_thresholds: List[int] = None):
        """
        Initialize DwellRateIndicator with optional dwell time thresholds.

        :param dwell_time_thresholds: List of thresholds to segment users based on dwell time.
        """
        super().__init__()
        self.dwell_data = None
        self.dwell_time_thresholds = dwell_time_thresholds or [60, 180, 300]  # Default thresholds

    def count(
        self,
        method: str = "simple",
        time_interval: Optional[Tuple[datetime, datetime]] = None
    ) -> pd.DataFrame:
        """
        Calculate the dwell rate for each tenant using the specified method.

        :param method: Method to calculate dwell rate ('simple' or 'advanced').
        :param time_interval: A tuple containing start and end times for filtering (optional, for 'simple').
        :return: A pandas DataFrame with dwell rates per tenant.
        """
        if method == "simple":
            self.dwell_data = DwellRateMethods.simple(
                terminal_data=self.terminal_data["ble_cleaner"],
                tenant_mapping=self.tenant_mapping,
                rssi_thresholds=self._entry_rssi_threshold,
                time_interval=time_interval,
                dwell_time_thresholds = self.dwell_time_thresholds
            )
        elif method == "advanced":
            self.dwell_data = DwellRateMethods.advanced(
                terminal_data=self.terminal_data["ble_cleaner"],
                tenant_mapping=self.tenant_mapping
            )
        else:
            raise ValueError(f"Unsupported method: {method}")

        return self.dwell_data

    def rate(
        self,
        visit_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate the dwell rate for each tenant by comparing dwell counts to visit counts.

        :param visit_df: DataFrame containing visit counts with columns 'tenantName', 'terminalId', and 'visitCount'.
        :return: A pandas DataFrame with calculated dwell rates.
        """
        if self.dwell_data is None:
            raise ValueError("Dwell data is not calculated. Call 'count()' before 'rate()'.")

        # Merge dwell data with visit data
        merged_df = pd.merge(
            self.dwell_data,
            visit_df,
            on=["tenantName", "terminalId"],
            how="inner"
        )

        # Calculate dwell rates for each dwell threshold
        for threshold in self.dwell_time_thresholds:
            dwell_col = f"dwellCount_{threshold}"
            rate_col = f"dwellRate_{threshold}"
            merged_df[rate_col] = merged_df[dwell_col] / merged_df["visitCount"]

        return merged_df