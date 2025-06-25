import serial
import serial.tools.list_ports

class BluetoothConnection:
    def __init__(self):
        self.ser = None
        self.port = None
        self.baudrate = 9600

    def connect_to_hc05(self):
        """Подключается к HC-05 и возвращает объект соединения"""
        try:
            # Автопоиск порта HC-05 (можно заменить на конкретный порт)
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if "COM11" in port.description:
                    self.port = port.device
                    break
            
            if not self.port:
                print("HC-05 не найден! Проверьте подключение.")
                return None

            self.ser = serial.Serial(self.port, self.baudrate, timeout=10)
            return self.ser
            
        except Exception as e:
            return None

    def read_single_line(self):
        """Читает одну строку данных из подключенного устройства"""
        if not self.ser or not self.ser.is_open:

            return None
        
        try:
            if self.ser.in_waiting > 0:
                data = self.ser.readline().decode('utf-8', errors='ignore').strip()

                return data
            return None
        except Exception as e:
            print(f"Ошибка чтения данных: {e}")
            return None

    def close_connection(self):
        """Закрывает соединение"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Соединение закрыто.")