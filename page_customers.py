import customtkinter as ctk
import database


class CustomersPage(ctk.CTkFrame):
    def __init__(self, master):
        # 初始化這個 Frame
        super().__init__(master, corner_radius=10)
        
        # 1. 畫出 UI
        self.setup_ui()
        
        # 2. 載入資料
        self.refresh_vehicle_list()

    def setup_ui(self):
        """專門負責畫出客戶信息頁面的介面"""
        # --- 上半部：輸入表單 ---
        ctk.CTkLabel(self, text="🚗 客戶與車輛登錄", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))

        form_frame = ctk.CTkFrame(self)
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

        self.lbl_message = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14))
        self.lbl_message.pack(pady=5)

        # --- 分隔線 ---
        ctk.CTkFrame(self, height=2, fg_color="gray").pack(fill="x", padx=20, pady=5)
        
        # --- 下半部：資料列表區塊 ---
        # 客戶搜尋工具列
        search_frame_c = ctk.CTkFrame(self, fg_color="transparent")
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
        self.table_frame_customer = ctk.CTkScrollableFrame(self)
        self.table_frame_customer.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # ==================== 邏輯功能區 ====================
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

    def open_edit_popup(self, plate_number, owner_name, phone_number, brand, model):
        """開啟修改客戶資料的專屬彈出視窗"""
        self.edit_popup = ctk.CTkToplevel(self)
        self.edit_popup.title("✏️ 修改客戶資料")
        self.edit_popup.geometry("400x450")
        self.edit_popup.attributes('-topmost', True) # 保持在最上層
        self.edit_popup.grab_set()                   # 霸佔點擊焦點，一定要改完或關掉才能點原視窗

        ctk.CTkLabel(self.edit_popup, text="修改價目表項目", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        # 項目名稱輸入框 (預先填好舊資料)
        self.entry_edit_plate = ctk.CTkEntry(self.edit_popup, width=200)
        self.entry_edit_plate.pack(pady=10)
        self.entry_edit_plate.insert(0, plate_number) 

        # 項目單價輸入框 (預先填好舊資料)
        self.entry_edit_name = ctk.CTkEntry(self.edit_popup, width=200)
        self.entry_edit_name.pack(pady=10)
        self.entry_edit_name.insert(0, owner_name)

        # 項目單價輸入框 (預先填好舊資料)
        self.entry_edit_phone = ctk.CTkEntry(self.edit_popup, width=200)
        self.entry_edit_phone.pack(pady=10)
        self.entry_edit_phone.insert(0, phone_number)

        # 項目單價輸入框 (預先填好舊資料)
        self.entry_edit_brand = ctk.CTkEntry(self.edit_popup, width=200)
        self.entry_edit_brand.pack(pady=10)
        self.entry_edit_brand.insert(0, brand)

        # 項目單價輸入框 (預先填好舊資料)
        self.entry_edit_model = ctk.CTkEntry(self.edit_popup, width=200)
        self.entry_edit_model.pack(pady=10)
        self.entry_edit_model.insert(0, model)

        # 錯誤訊息顯示區
        self.lbl_edit_msg = ctk.CTkLabel(self.edit_popup, text="")
        self.lbl_edit_msg.pack(pady=5)

        # 儲存按鈕 (把 ID 傳遞給儲存函式)
        btn_save_edit = ctk.CTkButton(self.edit_popup, text="💾 儲存修改", fg_color="#E67E22", hover_color="#D35400",
                                      command=lambda: self.save_edit_action(plate_number))
        btn_save_edit.pack(pady=10)

    def save_edit_action(self, plate):
        """儲存彈出視窗裡的修改內容，並寫入資料庫"""
        new_plate = self.entry_edit_plate.get().strip().upper()
        new_name = self.entry_edit_name.get().strip()
        new_phone = self.entry_edit_phone.get().strip()
        new_brand = self.entry_edit_brand.get().strip()
        new_model = self.entry_edit_model.get().strip()

        if not new_plate:
            self.lbl_edit_msg.configure(text="❌ 車牌號碼不能為空！", text_color="red")
            return

        success, msg = database.update_vehicle(plate, new_plate, new_name, new_phone, new_brand, new_model)
        
        if success:
            self.edit_popup.destroy()     # 修改成功，立刻關閉彈出視窗
            self.refresh_vehicle_list()  # 重新整理背後主畫面的列表
        else:
            self.lbl_edit_msg.configure(text=msg, text_color="red")

    def refresh_vehicle_list(self,search_keyword=""):
        """從資料庫抓取資料，並更新表格畫面"""
        # 1. 清空舊畫面
        for widget in self.table_frame_customer.winfo_children():
            widget.destroy()

        # 2. 標題列多加一個「操作」欄位
        headers = ["車牌號碼", "車主姓名", "聯絡電話", "品牌", "車型", "操作"]
        for i, text in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame_customer, text=text, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=i, sticky="w", padx=20, pady=5)
            self.table_frame_customer.grid_columnconfigure(i, weight=1)

        if search_keyword != "":
            vehicles = database.search_vehicles_by_keyword(search_keyword)
        else:
            vehicles = database.get_all_vehicles()
            # 如果是顯示全部，順便把搜尋框清空 (用 hasattr 防呆，避免剛啟動時報錯)
            if hasattr(self, 'entry_search_customer'):
                self.entry_search_customer.delete(0, 'end')

        # 3. 撈取資料並印出
        for row_idx, vehicle in enumerate(vehicles, start=1):
            plate, owner, phone, brand, model = vehicle
            
            # 畫出文字資料
            for col_idx, value in enumerate(vehicle):
                display_text = str(value) if value else "-"
                lbl = ctk.CTkLabel(self.table_frame_customer, text=display_text)
                lbl.grid(row=row_idx, column=col_idx, sticky="w", padx=20, pady=5)
            
            action_frame = ctk.CTkFrame(self.table_frame_customer, fg_color="transparent")
            action_frame.grid(row=row_idx, column=5, padx=10, pady=2, sticky="w")

            # 編輯按鈕
            btn_edit = ctk.CTkButton(action_frame, text="✏️ 修改", width=50, fg_color="#F39C12", hover_color="#D68910",
                                     command=lambda p=plate, o=owner, ph=phone, b=brand, m=model: self.open_edit_popup(p, o, ph, b, m))
            btn_edit.pack(side="left", padx=(0, 5))

            # 刪除按鈕
            btn_delete = ctk.CTkButton(action_frame, text="🗑️ 刪除", width=50, fg_color="darkred", hover_color="red",
                                        command=lambda p=plate: self.delete_car_action(p))
            btn_delete.pack(side="left")
    
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