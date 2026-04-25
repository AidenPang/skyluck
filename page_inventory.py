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
        row1.pack(fill="x", padx=10, pady=(15, 5))
        
        self.entry_name = ctk.CTkEntry(row1, placeholder_text="零件名稱 (必填)", width=200)
        self.entry_name.pack(side="left", padx=5)
        
        self.combo_category = ctk.CTkComboBox(row1, values=["油品", "耗材", "輪胎", "電瓶", "改裝品", "其他"], width=100)
        self.combo_category.pack(side="left", padx=5)
        self.combo_category.set("耗材")

        self.entry_qty = ctk.CTkEntry(row1, placeholder_text="初始庫存量", width=100)
        self.entry_qty.pack(side="left", padx=5)
        
        self.combo_unit = ctk.CTkComboBox(row1, values=["個", "瓶", "條", "組", "L", "pc"], width=80)
        self.combo_unit.pack(side="left", padx=5)
        self.combo_unit.set("個")

        # 第二排輸入
        row2 = ctk.CTkFrame(add_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(5, 15))

        self.entry_cost = ctk.CTkEntry(row2, placeholder_text="進貨成本 ($)", width=100)
        self.entry_cost.pack(side="left", padx=5)

        self.entry_price = ctk.CTkEntry(row2, placeholder_text="預設售價 ($)", width=100)
        self.entry_price.pack(side="left", padx=5)

        self.btn_add = ctk.CTkButton(row2, text="➕ 新增入庫", fg_color="#27AE60", hover_color="#2ECC71", command=self.add_item_action)
        self.btn_add.pack(side="left", padx=20)

        self.lbl_msg = ctk.CTkLabel(row2, text="")
        self.lbl_msg.pack(side="left", padx=5)

        # --- 下半區：列表 ---
        ctk.CTkFrame(self, height=2, fg_color="gray").pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(self, text="📋 現有庫存清單", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20)

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
            ctk.CTkLabel(self.table_frame, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, sticky="w", padx=10, pady=5)
            self.table_frame.grid_columnconfigure(i, weight=1)

        items = database.get_all_inventory()
        for row_idx, item in enumerate(items, start=1):
            p_id, name, cat, qty, unit, cost, price = item
            
            # 庫存過低時，數字變紅色提醒
            qty_color = "red" if qty < 5 else "white"

            ctk.CTkLabel(self.table_frame, text=str(p_id)).grid(row=row_idx, column=0, sticky="w", padx=10)
            ctk.CTkLabel(self.table_frame, text=name).grid(row=row_idx, column=1, sticky="w", padx=10)
            ctk.CTkLabel(self.table_frame, text=cat).grid(row=row_idx, column=2, sticky="w", padx=10)
            ctk.CTkLabel(self.table_frame, text=str(qty), text_color=qty_color, font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=3, sticky="w", padx=10)
            ctk.CTkLabel(self.table_frame, text=unit).grid(row=row_idx, column=4, sticky="w", padx=10)
            ctk.CTkLabel(self.table_frame, text=f"${cost} / ${price}").grid(row=row_idx, column=5, sticky="w", padx=10)
            
            action_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            action_frame.grid(row=row_idx, column=6, padx=10, pady=2, sticky="w")

            # 進貨按鈕
            ctk.CTkButton(action_frame, text="📦 進貨", width=50, fg_color="#27AE60", hover_color="#2ECC71",
                          command=lambda pid=p_id, n=name: self.open_restock_popup(pid, n)).pack(side="left", padx=(0, 5))
            # 刪除按鈕
            ctk.CTkButton(action_frame, text="🗑️", width=30, fg_color="darkred", 
                          command=lambda pid=p_id: self.delete_action(pid)).pack(side="left")

    def delete_action(self, part_id):
        confirm = messagebox.askyesno("⚠️ 確認刪除", "確定要刪除這筆庫存紀錄嗎？")
        if confirm:
            database.delete_inventory(part_id)
            self.refresh_inventory_list()