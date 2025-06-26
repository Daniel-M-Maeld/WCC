import sys
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
from signal_reader import BluetoothConnection
import threading

if sys.platform == 'win32':
    # Скрываем консольное окно на Windows
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

class CharacterFrame:
    def __init__(self, master, width=300, height=500):
        self.master = master
        self.width = width
        self.height = height
        self.current_gender = 'male'
        
        self.frame = tk.Frame(master, width=width, height=height)
        self.canvas = tk.Canvas(self.frame, width=width, height=height)
        self.canvas.pack()

        self.original_bg_image = None
        self.load_character_image()
       
    def load_character_image(self):
        """Загружаем базовое изображение персонажа"""
        try:
            filename = "Boybg.png" if self.current_gender == 'male' else "Girlbg.png"
            self.original_bg_image = Image.open(os.path.join(os.path.dirname(__file__), filename)).convert("RGBA")
            self.original_bg_image = self.original_bg_image.resize((self.width, self.height))
            self.bg_image = self.original_bg_image.copy()
        except FileNotFoundError:
            self.original_bg_image = Image.new('RGB', (self.width, self.height), '#f0f0f0')
            draw = ImageDraw.Draw(self.original_bg_image)
            text = f"{'Boybg.png' if self.current_gender == 'male' else 'Girlbg.png'} not found"
            draw.text((50, 50), text, fill="black")
            self.bg_image = self.original_bg_image.copy()
        
        self.update_canvas()
    
    def load_full_outfit(self, image_path):
        """Загружаем полный образ персонажа из файла"""
        try:
            outfit_image = Image.open(os.path.join(os.path.dirname(__file__), image_path)).convert("RGBA")
            outfit_image = outfit_image.resize((self.width, self.height))
            self.bg_image = outfit_image
            self.update_canvas()
            return True
        except Exception as e:
            print(f"Ошибка загрузки полного образа: {e}")
            return False
    
    def update_canvas(self):
        """Обновляем изображение на canvas"""
        self.canvas.delete("all")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.canvas.create_image(0, 0, anchor='nw', image=self.bg_photo)
    
    def switch_gender(self):
        """Переключаем между мужским и женским вариантом"""
        self.current_gender = 'female' if self.current_gender == 'male' else 'male'
        self.load_character_image()
    
    def clear_outfit(self):
        """Очищаем все нарисованные элементы, оставляя только фон"""
        self.bg_image = self.original_bg_image.copy()
        self.update_canvas()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title('WCC Weather Check Controll')
        self.root.geometry('1000x600')
        
        self.bluetooth = BluetoothConnection()
        self.loading_frame = None

        self.temp = float(0.00)
        self.hum = float(0.00)
        self.pressure = float(0.00)

        # Background
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            loading_img_path = os.path.join(base_dir, 'background.png')
            self.bg_img = tk.PhotoImage(file=loading_img_path)
            self.label_pic = tk.Label(self.root, image=self.bg_img)
            self.label_pic.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            pass

        # Character frame
        self.character_frame = CharacterFrame(root)
        self.character_frame.frame.place(x=450, y=50)


        # Weather info display 

        self.temp_label = tk.Label(root, text= f"Температура: {self.temp}°C", 
                                 bg='white', anchor='w', font=('Arial', 16))
        self.temp_label.place(x=20, y=450)
        
        self.hum_label = tk.Label(root, text= f"Влажность: {self.hum}%", 
                                bg='white', anchor='w', font=('Arial', 16))
        self.hum_label.place(x=20, y=500)
        
        self.pressure_label = tk.Label(root, text= f"Давление: {self.pressure} hPa", 
                                     bg='white', anchor='w', font=('Arial', 16))
        self.pressure_label.place(x=20, y=550)
        
    
        # Buttons
        self.switch_btn = tk.Button(root, text="Переключить персонажа", 
                                 command=self.switch_character) 
        self.switch_btn.place(x=525, y=10)


        # Clear button
        tk.Button(root, text="Очистить", 
                command=self.character_frame.clear_outfit).place(x=800, y=350)
        
        # Bluetooth buttons
        tk.Button(root, text="Подключиться к передатчику", 
                command=self.show_loading_screen).place(x=0, y=0)
        
        tk.Button(root, text="Прочитать данные", 
                command=self.read_bluetooth_data).place(x=800, y=275)

    

    def switch_character(self):
        """Обработчик переключения персонажа"""
        self.character_frame.switch_gender()

    def show_loading_screen(self):
        """Показывает экран загрузки и подключается к HC-05"""
        self.loading_frame = tk.Frame(
            self.root,
            bg="black",
            width=self.root.winfo_width(),
            height=self.root.winfo_height()
        )
        self.loading_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.loading_frame.lift()

        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            loading_img_path = os.path.join(base_dir, 'загрузочный экран.png')
            self.loading_bg_img = tk.PhotoImage(file=loading_img_path)
            self.loading_label_pic = tk.Label(self.loading_frame, image=self.loading_bg_img)
            self.loading_label_pic.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            pass

        # Запускаем подключение в отдельном потоке
        threading.Thread(target=self.connect_bluetooth_in_thread, daemon=True).start()

    def connect_bluetooth_in_thread(self):
        """Подключается к Bluetooth в отдельном потоке"""
        if self.bluetooth.connect_to_hc05():
            # После успешного подключения закрываем экран загрузки
            self.root.after(0, self.hide_loading_screen)
        else:
            # Если подключение не удалось, показываем сообщение
            self.root.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось подключиться к HC-05"))
            self.root.after(0, self.hide_loading_screen)

    def read_bluetooth_data(self):
        """Читает данные с Bluetooth устройства и выводит нужную картинку, а также текущие значения температуры, влажности и давления"""

        data = self.bluetooth.read_single_line()

        if data == None:
            messagebox.showerror("Ошибка","Сначала подключитесь к устройству!")
        else:
            data = data.split(" ")
            self.temp = float(data[0])
            self.hum = float(data[1])
            self.pressure = float(data[2])

            if self.character_frame.current_gender == 'male':

                if 25 <= self.temp <= 35 and self.hum >= 70:
                    outfit_file = "25-35 70.jfif"

                elif self.temp >= 25:
                    outfit_file = "+30 50.jfif"
                
                elif 18 <= self.temp < 25:
                    outfit_file = "18-25.jfif"

                elif 10 <= self.temp < 18 and self.hum >= 70:
                    outfit_file = "10-18.jfif"

                elif 0 <= self.temp < 10:
                    outfit_file = "0-10.jfif"

                else:
                    outfit_file = "-0.jfif"


            else:

                if 25 <= self.temp <= 35 and self.hum >= 70:
                    outfit_file = "25-35 70 д.jfif"

                elif self.temp >= 25:
                    outfit_file = "+30 50 д.jfif"
                
                elif 18 <= self.temp < 25:
                    outfit_file = "18-25 д.jfif"

                elif 10 <= self.temp < 18 and self.hum >= 70:
                    outfit_file = "10-18 д.jfif"

                elif 0 <= self.temp < 10:
                    outfit_file = "0-10 д.jfif"

                else:
                    outfit_file = "-0 д.jfif"

            self.character_frame.load_full_outfit(outfit_file)

            self.temp_label.config(text= f"Температура: {self.temp}°C")
            self.hum_label.config(text= f"Влажность: {self.hum}%")
            self.pressure_label.config(text=  f"Давление: {self.pressure}hPa")


    def hide_loading_screen(self):
        """Скрывает экран загрузки"""
        if hasattr(self, 'loading_frame') and self.loading_frame:
            self.loading_frame.destroy()
            self.loading_frame = None

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = App(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
        root.destroy()
