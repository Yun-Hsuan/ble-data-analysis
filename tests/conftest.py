from dotenv import load_dotenv
import os
import sys

# 加載環境變量
load_dotenv("dev.env")

# 將 PYTHONPATH 添加到 sys.path，確保測試代碼能導入
python_path = os.getenv("PYTHONPATH")
if python_path and python_path not in sys.path:
    sys.path.append(os.path.abspath(python_path))