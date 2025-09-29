import joblib
import pandas as pd
# Tải mô hình
model = joblib.load('/home/minh/Downloads/decision_tree_model.pkl')
print("Mô hình đã sẵn sàng!")
print("Nhập thông số để dự đoán:")
# Nhập dữ liệu
temp = float(input("Nhiệt độ nước (°C): "))
ph = float(input("Giá trị pH: "))
tds = float(input("Giá trị TDS (ppm): "))
# Đặt tên cột đúng như lúc huấn luyện
input_data = pd.DataFrame([[ph, tds, temp]], columns=["water_pH", "TDS", "water_temp"])
# Dự đoán
status = model.predict(input_data)[0]
print("Dự đoán Status:", "Tốt (0)" if status == 0 else "Không đạt (1)
