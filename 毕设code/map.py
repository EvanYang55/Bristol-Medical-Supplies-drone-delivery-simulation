import folium
import pandas as pd
from folium.features import DivIcon

# 1. 创建数据框（从图片中的表格数据）
data = {
    "Name": [
        "NHS Blood Centre (Filton)",
        "South Bristol NHS Community Hospital",
        "UWE Health Tech Hub",
        "Southmead Hospital",
        "Bristol Royal Infirmary (BRI)",
        "St Michael's Hospital",
        "Eastville Medical Centre",
        "Fishponds Primary Care Centre",
        "Bristol Haematology and Oncology Centre (BHOC)",
        "Emersons Green NHS Treatment Centre",
        "Lawrence Hill Health Centre",
        "Montpelier Health Centre"
    ],
    "Type": ["Start"] * 3 + ["Destination"] * 9,
    "Latitude": [
        "51° 31'06\"N", "51° 24'45\"N", "51° 30'03\"N",
        "51° 29'45\"N", "51° 27'29\"N", "51° 27'32\"N",
        "51° 28'13\"N", "51° 28'47\"N", "51° 27'30\"N",
        "51° 30'12\"N", "51° 27'27\"N", "51° 28'01\"N"
    ],
    "Longitude": [
        "2°33'55\"W", "2°34'59\"W", "2°33'07\"W",
        "2°35'29\"W", "2°35'49\"W", "2°35'58\"W",
        "2°33'44\"W", "2°31'36\"W", "2°35'51\"W",
        "2°29'47\"W", "2°34'19\"W", "2°35'21\"W"
    ]
}

df = pd.DataFrame(data)


# 2. 转换度分秒为十进制格式的函数
def dms_to_decimal(dms):
    parts = dms.replace("°", " ").replace("'", " ").replace("\"", " ").split()
    degrees = float(parts[0])
    minutes = float(parts[1])
    seconds = float(parts[2])
    direction = parts[3]

    decimal = degrees + minutes / 60 + seconds / 3600
    if direction in ['W', 'S']:
        decimal *= -1
    return decimal


# 3. 转换所有坐标
df['Lat_Decimal'] = df['Latitude'].apply(lambda x: dms_to_decimal(x))
df['Lon_Decimal'] = df['Longitude'].apply(lambda x: dms_to_decimal(x))

# 4. 创建地图（以第一个点为初始中心点）
map_center = [df.loc[0, 'Lat_Decimal'], df.loc[0, 'Lon_Decimal']]
m = folium.Map(location=map_center, zoom_start=12, tiles='OpenStreetMap')

# 5. 添加起点和目标点到地图
starts = df[df['Type'] == 'Start']
destinations = df[df['Type'] == 'Destination']

# 添加起点（绿色标记）
for idx, row in starts.iterrows():
    tooltip = f"START: {row['Name']}"
    folium.Marker(
        location=[row['Lat_Decimal'], row['Lon_Decimal']],
        popup=row['Name'],
        tooltip=tooltip,
        icon=folium.Icon(color='green', icon='play', prefix='fa')
    ).add_to(m)

    # 添加起点名称标签
    folium.map.Marker(
        [row['Lat_Decimal'] - 0.005, row['Lon_Decimal']],
        icon=DivIcon(
            icon_size=(200, 36),
            icon_anchor=(0, 0),
            html=f'<div style="font-weight:bold; color:green;">Start: {row["Name"]}</div>'
        )
    ).add_to(m)

# 添加目标点（红色标记）
for idx, row in destinations.iterrows():
    tooltip = f"DESTINATION: {row['Name']}"
    folium.Marker(
        location=[row['Lat_Decimal'], row['Lon_Decimal']],
        popup=row['Name'],
        tooltip=tooltip,
        icon=folium.Icon(color='red', icon='hospital', prefix='fa')
    ).add_to(m)

# 6. 添加覆盖聚簇以增强可视化
from folium.plugins import MarkerCluster

marker_cluster = MarkerCluster().add_to(m)

for idx, row in df.iterrows():
    icon_color = 'green' if row['Type'] == 'Start' else 'red'
    icon_type = 'play' if row['Type'] == 'Start' else 'hospital'

    folium.Marker(
        location=[row['Lat_Decimal'], row['Lon_Decimal']],
        popup=row['Name'],
        tooltip=f"{row['Type']}: {row['Name']}",
        icon=folium.Icon(color=icon_color, icon=icon_type, prefix='fa')
    ).add_to(marker_cluster)

# 7. 添加图例
legend_html = '''
     <div style="position: fixed; 
                 bottom: 50px; left: 50px; width: 150px; height: 90px; 
                 border:2px solid grey; z-index:9999; font-size:14px;
                 background-color:white;
                 opacity:0.85">
         <div style="padding:5px">
             <i class="fa fa-play fa-2x" style="color:green"></i> Start<br>
             <i class="fa fa-hospital fa-2x" style="color:red"></i> Destination<br>
             <i class="fa fa-circle" style="color:lightblue"></i> Cluster
         </div>
     </div>
'''

m.get_root().html.add_child(folium.Element(legend_html))

# 8. 保存地图
m.save('medical_delivery_map.html')
print("地图已保存为 medical_delivery_map.html - 请在浏览器中打开查看")