import customtkinter as ctk
import database
from tkinter import messagebox

class InventoryPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=10)
        self.setup_ui()
        self.refresh_inventory_list()

    def setup_ui(self):
        ctk.CTkLabel(self, text="📦 庫存與貨物管理", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 10))

        # --- 上半區：新增零件 ---
        add_frame = ctk.CTkFrame(self)
        add_frame.pack(fill="x", padx=20, pady=10)

        # 第一排輸入
        row1 = ctk.CTkFrame(add_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=(10, 5))
        
        self.entry_name = ctk.CTkEntry(row1, placeholder_text="零件名稱 (必填)", width=200)
        self.entry_name.grid(row=0, column=0, padx=5, pady=5)
        
        self.combo_category = ctk.CTkComboBox(row1, values=["油品", "耗材", "輪胎", "電瓶", "改裝品", "其他"], width=100)
        self.combo_category.grid(row=0, column=1, padx=5, pady=5)
        self.combo_category.set("耗材")

        self.entry_qty = ctk.CTkEntry(row1, placeholder_text="初始庫存量", width=100)
        self.entry_qty.grid(row=0, column=2, padx=5, pady=5)
        
        self.combo_unit = ctk.CTkComboBox(row1, values=["個", "瓶", "條", "組", "L", "pc"], width=80)
        self.combo_unit.grid(row=0, column=3, padx=5, pady=5)
        self.combo_unit.set("個")

        # 第二排輸入
        row2 = ctk.CTkFrame(add_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(5, 10))

        self.entry_cost = ctk.CTkEntry(row2, placeholder_text="進貨成本 ($)", width=100)
        self.entry_cost.grid(row=0, column=0, padx=5, pady=5)

        self.entry_price = ctk.CTkEntry(row2, placeholder_text="預設售價 ($)", width=100)
        self.entry_price.grid(row=0, column=1, padx=5, pady=5)

        self.btn_add = ctk.CTkButton(row2, text="➕ 新增入庫", font=ctk.CTkFont(size=14), fg_color="#27AE60", hover_color="#2ECC71", command=self.add_item_action)
        self.btn_add.grid(row=0, column=2, padx=20, pady=5)

        self.lbl_msg = ctk.CTkLabel(row2, text="")
        self.lbl_msg.grid(row=0, column=3, padx=5, pady=5)

        # --- 下半區：列表 ---
        ctk.CTkFrame(self, height=2, fg_color="gray").pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(self, text="📋 現有庫存清單", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20)

        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))

    # ==================== 邏輯功能區 ====================
    def add_item_action(self):
        name = self.entry_name.get().strip()
        cat = self.combo_category.get()
        qty = self.entry_qty.get().strip()
        unit = self.combo_unit.get()
        cost = self.entry_cost.get().strip()
        price = self.entry_price.get().strip()

        if not name or not qty.isdigit() or not cost.isdigit() or not price.isdigit():
            self.lbl_msg.configure(text="❌ 請檢查名稱，且數量與價格須為數字！", text_color="red")
            return

        success, msg = database.add_inventory(name, cat, int(qty), unit, int(cost), int(price))
        if success:
            self.lbl_msg.configure(text=msg, text_color="green")
            self.entry_name.delete(0, 'end'); self.entry_qty.delete(0, 'end')
            self.entry_cost.delete(0, 'end'); self.entry_price.delete(0, 'end')
            self.refresh_inventory_list()
        else:
            self.lbl_msg.configure(text=msg, text_color="red")

    def open_restock_popup(self, part_id, part_name):
        """開啟專門用來『進貨』的彈出視窗"""
        popup = ctk.CTkToplevel(self)
        popup.attributes('-alpha', 0.0)
        popup.title("📦 零件進貨")
        popup.geometry("300x250")
        popup.attributes('-topmost', True); popup.grab_set()

        ctk.CTkLabel(popup, text=f"為「{part_name}」進貨", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        
        entry_add_qty = ctk.CTkEntry(popup, placeholder_text="請輸入進貨數量", width=150)
        entry_add_qty.pack(pady=10)

        lbl_popup_msg = ctk.CTkLabel(popup, text="")
        lbl_popup_msg.pack(pady=5)

        def save_restock():
            qty = entry_add_qty.get().strip()
            if not qty.isdigit() or int(qty) <= 0:
                lbl_popup_msg.configure(text="❌ 請輸入有效的正整數", text_color="red"); return
            
            success, msg = database.restock_inventory(part_id, int(qty))
            if success:
                popup.destroy()
                self.refresh_inventory_list()
            else:
                lbl_popup_msg.configure(text=msg, text_color="red")

        ctk.CTkButton(popup, text="💾 確認進貨", fg_color="#2980B9", command=save_restock).pack(pady=10)
        popup.after(50, lambda: popup.attributes('-alpha', 1.0))

    def refresh_inventory_list(self):
        for widget in self.table_frame.winfo_children(): widget.destroy()
        
        headers = ["ID", "零件名稱", "類別", "庫存量", "單位", "成本/售價", "操作"]
        for i, text in enumerate(headers):
            ctk.CTkLabel(self.table_frame, text=text, font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=i, sticky="w", padx=10, pady=5)
            self.table_frame.grid_columnconfigure(i, weight=1)

        items = database.get_all_inventory()
        for row_idx, item in enumerate(items, start=1):
            p_id, name, cat, qty, unit, cost, price = item
            qty_color = "#FF5733" if qty < 5 else "white"

            ctk.CTkLabel(self.table_frame, text=str(p_id), font=ctk.CTkFont(size=14)).grid(row=row_idx, column=0, sticky="w", padx=10)
            ctk.CTkLabel(self.table_frame, text=name, font=ctk.CTkFont(size=14)).grid(row=row_idx, column=1, sticky="w", padx=10)
            ctk.CTkLabel(self.table_frame, text=cat, font=ctk.CTkFont(size=14)).grid(row=row_idx, column=2, sticky="w", padx=10)
            ctk.CTkLabel(self.table_frame, text=str(qty), text_color=qty_color, font=ctk.CTkFont(size=14, weight="bold")).grid(row=row_idx, column=3, sticky="w", padx=10)
            ctk.CTkLabel(self.table_frame, text=unit, font=ctk.CTkFont(size=14)).grid(row=row_idx, column=4, sticky="w", padx=10)
            ctk.CTkLabel(self.table_frame, text=f"${cost} / ${price}", font=ctk.CTkFont(size=14)).grid(row=row_idx, column=5, sticky="w", padx=10)
            
            action_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            action_frame.grid(row=row_idx, column=6, padx=10, pady=2, sticky="w")

            # 車款綁定按鈕
            ctk.CTkButton(action_frame, text="🚗 車款", width=60, font=ctk.CTkFont(size=14), fg_color="#8E44AD", hover_color="#9B59B6",
                          command=lambda pid=p_id, n=name: self.open_compatibility_popup(pid, n)).pack(side="left", padx=(0, 5))

            # 進貨按鈕
            ctk.CTkButton(action_frame, text="📦 進貨", width=60, font=ctk.CTkFont(size=14), fg_color="#27AE60", hover_color="#2ECC71",
                          command=lambda pid=p_id, n=name: self.open_restock_popup(pid, n)).pack(side="left", padx=(0, 5))
            # 刪除按鈕
            ctk.CTkButton(action_frame, text="🗑️", width=30, fg_color="darkred", 
                          command=lambda pid=p_id: self.delete_action(pid)).pack(side="left")

    def delete_action(self, part_id):
        confirm = messagebox.askyesno("⚠️ 確認刪除", "確定要刪除這筆庫存紀錄嗎？")
        if confirm:
            database.delete_inventory(part_id)
            self.refresh_inventory_list()
    
    def open_compatibility_popup(self, part_id, part_name):
        """開啟『設定通用或適用車款』的專屬彈出視窗"""
        popup = ctk.CTkToplevel(self)
        popup.attributes('-alpha', 0.0)
        popup.title("🚗 零件適配設定")
        popup.geometry("450x300")
        popup.attributes('-topmost', True); popup.grab_set()

        ctk.CTkLabel(popup, text=f"【{part_name}】適配設定", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        # 🌟 1. 通用選項打勾框
        is_universal = ctk.BooleanVar(value=False)
        
        def toggle_combos():
            # 如果打勾了「通用」，就把下面的選單反灰不給選
            state = "disabled" if is_universal.get() else "normal"
            combo_brand.configure(state=state)
            combo_model.configure(state=state)
            combo_year.configure(state=state)

        chk_univ = ctk.CTkCheckBox(popup, text="🌐 此為全車系通用零件 (如機油、水箱精)", variable=is_universal, command=toggle_combos)
        chk_univ.pack(pady=5)

        # 🌟 2. 專車專用選項
        combo_frame = ctk.CTkFrame(popup, fg_color="transparent")
        combo_frame.pack(pady=10)
        
        def update_years(model_choice):
            """連動更新年份下拉選單"""
            brand_choice = combo_brand.get()
            models = database.get_models_by_brand(brand_choice)
            year_list = [m[1] for m in models if m[0] == model_choice]
            year_list = list(dict.fromkeys(year_list)) # 去重複
            year_list.insert(0, "通用") # 預設加入通用，代表該車款全車系年份皆適用
            
            combo_year.configure(values=year_list)
            if year_list:
                combo_year.set(year_list[0])
            else:
                combo_year.set("")

        def update_models(brand_choice):
            """連動更新車型下拉選單"""
            models = database.get_models_by_brand(brand_choice)
            # 提取車型名稱並去重複，保留唯一車型
            model_list = list(dict.fromkeys([m[0] for m in models]))
            combo_model.configure(values=model_list)
            if model_list:
                combo_model.set(model_list[0])
                update_years(model_list[0]) # 🌟 同步更新年份
            else:
                combo_model.set("")
                combo_year.configure(values=[])
                combo_year.set("")

        brands = database.get_all_brands()
        combo_brand = ctk.CTkComboBox(combo_frame, values=brands, width=120, command=update_models)
        combo_brand.pack(side="left", padx=5)
        
        combo_model = ctk.CTkComboBox(combo_frame, values=[], width=120, command=update_years)
        combo_model.pack(side="left", padx=5)

        combo_year = ctk.CTkComboBox(combo_frame, values=[], width=90)
        combo_year.pack(side="left", padx=5)

        if brands: 
            combo_brand.set(brands[0])
            update_models(brands[0])

        lbl_msg = ctk.CTkLabel(popup, text="")
        
        def save_comp():
            b, m, y = combo_brand.get().strip(), combo_model.get().strip(), combo_year.get().strip()
            success, msg = database.set_part_compatibility(part_id, b, m, y, is_universal.get())
            if success:
                lbl_msg.configure(text=msg, text_color="green")
                popup.after(800, popup.destroy) # 成功後自動關閉
            else:
                lbl_msg.configure(text=msg, text_color="red")

        ctk.CTkButton(popup, text="💾 儲存綁定", font=ctk.CTkFont(size=14), fg_color="#2980B9", command=save_comp).pack(pady=10)
        lbl_msg.pack()
        popup.after(50, lambda: popup.attributes('-alpha', 1.0))