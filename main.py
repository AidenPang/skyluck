import customtkinter as ctk
import database
from tkinter import messagebox  
from page_settings import SettingsPage 
from page_orders import OrdersPage 
from page_customers import CustomersPage 
from page_inventory import InventoryPage 
from page_vehicle_parts import VehiclePartsPage

database.init_db()
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("車廠管理系統 v1.0")
        self.geometry("1280x720")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ==================== 左側導覽列 ====================
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1) # 🌟 改為 7，把多餘的空白擠到所有按鈕的最下方

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="🛠️ 車廠管理系統", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="📊 儀表板", font=ctk.CTkFont(size=16), command=lambda: self.select_frame("dashboard"))
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        self.btn_orders = ctk.CTkButton(self.sidebar_frame, text="📝 維修工單", font=ctk.CTkFont(size=16), command=lambda: self.select_frame("orders"))
        self.btn_orders.grid(row=2, column=0, padx=20, pady=10)

        self.btn_customers = ctk.CTkButton(self.sidebar_frame, text="🚗 客戶車輛", font=ctk.CTkFont(size=16), command=lambda: self.select_frame("customers"))
        self.btn_customers.grid(row=3, column=0, padx=20, pady=10)

        # 🌟 3. 新增庫存按鈕
        self.btn_inventory = ctk.CTkButton(self.sidebar_frame, text="📦 庫存管理", font=ctk.CTkFont(size=16), command=lambda: self.select_frame("inventory"))
        self.btn_inventory.grid(row=4, column=0, padx=20, pady=10)

        self.btn_parts_query = ctk.CTkButton(self.sidebar_frame, text="🔍 零件導覽", font=ctk.CTkFont(size=16), command=lambda: self.select_frame("parts_query"))
        self.btn_parts_query.grid(row=5, column=0, padx=20, pady=10)

        # 🌟 4. 設定按鈕
        self.btn_settings = ctk.CTkButton(self.sidebar_frame, text="⚙️ 系統設定", font=ctk.CTkFont(size=16), command=lambda: self.select_frame("settings"))
        self.btn_settings.grid(row=6, column=0, padx=20, pady=10)

        # ==================== 右側分頁 ====================
        self.frames = {}
        self.frames["dashboard"] = ctk.CTkFrame(self, corner_radius=10)
        ctk.CTkLabel(self.frames["dashboard"], text="這裡是儀表板總覽", font=ctk.CTkFont(size=24)).pack(pady=50)
        
        self.frames["orders"] = OrdersPage(self)
        self.frames["customers"] = CustomersPage(self)
        self.frames["inventory"] = InventoryPage(self) # 🌟 5. 掛載庫存分頁
        self.frames["parts_query"] = VehiclePartsPage(self)
        self.frames["settings"] = SettingsPage(self)

        self.select_frame("dashboard") 

    def select_frame(self, name):
        """處理分頁切換 (無殘影版)"""
        for frame in self.frames.values():
            frame.grid_forget()
            
        self.frames[name].grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        def load_data():
            if name == "orders": self.frames["orders"].refresh_order_list()
            elif name == "customers": self.frames["customers"].refresh_vehicle_list()
            elif name == "inventory": self.frames["inventory"].refresh_inventory_list() # 🌟 6. 切換時自動重整庫存
            elif name == "parts_query": self.frames["parts_query"].refresh_brands()
            elif name == "settings": self.frames["settings"].refresh_services_list()

        self.after(20, load_data)

if __name__ == "__main__":
    app = App()
    app.mainloop()