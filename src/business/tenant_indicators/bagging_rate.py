from business.base_tenant_indicator import BaseTenantIndicator
from business.tenant_indicators.analytic_methods.bagging_rate_methods import BaggingRateMethods
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import pandas as pd

class BaggingRateIndicator(BaseTenantIndicator):
    """
    Bagging Rate Indicator: Calculates the bagging rate for tenants.
    """

    def __init__(self):
        super().__init__()
        self.bagging_data = None

    def count(
        self,
        method: str = "simple",
        time_interval: Optional[Tuple[datetime, datetime]] = None
    ) -> pd.DataFrame:
        """
        Calculate the bagging count for each tenant using the specified method.

        :param method: Method to calculate bagging metrics ('simple' or 'advanced').
        :param time_interval: A tuple containing start and end times for filtering (optional, for 'simple').
        :return: A pandas DataFrame with bagging metrics per tenant.
        """
        if method == "simple":
            self.bagging_data = BaggingRateMethods.simple(
                terminal_data=self.terminal_data["transaction_cleaner"],
                tenant_mapping=self.tenant_mapping,
                rssi_threshold=self._transaction_rssi_threshold,
                time_interval=time_interval
            )
        elif method == "advanced":
            self.bagging_data = BaggingRateMethods.advanced(
                terminal_data=self.terminal_data["transaction_cleaner"],
                tenant_mapping=self.tenant_mapping
            )
        else:
            raise ValueError(f"Unsupported method: {method}")

        return self.bagging_data

    def rate(
        self,
        dwell_df: pd.DataFrame,
        visit_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate the bagging rate for each tenant by comparing bagging count to dwell count and visit count.

        :param dwell_df: DataFrame containing dwell counts with columns 'tenantName', 'terminalId', and 'dwellCount_XX'.
        :param visit_df: DataFrame containing visit counts with columns 'tenantName', 'terminalId', and 'visitCount'.
        :return: A pandas DataFrame with calculated bagging rates.
        """
        if self.bagging_data is None:
            raise ValueError("Bagging data is not calculated. Call 'count()' before 'rate()'.")

        # Merge bagging data with dwell data
        merged_df = pd.merge(
            self.bagging_data,
            dwell_df,
            on=["tenantName", "terminalId"],
            how="inner"
        )

        # Merge with visit data
        merged_df = pd.merge(
            merged_df,
            visit_df,
            on=["tenantName", "terminalId"],
            how="inner"
        )

        # Calculate bagging rates for each dwell threshold
        for column in dwell_df.columns:
            if column.startswith("dwellCount_"):
                dwell_threshold = column.split("_")[-1]
                rate_col = f"baggingRate_{dwell_threshold}"
                merged_df[rate_col] = merged_df["baggingCount"] / merged_df[column]

        # Calculate bagging rate based on visit count
        merged_df["baggingRate_visit"] = merged_df["baggingCount"] / merged_df["visitCount"]

        return merged_df