# 安裝必要的套件
# pip install movingpandas geopandas matplotlib shapely

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from movingpandas.trajectory_collection import TrajectoryCollection
import matplotlib.pyplot as plt
import numpy as np

# 1. 隨機生成測試數據
np.random.seed(42)  # 固定隨機種子以保證結果可重現
num_points = 50  # 每條軌跡包含的點數
num_devices = 3  # 設備數量

ble_data = {
    'id': [f'device{i+1}' for i in range(num_devices) for _ in range(num_points)],
    'timestamp': [
        pd.Timestamp('2025-01-01 12:00:00') + pd.Timedelta(minutes=5 * j)
        for _ in range(num_devices) for j in range(num_points)
    ],
    'x': np.random.randint(0, 500, num_devices * num_points),
    'y': np.random.randint(0, 500, num_devices * num_points)
}

# 創建 DataFrame
df = pd.DataFrame(ble_data)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)  # 設置 DatetimeIndex

# 2. 創建 GeoDataFrame
# 使用 x, y 坐標創建 Point 幾何對象
gdf = gpd.GeoDataFrame(
    df,
    geometry=[Point(xy) for xy in zip(df.x, df.y)],
    crs=None  # 不使用地理坐標系
)

# 3. 創建 TrajectoryCollection
traj_collection = TrajectoryCollection(
    gdf, traj_id_col='id'
)

# 4. 增加速度計算
for traj in traj_collection:
    traj.add_speed(overwrite=True)
    print(f"Trajectory for {traj.id}:\n", traj.df[['id', 'speed']])

# 5. 可視化軌跡
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_title("Randomly Simulated Trajectory Path Based on BLE Data")
ax.set_xlabel("X Coordinate")
ax.set_ylabel("Y Coordinate")

# 在圖像上繪製每個軌跡
colors = ['r', 'g', 'b']
for i, traj in enumerate(traj_collection):
    traj.plot(ax=ax, label=f"{traj.id}", color=colors[i % len(colors)])

ax.legend()
plt.grid()

# 儲存圖像到檔案，避免後端無法顯示的問題
plt.savefig("random_trajectory_output.png")
print("Figure saved as random_trajectory_output.png")



