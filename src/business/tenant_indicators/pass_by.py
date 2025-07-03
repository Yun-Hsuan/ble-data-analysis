from src.business.base_tenant_indicator import BaseTenantIndicator
from src.business.tenant_indicators.analytic_methods.pass_by_methods import PassByMethods
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import pandas as pd

class PassByIndicator(BaseTenantIndicator):
    """
    Pass By Indicator: Calculates the number of people passing by a tenant.
    """

    def count(
        self,
        method: str = "simple",
        time_interval: Optional[Tuple[datetime, datetime]] = None
    ) -> pd.DataFrame:
        """
        Calculate the pass-by count for each tenant using the specified method.

        :param method: Method to calculate pass-by count ('simple' or 'advanced').
        :param rssi_thresholds: Dictionary of terminal-specific RSSI thresholds (optional, for 'simple').
        :param time_interval: A tuple containing start and end times for filtering (optional, for 'simple').
        :return: A pandas DataFrame with pass-by counts per tenant.
        """
        if method == "simple":
            # Ensure the BLE cleaner data is used for calculations
            
            # ble_data = self.cleaners.get("ble_cleaner")
            # terminal_data = {
            #     terminal_id: df for terminal_id, df in ble_data.get_data().groupby("terminalId")
            # }
            # print(self.terminal_data["ble_cleaner"])
            # exit()
            return PassByMethods.simple(
                terminal_data=self.terminal_data["ble_cleaner"],
                tenant_mapping=self.tenant_mapping,
                rssi_thresholds=self._pass_by_rssi_threshold,
                time_interval=time_interval
            )

        elif method == "advanced":
            # Ensure the BLE cleaner data is used for calculations
            ble_data = self.cleaners.get("ble_cleaner")
            if not ble_data:
                raise ValueError("BLECleaner data is required for pass-by calculations.")

            terminal_data = {
                terminal_id: df for terminal_id, df in ble_data.get_data().groupby("terminalId")
            }

            return PassByMethods.advanced(
                terminal_data=terminal_data,
                tenant_mapping=self.tenant_mapping
            )

        else:
            raise ValueError(f"Unsupported method: {method}")