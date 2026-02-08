# 📚 คู่มืออธิบายการทำงานของระบบล็อกอิน (Login System)

## 📋 สารบัญ
1. [ภาพรวมระบบ](#ภาพรวมระบบ)
2. [Flow การทำงาน](#flow-การทำงาน)
3. [โครงสร้างฐานข้อมูล](#โครงสร้างฐานข้อมูล)
4. [Template (Frontend)](#template-frontend)
5. [View Function (Backend Logic)](#view-function-backend-logic)
6. [Authentication System](#authentication-system)
7. [Security Features](#security-features)

---

## 🎯 ภาพรวมระบบ

ระบบล็อกอินใช้ Django Authentication Framework ร่วมกับ Custom User Model ที่รองรับ 3 บทบาท:
- **Admin** (ผู้ดูแลระบบ)
- **Teacher** (อาจารย์)
- **Student** (นักศึกษา)

---

## 🔄 Flow การทำงาน

### 1. **URL Routing**

📁 **ตำแหน่งโค้ด:**
- **Root URL Config:** `checkin_project/urls.py` บรรทัด **11**
  ```python
  path('', include('accounts.urls'))
  ```
- **Accounts URL Config:** `accounts/urls.py` บรรทัด **11**
  ```python
  path('login/', views.login_view, name='login')
  ```
- **View Function:** `accounts/views.py` บรรทัด **30-59**
  ```python
  @require_http_methods(["GET", "POST"])
  def login_view(request):
      ...
  ```

```
User เข้า URL: http://127.0.0.1:8000/login/
     ↓
checkin_project/urls.py (บรรทัด 11)
     ↓
accounts/urls.py (บรรทัด 11): path('login/', views.login_view, name='login')
     ↓
accounts/views.py (บรรทัด 30-59): login_view()
```

### 2. **Process Flow Diagram**
```
┌─────────────────────────────────────────────────────────────┐
│  1. GET Request: User เข้าสู่หน้า login                      │
│     ↓                                                        │
│  2. login_view() ตรวจสอบ: request.user.is_authenticated?     │
│     - ถ้า login อยู่แล้ว → redirect ไป profile               │
│     - ถ้ายังไม่ login → แสดงหน้า login                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  3. User กรอก Username และ Password แล้วกด Submit            │
│     ↓                                                        │
│  4. POST Request ไปที่ login_view()                         │
│     ↓                                                        │
│  5. ดึงข้อมูลจาก Form:                                       │
│     - username = request.POST.get('username')                │
│     - password = request.POST.get('password')                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  6. Django authenticate() function                           │
│     - เช็คว่า username และ password ถูกต้องหรือไม่           │
│     - Query ข้อมูลจาก Database (accounts_user table)         │
│     - ตรวจสอบ password ที่ hash แล้ว                         │
│     - Return User object หรือ None                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    ┌──────┴──────┐
                    │             │
            ✅ สำเร็จ      ❌ ล้มเหลว
                    │             │
                    ↓             ↓
        ┌───────────────┐  ┌───────────────┐
        │ 7. login()    │  │ แสดง Error    │
        │    สร้าง      │  │ Message       │
        │    Session    │  │ และแสดงหน้า   │
        │    Cookie     │  │ login อีกครั้ง│
        └───────────────┘  └───────────────┘
                    ↓
        ┌───────────────────────────┐
        │ 8. Redirect ตาม Role:     │
        │  - Admin → course_list    │
        │  - Teacher → dashboard    │
        │  - Student → scan_page    │
        └───────────────────────────┘
```

---

## 💾 โครงสร้างฐานข้อมูล

### 1. **ตาราง `accounts_user`**

📁 **ตำแหน่งโค้ด:**
- `accounts/models.py` บรรทัด **8-70**: `class User(AbstractUser)`

ตารางหลักสำหรับเก็บข้อมูลผู้ใช้ทั้งหมด ใช้ Django AbstractUser เป็น Base

**Fields:**
```sql
- id (Primary Key, Auto Increment)
- username (VARCHAR, UNIQUE, NOT NULL)
- password (VARCHAR, Hashed) - Django ใช้ PBKDF2
- email (VARCHAR, Optional)
- first_name (VARCHAR)
- last_name (VARCHAR)
- role (VARCHAR) - 'admin', 'teacher', 'student'
- phone (VARCHAR, Optional)
- profile_picture (File Path, Optional)
- is_active (BOOLEAN) - ใช้งานได้หรือไม่
- is_staff (BOOLEAN) - เข้า Django Admin ได้หรือไม่
- is_superuser (BOOLEAN)
- date_joined (DATETIME)
- last_login (DATETIME)
- created_at (DATETIME)
- updated_at (DATETIME)
```

**ตัวอย่างข้อมูล:**
```
id | username  | password (hashed)              | role    | first_name | last_name
---|-----------|--------------------------------|---------|------------|-----------
1  | admin     | pbkdf2_sha256$...$abc123...    | admin   | Admin      | User
2  | teacher1  | pbkdf2_sha256$...$def456...    | teacher | วิมลศรี    | เกตุโสภณ
3  | student1  | pbkdf2_sha256$...$ghi789...    | student | กิตติพัฒน์  | โสระมรรค
```

### 2. **ตาราง `accounts_userprofile`**

📁 **ตำแหน่งโค้ด:**
- `accounts/models.py` บรรทัด **73-159**: `class UserProfile(models.Model)`

ตารางเก็บข้อมูลเพิ่มเติมของผู้ใช้ (Profile) แยกตาม Role

**Fields:**
```sql
- id (Primary Key)
- user_id (Foreign Key → accounts_user.id, OneToOne)
- teacher_employee_id (VARCHAR, UNIQUE) - สำหรับ Teacher
- student_id (VARCHAR, UNIQUE) - สำหรับ Student
- admin_department (VARCHAR) - สำหรับ Admin
- ... (fields อื่นๆ)
```

**Relationship:**
```
accounts_user (1) ────── (1) accounts_userprofile
```

---

## 🎨 Template (Frontend)

### ไฟล์: `templates/accounts/login.html`

📁 **ตำแหน่งโค้ด:**
- `templates/accounts/login.html` บรรทัด **1-127** (ทั้งไฟล์)

#### 1. **HTML Structure**

```html
<!DOCTYPE html>
<html lang="th">
<head>
    <!-- Meta tags, CSS, Icons -->
</head>
<body>
    <div class="auth-background"></div>  <!-- Background image -->
    <div class="login-container">
        <div class="login-card">
            <!-- Logo, Form, Links -->
        </div>
    </div>
</body>
</html>
```

#### 2. **ส่วนประกอบสำคัญ**

**A. Background Image**

📁 **ตำแหน่งโค้ด:**
- HTML: `templates/accounts/login.html` บรรทัด **60**
- CSS: `templates/accounts/login.html` บรรทัด **18-38**

```html
<!-- บรรทัด 60 -->
<div class="auth-background"></div>
```

```css
/* บรรทัด 18-29: Background container */
.auth-background {
    position: fixed;
    background-image: url('{% static "image/61619313_2057854727652954_7664118163298058240_n.jpg" %}');
    /* บรรทัด 24 */
    background-size: cover;
}

/* บรรทัด 30-38: Overlay layer */
.auth-background::before {
    background-color: rgba(0, 0, 0, 0.15);  /* บรรทัด 37 */
}
```
- แสดงรูปภาพมหาวิทยาลัยเป็น background
- ใช้ CSS `background-image` จาก static files (บรรทัด 24)
- มี overlay สีดำโปร่งใส (rgba(0,0,0,0.15)) (บรรทัด 37)

**B. Login Form**

📁 **ตำแหน่งโค้ด:** `templates/accounts/login.html` บรรทัด **76-100**

```html
<!-- บรรทัด 76: Form opening tag -->
<form method="post" action="{% url 'accounts:login' %}">
    <!-- บรรทัด 77: CSRF Token -->
    {% csrf_token %}
    
    <!-- บรรทัด 78-86: Username field -->
    <div class="form-group">
        <label for="username">ชื่อผู้ใช้</label>
        <input type="text" id="username" name="username" required 
               autofocus placeholder="กรอกชื่อผู้ใช้">  <!-- บรรทัด 84 -->
    </div>
    
    <!-- บรรทัด 87-98: Password field -->
    <div class="form-group">
        <label for="password">รหัสผ่าน</label>
        <input type="password" id="password" name="password" required 
               placeholder="กรอกรหัสผ่าน">  <!-- บรรทัด 93 -->
    </div>
    
    <!-- บรรทัด 99: Submit button -->
    <button type="submit" class="auth-btn-primary">เข้าสู่ระบบ</button>
</form>
```

**C. CSRF Token**

📁 **ตำแหน่งโค้ด:** `templates/accounts/login.html` บรรทัด **77**

```html
{% csrf_token %}
```
- สร้าง hidden input field อัตโนมัติ
- Django ใช้ป้องกัน Cross-Site Request Forgery (CSRF) attacks
- Browser จะส่ง token นี้ไปพร้อม POST request
- CSRF Middleware: `checkin_project/settings.py` บรรทัด **58**

**D. Password Toggle**

📁 **ตำแหน่งโค้ด:**
- HTML Button: `templates/accounts/login.html` บรรทัด **94-96**
- JavaScript Function: `templates/accounts/login.html` บรรทัด **108-123**

```html
<!-- บรรทัด 94-96: Toggle button -->
<div class="auth-password-toggle" onclick="togglePassword()">
    <i class="fas fa-eye" id="password-toggle-icon"></i>
</div>
```

```javascript
// บรรทัด 108-123: Toggle function
function togglePassword() {
    const passwordInput = document.getElementById('password');  // บรรทัด 110
    const toggleIcon = document.getElementById('password-toggle-icon');  // บรรทัด 111
    
    if (passwordInput.type === 'password') {  // บรรทัด 113
        passwordInput.type = 'text';  // บรรทัด 114
        // เปลี่ยน icon เป็น fa-eye-slash (บรรทัด 115-116)
    } else {
        passwordInput.type = 'password';  // บรรทัด 118
        // เปลี่ยน icon เป็น fa-eye (บรรทัด 119-120)
    }
}
```

#### 3. **CSS Styling**

📁 `templates/accounts/login.html` บรรทัด **12-57**

**Key Styles:**
```css
.login-card {
    background: rgba(255, 255, 255, 0.85);  /* บรรทัด 54 */
    backdrop-filter: blur(15px);  /* Glass morphism effect (บรรทัด 55) */
}

.auth-background {
    position: fixed;  /* บรรทัด 19-28 */
    background-image: url('...');
    background-size: cover;
}
```

---

## ⚙️ View Function (Backend Logic)

### ไฟล์: `accounts/views.py`

📁 **ตำแหน่งโค้ด:**
- `accounts/views.py` บรรทัด **1-10**: Import statements
- `accounts/views.py` บรรทัด **29-59**: `login_view()` function

### Function: `login_view(request)`

```python
@require_http_methods(["GET", "POST"])  # บรรทัด 29
def login_view(request):  # บรรทัด 30
    """
    Process 1: ตรวจสอบสิทธิ์ (Login)
    """
```

#### Step-by-Step Explanation:

**Step 1: Check Authentication Status**
📁 `accounts/views.py` บรรทัด **34-35**
```python
if request.user.is_authenticated:
    return redirect('accounts:profile')
```
- ตรวจสอบว่าผู้ใช้ login อยู่แล้วหรือไม่
- `request.user` มาจาก `AuthenticationMiddleware`
- ถ้า login อยู่แล้ว → redirect ไปหน้า profile

**Step 2: Handle GET Request**
📁 `accounts/views.py` บรรทัด **37, 59**
```python
if request.method == 'POST':  # บรรทัด 37
    # Process login
else:
    return render(request, 'accounts/login.html')  # บรรทัด 59
```
- GET Request → แสดงหน้า login
- POST Request → ประมวลผลการ login

**Step 3: Extract Form Data**
📁 `accounts/views.py` บรรทัด **38-39**
```python
username = request.POST.get('username')  # บรรทัด 38
password = request.POST.get('password')  # บรรทัด 39
```
- ดึงข้อมูลจาก form ที่ส่งมา
- `request.POST` เป็น dictionary ของข้อมูลจาก POST request

**Step 4: Validate Input**
📁 `accounts/views.py` บรรทัด **41, 56-57**
```python
if username and password:  # บรรทัด 41
    # Process authentication
else:
    messages.error(request, 'กรุณากรอกชื่อผู้ใช้และรหัสผ่าน')  # บรรทัด 57
```
- ตรวจสอบว่ามีการกรอกข้อมูลครบหรือไม่

**Step 5: Authenticate User**

📁 **ตำแหน่งโค้ด:**
- Function call: `accounts/views.py` บรรทัด **42**
- Import: `accounts/views.py` บรรทัด **5**

```python
# บรรทัด 5: Import authenticate function
from django.contrib.auth import login, logout, authenticate

# บรรทัด 42: Authenticate user
user = authenticate(request, username=username, password=password)
```
- `authenticate()` เป็น Django function
- **กระบวนการทำงาน:**
  1. Query database หา User ที่มี `username` ตรงกัน
     - Query: `SELECT * FROM accounts_user WHERE username = ? AND is_active = TRUE`
  2. ตรวจสอบ `is_active=True`
  3. Hash password ที่กรอกมา (PBKDF2)
  4. เปรียบเทียบกับ password ที่เก็บใน database
  5. Return User object หรือ None

**Step 6: Create Session**
📁 `accounts/views.py` บรรทัด **43-44**
```python
if user is not None:  # บรรทัด 43
    login(request, user)  # บรรทัด 44
```
- `login()` สร้าง session สำหรับ user (import จาก `django.contrib.auth` บรรทัด 5)
- เก็บ session ID ใน cookie
- Session ถูกเก็บใน database (django_session table)

**Step 7: Redirect Based on Role**
📁 `accounts/views.py` บรรทัด **48-53**
```python
if user.is_admin():  # บรรทัด 48
    return redirect('academic:course_list')  # บรรทัด 49
elif user.is_teacher():  # บรรทัด 50
    return redirect('teacher:dashboard')  # บรรทัด 51
else:
    return redirect('attendance:scan_page')  # บรรทัด 53
```
- ตรวจสอบ role ของ user (ใช้ method จาก User model)
- Redirect ไปหน้าที่เหมาะสมตาม role

**Step 8: Error Handling**
📁 `accounts/views.py` บรรทัด **54-55**
```python
else:  # บรรทัด 54
    messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')  # บรรทัด 55
```
- แสดง error message หาก authentication ล้มเหลว
- Django Messages Framework เก็บ message ใน session (import จาก `django.contrib` บรรทัด 7)

---

## 🔐 Authentication System

### 1. **Django Authentication Backend**

📁 **ตำแหน่งโค้ด:**
- `checkin_project/settings.py` บรรทัด **151, 154-155**

**Settings: `checkin_project/settings.py`**
```python
AUTH_USER_MODEL = 'accounts.User'  # บรรทัด 151
LOGIN_URL = 'accounts:login'  # บรรทัด 154
LOGIN_REDIRECT_URL = 'accounts:profile'  # บรรทัด 155
```

- `AUTH_USER_MODEL`: ระบุ Custom User Model
- `LOGIN_URL`: URL สำหรับ redirect เมื่อต้อง login
- `LOGIN_REDIRECT_URL`: URL default หลังจาก login สำเร็จ

### 2. **Middleware Chain**

📁 **ตำแหน่งโค้ด:** `checkin_project/settings.py` บรรทัด **54-63**

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # บรรทัด 55
    'django.contrib.sessions.middleware.SessionMiddleware',  # บรรทัด 56 - สร้าง session
    'django.middleware.common.CommonMiddleware',  # บรรทัด 57
    'django.middleware.csrf.CsrfViewMiddleware',  # บรรทัด 58 - CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # บรรทัด 59 - เพิ่ม request.user
    'django.contrib.messages.middleware.MessageMiddleware',  # บรรทัด 60
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # บรรทัด 61
    'checkin_project.middleware.StaticFilesCacheMiddleware',  # บรรทัด 62
]
```

**AuthenticationMiddleware:**
- ดึง session ID จาก cookie
- Query session จาก database
- เพิ่ม `request.user` object ให้ทุก request

### 3. **Session Management**

**Session Storage:**
- Default: Database (django_session table)
- Session ID ถูกเก็บใน cookie (sessionid)
- Session data ถูกเก็บใน database (encoded)

**Session Flow:**
```
1. User login สำเร็จ
2. Django สร้าง session record ใน database
3. Session ID ถูกส่งไปยัง browser ใน cookie
4. Browser ส่ง Session ID กลับมาในทุก request
5. Django ใช้ Session ID หา session data
6. เพิ่ม request.user จาก session data
```

### 4. **Password Hashing**

Django ใช้ **PBKDF2** algorithm:
```python
# Password ถูก hash ก่อนเก็บใน database
hash = pbkdf2_sha256(iterations=260000, salt=salt, password=raw_password)
# Format: pbkdf2_sha256$260000$salt$hash
```

**ตัวอย่าง:**
```
Raw password: "admin123"
Hashed: "pbkdf2_sha256$260000$abc123salt$def456hash789"
```

---

## 🛡️ Security Features

### 1. **CSRF Protection**

📁 **ตำแหน่งโค้ด:**
- Middleware: `checkin_project/settings.py` บรรทัด **58**
- Template: `templates/accounts/login.html` บรรทัด **77**

```python
# checkin_project/settings.py บรรทัด 58
'django.middleware.csrf.CsrfViewMiddleware'
```

```html
<!-- templates/accounts/login.html บรรทัด 77 -->
{% csrf_token %}
```

- ป้องกัน Cross-Site Request Forgery (CSRF) attacks
- ต้องมี CSRF token ใน POST request
- Django เปรียบเทียบ token จาก form กับ token ใน session

### 2. **Password Security**

- Password ไม่ถูกเก็บในรูปแบบ plain text
- ใช้ PBKDF2 hashing algorithm
- มี salt เพื่อป้องกัน rainbow table attacks

### 3. **Session Security**

- Session ID เป็น random string ยาว
- HTTPS ควรใช้ใน production เพื่อ encrypt cookie
- Session timeout สามารถตั้งค่าได้

### 4. **Input Validation**

📁 **ตำแหน่งโค้ด:** `accounts/views.py` บรรทัด **41, 56-57**

```python
# บรรทัด 41: ตรวจสอบว่ามีการกรอกข้อมูลครบ
if username and password:
    user = authenticate(request, username=username, password=password)  # Validate กับ database
else:
    # บรรทัด 56-57: แสดง error ถ้าไม่ครบ
    messages.error(request, 'กรุณากรอกชื่อผู้ใช้และรหัสผ่าน')
```

### 5. **SQL Injection Protection**

- Django ORM ป้องกัน SQL injection อัตโนมัติ
- ใช้ parameterized queries

---

## 📊 Database Queries During Login

### 1. **Authentication Query**

📁 **ตำแหน่งโค้ด:** Django Framework (`django.contrib.auth.backends.ModelBackend`)
- เรียกใช้จาก: `accounts/views.py` บรรทัด **42** (`authenticate()`)

```sql
SELECT * FROM accounts_user 
WHERE username = 'admin' 
AND is_active = TRUE;
```

### 2. **Password Verification**

📁 **ตำแหน่งโค้ด:**
- Django Framework: `django.contrib.auth.hashers.check_password()`
- เรียกใช้ภายใน `authenticate()` function

```python
# Django ใช้ Python code เปรียบเทียบ hash
check_password(raw_password, stored_hash)
```

### 3. **Session Creation**

📁 **ตำแหน่งโค้ด:**
- เรียกใช้จาก: `accounts/views.py` บรรทัด **44** (`login()`)
- Django Framework: `django.contrib.sessions.backends.db`

```sql
INSERT INTO django_session (session_key, session_data, expire_date)
VALUES ('abc123...', 'encoded_data...', '2025-01-06 12:00:00');
```

### 4. **Profile Query (if needed)**

📁 **ตำแหน่งโค้ด:** ไม่ได้ query โดยตรงใน login_view แต่จะ query เมื่อเข้าหน้า profile

```sql
SELECT * FROM accounts_userprofile 
WHERE user_id = 1;
```

---

## 🔍 Code Examples

### 1. **ตรวจสอบ User Role**

```python
if user.is_admin():
    # Admin logic
elif user.is_teacher():
    # Teacher logic
else:
    # Student logic
```

### 2. **ตรวจสอบ Authentication**

📁 **ตำแหน่งโค้ด:** `accounts/views.py` บรรทัด **34**

```python
# บรรทัด 34: ตรวจสอบว่า login อยู่แล้วหรือไม่
if request.user.is_authenticated:
    # User is logged in
    return redirect('accounts:profile')
else:
    # User is not logged in
    # แสดงหน้า login
```

### 3. **Logout**

📁 **ตำแหน่งโค้ด:**
- View Function: `accounts/views.py` บรรทัด **62-69**
- URL Config: `accounts/urls.py` บรรทัด **13**

```python
# accounts/views.py บรรทัด 62-69
@login_required
def logout_view(request):
    """
    Logout view
    """
    logout(request)  # บรรทัด 67 - ลบ session
    messages.info(request, 'คุณได้ออกจากระบบแล้ว')  # บรรทัด 68
    return redirect('accounts:login')  # บรรทัด 69
```

---

## 📍 ตารางสรุปตำแหน่งโค้ดทั้งหมด

| ส่วน | โฟลเดอร์ | ไฟล์ | บรรทัด | คำอธิบาย |
|------|---------|------|--------|----------|
| **URL Routing** |
| Root URL Config | `checkin_project/` | `urls.py` | 11 | Include accounts URLs |
| Login URL | `accounts/` | `urls.py` | 11 | Map `/login/` to view |
| **View Function** |
| Import Statements | `accounts/` | `views.py` | 1-10 | Import Django functions |
| Login View | `accounts/` | `views.py` | 29-59 | Main login logic |
| Check Auth Status | `accounts/` | `views.py` | 34-35 | Check if already logged in |
| Extract Form Data | `accounts/` | `views.py` | 38-39 | Get username/password |
| Authenticate | `accounts/` | `views.py` | 42 | Verify credentials |
| Create Session | `accounts/` | `views.py` | 44 | Login user |
| Role-based Redirect | `accounts/` | `views.py` | 48-53 | Redirect by role |
| Error Handling | `accounts/` | `views.py` | 54-57 | Show error messages |
| **Template** |
| Login Template | `templates/accounts/` | `login.html` | 1-127 | Full login page |
| HTML Structure | `templates/accounts/` | `login.html` | 1-59 | HTML head & body |
| Background Image | `templates/accounts/` | `login.html` | 60, 18-38 | Background styling |
| Login Form | `templates/accounts/` | `login.html` | 76-100 | Form HTML |
| CSRF Token | `templates/accounts/` | `login.html` | 77 | CSRF protection |
| Username Input | `templates/accounts/` | `login.html` | 84 | Username field |
| Password Input | `templates/accounts/` | `login.html` | 93 | Password field |
| Password Toggle | `templates/accounts/` | `login.html` | 94-96, 108-123 | Show/hide password |
| **Model** |
| User Model | `accounts/` | `models.py` | 8-70 | Custom User class |
| UserProfile Model | `accounts/` | `models.py` | 73-159 | Profile information |
| **Settings** |
| Custom User Model | `checkin_project/` | `settings.py` | 151 | AUTH_USER_MODEL |
| Login URL | `checkin_project/` | `settings.py` | 154 | LOGIN_URL |
| Login Redirect | `checkin_project/` | `settings.py` | 155 | LOGIN_REDIRECT_URL |
| Middleware | `checkin_project/` | `settings.py` | 54-63 | Middleware chain |
| CSRF Middleware | `checkin_project/` | `settings.py` | 58 | CSRF protection |
| Auth Middleware | `checkin_project/` | `settings.py` | 59 | Authentication |
| Session Middleware | `checkin_project/` | `settings.py` | 56 | Session management |

---

## 📝 สรุป

### **Flow สั้นๆ:**

1. **User เข้าหน้า login** → แสดง form (`templates/accounts/login.html`)
2. **User กรอกข้อมูล** → POST request ไปยัง server (`accounts/views.py:38-39`)
3. **Server authenticate** → ตรวจสอบ username/password กับ database (`accounts/views.py:42`)
4. **สร้าง session** → เก็บ session ID ใน cookie (`accounts/views.py:44`)
5. **Redirect** → ไปหน้าที่เหมาะสมตาม role (`accounts/views.py:48-53`)

### **Key Components:**

- **Frontend:** 
  - Template: `templates/accounts/login.html` (บรรทัด 1-127)
  - CSS: Embedded styles (บรรทัด 12-57)
  - JavaScript: Password toggle (บรรทัด 108-123)

- **Backend:** 
  - View: `accounts/views.py` (บรรทัด 29-59)
  - URL: `accounts/urls.py` (บรรทัด 11)

- **Database:** 
  - User Model: `accounts/models.py` (บรรทัด 8-70)
  - Profile Model: `accounts/models.py` (บรรทัด 73-159)

- **Security:** 
  - CSRF: `checkin_project/settings.py:58`
  - Password hashing: Django PBKDF2 (automatic)
  - Session management: Django Sessions (automatic)

### **Dependencies:**

- Django Authentication Framework
- Django Sessions Framework
- Custom User Model (`accounts.User`)
- PostgreSQL Database

---

**สร้างเมื่อ:** 2025-01-05  
**อัปเดตล่าสุด:** 2025-01-05

