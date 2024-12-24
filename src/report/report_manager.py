import pandas as pd
from datetime import datetime, timedelta
from typing import List
from pathlib import Path
import json
from datetime import datetime, timedelta
from src.data_processing.cleaners.ble_cleaner import BLECleaner
from src.data_processing.cleaners.transaction_cleaner import TransactionCleaner
from src.business.tenant_indicators.visit_rate import VisitRateIndicator
from src.business.tenant_indicators.pass_by import PassByIndicator
from src.business.tenant_indicators.dwell_rate import DwellRateIndicator
from src.business.tenant_indicators.bagging_rate import BaggingRateIndicator

class ReportManager:
    """
    Manages the generation of daily tenant reports based on multiple indicators.
    """

    def __init__(self, output_dir: str, tenant_mapping_path: str):
        self.output_dir = Path(output_dir)
        self.tenant_mapping_path = tenant_mapping_path
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_daily_report(
        self,
        date: str,
        pass_by_indicator,
        visit_indicator,
        dwell_indicator,
        bagging_indicator,
        time_interval: List[tuple]
    ):
        """
        Generate a daily report for all tenants, including pass-by, visit, dwell, and bagging metrics.
        """
        # Load tenant mapping
        tenant_mapping = pd.read_excel(self.tenant_mapping_path).set_index("terminalId")["tenantName"].to_dict()

        # Prepare Excel writer
        output_file = self.output_dir / f"tenant_report_{date}.xlsx"
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            for tenant in tenant_mapping.values():
                print(f"Processing tenant: {tenant}")
                tenant_data = []
                
                if tenant == "ADIDAS ORIGINALS":
                    continue

                for interval in time_interval:
                    pass_by_results = pass_by_indicator.count(method="simple", time_interval=interval)
                    visit_results = visit_indicator.count(method="simple", time_interval=interval)
                    dwell_results = dwell_indicator.count(method="simple", time_interval=interval)
                    bagging_results = bagging_indicator.count(method="simple", time_interval=interval)

                    # Calculate rates
                    visit_rate_results = visit_indicator.rate(pass_by_results)
                    dwell_rate_results = dwell_indicator.rate(visit_results)
                    bagging_rate_results = bagging_indicator.rate(dwell_results, visit_results)

                    # Calculate average dwell time
                    average_dwell_time_results = visit_indicator.average_dwell_time(time_interval=interval)

                    # Collect data for this tenant
                        # Collect data for this tenant
                    tenant_row = {
                        "date": date,
                        "timeInterval": f"{interval[0].time()}-{interval[1].time()}",
                    }

                    # Check and update pass_by_results
                    pass_by_filtered = pass_by_results[pass_by_results["tenantName"] == tenant]
                    if not pass_by_filtered.empty:
                        tenant_row.update(pass_by_filtered.to_dict(orient="records")[0])
                    else:
                        print(f"Warning: Missing pass-by data for tenant '{tenant}' in time interval {interval}. Filling with 0.")
                        tenant_row.update({"passByCount": 0})

                    # Check and update visit_rate_results
                    visit_rate_filtered = visit_rate_results[visit_rate_results["tenantName"] == tenant]
                    if not visit_rate_filtered.empty:
                        tenant_row.update(visit_rate_filtered.to_dict(orient="records")[0])
                    else:
                        print(f"Warning: Missing visit rate data for tenant '{tenant}' in time interval {interval}. Filling with 0.")
                        tenant_row.update({"visitCount": 0, "visitRate": 0})

                    # Check and update dwell_rate_results
                    dwell_rate_filtered = dwell_rate_results[dwell_rate_results["tenantName"] == tenant]
                    if not dwell_rate_filtered.empty:
                        tenant_row.update(dwell_rate_filtered.to_dict(orient="records")[0])
                    else:
                        print(f"Warning: Missing dwell rate data for tenant '{tenant}' in time interval {interval}. Filling with 0.")
                        tenant_row.update({"dwellCount_60": 0, "dwellRate_60": 0})

                    # Check and update bagging_rate_results
                    bagging_rate_filtered = bagging_rate_results[bagging_rate_results["tenantName"] == tenant]
                    if not bagging_rate_filtered.empty:
                        tenant_row.update(bagging_rate_filtered.to_dict(orient="records")[0])
                    else:
                        print(f"Warning: Missing bagging rate data for tenant '{tenant}' in time interval {interval}. Filling with 0.")
                        tenant_row.update({"baggingCount": 0, "baggingRate_60": 0, "baggingRate_visit": 0})

                    # Check and update average_dwell_time_results
                    average_dwell_time_filtered = average_dwell_time_results[average_dwell_time_results["tenantName"] == tenant]
                    if not average_dwell_time_filtered.empty:
                        tenant_row.update(average_dwell_time_filtered.to_dict(orient="records")[0])
                    else:
                        tenant_row.update({"averageDwellTime": 0})

                    tenant_data.append(tenant_row)

                # Save tenant-specific data to its sheet
                if tenant_data:
                    tenant_df = pd.DataFrame(tenant_data)
                    unique_terminal_id = tenant_df["terminalId"].iloc[0] if "terminalId" in tenant_df.columns else None
                    total_row = {
                        "date": "Total",
                        "timeInterval": "11:00:00-22:00:00",
                        "terminalId": unique_terminal_id,
                        "passByCount": tenant_df["passByCount"].sum(),
                        "visitCount": tenant_df["visitCount"].sum(),
                        "dwellCount_60": tenant_df["dwellCount_60"].sum(),
                        "baggingCount": tenant_df["baggingCount"].sum(),
                        "averageDwellTime": tenant_df["averageDwellTime"].mean(),
                    }

                    # Calculate rates for "Total" row
                    total_row["visitRate"] = (
                        total_row["visitCount"] / total_row["passByCount"]
                        if total_row["passByCount"] > 0 else 0
                    )
                    total_row["dwellRate_60"] = (
                        total_row["dwellCount_60"] / total_row["visitCount"]
                        if total_row["visitCount"] > 0 else 0
                    )
                    total_row["baggingRate_60"] = (
                        total_row["baggingCount"] / total_row["dwellCount_60"]
                        if total_row["dwellCount_60"] > 0 else 0
                    )
                    total_row["baggingRate_visit"] = (
                        total_row["baggingCount"] / total_row["visitCount"]
                        if total_row["visitCount"] > 0 else 0
                    )

                    # Append "Total" row to tenant data
                    tenant_df = pd.concat([tenant_df, pd.DataFrame([total_row])], ignore_index=True)

                    tenant_df = tenant_df.drop(columns=["tenantName"], errors="ignore")

                    # Rename columns according to the mapping and drop "tenantName"
                    column_mapping = {
                        "date": "日期",
                        "timeInterval": "時間區間",
                        "terminalId": "機號",
                        "passByCount": "行經數 A",
                        "visitCount": "入櫃數 B",
                        "dwellCount_60": "停留數 C",
                        "baggingCount": "交易數 D",
                        "visitRate": "入櫃率 B/A",
                        "dwellRate_60": "停留率 C/B",
                        "baggingRate_60": "提袋率 D/C",
                        "baggingRate_visit": "提袋率 D/B",
                        "averageDwellTime": "平均停留時長 (s)",
                    }
                    tenant_df = tenant_df.rename(columns=column_mapping)
                    tenant_df.to_excel(writer, sheet_name=tenant, index=False)

                    # Apply percentage formatting to rate columns
                    workbook = writer.book
                    worksheet = writer.sheets[tenant]
                    for col_idx, col_name in enumerate(tenant_df.columns, start=1):
                        if "率" in col_name.lower():
                            for row_idx in range(2, len(tenant_df) + 2):  # Exclude header
                                cell = worksheet.cell(row=row_idx, column=col_idx)
                                cell.number_format = "0.00%"

        print(f"Daily report generated: {output_file}")

    def generate_reports_for_date_range(
        self,
        start_date: str,
        end_date: str,
        pass_by_indicator,
        visit_indicator,
        dwell_indicator,
        bagging_indicator
    ):
        """
        Generate reports for a range of dates.
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        while start <= end:
            date_str = start.strftime("%Y-%m-%d")
            time_intervals = [
                (datetime(start.year, start.month, start.day, hour, 0),
                datetime(start.year, start.month, start.day, hour + 1, 0))
                for hour in range(11, 22)
            ]

            self.generate_daily_report(
                date=date_str,
                pass_by_indicator=pass_by_indicator,
                visit_indicator=visit_indicator,
                dwell_indicator=dwell_indicator,
                bagging_indicator=bagging_indicator,
                time_interval=time_intervals
            )
            start += timedelta(days=1)
