import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib
# Đọc dữ liệu và tạo nhãn
df = pd.read_csv('/home/minh/Downloads/pond_iot_2023_raw.csv')
df = df.iloc[:, -3:]
df.columns = ['water_pH', 'TDS','water_temp']
# Gán nhãn
df['Status'] = df.apply(lambda row: 0 if 6.5 <= row['water_pH'] <= 8.5 and row['TDS'] < 500 and 24 <= row['water_temp'] <= 27 else 1, axis=1)
X = df[['water_pH', 'TDS','water_temp']]
y = df['Status']
# Huấn luyện
model = DecisionTreeClassifier()
model.fit(X, y)
# Lưu mô hình
joblib.dump(model, '/home/minh/Downloads/decision_tree_model.pkl')
print(" Đã lưu mô hình vào decision_tree_model.pkl")
