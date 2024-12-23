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