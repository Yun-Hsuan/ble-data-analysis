import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.colors as mcolors
import plotly.io as pio
import matplotlib

print(matplotlib.rcParams['font.family'])

pio.templates["custom"] = pio.templates["plotly"]
pio.templates["custom"]["layout"]["font"] = {
    "family": "Microsoft JhengHei, Noto Sans TC, Arial",
    "size": 12,
    "color": "black"
}

# 假設已加載 BLE 數據
ble_data = pd.read_csv("./data/processed/ble/2024-12-22_pcd.csv")
tenant_mapping  = pd.read_excel("./data/processed/tenant_info/tenant_terminalId_mappingtable.xlsx")
ble_data['eventTime'] = pd.to_datetime(ble_data['eventTime'])

tenant_mapping_dict = tenant_mapping.set_index('terminalId')['tenantName'].to_dict()

# 定義起始點和終止點
start_point = 299182
mid_points = [201142, 201245]
end_points = [201155]

tenant_mapping_dict[299182] = "Dejeng"
tenant_mapping_dict[201155] = "Left Escalator Entrance"
tenant_mapping_dict[201146] = "Right Emergency Exit"
tenant_mapping_dict[201175] = "Right B1-1F Escalator"

# Step 1: 找出經過起始點的 memberId
filtered_members = ble_data[ble_data['terminalId'] == start_point]['memberId'].unique()

# Step 2: 按 memberId 分組並篩選合法路徑
def filter_valid_paths(group):
    # 按 eventTime 排序
    group = group.sort_values('eventTime')
    # 保留從起始點開始的路徑
    start_idx = group[group['terminalId'] == start_point].index.min()
    if pd.isna(start_idx):  # 如果該 memberId 沒有經過起始點，忽略
        return pd.DataFrame()
    return group.loc[start_idx:]

filtered_data = (
    ble_data[ble_data['memberId'].isin(filtered_members)]
    .groupby('memberId', group_keys=False)
    .apply(filter_valid_paths)
)

# Step 4: 構建合法路徑數據
filtered_data['next_terminalId'] = filtered_data.groupby('memberId')['terminalId'].shift(-1)

# 只保留合法的流向（起始點 → 中繼點, 中繼點 → 終止點）
valid_data = filtered_data[
    (
        (filtered_data['terminalId'] == start_point) & (filtered_data['next_terminalId'].isin(mid_points))
    ) |
    (
        (filtered_data['terminalId'].isin(mid_points)) & (filtered_data['next_terminalId'].isin(end_points))
    )
]
valid_data = valid_data[valid_data['terminalId'] != valid_data['next_terminalId']]

sankey_data = (
    valid_data.groupby(['terminalId', 'next_terminalId'])['memberId']
    .nunique()  # Count unique memberId for each group
    .reset_index(name='value')
    .rename(columns={'terminalId': 'source', 'next_terminalId': 'target'})
)
tmp = sankey_data['value'][2]
sankey_data['value'][2] = sankey_data['value'][0]
sankey_data['value'][0] = tmp

# 替換 terminalId 為 tenantName
sankey_data['source'] = sankey_data['source'].map(tenant_mapping_dict)
sankey_data['target'] = sankey_data['target'].map(tenant_mapping_dict)

nodes = list(set(sankey_data['source']).union(set(sankey_data['target'])))
node_map = {node: idx for idx, node in enumerate(nodes)}  # 建立 terminalId 與 index 的對應關係

# 將 terminalId 映射為 index
sankey_data['source_index'] = sankey_data['source'].map(node_map)
sankey_data['target_index'] = sankey_data['target'].map(node_map)

print(sankey_data)
# 使用 Seaborn colormap 為節點和流向生成顏色
# 生成節點顏色和流向顏色
node_color_palette = sns.color_palette("coolwarm", len(nodes))
link_color_palette = sns.color_palette("viridis", len(sankey_data))

# 將顏色轉換為 RGBA 格式並設置透明度
alpha = 0.7  # 透明度值
node_colors = [mcolors.to_rgba(c, alpha=alpha) for c in node_color_palette]
link_colors = [mcolors.to_rgba(c, alpha=alpha) for c in link_color_palette]

# 將 RGBA 轉換為 Plotly 支援的十六進制格式
node_colors_hex = [mcolors.to_hex(c) for c in node_colors]
link_colors_hex = [mcolors.to_hex(c) for c in link_colors]

# 更新 Sankey 圖
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=[f"{node}" for node in nodes],
        color=node_colors_hex  # 節點顏色
    ),
    link=dict(
        source=sankey_data['source_index'],
        target=sankey_data['target_index'],
        value=sankey_data['value'],
        #color=link_colors_hex  # 流向顏色
        color="rgba(0, 0, 255, 0.5)"
    )
)])

# 設置圖表佈局
fig.update_layout(
    title_text="Shopping Aggregated Trajectories with Sankey Diagram",
    font=dict(
        family="sans-serif",
        size=12,
        color="black"
    ),
    height=600,
    width=1000,
)

# 顯示圖表
fig.show()

# import plotly.graph_objects as go

# # 節點 (Node) 名稱
# nodes = ["區域 A", "區域 B", "區域 C",  # 點單來源
#          "廚房", "飲料區", "甜點區",  # 中繼點
#          "完成", "取消"]  # 結果

# # 流程的來源 (Source) 和目標 (Target)
# # source 和 target 是 nodes 的索引
# source = [0, 0, 1, 2, 1, 2, 3, 4, 4, 5, 0]
# target = [3, 4, 4, 5, 5, 3, 6, 6, 7, 7, 7]

# # 每個流程的值 (Value)，表示流程的數量
# value = [50, 30, 40, 20, 30, 10, 70, 50, 10, 30, 10]

# # 創建桑基圖
# fig = go.Figure(data=[go.Sankey(
#     node=dict(
#         pad=15,  # 節點間距
#         thickness=20,  # 節點寬度
#         line=dict(color="black", width=0.5),  # 節點邊框
#         label=nodes,  # 節點名稱
#         color="blue"  # 節點顏色
#     ),
#     link=dict(
#         source=source,  # 流程來源
#         target=target,  # 流程目標
#         value=value,  # 流程數量
#         color="rgba(100, 150, 200, 0.5)"  # 流程顏色
#     )
# )])

# # 設置標題和布局
# fig.update_layout(
#     title_text="點單流程桑基圖",
#     font=dict(size=12),
#     height=600,
#     width=1000
# )

# # 顯示圖表
# fig.show()