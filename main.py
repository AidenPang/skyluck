import customtkinter as ctk
import database
from tkinter import messagebox  #匯入內建的彈出視窗工具
from datetime import datetime #用來自動取得今天日期

# 啟動時確保資料庫存在
database.init_db()

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("車廠管理系統 v1.0")
        self.geometry("900x600")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ==================== 左側導覽列 ====================
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) 

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="🛠️ 車廠管理系統", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="📊 儀表板", command=lambda: self.select_frame("dashboard"))
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        self.btn_orders = ctk.CTkButton(self.sidebar_frame, text="📝 維修工單", command=lambda: self.select_frame("orders"))
        self.btn_orders.grid(row=2, column=0, padx=20, pady=10)

        self.btn_customers = ctk.CTkButton(self.sidebar_frame, text="🚗 客戶車輛", command=lambda: self.select_frame("customers"))
        self.btn_customers.grid(row=3, column=0, padx=20, pady=10)

        # ==================== 右側分頁 ====================
        self.frames = {}

        # 1. 儀表板分頁
        self.frames["dashboard"] = ctk.CTkFrame(self, corner_radius=10)
        ctk.CTkLabel(self.frames["dashboard"], text="這裡是儀表板總覽", font=ctk.CTkFont(size=24)).pack(pady=50)
        
        # 2. 維修工單分頁
        self.frames["orders"] = ctk.CTkFrame(self, corner_radius=10)
        ctk.CTkLabel(self.frames["orders"], text="📝 維修工單系統", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 10))
        
        # 🛠️ 核心改動：主畫面現在只留這顆按鈕，點擊就開啟彈出視窗！
        self.btn_open_order = ctk.CTkButton(self.frames["orders"], text="➕ 新增維修工單", font=ctk.CTkFont(weight="bold"), fg_color="#27AE60", hover_color="#2ECC71", height=40, command=self.open_order_window)
        self.btn_open_order.pack(pady=10)

        # ================= 📦 下半區：歷史紀錄 (維持原本的不要動) =================
        ctk.CTkFrame(self.frames["orders"], height=2, fg_color="gray").pack(fill="x", padx=20, pady=10)

        search_frame = ctk.CTkFrame(self.frames["orders"], fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=0)
        
        ctk.CTkLabel(search_frame, text="📋 歷史維修紀錄", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="搜車牌/車主/電話/項目...", width=120)
        self.entry_search.pack(side="left", padx=(20, 10))
        self.entry_search.bind("<Return>", lambda event: self.search_orders())
        self.btn_search = ctk.CTkButton(search_frame, text="🔍 搜尋", width=60, command=self.search_orders)
        self.btn_search.pack(side="left")
        self.btn_clear = ctk.CTkButton(search_frame, text="✖️ 顯示全部", width=80, fg_color="gray", command=self.refresh_order_list)
        self.btn_clear.pack(side="left", padx=10)

        self.table_frame_order = ctk.CTkScrollableFrame(self.frames["orders"])
        self.table_frame_order.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        # ======================================================
        

        # 3. 客戶與車輛管理分頁
        self.frames["customers"] = ctk.CTkFrame(self, corner_radius=10)
        # ==================== 客戶與車輛管理分頁 ====================
        # --- 上半部：輸入表單 ---
        ctk.CTkLabel(self.frames["customers"], text="🚗 客戶與車輛登錄", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))

        form_frame = ctk.CTkFrame(self.frames["customers"])
        form_frame.pack(pady=10, padx=20, fill="x")

        self.entry_plate = ctk.CTkEntry(form_frame, placeholder_text="車牌號碼 (必填)*")
        self.entry_plate.grid(row=0, column=0, padx=10, pady=10)
        
        self.entry_owner = ctk.CTkEntry(form_frame, placeholder_text="車主姓名")
        self.entry_owner.grid(row=0, column=1, padx=10, pady=10)
        
        self.entry_phone = ctk.CTkEntry(form_frame, placeholder_text="聯絡電話")
        self.entry_phone.grid(row=0, column=2, padx=10, pady=10)

        self.entry_brand = ctk.CTkEntry(form_frame, placeholder_text="品牌 (例: Toyota)")
        self.entry_brand.grid(row=1, column=0, padx=10, pady=10)

        self.entry_model = ctk.CTkEntry(form_frame, placeholder_text="車款 (例: Altis)")
        self.entry_model.grid(row=1, column=1, padx=10, pady=10)

        self.btn_save_car = ctk.CTkButton(form_frame, text="➕ 儲存資料", fg_color="green", hover_color="darkgreen", command=self.save_vehicle)
        self.btn_save_car.grid(row=1, column=2, padx=10, pady=10)

        self.lbl_message = ctk.CTkLabel(self.frames["customers"], text="", font=ctk.CTkFont(size=14))
        self.lbl_message.pack(pady=5)

        # --- 分隔線 ---
        ctk.CTkFrame(self.frames["customers"], height=2, fg_color="gray").pack(fill="x", padx=20, pady=5)
        
        # --- 下半部：資料列表區塊 (🛠️ 本次新增) ---
        # 客戶搜尋工具列
        search_frame_c = ctk.CTkFrame(self.frames["customers"], fg_color="transparent")
        search_frame_c.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(search_frame_c, text="📋 已登錄車輛列表", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")

        self.entry_search_customer = ctk.CTkEntry(search_frame_c, placeholder_text="搜車牌/車主/電話...", width=180)
        self.entry_search_customer.pack(side="left", padx=(20, 10))
        self.entry_search_customer.bind("<Return>", lambda event: self.search_customers())

        self.btn_search_customer = ctk.CTkButton(search_frame_c, text="🔍 搜尋", width=60, command=self.search_customers)
        self.btn_search_customer.pack(side="left")

        self.btn_clear_customer = ctk.CTkButton(search_frame_c, text="✖️ 顯示全部", width=80, fg_color="gray", command=self.refresh_vehicle_list)
        self.btn_clear_customer.pack(side="left", padx=10)

        # 建立一個可捲動的框架來當作表格
        self.table_frame = ctk.CTkScrollableFrame(self.frames["customers"])
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # 啟動時先載入一次資料
        self.refresh_vehicle_list()
        # ======================================================

        # 預設啟動畫面切到工單頁
        self.select_frame("customers") 

    # ==================== 邏輯功能區 ====================
    def select_frame(self, name):
        """處理分頁切換"""
        for frame in self.frames.values():
            frame.grid_forget()
        self.frames[name].grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # 🧑‍🏫 重點：當切換到工單頁面時，自動更新車牌的下拉選單
        if name == "orders":
            self.refresh_order_list()

    def open_order_window(self):
        """開啟完整的『新增工單』彈出視窗"""
        # 1. 建立彈出視窗
        self.order_popup = ctk.CTkToplevel(self)
        self.order_popup.title("新增維修工單")
        self.order_popup.geometry("650x700")
        self.order_popup.attributes('-topmost', True) # 保持在最上層
        self.order_popup.grab_set()                   # 霸佔焦點，防呆

        self.current_order_items = [] # 每次開新單，購物車先清空

        # --- 📦 區塊 1：基本資料 ---
        info_frame = ctk.CTkFrame(self.order_popup)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        self.entry_date = ctk.CTkEntry(info_frame, placeholder_text="日期", width=120)
        self.entry_date.grid(row=0, column=0, padx=10, pady=10)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # 智慧車牌搜尋 (直接裝在 popup 裡面)
        self.entry_search_plate = ctk.CTkEntry(info_frame, placeholder_text="車牌", width=150)
        self.entry_search_plate.grid(row=0, column=1, padx=10, pady=10)
        self.entry_search_plate.bind("<KeyRelease>", self.show_dropdown) 
        self.dropdown_frame = ctk.CTkScrollableFrame(self.order_popup, height=120)

        self.entry_mileage = ctk.CTkEntry(info_frame, placeholder_text="進廠里程數", width=120)
        self.entry_mileage.grid(row=0, column=2, padx=10, pady=10)

        # --- 📦 區塊 2：零件購物車輸入 ---
        item_frame = ctk.CTkFrame(self.order_popup)
        item_frame.pack(fill="x", padx=20, pady=5)

        self.entry_item_name = ctk.CTkEntry(item_frame, placeholder_text="項目 (例: 機油)", width=150)
        self.entry_item_name.grid(row=0, column=0, padx=10, pady=10)
        self.entry_item_qty = ctk.CTkEntry(item_frame, placeholder_text="數量", width=60)
        self.entry_item_qty.grid(row=0, column=1, padx=10, pady=10)
        self.entry_item_price = ctk.CTkEntry(item_frame, placeholder_text="單價", width=80)
        self.entry_item_price.grid(row=0, column=2, padx=10, pady=10)
        
        self.btn_add_item = ctk.CTkButton(item_frame, text="➕ 加入", width=60, fg_color="#2980B9", command=self.add_to_cart)
        self.btn_add_item.grid(row=0, column=3, padx=10, pady=10)

       # --- 📦 區塊 3：購物車清單 ---
        self.cart_frame = ctk.CTkScrollableFrame(self.order_popup, height=150)
        self.cart_frame.pack(fill="both", expand=True, padx=20, pady=5)

        # ================= 🛡️ 絕招：強制釘選在底部的區塊 =================
        bottom_frame = ctk.CTkFrame(self.order_popup, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", pady=20) # side="bottom" 讓它死死貼在視窗最下方！

        # 注意：這裡的第一個參數要改成 bottom_frame 喔！
        self.btn_save_order = ctk.CTkButton(bottom_frame, text="💾 儲存並送出", font=ctk.CTkFont(weight="bold"), fg_color="#E67E22", height=40, command=self.save_order)
        self.btn_save_order.pack(pady=5)

        self.lbl_msg_order = ctk.CTkLabel(bottom_frame, text="")
        self.lbl_msg_order.pack()
        
    def show_dropdown(self, event):
        """根據打字內容，顯示並過濾浮動選單"""
        typed_text = self.entry_search_plate.get().strip().upper()
        all_plates = database.get_all_plate_numbers()

        # 情況 A：如果輸入框沒半個字，就把選單藏起來
        if not typed_text:
            self.dropdown_frame.place_forget()
            return

        # 找出符合打字內容的車牌
        filtered = [p for p in all_plates if typed_text in p]

        # 清空舊的按鈕
        for widget in self.dropdown_frame.winfo_children(): 
            widget.destroy()

        # 情況 B：如果有找到符合的車牌，就把選單秀出來
        if filtered:
            # 魔法指令 place()：讓選單死死貼在輸入框的正下方
            self.dropdown_frame.place(in_=self.entry_search_plate, rely=1.0, relx=0, y=2, relwidth=1.0)
            
            # 把車牌變成按鈕塞進選單
            for p in filtered:
                btn = ctk.CTkButton(self.dropdown_frame, text=p, fg_color="transparent", hover_color="gray", anchor="w",
                                    command=lambda plate=p: self.pick_plate(plate))
                btn.pack(fill="x", padx=5, pady=2)
        else:
            self.dropdown_frame.place_forget()

    def pick_plate(self, plate):
        """當點擊選單裡的車牌時執行的動作"""
        self.entry_search_plate.delete(0, 'end') # 清空輸入框
        self.entry_search_plate.insert(0, plate) # 填入完整車牌
        self.dropdown_frame.place_forget()       # 收合選單
    
    def save_vehicle(self):
        """儲存車輛資料"""
        plate = self.entry_plate.get().strip().upper()
        owner = self.entry_owner.get().strip()
        phone = self.entry_phone.get().strip()
        brand = self.entry_brand.get().strip()
        model = self.entry_model.get().strip()

        if not plate:
            self.lbl_message.configure(text="❌ 車牌號碼為必填欄位！", text_color="red")
            return

        success, msg = database.add_vehicle(plate, owner, phone, brand, model)
        
        if success:
            self.lbl_message.configure(text=msg, text_color="green")
            self.entry_plate.delete(0, 'end')
            self.entry_owner.delete(0, 'end')
            self.entry_phone.delete(0, 'end')
            self.entry_brand.delete(0, 'end')
            self.entry_model.delete(0, 'end')
            
            # 🛠️ 儲存成功後，立刻重新整理下方的表格
            self.refresh_vehicle_list()
        else:
            self.lbl_message.configure(text=msg, text_color="red")

    def refresh_vehicle_list(self,search_keyword=""):
        """從資料庫抓取資料，並更新表格畫面"""
        # 1. 清空舊畫面
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # 2. 標題列多加一個「操作」欄位
        headers = ["車牌號碼", "車主姓名", "聯絡電話", "品牌", "車型", "操作"]
        for i, text in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame, text=text, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=i, sticky="w", padx=20, pady=5)
            self.table_frame.grid_columnconfigure(i, weight=1)

        if search_keyword != "":
            vehicles = database.search_vehicles_by_keyword(search_keyword)
        else:
            vehicles = database.get_all_vehicles()
            # 如果是顯示全部，順便把搜尋框清空 (用 hasattr 防呆，避免剛啟動時報錯)
            if hasattr(self, 'entry_search_customer'):
                self.entry_search_customer.delete(0, 'end')

        # 3. 撈取資料並印出
        for row_idx, vehicle in enumerate(vehicles, start=1):
            plate = vehicle[0] # 車牌是這筆資料的第一個項目
            
            # 畫出文字資料
            for col_idx, value in enumerate(vehicle):
                display_text = str(value) if value else "-"
                lbl = ctk.CTkLabel(self.table_frame, text=display_text)
                lbl.grid(row=row_idx, column=col_idx, sticky="w", padx=20, pady=5)
            
            # 4. 在最右邊加上刪除按鈕
            # 🧑‍🏫 重點教學：lambda p=plate 是為了解決 Python 迴圈綁定變數的問題
            btn_delete = ctk.CTkButton(
                self.table_frame, 
                text="🗑️ 刪除", 
                width=60, 
                fg_color="darkred", 
                hover_color="red",
                command=lambda p=plate: self.delete_car_action(p)
            )
            btn_delete.grid(row=row_idx, column=5, padx=10, pady=2)
    
    def search_customers(self):
        """按下客戶搜尋按鈕時執行的動作"""
        keyword = self.entry_search_customer.get().strip()
        self.refresh_vehicle_list(search_keyword=keyword)

    def delete_car_action(self, plate):
        """執行刪除車輛的動作（加入確認視窗防呆機制）"""
        
        # 1. 彈出警告視窗 (標題, 內容文字)
        # askyesno 會回傳一個布林值：按「是」會得到 True，按「否」會得到 False
        confirm = messagebox.askyesno(
            title="⚠️ 確認刪除", 
            message=f"你確定要徹底刪除車牌「{plate}」的資料嗎？\n(注意：刪除後將無法復原！)"
        )
        
        # 2. 判斷使用者的選擇
        if confirm == True:
            # 只有當老闆按下「是」，才真正去呼叫資料庫刪除
            success, msg = database.delete_vehicle(plate)
            
            if success:
                self.lbl_message.configure(text=msg, text_color="green")
                self.refresh_vehicle_list() # 重新整理畫面
        else:
            # 如果老闆按下「否」或直接關閉視窗，就什麼都不做，只顯示取消提示
            self.lbl_message.configure(text=f"已取消刪除 {plate} 的操作。", text_color="gray")
    
    # --- 工單相關功能 ---  
    def add_to_cart(self):
        """把項目加入彈出視窗的暫存購物車"""
        name = self.entry_item_name.get().strip()
        qty = self.entry_item_qty.get().strip()
        price = self.entry_item_price.get().strip()

        if not name or not qty.isdigit() or not price.isdigit():
            self.lbl_msg_order.configure(text="❌ 請填寫完整，且數量單價須為數字！", text_color="red")
            return

        # 把項目塞進暫存清單
        item_data = {"name": name, "qty": int(qty), "price": int(price)}
        self.current_order_items.append(item_data)

        # 清空輸入框
        self.entry_item_name.delete(0, 'end')
        self.entry_item_qty.delete(0, 'end')
        self.entry_item_price.delete(0, 'end')

        # 顯示在購物車畫面上
        subtotal = item_data["qty"] * item_data["price"]
        ctk.CTkLabel(self.cart_frame, text=f"✅ {name} x{qty} | 單價: ${price} | 小計: ${subtotal}").pack(anchor="w", padx=10, pady=2)
        self.lbl_msg_order.configure(text="")

    def save_order(self):
        date = self.entry_date.get()
        plate = self.entry_search_plate.get().strip().upper()
        mileage = self.entry_mileage.get().strip()

        if mileage != "" and not mileage.isdigit():
            self.lbl_msg_order.configure(text="❌ 里程數必須是純數字！", text_color="red")
            return
        if len(self.current_order_items) == 0:
            self.lbl_msg_order.configure(text="❌ 請先加入維修項目！", text_color="red")
            return

        #如果留白，就預設為 0
        final_mileage = int(mileage) if mileage.isdigit() else 0

        # 直接把整個清單交給資料庫處理！
        success, msg = database.add_repair_order(plate, date, final_mileage, self.current_order_items)
        
        if success:
            # 🛠️ 1. 關閉這個彈出的視窗
            self.order_popup.destroy()
            
            # 🛠️ 2. 重新整理主畫面的歷史表格
            self.refresh_order_list()
        else:
            self.lbl_msg_order.configure(text=msg, text_color="red")

    def search_orders(self):
        """按下搜尋按鈕時執行的動作"""
        keyword = self.entry_search.get().strip().upper()
        # 把關鍵字傳遞給表格更新函式
        self.refresh_order_list(search_keyword=keyword)

    def refresh_order_list(self, search_keyword=""):
        """更新工單表格。如果有傳入關鍵字，就只顯示搜尋結果"""
        for widget in self.table_frame_order.winfo_children(): widget.destroy()
        
        headers = ["日期", "車牌號碼", "里程數", "維修項目", "總金額"]
        for i, text in enumerate(headers):
            ctk.CTkLabel(self.table_frame_order, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, sticky="w", padx=15, pady=5)
            self.table_frame_order.grid_columnconfigure(i, weight=1)
        
        # 🧑‍🏫 學習重點：根據有沒有關鍵字，決定向資料庫要什麼資料！
        if search_keyword != "":
            orders = database.search_orders_by_keyword(search_keyword)
        else:
            orders = database.get_all_orders()
            self.entry_search.delete(0, 'end') # 如果是顯示全部，就順便清空搜尋框
            
        for row_idx, order in enumerate(orders, start=1):
            for col_idx, value in enumerate(order):
                display_text = f"${value}" if col_idx == 4 else str(value)
                ctk.CTkLabel(self.table_frame_order, text=display_text).grid(row=row_idx, column=col_idx, sticky="w", padx=15, pady=5)
    # -------------------

if __name__ == "__main__":
    app = App()
    app.mainloop()