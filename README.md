# ระบบบริหารจัดการการเรียน - ระบบเช็คชื่อด้วย QR Code

ระบบบริหารจัดการการเรียนที่ใช้ QR Code สำหรับการเช็คชื่อนักศึกษา โดยใช้ Django Framework และ PostgreSQL Database

## 🎯 คุณสมบัติหลัก

### สำหรับผู้ดูแลระบบ (Admin)
- จัดการข้อมูลพื้นฐาน (รายวิชา, ภาคเรียน, ปีการศึกษา)
- กำหนดอาจารย์ให้กับกลุ่มเรียน
- ดูรายงานการเข้าเรียนทั้งหมด

### สำหรับอาจารย์ (Teacher)
- ดูกลุ่มเรียนที่สอน
- จัดการนักศึกษาในกลุ่มเรียน
- สร้าง QR Code สำหรับเช็คชื่อ
- ตรวจสอบและแก้ไขสถานะการเข้าเรียน
- ดูรายงานการเข้าเรียนของกลุ่มเรียน

### สำหรับนักศึกษา (Student)
- สแกน QR Code เพื่อเช็คชื่อ
- ดูรายงานการเข้าเรียนของตนเอง

## 📋 ความต้องการของระบบ

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## 🚀 การติดตั้ง

### 1. Clone หรือ Download โปรเจกต์

```bash
cd mtr
```

### 2. สร้าง Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 4. ตั้งค่า PostgreSQL Database

สร้างฐานข้อมูล PostgreSQL:

```sql
CREATE DATABASE checkin_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE checkin_db TO postgres;
```

### 5. ตั้งค่า Environment Variables

คัดลอกไฟล์ `.env.example` เป็น `.env` และแก้ไขค่า:

```bash
cp .env.example .env
```

แก้ไขไฟล์ `.env`:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=checkin_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### 6. รัน Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. สร้าง Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 8. รัน Server

```bash
python manage.py runserver
```

เปิดเบราว์เซอร์ไปที่: http://127.0.0.1:8000

### 🔐 บัญชีเข้าสู่ระบบ (ตัวอย่าง)

- Admin: `admin` / `admin123`
- Teacher: `teacher1` / `teacher123`
- Student: `student1` / `student123`

## 📁 โครงสร้างโปรเจกต์

```
checkin_project/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── checkin_project/          # Project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                 # App: จัดการผู้ใช้ (P1)
│   ├── models.py            # User, AdminProfile, TeacherProfile, StudentProfile
│   ├── views.py             # Login, Logout
│   └── urls.py
├── academic/                 # App: จัดการข้อมูลการศึกษา (P2, P3, P4)
│   ├── models.py            # AcademicYear, Semester, Course, Section, Enrollment
│   ├── views.py             # จัดการรายวิชา, กำหนดอาจารย์, จัดการนักศึกษา
│   └── urls.py
├── attendance/              # App: จัดการเช็คชื่อ (P5, P6, P7, P8)
│   ├── models.py            # AttendanceSession, AttendanceRecord
│   ├── views.py             # สร้าง QR, สแกน QR, แก้ไขสถานะ, รายงาน
│   └── urls.py
├── templates/               # HTML Templates
│   ├── base.html
│   ├── accounts/
│   ├── academic/
│   └── attendance/
└── static/                  # CSS, JavaScript
    ├── css/
    └── js/
```

## 🔐 การใช้งานครั้งแรก

### สร้างบัญชีผู้ใช้

1. ใช้ Django Admin (http://127.0.0.1:8000/admin) เพื่อสร้างผู้ใช้:
   - สร้าง User กับ role = 'admin', 'teacher', หรือ 'student'
   - สร้าง Profile ที่เกี่ยวข้อง (AdminProfile, TeacherProfile, StudentProfile)

2. หรือใช้ Django Shell:

```python
python manage.py shell

from accounts.models import User, TeacherProfile, StudentProfile
from academic.models import AcademicYear, Semester, Course, Section

# สร้างอาจารย์
teacher = User.objects.create_user(
    username='teacher1',
    password='password123',
    role='teacher',
    email='teacher@example.com'
)
TeacherProfile.objects.create(user=teacher, employee_id='T001')

# สร้างนักศึกษา
student = User.objects.create_user(
    username='student1',
    password='password123',
    role='student',
    email='student@example.com'
)
StudentProfile.objects.create(user=student, student_id='S001')
```

## 📱 การใช้งาน

### สำหรับอาจารย์
1. เข้าสู่ระบบ
2. ไปที่ "กลุ่มเรียนของฉัน"
3. เลือกกลุ่มเรียน → "สร้าง QR Code"
4. กำหนดวันที่และเวลา → สร้าง QR Code
5. แสดง QR Code บนโปรเจคเตอร์ให้นักศึกษาสแกน

### สำหรับนักศึกษา
1. เข้าสู่ระบบ
2. ไปที่ "สแกน QR Code"
3. กด "เริ่มสแกน"
4. สแกน QR Code ที่อาจารย์แสดง
5. ระบบจะบันทึกการเข้าเรียนอัตโนมัติ

## 🛠️ เทคโนโลยีที่ใช้

- **Backend**: Django 4.2+
- **Database**: PostgreSQL
- **QR Code**: qrcode library
- **Frontend**: HTML, CSS, JavaScript (jsQR library)

## 📝 License

โปรเจกต์นี้เป็น open source

## 👥 ผู้พัฒนา

พัฒนาตาม DFD (Data Flow Diagram) สำหรับระบบบริหารจัดการการเรียน By ทีมงานคุณภาพ

## 📞 การติดต่อ

หากมีคำถามหรือปัญหาการใช้งาน กรุณาติดต่อ 090-895-4126 (เบส)

