import pandas as pd
from pathlib import Path
from openpyxl.utils import get_column_letter
from openpyxl.styles import NamedStyle, numbers
import json
import pandas as pd
from datetime import datetime, timedelta
from src.data_processing.cleaners.ble_cleaner import BLECleaner
from src.data_processing.cleaners.transaction_cleaner import TransactionCleaner
from src.business.tenant_indicators.visit_rate import VisitRateIndicator
from src.business.tenant_indicators.pass_by import PassByIndicator
from src.business.tenant_indicators.dwell_rate import DwellRateIndicator
from src.business.tenant_indicators.bagging_rate import BaggingRateIndicator
from src.report.report_manager import ReportManager



if __name__ == "__main__":


    date = "2024-12-19"
    report_manager = ReportManager(
        daily_reports_dir="./daily_reports",  # 日報表的目錄
        comparison_report_path = f"./comparison_reports/tenant_comparison_{date}.xlsx"
    )

    # 載入日報表的資料
    tenant_data = report_manager.load_tenant_data(start_date=date, end_date=date)

    # 生成比較報表
    report_manager.generate_comparison_report(tenant_data=tenant_data)