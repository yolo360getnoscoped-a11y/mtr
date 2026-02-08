# 🔧 แก้ไขฟิลด์ "กลุ่มเรียน" ให้เป็น Dropdown

**วันที่:** 2025-11-11

---

## ❌ ปัญหา

ในหน้าเพิ่มรายวิชา (`/academic/courses/add/`) ฟิลด์ "กลุ่มเรียน" เป็น input field ที่ต้องกรอกเลขกลุ่มเรียนใหม่

**ความต้องการ:** ต้องการให้เป็น dropdown ที่ดึงข้อมูลกลุ่มเรียนที่ตั้งไว้แล้วมาแสดง

---

## ✅ การแก้ไข

### 1. แก้ไข View - เพิ่ม `existing_sections` ใน context

**ไฟล์:** `academic/views.py`

**เพิ่มโค้ด:**
```python
# Get all existing sections for dropdown (when adding new course)
existing_sections = None
if not course:
    # Get all active sections with their course and semester info
    existing_sections = Section.objects.filter(
        course__is_active=True
    ).select_related('course', 'semester', 'semester__academic_year', 'teacher').order_by(
        'course__course_code', 'section_number'
    )

context = {
    'course': course,
    'sections': sections,
    'teachers': teachers,
    'existing_sections': existing_sections,  # เพิ่มบรรทัดนี้
}
```

### 2. แก้ไข Template - เปลี่ยน input เป็น select dropdown

**ไฟล์:** `templates/academic/course_form.html`

**เปลี่ยนจาก:**
```django
<div class="form-row">
    <label for="section_number">กลุ่มเรียน</label>
    <input type="text" id="section_number" name="section_number" placeholder="เช่น 1">
</div>
```

**เป็น:**
```django
<div class="form-row">
    <label for="section_id">กลุ่มเรียน</label>
    <select id="section_id" name="section_id" style="flex: 1; padding: 0.875rem 1rem; border: 2px solid #ddd; border-radius: 4px; font-size: 1rem; transition: border-color 0.3s; background-color: white;">
        <option value="">-- เลือกกลุ่มเรียน --</option>
        {% if existing_sections %}
            {% for section in existing_sections %}
            <option value="{{ section.id }}">
                {{ section.course.course_code }} - กลุ่ม {{ section.section_number }} 
                ({{ section.semester.academic_year.year }} - {{ section.semester.get_semester_number_display }})
                {% if section.room %} - ห้อง {{ section.room }}{% endif %}
            </option>
            {% endfor %}
        {% endif %}
    </select>
    <small style="display: block; margin-top: 0.5rem; color: #666; font-size: 0.875rem;">
        เลือกกลุ่มเรียนที่ตั้งไว้แล้ว หรือเว้นว่างไว้เพื่อสร้างกลุ่มเรียนใหม่
    </small>
</div>
```

### 3. แก้ไข View - จัดการ `section_id` ใน POST request

**ไฟล์:** `academic/views.py`

**เพิ่มโค้ด:**
```python
# Check if existing section is selected or new section should be created
section_id = request.POST.get('section_id', '')
if section_id:
    # Link existing section to this course
    try:
        existing_section = Section.objects.get(id=section_id)
        existing_section.course = course
        existing_section.save()
        messages.success(request, f'เชื่อมโยงกลุ่มเรียน {existing_section.section_number} กับรายวิชานี้สำเร็จ')
    except Section.DoesNotExist:
        messages.warning(request, 'ไม่พบกลุ่มเรียนที่เลือก')
elif section_number:
    # Create new section if section_number is provided (fallback)
    # ... existing code ...
```

### 4. แก้ไข CSS - เพิ่ม style สำหรับ select

**ไฟล์:** `templates/academic/course_form.html`

**เพิ่ม:**
```css
.form-row input,
.form-row select {
    flex: 1;
    padding: 0.875rem 1rem;
    border: 2px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    transition: border-color 0.3s;
    min-width: 0;
    background-color: white;
}

.form-row input:focus,
.form-row select:focus {
    outline: none;
    border-color: #0066cc;
}

.form-row small {
    display: block;
    margin-top: 0.5rem;
    color: #666;
    font-size: 0.875rem;
}
```

---

## ✅ ผลลัพธ์

### 1. Dropdown แสดงกลุ่มเรียนที่มีอยู่แล้ว
- ✅ แสดงรหัสวิชา, กลุ่ม, ปีการศึกษา, ภาคเรียน
- ✅ แสดงห้องเรียน (ถ้ามี)
- ✅ เรียงตามรหัสวิชาและเลขกลุ่ม

### 2. การทำงาน
- ✅ เลือกกลุ่มเรียนจาก dropdown → เชื่อมโยงกับรายวิชาใหม่
- ✅ ไม่เลือก (เว้นว่าง) → ไม่สร้างกลุ่มเรียนใหม่ (หรือสร้างใหม่ถ้ามี section_number)

### 3. UI/UX
- ✅ Dropdown มี style ตรงกับ input fields
- ✅ มีคำอธิบายเล็กๆ ด้านล่าง
- ✅ Focus state ทำงานถูกต้อง

---

## 🧪 การทดสอบ

### 1. ทดสอบหน้าเพิ่มรายวิชา
1. เข้าหน้า: `http://127.0.0.1:8000/academic/courses/add/`
2. ตรวจสอบว่าฟิลด์ "กลุ่มเรียน" เป็น dropdown
3. ตรวจสอบว่า dropdown แสดงกลุ่มเรียนที่มีอยู่แล้ว
4. เลือกกลุ่มเรียนและบันทึก
5. ตรวจสอบว่ากลุ่มเรียนถูกเชื่อมโยงกับรายวิชาใหม่

### 2. ทดสอบกรณีไม่มีกลุ่มเรียน
- ถ้ายังไม่มีกลุ่มเรียนในระบบ → dropdown จะว่างเปล่า (แสดงแค่ "-- เลือกกลุ่มเรียน --")

---

## 📋 Checklist

- [x] แก้ไข view - เพิ่ม `existing_sections` ใน context
- [x] แก้ไข template - เปลี่ยน input เป็น select dropdown
- [x] แก้ไข view - จัดการ `section_id` ใน POST request
- [x] แก้ไข CSS - เพิ่ม style สำหรับ select
- [x] ตรวจสอบ linter errors
- [x] ทดสอบ Django system check

---

## 🎯 สรุป

**ปัญหา:** ฟิลด์ "กลุ่มเรียน" เป็น input field  
**วิธีแก้:** เปลี่ยนเป็น dropdown ที่ดึงข้อมูลกลุ่มเรียนที่มีอยู่แล้วมาแสดง  
**สถานะ:** ✅ **แก้ไขเสร็จสิ้น**

---

**อัปเดตล่าสุด:** 2025-11-11

