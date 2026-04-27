import customtkinter as ctk
import database

class VehiclePartsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=10)
        self.setup_ui()
        self.refresh_brands()

    def setup_ui(self):
        ctk.CTkLabel(self, text="🔍 車型專屬零件導覽", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)

        # --- 區塊 1：在這裡新增車型與年份 ---
        add_frame = ctk.CTkFrame(self)
        add_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(add_frame, text="➕ 新增車款主檔:", font=ctk.CTkFont(size=16)).grid(row=0, column=0, padx=10, pady=10)
        
        self.entry_new_brand = ctk.CTkEntry(add_frame, placeholder_text="品牌 (例: TOYOTA)", width=120)
        self.entry_new_brand.grid(row=0, column=1, padx=5, pady=10)
        self.entry_new_model = ctk.CTkEntry(add_frame, placeholder_text="車型 (例: ALTIS)", width=120)
        self.entry_new_model.grid(row=0, column=2, padx=5, pady=10)
        self.entry_new_year = ctk.CTkEntry(add_frame, placeholder_text="年份 (例: 2024)", width=80)
        self.entry_new_year.grid(row=0, column=3, padx=5, pady=10)
        
        ctk.CTkButton(add_frame, text="💾 儲存車款", width=100, font=ctk.CTkFont(size=14), command=self.add_car_model).grid(row=0, column=4, padx=10, pady=10)
        self.lbl_add_msg = ctk.CTkLabel(add_frame, text="")
        self.lbl_add_msg.grid(row=0, column=5, padx=5, pady=10)

        ctk.CTkFrame(self, height=2, fg_color="gray").pack(fill="x", padx=20, pady=10)

        # --- 區塊 2：三層式下拉查詢 ---
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(search_frame, text="1. 選擇品牌:", font=ctk.CTkFont(size=16)).pack(side="left", padx=5)
        self.combo_brand = ctk.CTkComboBox(search_frame, values=[], command=self.on_brand_select, width=120)
        self.combo_brand.pack(side="left", padx=5)

        ctk.CTkLabel(search_frame, text="2. 選擇車型:", font=ctk.CTkFont(size=16)).pack(side="left", padx=10)
        self.combo_model = ctk.CTkComboBox(search_frame, values=[], width=150)
        self.combo_model.pack(side="left", padx=5)

        # --- 區塊 3：點選部件分類 ---
        cat_frame = ctk.CTkFrame(self, fg_color="transparent")
        cat_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(cat_frame, text="3. 點選部件看零件:", font=ctk.CTkFont(size=16)).pack(side="left", padx=5)
        
        for cat in ["油品", "耗材", "輪胎", "電瓶", "改裝品", "其他"]:
            ctk.CTkButton(cat_frame, text=cat, width=80, font=ctk.CTkFont(size=14), fg_color="#8E44AD", hover_color="#9B59B6",
                          command=lambda c=cat: self.show_parts(c)).pack(side="left", padx=5)

        # --- 結果顯示區 ---
        self.result_frame = ctk.CTkScrollableFrame(self)
        self.result_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def add_car_model(self):
        b, m, y = self.entry_new_brand.get().strip(), self.entry_new_model.get().strip(), self.entry_new_year.get().strip()
        if not b or not m or not y:
            self.lbl_add_msg.configure(text="❌ 請填寫完整", text_color="red"); return
        success, msg = database.add_vehicle_model(b, m, y)
        self.lbl_add_msg.configure(text=msg, text_color="green" if success else "red")
        if success:
            self.entry_new_brand.delete(0, 'end'); self.entry_new_model.delete(0, 'end'); self.entry_new_year.delete(0, 'end')
            self.refresh_brands()

    def refresh_brands(self):
        brands = database.get_all_brands()
        self.combo_brand.configure(values=brands)
        if brands: 
            self.combo_brand.set(brands[0])
            self.on_brand_select(brands[0])

    def on_brand_select(self, brand):
        models = database.get_models_by_brand(brand)
        model_strs = [f"{m[0]} ({m[1]})" for m in models] # 顯示成: ALTIS (2024)
        self.combo_model.configure(values=model_strs)
        if model_strs: self.combo_model.set(model_strs[0])
        else: self.combo_model.set("")

    def show_parts(self, category):
        for w in self.result_frame.winfo_children(): w.destroy()
        brand, model_raw = self.combo_brand.get(), self.combo_model.get()
        if not brand or not model_raw: return
        
        model = model_raw.split(" (")[0] # 只拿車型名稱
        year = model_raw.split(" (")[1].replace(")", "") # 🌟 新增：提取括號內的年份
        
        # --- 頂部操作區 ---
        action_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(action_frame, text=f"📂 {brand} {model} ({year}) - 【{category}】", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=10)
        
        btn_bind = ctk.CTkButton(action_frame, text="➕ 綁定新零件", font=ctk.CTkFont(size=14), fg_color="#27AE60", hover_color="#2ECC71", width=100, command=lambda: self.open_bind_part_popup(brand, model, year, category))
        btn_bind.pack(side="right", padx=10)

        parts = database.get_fit_parts(brand, model, year, category)
        
        if not parts:
            ctk.CTkLabel(self.result_frame, text=f"⚠️ 尚未綁定任何【{category}】的零件喔！", font=ctk.CTkFont(size=16), text_color="gray").pack(pady=20)

        for part_name, qty, unit, price, comp_brand in parts:
            row = ctk.CTkFrame(self.result_frame, fg_color="transparent")
            row.pack(fill="x", pady=8)
            
            # 區分是通用件還是專用件
            tag = "🌐 [通用]" if comp_brand == "通用" else "🚗 [專用]"
            qty_color = "#FF5733" if qty < 5 else "white"
            
            ctk.CTkLabel(row, text=f"{tag} {part_name}", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"庫存: {qty} {unit}", text_color=qty_color, font=ctk.CTkFont(size=15, weight="bold")).pack(side="right", padx=20)
            ctk.CTkLabel(row, text=f"售價: ${price}", font=ctk.CTkFont(size=15)).pack(side="right", padx=10)

    def open_bind_part_popup(self, brand, model, year, category):
        """開啟『反向綁定』彈出視窗：為目前車款挑選庫存零件"""
        popup = ctk.CTkToplevel(self)
        popup.attributes('-alpha', 0.0)
        popup.title("➕ 綁定新零件")
        popup.geometry("450x250")
        popup.attributes('-topmost', True); popup.grab_set()

        ctk.CTkLabel(popup, text=f"為 {brand} {model} ({year})\n綁定【{category}】零件", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)

        # 只把「該分類」的庫存零件撈出來
        all_inventory = database.get_all_inventory()
        category_parts = [item for item in all_inventory if item[2] == category]

        if not category_parts:
            ctk.CTkLabel(popup, text=f"庫存中沒有【{category}】的零件！請先至庫存管理新增。", text_color="red").pack(pady=20)
            popup.after(50, lambda: popup.attributes('-alpha', 1.0))
            return

        # 製作 下拉選單顯示字串 -> part_id 的對照表
        part_dict = {f"{item[1]} (庫存: {item[3]} {item[4]})": item[0] for item in category_parts}
        part_names = list(part_dict.keys())

        combo_parts = ctk.CTkComboBox(popup, values=part_names, width=280)
        combo_parts.pack(pady=10)
        if part_names: combo_parts.set(part_names[0])

        lbl_msg = ctk.CTkLabel(popup, text="")
        
        def save_binding():
            selected = combo_parts.get()
            if not selected: return
            part_id = part_dict[selected]
            
            success, msg = database.set_part_compatibility(part_id, brand, model, year, False)
            if success:
                lbl_msg.configure(text=msg, text_color="green")
                popup.after(800, popup.destroy)
                self.show_parts(category) # 🌟 綁定成功後，自動刷新底下的清單！
            else:
                lbl_msg.configure(text=msg, text_color="red")

        ctk.CTkButton(popup, text="💾 儲存綁定", font=ctk.CTkFont(size=14), fg_color="#2980B9", command=save_binding).pack(pady=10)
        lbl_msg.pack(pady=5)
        
        popup.after(50, lambda: popup.attributes('-alpha', 1.0))