import customtkinter as ctk
import database
from datetime import datetime #用來自動取得今天日期
from tkinter import messagebox # 🌟 新增：用來顯示刪除警告視窗

class OrdersPage(ctk.CTkFrame):
    def __init__(self, master):
        # 初始化這個 Frame
        super().__init__(master, corner_radius=10)
        
        # 1. 畫出 UI
        self.setup_ui()
        
        # 2. 載入資料
        self.refresh_order_list()

    def setup_ui(self):
        """專門負責畫出維修工單頁面的介面"""
        ctk.CTkLabel(self, text="📝 維修工單系統", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 10))
        
        # 🛠️ 核心改動：主畫面現在只留這顆按鈕，點擊就開啟彈出視窗！
        self.btn_open_order = ctk.CTkButton(self, text="➕ 新增維修工單", font=ctk.CTkFont(weight="bold"), fg_color="#27AE60", hover_color="#2ECC71", height=40, command=self.open_order_window)
        self.btn_open_order.pack(pady=10)

        # ----------- 歷史紀錄 -----------
        ctk.CTkFrame(self, height=2, fg_color="gray").pack(fill="x", padx=20, pady=10)

        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=0)
        
        ctk.CTkLabel(search_frame, text="📋 歷史維修紀錄", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="搜車牌/車主/電話/項目...", width=120)
        self.entry_search.pack(side="left", padx=(20, 10))
        self.entry_search.bind("<Return>", lambda event: self.search_orders())
        self.btn_search = ctk.CTkButton(search_frame, text="🔍 搜尋", width=60, command=self.search_orders)
        self.btn_search.pack(side="left")
        self.btn_clear = ctk.CTkButton(search_frame, text="✖️ 顯示全部", width=80, fg_color="gray", command=self.refresh_order_list)
        self.btn_clear.pack(side="left", padx=10)

        self.table_frame_order = ctk.CTkScrollableFrame(self)
        self.table_frame_order.pack(fill="both", expand=True, padx=20, pady=(5, 20))

    # ==================== 邏輯功能區 ====================
    # 🌟 修改：加入 order_id=None 讓這個彈窗能同時處理「新增」與「修改」
    def open_order_window(self, order_id=None):
        """開啟完整的『新增/修改工單』彈出視窗"""
        # 1. 建立彈出視窗
        self.order_popup = ctk.CTkToplevel(self)
        self.order_popup.attributes('-alpha', 0.0) # 🌟 隱形魔法防閃爍
        
        # 根據模式決定標題
        self.order_popup.title("新增維修工單" if order_id is None else f"✏️ 修改工單 #{order_id}")
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
        self.entry_search_plate.bind("<KeyRelease>", self.show_plate_dropdown) 
        self.plate_dropdown_frame = ctk.CTkScrollableFrame(self.order_popup, height=120)

        self.entry_mileage = ctk.CTkEntry(info_frame, placeholder_text="進廠里程數", width=120)
        self.entry_mileage.grid(row=0, column=2, padx=10, pady=10)

        # --- 📦 區塊 2：零件購物車輸入 ---
        item_frame = ctk.CTkFrame(self.order_popup)
        item_frame.pack(fill="x", padx=20, pady=5)

        # 🌟 1. 新增：大分類下拉選單
        self.combo_item_cat = ctk.CTkComboBox(item_frame, values=["🛠️ 服務工資", "油品", "耗材", "輪胎", "電瓶", "其他"], width=100, command=self.change_category)
        self.combo_item_cat.grid(row=0, column=0, padx=(10, 5), pady=10)

        # 🌟 2. 改良：同時抓取「工資」與「實體庫存」，準備給後面的智慧選單過濾用
        self.services_data = {s[1]: {"price": s[2], "unit": "次"} for s in database.get_all_services()}
        self.inventory_data = database.get_all_inventory() # 抓取庫存所有品牌零件
        
        self.entry_item_name = ctk.CTkEntry(item_frame, placeholder_text="輸入名稱或品牌", width=150)
        self.entry_item_name.grid(row=0, column=1, padx=5, pady=10)
        self.entry_item_name.bind("<KeyRelease>", self.show_item_dropdown)
        self.item_dropdown_frame = ctk.CTkScrollableFrame(self.order_popup, height=120)

        self.entry_item_qty = ctk.CTkEntry(item_frame, placeholder_text="數量", width=50)
        self.entry_item_qty.grid(row=0, column=2, padx=5, pady=10)
        
        self.combo_item_unit = ctk.CTkComboBox(item_frame, values=["pc", "L", "瓶", "條", "set", "次"], width=70)
        self.combo_item_unit.grid(row=0, column=3, padx=5, pady=10)
        
        self.entry_item_price = ctk.CTkEntry(item_frame, placeholder_text="單價", width=80)
        self.entry_item_price.grid(row=0, column=4, padx=5, pady=10)
        
        self.btn_add_item = ctk.CTkButton(item_frame, text="➕ 加入", width=60, fg_color="#2980B9", command=self.add_to_cart)
        self.btn_add_item.grid(row=0, column=5, padx=10, pady=10)

       # --- 📦 區塊 3：購物車清單 ---
        self.cart_frame = ctk.CTkScrollableFrame(self.order_popup, height=150)
        self.cart_frame.pack(fill="both", expand=True, padx=20, pady=5)

        # ================= 🛡️ 絕招：強制釘選在底部的區塊 =================
        bottom_frame = ctk.CTkFrame(self.order_popup, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", pady=20) # side="bottom" 讓它死死貼在視窗最下方！

        # 🌟 如果是修改模式，立刻從資料庫拿舊資料填入
        if order_id is not None:
            order_info, items = database.get_order_details(order_id)
            self.entry_date.delete(0, 'end'); self.entry_date.insert(0, order_info[0])
            self.entry_search_plate.delete(0, 'end'); self.entry_search_plate.insert(0, order_info[1])
            self.entry_mileage.delete(0, 'end'); self.entry_mileage.insert(0, str(order_info[2]))
            self.current_order_items = items
            
            btn_text = "💾 儲存修改"
            btn_color = "#D35400"
        else:
            btn_text = "💾 儲存並送出"
            btn_color = "#E67E22"

        # 注意：這裡呼叫 save_order 時，要把 order_id 傳進去
        self.btn_save_order = ctk.CTkButton(bottom_frame, text=btn_text, font=ctk.CTkFont(weight="bold"), fg_color=btn_color, height=40, command=lambda: self.save_order(order_id))
        self.btn_save_order.pack(pady=5)

        self.lbl_msg_order = ctk.CTkLabel(bottom_frame, text="")
        self.lbl_msg_order.pack()

        # 🌟 載入舊購物車畫面
        if order_id is not None:
            self.redraw_cart() 

        self.order_popup.after(50, lambda: self.order_popup.attributes('-alpha', 1.0))

    def show_plate_dropdown(self, event):
        """根據打字內容，顯示並過濾浮動選單"""
        typed_text = self.entry_search_plate.get().strip().upper()
        all_plates = database.get_all_plate_numbers()

        # 情況 A：如果輸入框沒半個字，就把選單藏起來
        if not typed_text:
            self.plate_dropdown_frame.place_forget()
            return

        # 找出符合打字內容的車牌
        filtered = [p for p in all_plates if typed_text in p]

        # 清空舊的按鈕
        for widget in self.plate_dropdown_frame.winfo_children(): 
            widget.destroy()

        # 情況 B：如果有找到符合的車牌，就把選單秀出來
        if filtered:
            # 魔法指令 place()：讓選單死死貼在輸入框的正下方
            self.plate_dropdown_frame.place(in_=self.entry_search_plate, rely=1.0, relx=0, y=2, relwidth=1.0)
            self.plate_dropdown_frame.lift()
            
            # 把車牌變成按鈕塞進選單
            for p in filtered:
                btn = ctk.CTkButton(self.plate_dropdown_frame, text=p, fg_color="transparent", hover_color="gray", anchor="w",
                                    command=lambda plate=p: self.pick_plate(plate))
                btn.pack(fill="x", padx=5, pady=2)
        else:
            self.plate_dropdown_frame.place_forget()
    
    def pick_plate(self, plate):
        """當點擊選單裡的車牌時執行的動作"""
        self.entry_search_plate.delete(0, 'end') # 清空輸入框
        self.entry_search_plate.insert(0, plate) # 填入完整車牌
        self.plate_dropdown_frame.place_forget()       # 收合選單
    
    def change_category(self, choice):
        """🌟 當老闆切換大分類 (例如切到『油品』) 時，清空後面的輸入框"""
        self.entry_item_name.delete(0, 'end')
        self.entry_item_price.delete(0, 'end')
        self.item_dropdown_frame.place_forget()

    def show_item_dropdown(self, event):
        """🌟 根據『大分類』與『打字內容』來精準過濾選單"""
        selected_cat = self.combo_item_cat.get()
        typed_text = self.entry_item_name.get().strip()
        
        if not typed_text:
            self.item_dropdown_frame.place_forget()
            return

        # 核心邏輯：只挑出符合該分類的項目
        filtered_items = []
        if selected_cat == "🛠️ 服務工資":
            filtered_items = [name for name in self.services_data.keys() if typed_text in name]
        else:
            # 如果是實體零件，去 inventory_data 裡面比對 分類(item[2]) 與 品牌名稱(item[1])
            filtered_items = [item[1] for item in self.inventory_data if item[2] == selected_cat and typed_text in item[1]]

        for widget in self.item_dropdown_frame.winfo_children(): 
            widget.destroy()

        if filtered_items:
            self.item_dropdown_frame.place(in_=self.entry_item_name, rely=1.0, relx=0, y=2, relwidth=1.0)
            self.item_dropdown_frame.lift()
            for item in filtered_items:
                btn = ctk.CTkButton(self.item_dropdown_frame, text=item, fg_color="transparent", hover_color="gray", anchor="w",
                                    command=lambda i=item: self.pick_item(i))
                btn.pack(fill="x", padx=5, pady=2)
        else:
            self.item_dropdown_frame.place_forget()

    def auto_fill_price(self, choice):
        """🌟 智慧帶入：連『單位』都一起自動幫你填好！"""
        selected_cat = self.combo_item_cat.get()
        
        if selected_cat == "🛠️ 服務工資" and choice in self.services_data:
            self.entry_item_price.delete(0, 'end')
            self.entry_item_price.insert(0, str(self.services_data[choice]["price"]))
            self.combo_item_unit.set(self.services_data[choice]["unit"])
        else:
            # 遍歷庫存資料，把 售價(item[6]) 和 單位(item[4]) 自動填入畫面
            for item in self.inventory_data:
                if item[1] == choice: 
                    self.entry_item_price.delete(0, 'end')
                    self.entry_item_price.insert(0, str(item[6])) 
                    self.combo_item_unit.set(item[4]) 
                    break

    def pick_item(self, item):
        """當點擊選單裡的維修項目時執行的動作"""
        self.entry_item_name.delete(0, 'end') 
        self.entry_item_name.insert(0, item)  # 填入完整項目名稱
        self.item_dropdown_frame.place_forget() # 收合選單
        
        # 🌟 靈魂連動：選完名字後，立刻呼叫自動填價函式！
        self.auto_fill_price(item)

    def add_to_cart(self):
        """把項目加入彈出視窗的暫存購物車"""
        name = self.entry_item_name.get().strip()
        qty = self.entry_item_qty.get().strip()
        unit = self.combo_item_unit.get()
        price = self.entry_item_price.get().strip()

        if not name or not qty.isdigit() or not price.isdigit():
            self.lbl_msg_order.configure(text="❌ 請填寫完整，且數量單價須為數字！", text_color="red")
            return

        # 把項目塞進暫存清單
        item_data = {"name": name, "qty": int(qty), "unit": unit, "price": int(price)}
        self.current_order_items.append(item_data)

        # 清空輸入框
        self.entry_item_name.delete(0, 'end')
        self.entry_item_qty.delete(0, 'end')
        self.entry_item_price.delete(0, 'end')

        self.lbl_msg_order.configure(text="")
        self.redraw_cart() # 🌟 改呼叫這個專門畫購物車的函式

    def redraw_cart(self):
        """🌟 把購物車裡的東西畫出來，並附上修改與刪除按鈕"""
        for w in self.cart_frame.winfo_children(): w.destroy()
        
        for idx, item in enumerate(self.current_order_items):
            subtotal = item["qty"] * item["price"]
            row_frame = ctk.CTkFrame(self.cart_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=10, pady=2)
            
            ctk.CTkLabel(row_frame, text=f"✅ {item['name']} x{item['qty']}{item['unit']} | 單價: ${item['price']} | 小計: ${subtotal}").pack(side="left")
            
            # 建立一個小容器來放兩個按鈕
            action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_frame.pack(side="right")

            # ✏️ 修改按鈕：點擊後呼叫 edit_cart_item
            ctk.CTkButton(action_frame, text="✏️", width=30, fg_color="#F39C12", hover_color="#D68910", height=20, 
                          command=lambda i=idx: self.edit_cart_item(i)).pack(side="left", padx=(0, 5))

            # ❌ 刪除按鈕
            ctk.CTkButton(action_frame, text="❌", width=30, fg_color="darkred", height=20, 
                          command=lambda i=idx: self.remove_from_cart(i)).pack(side="left")

    def remove_from_cart(self, index):
        """🌟 從購物車中移除某個項目 (防呆)"""
        self.current_order_items.pop(index)
        self.redraw_cart() # 刪掉後重新畫一次畫面
    
    def edit_cart_item(self, index):
        """🌟 提領修改邏輯：把購物車內的項目拿出來，放回上方輸入框供修改"""
        # 1. 取得老闆想修改的那筆資料
        item = self.current_order_items[index]
        
        # 2. 將資料一一填回上方的輸入框
        self.entry_item_name.delete(0, 'end')
        self.entry_item_name.insert(0, item['name'])
        
        self.entry_item_qty.delete(0, 'end')
        self.entry_item_qty.insert(0, str(item['qty']))
        
        self.combo_item_unit.set(item['unit'])
        
        self.entry_item_price.delete(0, 'end')
        self.entry_item_price.insert(0, str(item['price']))
        
        # 3. 從購物車中移除該項目 (等老闆改完數量，再自己按「➕ 加入」放回去)
        self.current_order_items.pop(index)
        self.redraw_cart() # 重新畫一次購物車

    def save_order(self, order_id=None):
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

        # 🌟 判斷現在是新增模式還是修改模式，呼叫不同的資料庫指令
        if order_id is None:
            success, msg = database.add_repair_order(plate, date, final_mileage, self.current_order_items)
        else:
            success, msg = database.update_repair_order(order_id, plate, date, final_mileage, self.current_order_items)
        
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
        
        # 🌟 表頭新增「訂單號」與「操作」
        headers = ["訂單號", "日期", "車牌號碼", "里程數", "維修項目", "總金額", "操作"]
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
            order_id = order[0]       # 第一個元素是 ID
            display_data = order[1:]  # 剩下的用來畫文字
            
            # 1. 畫 ID 欄位
            ctk.CTkLabel(self.table_frame_order, text=f"#{order_id}").grid(row=row_idx, column=0, sticky="w", padx=15, pady=5)

            # 2. 畫其他的文字 (日期、車牌...)
            for col_idx, value in enumerate(display_data):
                display_text = f"${value}" if col_idx == 4 else str(value) # 總金額在 display_data 的 index 4
                ctk.CTkLabel(self.table_frame_order, text=display_text).grid(row=row_idx, column=col_idx+1, sticky="w", padx=15, pady=5)       
            
            # 3. 🌟 畫操作按鈕 (修改/刪除)
            action_frame = ctk.CTkFrame(self.table_frame_order, fg_color="transparent")
            action_frame.grid(row=row_idx, column=6, padx=10, pady=2, sticky="w")

            btn_edit = ctk.CTkButton(action_frame, text="✏️ 修改", width=50, fg_color="#F39C12", hover_color="#D68910",
                                     command=lambda oid=order_id: self.open_order_window(oid))
            btn_edit.pack(side="left", padx=(0, 5))
            
            btn_del = ctk.CTkButton(action_frame, text="🗑️ 刪除", width=60, fg_color="darkred", hover_color="red",
                                    command=lambda oid=order_id: self.delete_order_action(oid))
            btn_del.pack(side="left")

    def delete_order_action(self, order_id):
        """🌟 刪除工單與確認視窗"""
        confirm = messagebox.askyesno("⚠️ 確認刪除", f"確定要徹底刪除工單 #{order_id} 嗎？\n(注意：明細也會一併刪除，且無法復原！)")
        if confirm:
            database.delete_repair_order(order_id)
            self.refresh_order_list()