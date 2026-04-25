import sqlite3
import os

DB_NAME = "repair_system.db"

def init_db():
    """初始化資料庫與資料表"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # ================= 1. 建立表格區 =================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT UNIQUE NOT NULL,
            owner_name TEXT,
            phone TEXT,
            brand TEXT,
            model TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Repair_Orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            date TEXT NOT NULL,
            mileage INTEGER,
            total_amount INTEGER,
            notes TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES Vehicles(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Order_Items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            item_name TEXT,
            quantity INTEGER,
            unit TEXT DEFAULT 'pc',
            unit_price INTEGER,
            subtotal INTEGER,
            FOREIGN KEY (order_id) REFERENCES Repair_Orders(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT UNIQUE NOT NULL,
            default_price INTEGER
        )
    ''')

    # 🌟 NEW: 建立全新的「實體庫存」資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_name TEXT UNIQUE NOT NULL,
            category TEXT,
            stock_qty INTEGER DEFAULT 0,
            unit TEXT DEFAULT 'pc',
            cost_price INTEGER DEFAULT 0,
            sell_price INTEGER DEFAULT 0
        )
    ''')

    # ================= 2. 播種區 (Seeding Data) =================
    cursor.execute('SELECT COUNT(*) FROM Services')
    if cursor.fetchone()[0] == 0:
        default_services = [
            ('一般保養工資', 300),
            ('冷氣系統檢修', 800),
            ('底盤異音檢查', 500)
        ]
        cursor.executemany('INSERT INTO Services (service_name, default_price) VALUES (?, ?)', default_services)

    # 🌟 NEW: 幫庫存表加入一些預設的測試零件
    cursor.execute('SELECT COUNT(*) FROM Inventory')
    if cursor.fetchone()[0] == 0:
        default_parts = [
            ('機油 (10W-40)', '油品', 50, '瓶', 200, 500),
            ('前輪煞車皮', '耗材', 20, '組', 600, 1200),
            ('輪胎 (15吋)', '輪胎', 16, '條', 1200, 2000)
        ]
        cursor.executemany('INSERT INTO Inventory (part_name, category, stock_qty, unit, cost_price, sell_price) VALUES (?, ?, ?, ?, ?, ?)', default_parts)

    cursor.execute('SELECT COUNT(*) FROM Vehicles')
    if cursor.fetchone()[0] == 0:
        test_vehicles = [
            ('ABC-1234', '王大明', '0912-345-678', 'TOYOTA', 'Altis'),
            ('XYZ-9876', '李小華', '0987-654-321', 'HONDA', 'CR-V')
        ]
        cursor.executemany('INSERT INTO Vehicles (plate_number, owner_name, phone, brand, model) VALUES (?, ?, ?, ?, ?)', test_vehicles)

        test_orders = [
            (1, '2026-04-20', 55000, 1550, '五萬公里定保'), 
            (2, '2026-04-22', 120000, 2400, '煞車異音檢查')  
        ]
        cursor.executemany('INSERT INTO Repair_Orders (vehicle_id, date, mileage, total_amount, notes) VALUES (?, ?, ?, ?, ?)', test_orders)

        test_items = [
            (1, '機油 (10W-40)', 2, '瓶', 500, 1000),
            (1, '一般保養工資', 1, '次', 300, 300),
            (1, '機油濾清器', 1, '個', 250, 250),
            (2, '前輪煞車皮', 2, '組', 1200, 2400)
        ]
        cursor.executemany('INSERT INTO Order_Items (order_id, item_name, quantity, unit, unit_price, subtotal) VALUES (?, ?, ?, ?, ?, ?)', test_items)

    conn.commit()
    conn.close()

# ================= 客戶信息專用功能 =================
def add_vehicle(plate_number, owner_name, phone, brand, model):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Vehicles (plate_number, owner_name, phone, brand, model) VALUES (?, ?, ?, ?, ?)', (plate_number, owner_name, phone, brand, model))
        conn.commit()
        return True, "✅ 新增車輛成功！"
    except sqlite3.IntegrityError: return False, "❌ 車牌號碼已存在，請檢查！"
    finally: conn.close()

def get_all_vehicles():
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute('SELECT plate_number, owner_name, phone, brand, model FROM Vehicles ORDER BY id DESC')
    rows = cursor.fetchall(); conn.close()
    return rows

def search_vehicles_by_keyword(search_keyword):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    keyword = f"%{search_keyword}%"
    cursor.execute('SELECT id, plate_number, owner_name, phone, brand, model FROM Vehicles WHERE plate_number LIKE ? OR owner_name LIKE ? OR phone LIKE ? OR brand LIKE ? OR model LIKE ? ORDER BY id DESC', (keyword, keyword, keyword, keyword, keyword))
    rows = cursor.fetchall(); conn.close()
    return rows

def update_vehicle(old_plate, new_plate, owner_name, phone, brand, model):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute('UPDATE Vehicles SET plate_number = ?, owner_name = ?, phone = ?, brand = ?, model = ? WHERE plate_number = ?', (new_plate, owner_name, phone, brand, model, old_plate))
        conn.commit(); return True, "✅ 客戶資料更新成功！"
    except sqlite3.IntegrityError: return False, "❌ 新的車牌號碼已與其他車輛重複！"
    except Exception as e: return False, f"❌ 發生錯誤: {e}"
    finally: conn.close()

def delete_vehicle(plate_number):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute('DELETE FROM Vehicles WHERE plate_number = ?', (plate_number,))
    conn.commit(); conn.close()
    return True, f"✅ 已成功刪除車牌 {plate_number} 的資料！"

# ==================== 維修工單專用功能 ====================
def get_all_plate_numbers():
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute('SELECT plate_number FROM Vehicles ORDER BY plate_number ASC')
    rows = cursor.fetchall(); conn.close()
    return [row[0] for row in rows]

def add_repair_order(plate_number, date, mileage, items_list):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute('SELECT id FROM Vehicles WHERE plate_number = ?', (plate_number,))
        vehicle = cursor.fetchone()
        if not vehicle: return False, "找不到此車牌！"
        total_amount = sum(item["qty"] * item["price"] for item in items_list)
        cursor.execute('INSERT INTO Repair_Orders (vehicle_id, date, mileage, total_amount, notes) VALUES (?, ?, ?, ?, ?)', (vehicle[0], date, mileage, total_amount, ""))
        order_id = cursor.lastrowid 
        for item in items_list:
            subtotal = item["qty"] * item["price"]
            cursor.execute('INSERT INTO Order_Items (order_id, item_name, quantity, unit, unit_price, subtotal) VALUES (?, ?, ?, ?, ?, ?)', (order_id, item["name"], item["qty"], item.get("unit", "pc"), item["price"], subtotal))
        conn.commit()
        return True, "✅ 工單新增成功！"
    except Exception as e: conn.rollback(); return False, f"❌ 發生錯誤: {e}"
    finally: conn.close()

def get_all_orders():
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute('''
        SELECT r.id, r.date, v.plate_number, r.mileage, GROUP_CONCAT(i.item_name || ' (x' || i.quantity || i.unit || ')', '、'), r.total_amount
        FROM Repair_Orders r JOIN Vehicles v ON r.vehicle_id = v.id LEFT JOIN Order_Items i ON r.id = i.order_id
        GROUP BY r.id ORDER BY r.id DESC
    ''')
    rows = cursor.fetchall(); conn.close()
    return rows

def search_orders_by_keyword(search_keyword):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    keyword = f"%{search_keyword}%"
    cursor.execute('''
        SELECT r.id, r.date, v.plate_number, r.mileage, GROUP_CONCAT(i.item_name || ' (x' || i.quantity || i.unit || ')', '、'), r.total_amount
        FROM Repair_Orders r JOIN Vehicles v ON r.vehicle_id = v.id LEFT JOIN Order_Items i ON r.id = i.order_id
        WHERE r.id IN (SELECT DISTINCT r2.id FROM Repair_Orders r2 JOIN Vehicles v2 ON r2.vehicle_id = v2.id LEFT JOIN Order_Items i2 ON r2.id = i2.order_id
        WHERE v2.plate_number LIKE ? OR v2.owner_name LIKE ? OR v2.phone LIKE ? OR i2.item_name LIKE ?)
        GROUP BY r.id ORDER BY r.date DESC
    ''', (keyword, keyword, keyword, keyword))
    rows = cursor.fetchall(); conn.close()
    return rows

def get_order_details(order_id):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute('SELECT r.date, v.plate_number, r.mileage FROM Repair_Orders r JOIN Vehicles v ON r.vehicle_id = v.id WHERE r.id = ?', (order_id,))
    order_info = cursor.fetchone()
    cursor.execute('SELECT item_name, quantity, unit, unit_price FROM Order_Items WHERE order_id = ?', (order_id,))
    items = cursor.fetchall(); conn.close()
    return order_info, [{"name": i[0], "qty": i[1], "unit": i[2], "price": i[3]} for i in items]

def update_repair_order(order_id, plate_number, date, mileage, items_list):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute('SELECT id FROM Vehicles WHERE plate_number = ?', (plate_number,))
        vehicle = cursor.fetchone()
        if not vehicle: return False, "找不到此車牌！"
        total_amount = sum(item["qty"] * item["price"] for item in items_list)
        cursor.execute('UPDATE Repair_Orders SET vehicle_id = ?, date = ?, mileage = ?, total_amount = ? WHERE id = ?', (vehicle[0], date, mileage, total_amount, order_id))
        cursor.execute('DELETE FROM Order_Items WHERE order_id = ?', (order_id,))
        for item in items_list:
            subtotal = item["qty"] * item["price"]
            cursor.execute('INSERT INTO Order_Items (order_id, item_name, quantity, unit, unit_price, subtotal) VALUES (?, ?, ?, ?, ?, ?)', (order_id, item["name"], item["qty"], item.get("unit", "pc"), item["price"], subtotal))
        conn.commit(); return True, "✅ 工單修改成功！"
    except Exception as e: conn.rollback(); return False, f"❌ 修改失敗: {e}"
    finally: conn.close()

def delete_repair_order(order_id):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Order_Items WHERE order_id = ?', (order_id,))
        cursor.execute('DELETE FROM Repair_Orders WHERE id = ?', (order_id,))
        conn.commit(); return True, f"✅ 已成功刪除工單 #{order_id}！"
    except Exception as e: return False, f"❌ 刪除失敗: {e}"
    finally: conn.close()

# ================= ⚙️ Phase 3：工資服務管理 (無形) =================
def add_service(name, price):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Services (service_name, default_price) VALUES (?, ?)', (name, price))
        conn.commit(); return True, "✅ 項目新增成功！"
    except sqlite3.IntegrityError: return False, "❌ 名稱已存在！"
    finally: conn.close()

def get_all_services():
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute('SELECT id, service_name, default_price FROM Services ORDER BY id DESC')
    rows = cursor.fetchall(); conn.close()
    return rows

def update_service(service_id, new_name, new_price):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute('UPDATE Services SET service_name = ?, default_price = ? WHERE id = ?', (new_name, new_price, service_id))
        conn.commit(); return True, "✅ 更新成功！"
    except sqlite3.IntegrityError: return False, "❌ 名稱重複！"
    finally: conn.close()

def delete_service(service_id):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute('DELETE FROM Services WHERE id = ?', (service_id,)); conn.commit(); conn.close()

# ================= 📦 NEW Phase 5：庫存與貨物管理 =================
def add_inventory(name, category, qty, unit, cost, price):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Inventory (part_name, category, stock_qty, unit, cost_price, sell_price) VALUES (?, ?, ?, ?, ?, ?)', (name, category, qty, unit, cost, price))
        conn.commit(); return True, "✅ 庫存零件新增成功！"
    except sqlite3.IntegrityError: return False, "❌ 零件名稱已存在！"
    finally: conn.close()

def get_all_inventory():
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute('SELECT id, part_name, category, stock_qty, unit, cost_price, sell_price FROM Inventory ORDER BY id DESC')
    rows = cursor.fetchall(); conn.close()
    return rows

def update_inventory(part_id, name, category, qty, unit, cost, price):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute('UPDATE Inventory SET part_name=?, category=?, stock_qty=?, unit=?, cost_price=?, sell_price=? WHERE id=?', (name, category, qty, unit, cost, price, part_id))
        conn.commit(); return True, "✅ 更新成功！"
    except sqlite3.IntegrityError: return False, "❌ 零件名稱重複！"
    finally: conn.close()

def restock_inventory(part_id, added_qty):
    """專門用來處理進貨 (只增加數量)"""
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute('UPDATE Inventory SET stock_qty = stock_qty + ? WHERE id = ?', (added_qty, part_id))
        conn.commit(); return True, f"✅ 成功進貨 {added_qty} 個單位！"
    except Exception as e: return False, f"❌ 進貨失敗: {e}"
    finally: conn.close()

def delete_inventory(part_id):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute('DELETE FROM Inventory WHERE id = ?', (part_id,)); conn.commit(); conn.close()

if __name__ == "__main__":
    init_db()
    print("資料庫設定完成。")