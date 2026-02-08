# 🔧 เพิ่มช่องจัดการอาจารย์ผู้สอนในหน้าเพิ่มรายวิชา

**วันที่:** 2025-11-11

---

## ❌ ปัญหา

ในหน้าเพิ่มรายวิชา (`/academic/courses/add/`) ไม่มีช่องจัดการอาจารย์ผู้สอน ทำให้ต้องไปแก้ไขทีหลัง

**ความต้องการ:** เพิ่มช่องจัดการอาจารย์ผู้สอนในหน้าเพิ่มรายวิชา เพื่อให้สามารถเลือกอาจารย์ได้ทันที

---

## ✅ การแก้ไข

### 1. แก้ไข View - เพิ่ม `teachers` ใน context สำหรับหน้าเพิ่มรายวิชา

**ไฟล์:** `academic/views.py`

**เพิ่มโค้ด:**
```python
else:
    # For adding new course, still get teachers list
    teachers = User.objects.filter(role='teacher').order_by('first_name', 'last_name', 'username')
```

### 2. แก้ไข View - เพิ่ม `teacher_id_value` ใน existing_sections

**ไฟล์:** `academic/views.py`

**เพิ่มโค้ด:**
```python
# Add teacher_id to each section for template
for section in existing_sections:
    section.teacher_id_value = section.teacher.id if section.teacher else None
```

### 3. แก้ไข View - จัดการ teacher assignment เมื่อสร้าง course ใหม่

**ไฟล์:** `academic/views.py`

**เพิ่มโค้ด:**
```python
# Handle teacher assignment for the linked section
teacher_id = request.POST.get(f'teacher_{section_id}')
if teacher_id:
    if teacher_id == 'none':
        existing_section.teacher = None
    else:
        teacher = get_object_or_404(User, id=teacher_id, role='teacher')
        existing_section.teacher = teacher
    existing_section.save()
```

### 4. แก้ไข Template - เพิ่มส่วนจัดการอาจารย์ผู้สอน

**ไฟล์:** `templates/academic/course_form.html`

**เพิ่มโค้ด:**
```django
<!-- จัดการอาจารย์ผู้สอน (สำหรับเพิ่มรายวิชาใหม่) -->
{% if not course and existing_sections %}
<div id="teacher-management-section" style="margin-top: 2.5rem; padding-top: 2rem; border-top: 2px solid #eee; display: none;">
    <h3 style="font-size: 1.2rem; font-weight: 600; color: #333; margin-bottom: 1.5rem;">จัดการอาจารย์ผู้สอน</h3>
    
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem;">
        <div id="selected-section-info" style="margin-bottom: 1rem; padding: 1rem; background: white; border-radius: 4px; border: 1px solid #dee2e6;">
            <strong id="section-display-name"></strong>
        </div>
        
        <div class="form-row" style="margin-bottom: 0;">
            <label for="selected_section_teacher" style="min-width: 140px;">เลือกอาจารย์ผู้สอน</label>
            <div class="input-wrapper">
                <select id="selected_section_teacher" name="selected_section_teacher" style="width: 100%;">
                    <option value="none">-- ไม่กำหนดอาจารย์ --</option>
                    {% for teacher in teachers %}
                    <option value="{{ teacher.id }}">
                        {{ teacher.get_full_name|default:teacher.username }}
                    </option>
                    {% endfor %}
                </select>
                <small class="help-text">
                    เลือกอาจารย์ผู้สอนสำหรับกลุ่มเรียนที่เลือก
                </small>
            </div>
        </div>
    </div>
</div>
{% endif %}
```

### 5. เพิ่ม JavaScript - จัดการการแสดง/ซ่อนส่วนจัดการอาจารย์

**ไฟล์:** `templates/academic/course_form.html`

**เพิ่มโค้ด:**
```javascript
{% block extra_js %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    const sectionSelect = document.getElementById('section_id');
    const teacherManagementSection = document.getElementById('teacher-management-section');
    const sectionDisplayName = document.getElementById('section-display-name');
    const selectedSectionTeacher = document.getElementById('selected_section_teacher');
    
    if (sectionSelect && teacherManagementSection) {
        sectionSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const sectionId = this.value;
            
            if (sectionId) {
                // Show teacher management section
                teacherManagementSection.style.display = 'block';
                
                // Update section display name
                sectionDisplayName.textContent = selectedOption.textContent.trim();
                
                // Update teacher select name to match section_id
                selectedSectionTeacher.name = 'teacher_' + sectionId;
                
                // Set current teacher if section has one
                const currentTeacherId = selectedOption.getAttribute('data-teacher-id');
                if (currentTeacherId) {
                    selectedSectionTeacher.value = currentTeacherId;
                } else {
                    selectedSectionTeacher.value = 'none';
                }
            } else {
                // Hide teacher management section
                teacherManagementSection.style.display = 'none';
            }
        });
        
        // Trigger change event on page load if section is already selected
        if (sectionSelect.value) {
            sectionSelect.dispatchEvent(new Event('change'));
        }
    }
});
</script>
{% endblock %}
```

### 6. แก้ไข Template - เพิ่ม `data-teacher-id` ใน option

**ไฟล์:** `templates/academic/course_form.html`

**เพิ่ม:**
```django
<option value="{{ section.id }}" {% if section.teacher_id_value %}data-teacher-id="{{ section.teacher_id_value }}"{% endif %}>
```

---

## ✅ ผลลัพธ์

### 1. ส่วนจัดการอาจารย์ผู้สอนแสดงเมื่อเลือกกลุ่มเรียน
- ✅ เมื่อเลือกกลุ่มเรียนจาก dropdown → แสดงส่วนจัดการอาจารย์
- ✅ แสดงชื่อกลุ่มเรียนที่เลือก
- ✅ แสดง dropdown เลือกอาจารย์ผู้สอน

### 2. การทำงาน
- ✅ เลือกกลุ่มเรียน → แสดงส่วนจัดการอาจารย์
- ✅ เลือกอาจารย์ผู้สอน → บันทึกพร้อมกับรายวิชา
- ✅ ถ้ากลุ่มเรียนมีอาจารย์อยู่แล้ว → แสดงอาจารย์ปัจจุบัน

### 3. UI/UX
- ✅ ส่วนจัดการอาจารย์ซ่อนไว้จนกว่าจะเลือกกลุ่มเรียน
- ✅ แสดงข้อมูลกลุ่มเรียนที่เลือก
- ✅ Dropdown อาจารย์มี style ตรงกับ form อื่นๆ

---

## 🧪 การทดสอบ

### 1. ทดสอบหน้าเพิ่มรายวิชา
1. เข้าหน้า: `http://127.0.0.1:8000/academic/courses/add/`
2. กรอกข้อมูล: รหัสวิชา, ชื่อวิชา, หน่วยกิต
3. เลือกกลุ่มเรียนจาก dropdown
4. ตรวจสอบว่าส่วนจัดการอาจารย์แสดงขึ้นมา
5. เลือกอาจารย์ผู้สอน
6. บันทึก
7. ตรวจสอบว่าอาจารย์ถูกกำหนดให้กับกลุ่มเรียน

### 2. ทดสอบกรณีไม่มีกลุ่มเรียน
- ถ้ายังไม่มีกลุ่มเรียนในระบบ → dropdown จะว่างเปล่า และส่วนจัดการอาจารย์จะไม่แสดง

---

## 📋 Checklist

- [x] แก้ไข view - เพิ่ม `teachers` ใน context สำหรับหน้าเพิ่มรายวิชา
- [x] แก้ไข view - เพิ่ม `teacher_id_value` ใน existing_sections
- [x] แก้ไข view - จัดการ teacher assignment เมื่อสร้าง course ใหม่
- [x] แก้ไข template - เพิ่มส่วนจัดการอาจารย์ผู้สอน
- [x] เพิ่ม JavaScript - จัดการการแสดง/ซ่อนส่วนจัดการอาจารย์
- [x] แก้ไข template - เพิ่ม `data-teacher-id` ใน option
- [x] ตรวจสอบ linter errors
- [x] ทดสอบ Django system check

---

## 🎯 สรุป

**ปัญหา:** ไม่มีช่องจัดการอาจารย์ผู้สอนในหน้าเพิ่มรายวิชา  
**วิธีแก้:** เพิ่มส่วนจัดการอาจารย์ผู้สอนที่แสดงเมื่อเลือกกลุ่มเรียน  
**สถานะ:** ✅ **แก้ไขเสร็จสิ้น**

---

**อัปเดตล่าสุด:** 2025-11-11

