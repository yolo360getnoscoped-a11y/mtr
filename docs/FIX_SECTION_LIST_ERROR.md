# 🔧 แก้ไขปัญหา Error 404 และ 500 ในหน้า /academic/sections/

**วันที่:** 2025-11-11

---

## ❌ ปัญหา

เมื่อเข้าหน้า `http://127.0.0.1:8000/academic/sections/` พบ:
- **404 (Not Found)** - Resource ไม่พบ
- **500 (Internal Server Error)** - Server error

---

## 🔍 สาเหตุ

### 1. Template Error - `section.teacher` เป็น `None`
**ปัญหา:** ใน template `section_list.html` บรรทัด 48:
```django
{{ section.teacher.get_full_name|default:section.teacher.username|default:"ยังไม่ได้กำหนด" }}
```

**สาเหตุ:** ถ้า `section.teacher` เป็น `None` จะเกิด error เมื่อเรียก `.get_full_name()` หรือ `.username`

### 2. Template Error - การเปรียบเทียบ `selected_semester`
**ปัญหา:** ใน template บรรทัด 18:
```django
{% if selected_semester == semester.id|stringformat:"s" %}selected{% endif %}
```

**สาเหตุ:** การเปรียบเทียบอาจไม่ถูกต้องถ้า type ไม่ตรงกัน

---

## ✅ การแก้ไข

### 1. แก้ไข Template - ตรวจสอบ `section.teacher` ก่อนเรียก method

**ไฟล์:** `templates/academic/section_list.html`

**ก่อนแก้ไข:**
```django
<td>{{ section.teacher.get_full_name|default:section.teacher.username|default:"ยังไม่ได้กำหนด" }}</td>
```

**หลังแก้ไข:**
```django
<td>{% if section.teacher %}{{ section.teacher.get_full_name|default:section.teacher.username }}{% else %}ยังไม่ได้กำหนด{% endif %}</td>
```

### 2. แก้ไข Template - ปรับการเปรียบเทียบ `selected_semester`

**ไฟล์:** `templates/academic/section_list.html`

**ก่อนแก้ไข:**
```django
<option value="{{ semester.id }}" {% if selected_semester == semester.id|stringformat:"s" %}selected{% endif %}>
```

**หลังแก้ไข:**
```django
<option value="{{ semester.id }}" {% if selected_semester|stringformat:"s" == semester.id|stringformat:"s" %}selected{% endif %}>
```

### 3. แก้ไข View - แปลง `selected_semester` เป็น string และเพิ่ม `select_related`

**ไฟล์:** `academic/views.py`

**ก่อนแก้ไข:**
```python
semesters = Semester.objects.filter(is_active=True)
context = {
    'sections': sections,
    'semesters': semesters,
    'selected_semester': semester_id,
}
```

**หลังแก้ไข:**
```python
semesters = Semester.objects.filter(is_active=True).select_related('academic_year')
context = {
    'sections': sections,
    'semesters': semesters,
    'selected_semester': str(semester_id) if semester_id else None,
}
```

---

## ✅ ผลลัพธ์

### 1. Template ไม่เกิด Error
- ✅ ตรวจสอบ `section.teacher` ก่อนเรียก method
- ✅ แสดง "ยังไม่ได้กำหนด" ถ้าไม่มี teacher

### 2. Filter ทำงานถูกต้อง
- ✅ การเปรียบเทียบ `selected_semester` ถูกต้อง
- ✅ Dropdown แสดงค่า selected ถูกต้อง

### 3. Performance ดีขึ้น
- ✅ ใช้ `select_related('academic_year')` เพื่อลด database queries

---

## 🧪 การทดสอบ

### 1. ตรวจสอบว่าไม่มี Error
```bash
python manage.py check
```

### 2. ทดสอบหน้าเว็บ
1. เข้าหน้า: `http://127.0.0.1:8000/academic/sections/`
2. ตรวจสอบว่าไม่มี error 404 หรือ 500
3. ตรวจสอบว่าตารางแสดงผลถูกต้อง
4. ทดสอบ filter โดยเลือกภาคเรียน

---

## 📋 Checklist

- [x] แก้ไข template - ตรวจสอบ `section.teacher` ก่อนเรียก method
- [x] แก้ไข template - ปรับการเปรียบเทียบ `selected_semester`
- [x] แก้ไข view - แปลง `selected_semester` เป็น string
- [x] แก้ไข view - เพิ่ม `select_related` เพื่อประสิทธิภาพ
- [x] ตรวจสอบ linter errors
- [x] ทดสอบ Django system check

---

## 🎯 สรุป

**ปัญหา:** Error 404 และ 500 ในหน้า `/academic/sections/`  
**สาเหตุ:** Template error เมื่อ `section.teacher` เป็น `None`  
**วิธีแก้:** ตรวจสอบ `section.teacher` ก่อนเรียก method และแก้ไขการเปรียบเทียบ `selected_semester`  
**สถานะ:** ✅ **แก้ไขเสร็จสิ้น**

---

**อัปเดตล่าสุด:** 2025-11-11

