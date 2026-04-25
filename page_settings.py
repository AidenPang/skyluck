import customtkinter as ctk
import database

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master):
        # 初始化這個 Frame
        super().__init__(master, corner_radius=10)
        
        # 1. 畫出 UI
        self.setup_ui()
        
        # 2. 載入資料
        self.refresh_services_list()

    def setup_ui(self):
        """專門負責畫出系統設定頁面的介面"""
        ctk.CTkLabel(self, text="⚙️ 系統設定 - 價目表主檔管理", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 10))

        # --- 上半區：新增維修項目 ---
        add_service_frame = ctk.CTkFrame(self)
        add_service_frame.pack(fill="x", padx=20, pady=10)

        self.entry_service_name = ctk.CTkEntry(add_service_frame, placeholder_text="維修項目名稱", width=200)
        self.entry_service_name.pack(side="left", padx=10, pady=15)

        self.entry_service_price = ctk.CTkEntry(add_service_frame, placeholder_text="預設單價 ($)", width=100)
        self.entry_service_price.pack(side="left", padx=10, pady=15)

        self.btn_save_service = ctk.CTkButton(add_service_frame, text="➕ 新增項目", fg_color="#2980B9", command=self.add_service_action)
        self.btn_save_service.pack(side="left", padx=10, pady=15)

        self.lbl_msg_service = ctk.CTkLabel(add_service_frame, text="")
        self.lbl_msg_service.pack(side="left", padx=10, pady=15)

        # 分隔線
        ctk.CTkFrame(self, height=2, fg_color="gray").pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(self, text="📋 現有價目表列表", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20)

        # --- 下半區：價目表列表 ---
        self.table_frame_services = ctk.CTkScrollableFrame(self)
        self.table_frame_services.pack(fill="both", expand=True, padx=20, pady=(5, 20))

    # ==================== 邏輯功能區 ====================
    def add_service_action(self):
        """按下新增維修項目"""
        name = self.entry_service_name.get().strip()
        price = self.entry_service_price.get().strip()

        if not name or not price.isdigit():
            self.lbl_msg_service.configure(text="❌ 填寫錯誤！", text_color="red")
            return

        success, msg = database.add_service(name, int(price))
        
        if success:
            self.lbl_msg_service.configure(text=msg, text_color="green")
            self.entry_service_name.delete(0, 'end')
            self.entry_service_price.delete(0, 'end')
            self.refresh_services_list()
        else:
            self.lbl_msg_service.configure(text=msg, text_color="red")

    def open_edit_popup(self, s_id, current_name, current_price):
        """開啟專屬的『修改項目』彈出視窗"""
        self.edit_popup = ctk.CTkToplevel(self)
        self.edit_popup.title("✏️ 修改維修項目")
        self.edit_popup.geometry("400x300")
        self.edit_popup.attributes('-topmost', True) # 保持在最上層
        self.edit_popup.grab_set()                   # 霸佔點擊焦點，一定要改完或關掉才能點原視窗

        ctk.CTkLabel(self.edit_popup, text="修改價目表項目", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        # 項目名稱輸入框 (預先填好舊資料)
        self.entry_edit_name = ctk.CTkEntry(self.edit_popup, width=200)
        self.entry_edit_name.pack(pady=10)
        self.entry_edit_name.insert(0, current_name) 

        # 項目單價輸入框 (預先填好舊資料)
        self.entry_edit_price = ctk.CTkEntry(self.edit_popup, width=200)
        self.entry_edit_price.pack(pady=10)
        self.entry_edit_price.insert(0, str(current_price))

        # 錯誤訊息顯示區
        self.lbl_edit_msg = ctk.CTkLabel(self.edit_popup, text="")
        self.lbl_edit_msg.pack(pady=5)

        # 儲存按鈕 (把 ID 傳遞給儲存函式)
        btn_save_edit = ctk.CTkButton(self.edit_popup, text="💾 儲存修改", fg_color="#E67E22", hover_color="#D35400",
                                      command=lambda: self.save_edit_action(s_id))
        btn_save_edit.pack(pady=10)

    def save_edit_action(self, s_id):
        """儲存彈出視窗裡的修改內容，並寫入資料庫"""
        new_name = self.entry_edit_name.get().strip()
        new_price = self.entry_edit_price.get().strip()

        if not new_name or not new_price.isdigit():
            self.lbl_edit_msg.configure(text="❌ 請填寫名稱且單價須為數字！", text_color="red")
            return

        success, msg = database.update_service(s_id, new_name, int(new_price))
        
        if success:
            self.edit_popup.destroy()     # 修改成功，立刻關閉彈出視窗
            self.refresh_services_list()  # 重新整理背後主畫面的列表
        else:
            self.lbl_edit_msg.configure(text=msg, text_color="red")


    def refresh_services_list(self):
        """從資料庫撈取價目表並畫在畫面上"""
        for widget in self.table_frame_services.winfo_children(): 
            widget.destroy()
        
        # 1. 畫標題
        headers = ["項目 ID", "維修項目名稱", "預設單價 ($)", "操作"]
        for i, text in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame_services, text=text, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=i, sticky="w", padx=20, pady=5)
            self.table_frame_services.grid_columnconfigure(i, weight=1)

        # 2. 畫資料
        services = database.get_all_services()
        for row_idx, service in enumerate(services, start=1):
            s_id, name, price = service

            ctk.CTkLabel(self.table_frame_services, text=str(s_id)).grid(row=row_idx, column=0, sticky="w", padx=20, pady=5)
            ctk.CTkLabel(self.table_frame_services, text=name).grid(row=row_idx, column=1, sticky="w", padx=20, pady=5)
            ctk.CTkLabel(self.table_frame_services, text=f"${price}").grid(row=row_idx, column=2, sticky="w", padx=20, pady=5)
            
            # 🌟 把操作區塊包裝在一個小 Frame 裡，讓兩顆按鈕並排
            action_frame = ctk.CTkFrame(self.table_frame_services, fg_color="transparent")
            action_frame.grid(row=row_idx, column=3, padx=10, pady=2, sticky="w")

            # 編輯按鈕
            btn_edit = ctk.CTkButton(action_frame, text="✏️ 修改", width=50, fg_color="#F39C12", hover_color="#D68910",
                                     command=lambda sid=s_id, n=name, p=price: self.open_edit_popup(sid, n, p))
            btn_edit.pack(side="left", padx=(0, 5))

            # 刪除按鈕
            btn_delete = ctk.CTkButton(action_frame, text="🗑️ 刪除", width=50, fg_color="darkred", 
                                       command=lambda sid=s_id: self.delete_service_action(sid))
            btn_delete.pack(side="left")

    def delete_service_action(self, service_id):
        """按下刪除項目的動作"""
        database.delete_service(service_id)
        self.refresh_services_list()