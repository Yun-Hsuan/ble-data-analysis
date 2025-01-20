# 安裝必要的套件
# pip install movingpandas geopandas matplotlib shapely networkx seaborn

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from movingpandas.trajectory_collection import TrajectoryCollection
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import seaborn as sns

# 1. 配置模擬參數
np.random.seed(42)  # 固定隨機種子以保證結果可重現
num_points_per_person = 10  # 每個人移動的點數
num_people = 20  # 總人數
num_ble_points = 10  # BLE 偵測點的數量

# 隨機生成 BLE 點位
ble_points = np.array([(np.random.randint(0, 500), np.random.randint(0, 500)) for _ in range(num_ble_points)])
ble_ids = [f"BLE{i+1}" for i in range(num_ble_points)]

# 隨機生成人員移動數據
def generate_random_movements(num_people, num_points_per_person, ble_points, ble_ids):
    data = {
        'person_id': [],
        'timestamp': [],
        'x': [],
        'y': [],
        'ble_id': []
    }

    for person in range(1, num_people + 1):
        for i in range(num_points_per_person):
            timestamp = pd.Timestamp('2025-01-01 12:00:00') + pd.Timedelta(seconds=10 * i)
            ble_index = np.random.randint(0, len(ble_points))
            x, y = ble_points[ble_index]

            data['person_id'].append(f"Person{person}")
            data['timestamp'].append(timestamp)
            data['x'].append(x + np.random.randint(-10, 10))  # 添加少量偏移量模擬真實移動
            data['y'].append(y + np.random.randint(-10, 10))
            data['ble_id'].append(ble_ids[ble_index])

    return pd.DataFrame(data)

movement_data = generate_random_movements(num_people, num_points_per_person, ble_points, ble_ids)
movement_data['timestamp'] = pd.to_datetime(movement_data['timestamp'])
movement_data.set_index('timestamp', inplace=True)  # 設置 DatetimeIndex

# 2. 計算點對點之間的流量
flow_counts = pd.DataFrame(0, index=ble_ids, columns=ble_ids)
for person_id, group in movement_data.groupby('person_id'):
    ble_sequence = group['ble_id'].tolist()
    for i in range(len(ble_sequence) - 1):
        flow_counts.loc[ble_sequence[i], ble_sequence[i+1]] += 1

# 3. 創建網絡圖並可視化
G = nx.DiGraph()

# 添加節點
for i, (x, y) in enumerate(ble_points):
    G.add_node(ble_ids[i], pos=(x, y))

# 添加邊，並根據流量設置邊的寬度和顏色
for source, target in flow_counts.stack().index:
    weight = flow_counts.loc[source, target]
    if weight > 0:
        G.add_edge(source, target, weight=weight)

# 4. 可視化網絡圖
pos = nx.get_node_attributes(G, 'pos')
edges = G.edges(data=True)

fig, ax = plt.subplots(figsize=(12, 12))
ax.set_title("BLE Movement Flow Visualization")
ax.set_xlabel("X Coordinate")
ax.set_ylabel("Y Coordinate")

# 定義顏色映射
max_flow = flow_counts.max().max()
cmap = sns.color_palette("coolwarm", as_cmap=True)

# 繪製節點
nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue', ax=ax)
nx.draw_networkx_labels(G, pos, font_size=10, font_color='black', ax=ax)

# 繪製邊，使用流量數據控制邊的寬度和顏色
for (u, v, d) in edges:
    weight = d['weight']
    color = cmap(weight / max_flow)
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=[(u, v)],
        width=weight * 0.5,
        edge_color=[color],
        ax=ax
    )

# 添加色條
sm = plt.cm.ScalarMappable(cmap="coolwarm", norm=plt.Normalize(vmin=0, vmax=max_flow))
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
cbar.set_label("Flow Intensity", fontsize=12)

# 保存圖像
plt.savefig("ble_movement_flow_colored_seaborn.png")
print("Figure saved as ble_movement_flow_colored_seaborn.png")