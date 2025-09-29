import serial
import time
import queue
import json
import Jetson.GPIO as GPIO
import paho.mqtt.client as mqtt
import threading
import requests
import joblib
import pandas as pd
from datetime import datetime
import datetime
from lora_e32_constants import UARTParity, UARTBaudRate, TransmissionPower, ForwardErrorCorrectionSwitch, \
    WirelessWakeUpTime, IODriveMode, FixedTransmission, AirDataRate, OperatingFrequency, TransmissionPower20,TransmissionPower27,\
    TransmissionPower33,TransmissionPower37
from lora_e32_operation_constant import ResponseStatusCode, ModeType, ProgramCommand, SerialUARTBaudRate
# from machine import UART
from lora_e32 import LoRaE32,Configuration,print_configuration
from lora_e32_operation_constant import ResponseStatusCode
#lora1 8->rx,10->tx ,aux 7,m0 13,m1 15
#lora2 usb uart ,aux 11,m0 16,m1 18
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
m0_1 = 15
m1_1 = 13
m0_2 = 18
m1_2 = 16
aux_1=12
aux_2=11
GPIO.setup(m0_1, GPIO.OUT)
GPIO.setup(m1_1, GPIO.OUT)
GPIO.setup(m0_2, GPIO.OUT)
GPIO.setup(m1_2, GPIO.OUT)
GPIO.setup(aux_1, GPIO.IN)
GPIO.setup(aux_2, GPIO.IN)
GPIO.output(m0_2, GPIO.LOW)
GPIO.output(m1_2, GPIO.HIGH)
GPIO.output(m0_1, GPIO.LOW)
GPIO.output(m1_1, GPIO.HIGH)
# GPIO setup
server1 = 29
server2 = 31
server3 = 33
button1 =  22 
GPIO.setup(server1, GPIO.IN)
GPIO.setup(server2, GPIO.IN)
GPIO.setup(server3, GPIO.IN)
GPIO.setup(button1, GPIO.IN)
ser1 = serial.Serial('/dev/ttyTHS1', baudrate=9600, timeout=1)
ser2 = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)
#Tao pin
e32ttl1 = LoRaE32('433T30D', '/dev/ttyTHS1', aux_pin=aux_1, m0_pin=m0_1, m1_pin=m1_1, uart_baudrate=9600)
e32ttl2 = LoRaE32('433T30D', '/dev/ttyUSB0', aux_pin=aux_2, m0_pin=m0_2, m1_pin=m1_2, uart_baudrate=9600)

now = datetime.datetime.now()
model = joblib.load('/home/minh/Downloads/decision_tree_model.pkl')
class TBDevice:
    def __init__(self, token, host="http://demo.thingsboard.io"):
        self.token = token
        self.host = host.rstrip('/')
        self.headers = {
            'Content-Type': 'application/json',
            'X-Authorization': f'Bearer {self.token}'
        }
    def write(self, key, value):
        """ Gửi telemetry (dữ liệu thời gian thực) """
        url = f"{self.host}/api/v1/{self.token}/telemetry"
        data = {key: value}
        try:
            response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data))
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print("Error sending telemetry:", e)
            return False
    def write_attr(self, key, value):
        """ Gửi attribute (thuộc tính của thiết bị) """
        url = f"{self.host}/api/v1/{self.token}/attributes"
        data = {key: value}
        try:
            response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data))
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print("Error sending attributes:", e)
            return False
    def read_attr(self, key):
        """ Đọc shared attribute """
        url = f"{self.host}/api/v1/{self.token}/attributes?sharedKeys={key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("shared", {}).get(key, None)
        except requests.exceptions.RequestException as e:
            print("Error reading attribute:", e)
            return None
device = TBDevice("niFC0vMGiZKgrSynm9JG")
#set dia chi, thong so lora 1
def diachilora1():
    #Bat dau khoi dong lora
    code1 = e32ttl1.begin()
    print(ResponseStatusCode.get_description(code1))#in bat dau 
    #lay dia chi hien tai lora
    # code1, configuration =e32ttl1.get_configuration()
    # print(ResponseStatusCode.get_description(code1))
    # print_configuration(configuration)
    #Set dia chi
    configuration_to_set = Configuration('433T30D')
    configuration_to_set.ADDL = 1
    configuration_to_set.ADDH = 0
    configuration_to_set.CHAN = 23
    configuration_to_set.SPED.uartBaudRate = UARTBaudRate.BPS_9600    
    configuration_to_set.SPED.airDataRate = AirDataRate.AIR_DATA_RATE_010_24
    configuration_to_set.SPED.uartParity = UARTParity.MODE_00_8N1         
    configuration_to_set.OPTION.ioDriveMode =IODriveMode.PUSH_PULLS_PULL_UPS
    configuration_to_set.OPTION.wirelessWakeupTime = WirelessWakeUpTime.WAKE_UP_250
    configuration_to_set.OPTION.fec = ForwardErrorCorrectionSwitch.FEC_0_OFF
    configuration_to_set.OPTION.transmissionPower =  TransmissionPower20.POWER_20
    configuration_to_set.OPTION.fixedTransmission = FixedTransmission.FIXED_TRANSMISSION
    code1, confSetted1 =e32ttl1.set_configuration(configuration_to_set, permanentConfiguration=True)
    print(ResponseStatusCode.get_description(code1))
    print("Written config bytes:", confSetted1.to_hex_array())
    print(confSetted1) 
#set dia chi, thong so lora 2
def diachilora2():
    #Bat dau khoi dong lora
    code2 = e32ttl2.begin()
    print(ResponseStatusCode.get_description(code2))#in bat dau 
    #lay dia chi hien tai lora
    code2, configuration =e32ttl2.get_configuration()
    print(ResponseStatusCode.get_description(code2))
    print_configuration(configuration)
    #Set dia chi
    configuration_to_set = Configuration('433T30D')
    configuration_to_set.ADDL = 3
    configuration_to_set.ADDH = 0
    configuration_to_set.CHAN = 23
    configuration_to_set.SPED.uartBaudRate = UARTBaudRate.BPS_9600    
    configuration_to_set.SPED.airDataRate = AirDataRate.AIR_DATA_RATE_010_24
    configuration_to_set.SPED.uartParity = UARTParity.MODE_00_8N1         
    configuration_to_set.OPTION.ioDriveMode =IODriveMode.PUSH_PULLS_PULL_UPS
    configuration_to_set.OPTION.wirelessWakeupTime = WirelessWakeUpTime.WAKE_UP_250
    configuration_to_set.OPTION.fec = ForwardErrorCorrectionSwitch.FEC_0_OFF
    configuration_to_set.OPTION.transmissionPower =  TransmissionPower20.POWER_20
    configuration_to_set.OPTION.fixedTransmission = FixedTransmission.FIXED_TRANSMISSION
    code2, confSetted =e32ttl2.set_configuration(configuration_to_set, permanentConfiguration=True)
    print(ResponseStatusCode.get_description(code2))
    print("Written config bytes:", confSetted.to_hex_array())
    print(confSetted)
def send_lora():
    while True:
        wakeupSwitch = checkSwitchState()
        if (wakeupSwitch==True):
            if GPIO.input(button1) == GPIO.LOW:
                do_auto_action_hardware()
            else:
                mode = device.read_attr("Mode")
                if mode == 0:
                    while device.read_attr("Mode") == 0:
                        do_auto_action_software()
                        if GPIO.input(button1) == GPIO.LOW:
                            break
                elif mode == 1:
                    while device.read_attr("Mode") == 1:
                        do_manual_action()
                        if GPIO.input(button1) == GPIO.LOW:
                            break
def do_auto_action_hardware():
    button1Pressed = GPIO.input(server1)
    button2Pressed = GPIO.input(server2)
    button3Pressed = GPIO.input(server3)
    print("phancung")
    buttonState1 = 0
    # print("auto")
    if (button1Pressed == False): buttonState1 |= 0x01 # Bit 0
    if (button2Pressed == False): buttonState1 |= 0x02  # Bit 1
    if (button3Pressed == False): buttonState1 |= 0x04 # Bit 2
    switch_case (buttonState1)
def do_auto_action_software():
    buttonState = 0
    # print("auto")
    if (device.read_attr("receivedata")== 1): buttonState |= 0x01 # Bit 0
    if (device.read_attr("receivedata2")== 1): buttonState |= 0x02  # Bit 1
    if (device.read_attr("receivedata3")== 1): buttonState |= 0x04 # Bit 2
    switch_case (buttonState)
def do_manual_action():
    switchmanual()
def switchmanual():
    if (device.read_attr("Manual1") == 1):
        manual1()        
    if (device.read_attr("Manual2") == 1):
        manual2()
    if (device.read_attr("Manual3") == 1):
        manual3()
    if (device.read_attr("Manual4") == 1):
        manual4()
    if (device.read_attr("Manual1_1") == 1):
        manualz1()
    if (device.read_attr("Manual2_2") == 1):
        manualz2()
def manualz1():
    send4()
    send5()
    send6()
    device.write_attr("Manual1_1", False)
    device.write("Manual1_1", False)
def manualz2():
    send7()
    send8()
    device.write_attr("Manual2_2", False)
    device.write("Manual2_2", False)
def case_1():
    hamdocauto(1)
    hamdocauto(2)
    hamdocauto(3)
    time.sleep(2)
def case_2():
    hamdocauto(1)
    hamdocauto(2)
    time.sleep(2)
def case_3():
    hamdocauto(1)
    hamdocauto(3)
    time.sleep(2)
def case_4():
    hamdocauto(2)
    hamdocauto(3)
    time.sleep(2)
def case_5():
    hamdocauto(1)
    time.sleep(2)
def case_6():
    hamdocauto(2)
    time.sleep(2)
def case_7():
    hamdocauto(3)
    time.sleep(2)
def switch_case(value):
    # print(value)
    if (value==1): case_5()
    if (value==2): case_6()
    if (value==3): case_2()
    if (value==4): case_7()
    if (value==5): case_3()
    if (value==6): case_4()
    if (value==7): case_1()
lora_lock = threading.Lock()
def manual1():
    payload = {'i': '5', 'd': 'Manual1'}
    with lora_lock:
        waitAUX()
        Response = e32ttl1.send_fixed_dict(0, 2, 23, payload)
        waitAUX()
        print(ResponseStatusCode.get_description(Response))
        print("Thu data mau 1")
        device.write_attr("Manual1", False)
        device.write("Manual1", False)
def manual2():
    payload = {'i': '5', 'd': 'Manual2'}
    with lora_lock:
        waitAUX()
        Response = e32ttl1.send_fixed_dict(0, 2, 23, payload)
        waitAUX()
        print(ResponseStatusCode.get_description(Response))
        print("Thu data mau 2")
        device.write_attr("Manual2", False)
        device.write("Manual2", False)
def manual3():
    payload = {'i': '5', 'd': 'Manual3'}
    with lora_lock:
        waitAUX()
        Response = e32ttl1.send_fixed_dict(0, 2, 23, payload)
        waitAUX()
        print(ResponseStatusCode.get_description(Response))
        print("Thu data mau 3")
        device.write_attr("Manual3", False)
        device.write("Manual3", False)
def manual4(): 
    payload = {'i': '5', 'd': 'Manual4'}
    with lora_lock:
        waitAUX()
        Response = e32ttl1.send_fixed_dict(0, 2, 23, payload)
        waitAUX()
        print(ResponseStatusCode.get_description(Response))
        print("Dung dich bao quan")
        device.write_attr("Manual4", False)
        device.write("Manual4", False)
def thu3mau():
    payload = {'i': '5', 'd': 'Auto'}
    # with lora_lock:
    waitAUX()
    Response = e32ttl1.send_fixed_dict(0, 2, 23, payload)
    waitAUX()
    # print(ResponseStatusCode.get_description(Response))
    print("Thu data 3 mau")
def send4():
    payload = json.dumps({'id': '1', 'd': 'Data'})
    with lora_lock:
        waitAUX()
        Response = e32ttl1.send_fixed_message(0, 4, 23,payload)
        print("Send 1.1")
        waitAUX()
def send5():
    payload = json.dumps({'id': '2', 'd': 'Data'})
    with lora_lock:
        waitAUX()   
        Response = e32ttl1.send_fixed_message(0, 5, 23,payload )
        print("Send 1.2")
        waitAUX()
def send6():
    payload = json.dumps({'id': '3', 'd': 'Data'})
    with lora_lock:
        waitAUX()
        Response = e32ttl1.send_fixed_message(0, 6, 23,payload)
        print("Send 1.3")
        waitAUX()
def send7():
    payload = json.dumps({'id': '4', 'd': 'Data'})
    with lora_lock:
        waitAUX()
        Response = e32ttl1.send_fixed_message(0, 7, 23,payload)
        print("Send 2.1")
        waitAUX()
def send8():
    payload = json.dumps({'id': '6', 'd': 'Data'})
    with lora_lock:
        waitAUX()
        Response = e32ttl1.send_fixed_message(0, 8, 23,payload)
        print("Send 2.2")
        waitAUX()
def waitAUX():
    start_time = time.time()
    while GPIO.input(aux_1) == GPIO.LOW and (time.time() - start_time <= 2.0):
        pass
    time.sleep(1)  
def hamdocauto(autozone):
    if (autozone == 1):
        json = device.read_attr("data_json1")
        hamchayauto(json, autozone)
        # print("bat zone 1")
    if (autozone == 2):
        json = device.read_attr("data_json2")
        hamchayauto(json, autozone)
        # print("bat zone 2")
    if (autozone == 3):
        json = device.read_attr("data_json3")
        hamchayauto(json, autozone)
        # print("bat zone ph")
bien = []
attr_cache = {
    "switch1": True,
    "receivedata": True,
    "wakeup": True,
    "data1": 5,
    "switch2": True,
    "receivedata2": True,
    "data2": 5,
    "Mode": False,
}
zone_threads = {1: None, 2: None}
zone_thread_flags = {1: False, 2: False}
zone_thread_started = {1: False, 2: False}  # Đảm bảo chỉ chạy thread 1 lần
def update_attr_cache(device):
    while True:
        try:
            attr_cache["switch1"] = device.read_attr("switch1")
            attr_cache["receivedata"] = device.read_attr("receivedata")
            attr_cache["wakeup"] = device.read_attr("wakeup")
            attr_cache["data1"] = int(device.read_attr("data1"))
            attr_cache["switch2"] = device.read_attr("switch2")
            attr_cache["receivedata2"] = device.read_attr("receivedata2")
            attr_cache["data2"] = int(device.read_attr("data2"))
            attr_cache["Mode"] = device.read_attr("Mode")
        except Exception as e:
            print("[Attr Cache] Lỗi khi cập nhật:", e)
        time.sleep(1)  # Cập nhật cache mỗi 1 giây
def periodic_runner(zone, interval, functions, switch_attr, receive_attr, wakeup_attr, data_attr,mode_attr,button_attr):
    last_interval = interval
    sleep_seconds = last_interval * 60
    start_time = time.time()
    while zone_thread_flags[zone]:
        # Kiểm tra điều kiện dừng
        if GPIO.input(button1) == GPIO.HIGH:
            if not attr_cache[switch_attr] or not attr_cache[receive_attr] or not attr_cache[wakeup_attr] or attr_cache[mode_attr] :
                print(f"[Zone {zone}] Dừng thread vì switch/receive/wakeup/mode = 0")
                break
        if GPIO.input(button1) == GPIO.LOW:
            if not attr_cache[switch_attr] or (GPIO.input(button_attr) == GPIO.HIGH )or not attr_cache[wakeup_attr] :
                print(f"[Zone {zone}] Dừng thread vì switch/buttonzone/wakeup = 0")
                break
        # Gửi dữ liệu
        for f in functions:
            f()
        # Chờ theo thời gian thực
        while True:
            time.sleep(1)
            elapsed = time.time() - start_time
            # print(elapsed)
            current_interval = attr_cache[data_attr]
            if current_interval != last_interval:
                print(f"[Zone {zone}] Phát hiện chu kỳ mới: {current_interval} phút, dừng thread để cập nhật.")
                break
            if GPIO.input(button1) == GPIO.HIGH:
                if not attr_cache[switch_attr] or not attr_cache[receive_attr] or not attr_cache[wakeup_attr]or attr_cache[mode_attr]:
                    print(f"[Zone {zone}] Dừng thread giữa chu kỳ vì switch/receive/wakeup = 0")
                    break
            if GPIO.input(button1) == GPIO.LOW:
                if not attr_cache[switch_attr] or (GPIO.input(button_attr) == GPIO.HIGH) or not attr_cache[wakeup_attr]:
                    print(f"[Zone {zone}] Dừng thread giữa chu kỳ vì switch/button/wakeup = 0")
                    break
            if elapsed >= sleep_seconds:
                break
        # Thoát vòng lặp lớn nếu có thay đổi hoặc tắt
        if current_interval != last_interval:
            break
        if GPIO.input(button1) == GPIO.HIGH:
            if not attr_cache[switch_attr] or not attr_cache[receive_attr] or not attr_cache[wakeup_attr] :
                break
        if GPIO.input(button1) == GPIO.LOW:
            if not attr_cache[switch_attr] or GPIO.input(button_attr) == GPIO.LOW or not attr_cache[wakeup_attr] or attr_cache[mode_attr] :
                break
        start_time = time.time()  # Reset thời gian đếm nếu vẫn tiếp tục
    zone_thread_flags[zone] = False
    zone_thread_started[zone] = False
    zone_threads[zone] = None
def start_periodic_thread(zone, interval, functions, switch_attr, receive_attr,wakeup_attr, mode_attr,data_attr,button_attr):
     # Nếu thread chưa khởi động hoặc đã kết thúc
    if zone_threads[zone] is None or not zone_thread_flags[zone]:
        zone_thread_flags[zone] = True
        zone_thread_started[zone] = True
        t = threading.Thread(target=periodic_runner, args=(zone, interval, functions, switch_attr, receive_attr,wakeup_attr, mode_attr,data_attr,button_attr))
        t.daemon = True
        zone_threads[zone] = t
        t.start()
def stop_periodic_thread(zone):
    zone_thread_flags[zone] = False
    zone_thread_started[zone] = False
    t = zone_threads[zone]
    if t and t.is_alive():
        t.join(timeout=0.1)
    zone_threads[zone] = None
def hamchayauto(jsons, autozone):
    global bien
    now = datetime.datetime.now()
    s = f"{now.hour}:{now.minute:02d}"
    # print(s)
    json_str = json.dumps(jsons)
    # print(json_str)
    try:
        doc = json.loads(json_str)
    except json.JSONDecodeError:
        print("Lỗi JSON")
        return
    # Xác định kích thước vector
    max_index = 0
    for key in doc.keys():
        try:
            index = int(key)
            if index > max_index:
                max_index = index
        except ValueError:
            continue
    bien = [''] * max_index
    # Gán giá trị
    for key, value in doc.items():
        try:
            index = int(key)
            if 1 <= index <= len(bien):
                bien[index - 1] = str(value)
        except ValueError:
            continue
    # So sánh từng phần tử với thời gian hiện tại
    for val in bien:
        if autozone == 1:
            if device.read_attr("switch1"):
                interval = int(device.read_attr("data1"))
                start_periodic_thread(1, interval, [send4, send5, send6],"switch1", "receivedata","wakeup","data1","Mode",server1)
            else:
                if val == s:
                    stop_periodic_thread(1)
                    send4()
                    send5()
                    send6()
        elif autozone == 2:
            if device.read_attr("switch2"):
                interval = int(device.read_attr("data2"))
                start_periodic_thread(2, interval, [send7, send8],"switch2", "receivedata2","wakeup", "data2","Mode",server2)
            else:
                 if val == s:
                    stop_periodic_thread(2)
                    send7()
                    send8()
        elif autozone == 3:
            # print(val)
            # print(s)
            if val == s:
                thu3mau()
        break
data_queue = queue.Queue()
def receive_lora():
    while True:
        if (ser2.in_waiting > 0):
            global line
            raw = ser2.readline()
            line = raw.decode('utf-8', errors='ignore').strip()
            print(line)
            data_queue.put(line) 
def thingsboard():  
    while True:
        line = data_queue.get()
        # print(line)
        try:
            # Phân tích chuỗi JSON
            data = json.loads(line)
            # Truy cập từng giá trị
            deviceId = data.get("i")
            tempVal = data.get("t")if "t" in data else None
            humVal = data.get("h") if "h" in data else None
            pHVal = data.get("p") if "p" in data else None
            mau = data.get("m") if "m" in data else None
            press = data.get("e") if "e" in data else None
            alti = data.get("a") if "a" in data else None
            tempwater = data.get("w") if "w" in data else None
            tds= data.get("tds") if "tds" in data else None
            if(deviceId ==1):#gui tu node 1_zone1
                device.write("nhietdo", tempVal)
                device.write("Doam", humVal)
                device.write_attr("nhietdo", tempVal)
                device.write_attr("Doam", humVal)
            if (deviceId ==2):#gui tu node 2_zone1
                device.write("nhietdo2", tempVal)
                device.write("Doam2", humVal)
                device.write_attr("nhietdo2", tempVal)
                device.write_attr("Doam2", humVal)
            if (deviceId ==3):#gui tu node 3_zone1
                device.write("nhietdo3", tempVal)
                device.write("Doam3", humVal)
                device.write_attr("nhietdo3", tempVal)
                device.write_attr("Doam3", humVal)
            if (deviceId ==4): #gui tu node 1_zone2
                device.write("nhietdo4", tempVal)
                device.write("Doam4", humVal)
                device.write_attr("nhietdo4", tempVal)
                device.write_attr("Doam4", humVal)
            if (deviceId ==5):#gui tu node_PH
                device.write("nhietdo6", tempVal)
                device.write("Doam6", humVal)
                device.write_attr("nhietdo6", tempVal)
                device.write_attr("Doam6", humVal)
                device.write("Ap_suat", press)
                device.write("alti", alti)
                device.write_attr("Ap_suat", press)
                device.write_attr("alti", alti)
                if (mau == 1):
                    # print("dagui")
                    device.write("water1", tempwater)
                    device.write_attr("water1", tempwater)
                    device.write("pH1", pHVal)
                    device.write_attr("pH1", pHVal)
                    device.write("tds1", tds)
                    device.write_attr("tds1", tds)
                if (mau == 2):
                    device.write("water2", tempwater)
                    device.write_attr("water2", tempwater)
                    device.write("pH2", pHVal)
                    device.write_attr("pH2", pHVal)
                    device.write("tds2", tds)
                    device.write_attr("tds2", tds)
                if (mau == 3):
                    device.write("water3", tempwater)
                    device.write_attr("water3", tempwater)
                    device.write("pH3", pHVal)
                    device.write_attr("pH3", pHVal)
                    device.write("tds3", tds)
                    device.write_attr("tds3", tds)
            if (deviceId ==6): #gui tu node 2_zone2
                device.write("nhietdo5", tempVal)
                device.write("Doam5", humVal)
                device.write_attr("nhietdo5", tempVal)
                device.write_attr("Doam5", humVal)
        except json.JSONDecodeError:
            print("Dữ liệu không phải là JSON hợp lệ:", line)
def dudoan():
    while True:
        if (device.read_attr("modetrain")==True):
            temp1 = float(device.read_attr("water1"))#cambiennuoc
            ph1 = float(device.read_attr("pH1"))#cambienph1
tds1 = float(device.read_attr("tds1"))#cambientds1
            input_data1 = pd.DataFrame([[ph1, tds1, temp1]], columns=["water_pH", "TDS", "water_temp"])
            status1 = model.predict(input_data1)[0]
            print(" Dự đoán mẫu 1:", "Đạt (0)" if status1 == 0 else "Không đạt (1)")
            temp2 = float(device.read_attr("water2"))#cambiennuoc
            ph2 = float(device.read_attr("pH2"))#cambienph2
            tds2 = float(device.read_attr("tds2"))#cambientds2
            input_data2 = pd.DataFrame([[ph2, tds2, temp2]], columns=["water_pH", "TDS", "water_temp"])
            status2 = model.predict(input_data2)[0]
            print(" Dự đoán mẫu 2:", "Đạt (0)" if status2 == 0 else "Không đạt (1)")
            temp3 = float(device.read_attr("water3"))#cambiennuoc
            ph3 = float(device.read_attr("pH3"))#cambienph3
            tds3 = float(device.read_attr("tds3"))#cambientds3
            input_data3 = pd.DataFrame([[ph3, tds3, temp3]], columns=["water_pH", "TDS", "water_temp"])
            status3 = model.predict(input_data3)[0]
            print(" Dự đoán mẫu 3:", "Đạt (0)" if status3 == 0 else "Không đạt (1)")
            if status1 == 0:
                device.write_attr("train1","Đạt")
                device.write("train1","Đạt")
            else:
                device.write_attr("train1","Không đạt")
                device.write("train1","Không đạt")
            if status2 == 0:
                device.write_attr("train2","Đạt")
                device.write("train2","Đạt")
            else:
                device.write_attr("train2","Không đạt")
                device.write("train2","Không đạt")
            if status3 == 0:
                device.write_attr("train3","Đạt")
                device.write("train3","Đạt")
            else:
                device.write_attr("train3","Không đạt")
                device.write("train3","Không đạt")
            device.write("modetrain",False)
            device.write_attr("modetrain",False)
# Tạo thread cho mỗi hàm
sendlora = threading.Thread(target=send_lora)
receivelora = threading.Thread(target=receive_lora)
dudoanketqua = threading.Thread(target=dudoan)
guithingsboard = threading.Thread(target=thingsboard)
def checkSwitchState():
    switchState = device.read_attr("wakeup")
    return switchState
if __name__ == "__main__":
    # device = TBDevice("niFC0vMGiZKgrSynm9JG")
    diachilora1()
    diachilora2()
    #Ta threat time
    attr_updater = threading.Thread(target=update_attr_cache, args=(device,))
    attr_updater.daemon = True
    attr_updater.start()
    # Khởi động 2 thread
    sendlora.start()
    receivelora.start()
    dudoanketqua.start()
    guithingsboard.start()
    sendlora.join()
    receivelora.join()
    dudoanketqua.join()
    guithingsboard.join()
    attr_updater.join()
