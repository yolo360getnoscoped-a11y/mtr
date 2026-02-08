# 🔧 แก้ไขปัญหา ModuleNotFoundError: No module named 'openpyxl'

**วันที่:** 2025-11-11

---

## ❌ ปัญหา

เมื่อรัน Django server พบ error:
```
ModuleNotFoundError: No module named 'openpyxl'
```

**สาเหตุ:** openpyxl ยังไม่ได้ติดตั้งใน virtual environment

---

## ✅ วิธีแก้ไข

### ขั้นตอนที่ 1: ตรวจสอบ virtual environment

```bash
cd C:\Users\yolo3\Downloads\mtr-20251105T112108Z-1-001\mtr
.\venv\Scripts\activate
```

**ตรวจสอบว่าเปิดใช้งานแล้ว:** ควรเห็น `(venv)` ด้านหน้า prompt

### ขั้นตอนที่ 2: ติดตั้ง openpyxl

**วิธีที่ 1: ติดตั้งจาก requirements.txt (แนะนำ)**
```bash
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

**วิธีที่ 2: ติดตั้ง openpyxl โดยตรง**
```bash
.\venv\Scripts\python.exe -m pip install openpyxl
```

### ขั้นตอนที่ 3: ตรวจสอบการติดตั้ง

```bash
.\venv\Scripts\python.exe -c "import openpyxl; print('✅ openpyxl version:', openpyxl.__version__)"
```

**ถ้าเห็น:** `✅ openpyxl version: 3.x.x` = ติดตั้งสำเร็จ  
**ถ้าเห็น error:** ตรวจสอบว่าใช้ virtual environment ที่ถูกต้อง

### ขั้นตอนที่ 4: ตรวจสอบ Django

```bash
.\venv\Scripts\python.exe manage.py check
```

**ถ้าไม่มี error:** ✅ พร้อมรัน server  
**ถ้ามี error:** แก้ไขตาม error ที่พบ

### ขั้นตอนที่ 5: รัน Django Server

```bash
.\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

---

## ⚠️ ข้อควรระวัง

1. **ต้องใช้ virtual environment ที่ถูกต้อง:**
   - ตรวจสอบว่าใช้ `.\venv\Scripts\python.exe` (Windows)
   - หรือ `source venv/bin/activate` (Linux/Mac)

2. **ตรวจสอบว่า openpyxl อยู่ใน requirements.txt:**
   ```
   openpyxl>=3.1.0
   ```

3. **ถ้ายังมีปัญหา:**
   - ลบ virtual environment และสร้างใหม่:
     ```bash
     rmdir /s venv
     python -m venv venv
     .\venv\Scripts\activate
     pip install -r requirements.txt
     ```

---

## ✅ ตรวจสอบว่าแก้ไขสำเร็จ

### 1. ตรวจสอบ openpyxl
```bash
.\venv\Scripts\python.exe -c "import openpyxl; print('OK')"
```

### 2. ตรวจสอบ Django
```bash
.\venv\Scripts\python.exe manage.py check
```

### 3. รัน Server
```bash
.\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

**ถ้าเห็น:**
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CTRL-BREAK.
```

**= ✅ สำเร็จ!**

---

## 📋 สรุป

**ปัญหา:** `ModuleNotFoundError: No module named 'openpyxl'`  
**วิธีแก้:** ติดตั้ง openpyxl ใน virtual environment  
**คำสั่ง:** `.\venv\Scripts\python.exe -m pip install openpyxl`

---

**อัปเดตล่าสุด:** 2025-11-11

