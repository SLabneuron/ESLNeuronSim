import pandas as pd
import plotly.graph_objects as go

# CSVファイルのパス（バックスラッシュをエスケープするか、生文字列として指定）
csv_path = r'c:\Storage\02_paper\03_2023_ELEX\04_Python\data\results\set 1\fem\results\parameter region\parameter_region_time_20241128101123.csv'

# CSVファイルの読み込み
df = pd.read_csv(csv_path)

# 'state' 列が存在するか確認
if 'state' not in df.columns:
    raise ValueError("CSVファイルに 'state' 列が存在しません。")

# 'state' 列が整数型であることを確認（必要に応じて変換）
df['state'] = df['state'].astype(int)

# データの確認
print(df.head())
print(df['state'].unique())

# ピボットテーブルの作成
heatmap_data = df.pivot(index='Q', columns='S', values='state')

# インデックスとカラムのソート（昇順）
heatmap_data = heatmap_data.sort_index(ascending=True)  # Qを昇順に（下が低い値、上が高い値）
heatmap_data = heatmap_data.sort_index(axis=1, ascending=True)  # Sを昇順に

# 色のマッピングを定義（視認性を考慮）
categorical_color_map = {
    1: '#A9A9A9',  # ダークグレー
    2: '#FFD700',  # ゴールド
    3: '#32CD32',  # ライムグリーン
    4: '#1E90FF',  # ディープブルー
    5: '#FF4500'   # オレンジレッド
}

# マッピングに存在しない state があるか確認
unique_states = df['state'].unique()
missing_states = set(unique_states) - set(categorical_color_map.keys())
if missing_states:
    print(f"Warning: The following states are not in the color_map and will use default colors: {missing_states}")

# ヒートマップの作成（Plotly Graph Objects）
fig = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=heatmap_data.columns,
    y=heatmap_data.index,
    colorscale=[
        [0.0, categorical_color_map[1]],    # state 1
        [0.2, categorical_color_map[2]],    # state 2
        [0.4, categorical_color_map[3]],    # state 3
        [0.6, categorical_color_map[4]],    # state 4
        [0.8, categorical_color_map[5]],    # state 5
        [1.0, categorical_color_map[5]]     # state 5
    ],
    zmin=1,
    zmax=5,
    colorbar=dict(
        title="State",
        tickvals=[1, 2, 3, 4, 5],
        ticktext=[
            '1: 平衡点1つだけ',
            '2: 平衡点2つだけ',
            '3: 周期軌道1つだけ',
            '4: 平衡点1つと周期軌道1つ',
            '5: その他'
        ]
    )
))

# レイアウトの調整
fig.update_layout(
    title="Parameter Region Analysis",
    xaxis_title="S",
    yaxis_title="Q",
    yaxis=dict(autorange='reversed'),  # Qを下から上に表示
    width=1000,
    height=800,
    plot_bgcolor='white',
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray')
)

# セルの中央に配置するための設定
fig.update_yaxes(scaleanchor="x", scaleratio=1)

# プロットの表示
fig.show()
