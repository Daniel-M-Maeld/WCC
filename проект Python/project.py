# project.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
from signal_reader import BluetoothConnection
import threading

def create_rounded_rect(width, height, radius, color):
    image = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([(0, 0), (width-1, height-1)], radius=radius, fill=color)
    return ImageTk.PhotoImage(image)

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
            self.original_bg_image = Image.open(filename).convert("RGBA")
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
            outfit_image = Image.open(image_path).convert("RGBA")
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
            self.bg_img = tk.PhotoImage(file='background.png')
            self.label_pic = tk.Label(self.root, image=self.bg_img)
            self.label_pic.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            pass

        # Character frame
        self.character_frame = CharacterFrame(root)
        self.character_frame.frame.place(x=450, y=50)
    
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
            self.loading_bg_img = tk.PhotoImage(file='загрузочный экран.png')
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
        """Читает данные с Bluetooth устройства"""

        data = self.bluetooth.read_single_line()

        if data == None:
            messagebox.showerror("Ошибка","Сначала подключитесь к устройству!")
        else:
            data = data.split(" ")
            self.temp = float(data[0])
            self.hum = float(data[1])
            self.pressure = float(data[2])

            if self.temp >= 30 and self.hum <= 50 and self.character_frame.current_gender == 'male':
                outfit_file = "+30 50.jfif"
                self.character_frame.load_full_outfit(outfit_file)
            elif 25 <= self.temp <= 35 and self.hum >= 70 and self.character_frame.current_gender == 'male':
                outfit_file = "25-35 70.jfif"
                self.character_frame.load_full_outfit(outfit_file)
            elif 18 <= self.temp < 25 and self.character_frame.current_gender == 'male':
                outfit_file = "18-25.jfif"
                self.character_frame.load_full_outfit(outfit_file)
            elif 10 <= self.temp < 18 and self.hum >= 70 and self.character_frame.current_gender == 'male':
                outfit_file = "10-18.jfif"
                self.character_frame.load_full_outfit(outfit_file)
            elif 0 <= self.temp < 10 and self.character_frame.current_gender == 'male':
                outfit_file = "0-10.jfif"
                self.character_frame.load_full_outfit(outfit_file)

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