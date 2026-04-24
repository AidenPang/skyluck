import sqlite3
import os

DB_NAME = "repair_system.db"

def init_db():
    """初始化資料庫與資料表"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # ================= 1. 建立表格區 =================
    # 1.建立車輛表
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
    
    # 2.建立工單表
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

    # 3.建立工單明細表 (用 order_id 綁定主檔)
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

    # 4. 服務與零件主檔 (價目表系統，供開單時下拉選擇)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT UNIQUE NOT NULL,
            default_price INTEGER
        )
    ''')

    # ================= 2. 播種區 (Seeding Data) =================
    
    # [播種 A]：服務與零件價目表
    cursor.execute('SELECT COUNT(*) FROM Services')
    if cursor.fetchone()[0] == 0:
        default_services = [
            ('一般保養工資', 300),
            ('機油 (10W-40)', 500),
            ('前輪煞車皮', 1200),
            ('冷氣濾網', 450),
            ('機油濾清器', 250),
            ('變速箱油', 600),
            ('輪胎 (15吋)', 2000)
        ]
        cursor.executemany('INSERT INTO Services (service_name, default_price) VALUES (?, ?)', default_services)

    # [播種 B]：客戶、車輛與工單測試資料
    cursor.execute('SELECT COUNT(*) FROM Vehicles')
    if cursor.fetchone()[0] == 0:
        # 1. 建立測試車輛
        test_vehicles = [
            ('ABC-1234', '王大明', '0912-345-678', 'TOYOTA', 'Altis'),
            ('XYZ-9876', '李小華', '0987-654-321', 'HONDA', 'CR-V')
        ]
        cursor.executemany('INSERT INTO Vehicles (plate_number, owner_name, phone, brand, model) VALUES (?, ?, ?, ?, ?)', test_vehicles)

        # 2. 建立測試工單 (對應 vehicle_id 1 和 2)
        test_orders = [
            (1, '2026-04-20', 55000, 1550, '五萬公里定保'), # 王大明的 Altis
            (2, '2026-04-22', 120000, 2400, '煞車異音檢查')  # 李小華的 CR-V
        ]
        cursor.executemany('INSERT INTO Repair_Orders (vehicle_id, date, mileage, total_amount, notes) VALUES (?, ?, ?, ?, ?)', test_orders)

        # 3. 建立工單明細 (對應 order_id 1 和 2，並包含單位)
        test_items = [
            # 工單 1 的明細 (總計 1550元)
            (1, '機油 (10W-40)', 2, '公升', 500, 1000),
            (1, '一般保養工資', 1, '次', 300, 300),
            (1, '機油濾清器', 1, '個', 250, 250),
            # 工單 2 的明細 (總計 2400元)
            (2, '前輪煞車皮', 2, '組', 1200, 2400)
        ]
        cursor.executemany('INSERT INTO Order_Items (order_id, item_name, quantity, unit, unit_price, subtotal) VALUES (?, ?, ?, ?, ?, ?)', test_items)

    conn.commit()
    conn.close()

# ================= 新增的功能 =================

def add_vehicle(plate_number, owner_name, phone, brand, model):
    """將新車輛存入資料庫"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        # 使用 ? 來防止 SQL 注入攻擊
        cursor.execute('''
            INSERT INTO Vehicles (plate_number, owner_name, phone, brand, model)
            VALUES (?, ?, ?, ?, ?)
        ''', (plate_number, owner_name, phone, brand, model))
        conn.commit()
        return True, "✅ 新增車輛成功！"
    except sqlite3.IntegrityError:
        # 因為 plate_number 設定為 UNIQUE，重複輸入會觸發這個錯誤
        return False, "❌ 車牌號碼已存在，請檢查！"
    finally:
        conn.close()

def get_all_vehicles():
    """從資料庫抓取所有車輛紀錄"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # 這裡原本漏掉了 phone，請補上去：
    cursor.execute('SELECT plate_number, owner_name, phone, brand, model FROM Vehicles ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_vehicles_by_keyword(search_keyword):
    """萬用搜尋：支援搜車牌、車主姓名、聯絡電話"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    keyword = f"%{search_keyword}%"
    
    # 用 OR 把車牌、車主、電話串起來搜尋
    cursor.execute('''
        SELECT plate_number, owner_name, phone, brand, model 
        FROM Vehicles 
        WHERE plate_number LIKE ? 
           OR owner_name LIKE ? 
           OR phone LIKE ?
           OR brand LIKE ?
           OR model LIKE ?
        ORDER BY id DESC
    ''', (keyword, keyword, keyword, keyword, keyword))
    
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_vehicle(plate_number):
    """根據車牌號碼刪除車輛資料"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # SQL 語法：從 Vehicles 表格中刪除，條件是 plate_number 等於我們傳入的值
    cursor.execute('DELETE FROM Vehicles WHERE plate_number = ?', (plate_number,))
    
    conn.commit()
    conn.close()
    return True, f"✅ 已成功刪除車牌 {plate_number} 的資料！"

# ==================== 維修工單專用功能 ====================

def get_all_plate_numbers():
    """1. 抓取所有已建檔的車牌（為了做下拉選單）"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT plate_number FROM Vehicles ORDER BY plate_number ASC')
    rows = cursor.fetchall()
    conn.close()
    # 這裡用了一個 Python 小技巧，把資料整理成單純的清單，例如 ['ABC-1234', 'XYZ-9876']
    return [row[0] for row in rows]

def add_repair_order(plate_number, date, mileage, items_list):
    """新增工單主檔與多個明細"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id FROM Vehicles WHERE plate_number = ?', (plate_number,))
        vehicle = cursor.fetchone()
        if not vehicle: return False, "找不到此車牌！"
        
        # 1. 自動計算總金額
        total_amount = sum(item["qty"] * item["price"] for item in items_list)

        # 2. 寫入主檔 (notes 暫時留空)
        cursor.execute('''
            INSERT INTO Repair_Orders (vehicle_id, date, mileage, total_amount, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (vehicle[0], date, mileage, total_amount, ""))
        
        order_id = cursor.lastrowid # 取得剛剛的主檔 ID
        
        # 3. 把清單裡的東西一個一個寫入明細表
        for item in items_list:
            subtotal = item["qty"] * item["price"]
            cursor.execute('''
                INSERT INTO Order_Items (order_id, item_name, quantity, unit, unit_price, subtotal) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (order_id, item["name"], item["qty"], item.get("unit", "pc"), item["price"], subtotal))

        conn.commit()
        return True, "✅ 包含明細的工單新增成功！"
    except Exception as e:
        conn.rollback() # 出錯就退回，避免資料寫一半
        return False, f"❌ 發生錯誤: {e}"
    finally:
        conn.close()

def get_all_orders():
    """抓取所有工單，並用 GROUP_CONCAT 把明細壓縮成一句話顯示"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.date, v.plate_number, r.mileage, 
               GROUP_CONCAT(i.item_name || ' (x' || i.quantity || i.unit || ')', '、'), 
               r.total_amount
        FROM Repair_Orders r
        JOIN Vehicles v ON r.vehicle_id = v.id
        LEFT JOIN Order_Items i ON r.id = i.order_id
        GROUP BY r.id
        ORDER BY r.id DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_orders_by_keyword(search_keyword):
    """進階搜尋：只要工單中任一條件符合，就顯示該工單的『完整』明細"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    keyword = f"%{search_keyword}%"
    
    # 🧑‍🏫 這裡用了子查詢：
    # 先找出所有符合條件的「工單 ID」，再根據這些 ID 抓出完整的明細
    cursor.execute('''
        SELECT r.date, v.plate_number, r.mileage, 
               GROUP_CONCAT(i.item_name || ' (x' || i.quantity || ')', '、'), 
               r.total_amount
        FROM Repair_Orders r
        JOIN Vehicles v ON r.vehicle_id = v.id
        LEFT JOIN Order_Items i ON r.id = i.order_id
        WHERE r.id IN (
            SELECT DISTINCT r2.id
            FROM Repair_Orders r2
            JOIN Vehicles v2 ON r2.vehicle_id = v2.id
            LEFT JOIN Order_Items i2 ON r2.id = i2.order_id
            WHERE v2.plate_number LIKE ? 
               OR v2.owner_name LIKE ? 
               OR v2.phone LIKE ?
               OR i2.item_name LIKE ?
        )
        GROUP BY r.id
        ORDER BY r.date DESC
    ''', (keyword, keyword, keyword, keyword))
    
    rows = cursor.fetchall()
    conn.close()
    return rows

# ==========================================
# ⚙️ Phase 3：服務與零件主檔管理 (價目表)
# ==========================================

def add_service(name, price):
    """新增一個服務項目到價目表"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Services (service_name, default_price) VALUES (?, ?)', (name, price))
        conn.commit()
        return True, "✅ 項目新增成功！"
    except sqlite3.IntegrityError:
        # 因為我們設了 UNIQUE，如果有重複的名字就會觸發這個錯誤
        return False, "❌ 項目名稱已存在，請換個名字！"
    except Exception as e:
        return False, f"❌ 發生錯誤: {e}"
    finally:
        conn.close()

def get_all_services():
    """抓取整張價目表"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, service_name, default_price FROM Services ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_service(service_id):
    """從價目表刪除某個項目"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Services WHERE id = ?', (service_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("資料庫設定完成。")