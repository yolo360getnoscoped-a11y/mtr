#!/usr/bin/env python
"""
สคริปต์ช่วยแก้ไขรหัสผ่าน PostgreSQL
"""
import getpass
import subprocess
import sys

print("=" * 60)
print("แก้ไขรหัสผ่าน PostgreSQL")
print("=" * 60)
print()

# วิธีที่ 1: ใช้รหัสผ่านปัจจุบันเพื่อเปลี่ยนเป็น 'postgres'
print("วิธีที่ 1: เปลี่ยนรหัสผ่าน PostgreSQL เป็น 'postgres'")
print("-" * 60)
current_password = getpass.getpass("กรุณากรอกรหัสผ่าน PostgreSQL ปัจจุบัน (ถ้าไม่ทราบ ให้กด Enter เพื่อข้าม): ")

if current_password:
    try:
        # ใช้ psql ผ่าน pgAdmin หรือ command line
        print("\nกรุณารันคำสั่งนี้ใน pgAdmin หรือ psql:")
        print("ALTER USER postgres WITH PASSWORD 'postgres';")
        print()
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

# วิธีที่ 2: แก้ไข .env ให้ใช้รหัสผ่านที่ถูกต้อง
print("\n" + "=" * 60)
print("วิธีที่ 2: แก้ไขไฟล์ .env ให้ใช้รหัสผ่านที่ถูกต้อง")
print("-" * 60)
new_password = getpass.getpass("กรุณากรอกรหัสผ่าน PostgreSQL ที่ถูกต้อง: ")

if new_password:
    try:
        # อ่านไฟล์ .env
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # แทนที่รหัสผ่าน
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.startswith('DB_PASSWORD='):
                new_lines.append(f'DB_PASSWORD={new_password}')
            else:
                new_lines.append(line)
        
        # เขียนไฟล์ .env ใหม่
        with open('.env', 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("\n✅ แก้ไขไฟล์ .env เรียบร้อยแล้ว!")
        print(f"   รหัสผ่านใหม่: {new_password}")
        print("\nตอนนี้ลองรัน Django server อีกครั้ง:")
        print("   python manage.py runserver 0.0.0.0:8000")
        
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        print("\nกรุณาแก้ไขไฟล์ .env ด้วยตนเอง:")
        print("   เปลี่ยน DB_PASSWORD=postgres เป็น DB_PASSWORD=[รหัสผ่านที่ถูกต้อง]")
else:
    print("\n❌ ไม่ได้กรอกรหัสผ่าน")
    print("\nกรุณาแก้ไขไฟล์ .env ด้วยตนเอง:")
    print("   เปลี่ยน DB_PASSWORD=postgres เป็น DB_PASSWORD=[รหัสผ่านที่ถูกต้อง]")

print("\n" + "=" * 60)

