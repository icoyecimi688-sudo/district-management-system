import sqlite3
import os
import hashlib
from datetime import datetime
import urllib.request
import pickle

REMOTE_SERVER_URL = None

def rpc_enabled(func):
    def wrapper(*args, **kwargs):
        if REMOTE_SERVER_URL:
            payload = pickle.dumps({
                "func": func.__name__,
                "args": args,
                "kwargs": kwargs
            })
            req = urllib.request.Request(
                REMOTE_SERVER_URL,
                data=payload,
                headers={'Content-Type': 'application/octet-stream'}
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_data = pickle.loads(response.read())
                    if isinstance(res_data, dict) and "error" in res_data:
                        print(f"RPC Error in {func.__name__}: {res_data['error']}")
                        return None
                    return res_data
            except Exception as e:
                print(f"Network Error in {func.__name__}: {e}")
                return None
        else:
            return func(*args, **kwargs)
    return wrapper

import sys
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "Hokimiyat_Data")
if not os.path.exists(DATA_DIR):
    try: os.makedirs(DATA_DIR)
    except: pass

DB_NAME = os.path.join(DATA_DIR, "hokimiyat.db")
if not os.path.exists(DB_NAME) and os.path.exists("hokimiyat.db"):
    try:
        import shutil
        shutil.copy("hokimiyat.db", DB_NAME)
    except: pass

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create people table with new columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            patronymic TEXT,
            passport TEXT DEFAULT '-',
            pinfl TEXT DEFAULT '-',
            birth_date TEXT,
            address TEXT,
            phone TEXT,
            position TEXT,
            secret_level INTEGER DEFAULT 1,
            photo_person BLOB,
            photo_passport BLOB,
            joined_date TEXT,
            left_date TEXT,
            is_active INTEGER DEFAULT 1,
            vacation_start TEXT,
            vacation_end TEXT,
            punishment_start TEXT,
            punishment_end TEXT,
            punishment_reason TEXT,
            email TEXT,
            marital_status TEXT,
            department TEXT,
            languages TEXT,
            certifications TEXT,
            projects TEXT,
            kpi_score INTEGER DEFAULT 0,
            birth_place TEXT,
            nationality TEXT,
            party_membership TEXT,
            education TEXT,
            graduated_from TEXT,
            education_specialty TEXT,
            academic_degree TEXT,
            academic_title TEXT,
            state_awards TEXT,
            deputy_status TEXT,
            employment_history TEXT,
            original_document BLOB,
            original_document_ext TEXT,
            is_external INTEGER DEFAULT 0
        )
    ''')
    
    # Migration: Try adding columns to existing database if they don't exist
    new_columns = [
        "joined_date TEXT", "left_date TEXT", "is_active INTEGER DEFAULT 1",
        "vacation_start TEXT", "vacation_end TEXT",
        "punishment_start TEXT", "punishment_end TEXT", "punishment_reason TEXT",
        "email TEXT", "marital_status TEXT", "department TEXT",
        "languages TEXT", "certifications TEXT", "projects TEXT", "kpi_score INTEGER DEFAULT 0",
        "meeting_status TEXT DEFAULT '⏳ Sababli'",
        "birth_place TEXT", "nationality TEXT", "party_membership TEXT",
        "education TEXT", "graduated_from TEXT", "education_specialty TEXT",
        "academic_degree TEXT", "academic_title TEXT", "state_awards TEXT",
        "deputy_status TEXT", "employment_history TEXT",
        "original_document BLOB", "original_document_ext TEXT",
        "is_external INTEGER DEFAULT 0"
    ]
    for col in new_columns:
        try:
            cursor.execute(f"ALTER TABLE people ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass # Column already exists
            
    # Create relatives table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relatives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            relationship TEXT,
            full_name TEXT,
            birth_info TEXT,
            work_info TEXT,
            residence TEXT
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL, -- 'user', 'owner', 'super_owner'
            access_level INTEGER DEFAULT 1
        )
    ''')
    
    # Create notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create activities table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            type TEXT NOT NULL, -- 'add', 'update', 'delete'
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Create meetings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            type TEXT,
            date_time TEXT,
            location TEXT,
            chairman TEXT,
            agenda TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Create meeting_attendees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meeting_attendees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER,
            person_id INTEGER,
            status TEXT DEFAULT '⏳ Kutilmoqda',
            UNIQUE(meeting_id, person_id)
        )
    ''')
    
    # Create organizations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            sector TEXT,
            leader TEXT,
            phone TEXT,
            address TEXT
        )
    ''')
    try:
        cursor.execute("ALTER TABLE organizations ADD COLUMN sector TEXT")
    except sqlite3.OperationalError: pass
    try:
        cursor.execute("ALTER TABLE organizations ADD COLUMN leader TEXT")
    except sqlite3.OperationalError: pass
    try:
        cursor.execute("ALTER TABLE organizations ADD COLUMN phone TEXT")
    except sqlite3.OperationalError: pass
    try:
        cursor.execute("ALTER TABLE organizations ADD COLUMN address TEXT")
    except sqlite3.OperationalError: pass
    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS internal_departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            date_str TEXT NOT NULL,
            status TEXT NOT NULL,
            UNIQUE(person_id, date_str)
        )
    ''')
    
    # Insert default super owner if no users exist
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO users (username, password, role, access_level)
            VALUES (?, ?, ?, ?)
        ''', ('admin', hash_password('admin123'), 'super_owner', 6))
        
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def auto_expire_records():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Clear vacation if end date is passed
    cursor.execute('''
        UPDATE people SET vacation_start = NULL, vacation_end = NULL 
        WHERE vacation_end IS NOT NULL AND vacation_end < ?
    ''', (today,))
    
    # Clear punishment if end date is passed
    cursor.execute('''
        UPDATE people SET punishment_start = NULL, punishment_end = NULL, punishment_reason = NULL 
        WHERE punishment_end IS NOT NULL AND punishment_end < ?
    ''', (today,))
    
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def login(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role, access_level FROM users WHERE username = ? AND password = ?', (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

@rpc_enabled
def add_person(first_name, last_name, patronymic, passport, pinfl, birth_date, address, phone, position, secret_level, photo_person, photo_passport, joined_date, email, marital_status, department, languages, certifications, projects, kpi_score):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO people (first_name, last_name, patronymic, passport, pinfl, birth_date, address, phone, position, secret_level, photo_person, photo_passport, joined_date, is_active, email, marital_status, department, languages, certifications, projects, kpi_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?)
    ''', (first_name, last_name, patronymic, passport, pinfl, birth_date, address, phone, position, secret_level, photo_person, photo_passport, joined_date, email, marital_status, department, languages, certifications, projects, kpi_score))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def add_guest(full_name, department, phone="", position=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Split full name into first and last
    parts = full_name.strip().split(maxsplit=1)
    first = parts[0] if parts else ""
    last = parts[1] if len(parts) > 1 else ""
    cursor.execute('''
        INSERT INTO people (first_name, last_name, department, phone, position, secret_level, is_active, meeting_status, passport, pinfl, is_external)
        VALUES (?, ?, ?, ?, ?, 1, 1, '⏳ Sababli', '-', '-', 1)
    ''', (first, last, department, phone, position))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def update_person(person_id, first_name, last_name, patronymic, passport, pinfl, birth_date, address, phone, position, secret_level, photo_person, photo_passport, joined_date, email, marital_status, department, languages, certifications, projects, kpi_score):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # If photo_person or photo_passport is None, we might not want to overwrite existing ones if they exist, but for simplicity we will overwrite or update only if provided, or handle it in the app logic.
    # Let's do a direct update
    if photo_person is not None and photo_passport is not None:
        cursor.execute('''
            UPDATE people SET first_name=?, last_name=?, patronymic=?, passport=?, pinfl=?, birth_date=?, address=?, phone=?, position=?, secret_level=?, photo_person=?, photo_passport=?, joined_date=?, email=?, marital_status=?, department=?, languages=?, certifications=?, projects=?, kpi_score=?
            WHERE id=?
        ''', (first_name, last_name, patronymic, passport, pinfl, birth_date, address, phone, position, secret_level, photo_person, photo_passport, joined_date, email, marital_status, department, languages, certifications, projects, kpi_score, person_id))
    elif photo_person is not None:
        cursor.execute('''
            UPDATE people SET first_name=?, last_name=?, patronymic=?, passport=?, pinfl=?, birth_date=?, address=?, phone=?, position=?, secret_level=?, photo_person=?, joined_date=?, email=?, marital_status=?, department=?, languages=?, certifications=?, projects=?, kpi_score=?
            WHERE id=?
        ''', (first_name, last_name, patronymic, passport, pinfl, birth_date, address, phone, position, secret_level, photo_person, joined_date, email, marital_status, department, languages, certifications, projects, kpi_score, person_id))
    elif photo_passport is not None:
        cursor.execute('''
            UPDATE people SET first_name=?, last_name=?, patronymic=?, passport=?, pinfl=?, birth_date=?, address=?, phone=?, position=?, secret_level=?, photo_passport=?, joined_date=?, email=?, marital_status=?, department=?, languages=?, certifications=?, projects=?, kpi_score=?
            WHERE id=?
        ''', (first_name, last_name, patronymic, passport, pinfl, birth_date, address, phone, position, secret_level, photo_passport, joined_date, email, marital_status, department, languages, certifications, projects, kpi_score, person_id))
    else:
        cursor.execute('''
            UPDATE people SET first_name=?, last_name=?, patronymic=?, passport=?, pinfl=?, birth_date=?, address=?, phone=?, position=?, secret_level=?, joined_date=?, email=?, marital_status=?, department=?, languages=?, certifications=?, projects=?, kpi_score=?
            WHERE id=?
        ''', (first_name, last_name, patronymic, passport, pinfl, birth_date, address, phone, position, secret_level, joined_date, email, marital_status, department, languages, certifications, projects, kpi_score, person_id))
        
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def get_people(user_access_level, is_active=1, department_filter=None):
    auto_expire_records()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if department_filter:
        cursor.execute('''
            SELECT id, first_name, last_name, patronymic, passport, pinfl, birth_date, address, phone, position, secret_level, joined_date, left_date, vacation_start, vacation_end, punishment_start, punishment_end, punishment_reason, email, marital_status, department, languages, certifications, projects, kpi_score, meeting_status, is_active
            FROM people WHERE secret_level <= ? AND is_active = ? AND is_external = 0 AND department = ?
        ''', (user_access_level, is_active, department_filter))
    else:
        cursor.execute('''
            SELECT id, first_name, last_name, patronymic, passport, pinfl, birth_date, address, phone, position, secret_level, joined_date, left_date, vacation_start, vacation_end, punishment_start, punishment_end, punishment_reason, email, marital_status, department, languages, certifications, projects, kpi_score, meeting_status, is_active
            FROM people WHERE secret_level <= ? AND is_active = ? AND is_external = 0
        ''', (user_access_level, is_active))
        
    rows = cursor.fetchall()
    conn.close()
    return rows

@rpc_enabled
def get_special_people(user_access_level, category):
    auto_expire_records()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    base_query = '''
        SELECT id, first_name, last_name, patronymic, passport, pinfl, birth_date, address, phone, position, secret_level, joined_date, left_date, vacation_start, vacation_end, punishment_start, punishment_end, punishment_reason, email, marital_status, department, languages, certifications, projects, kpi_score, meeting_status, is_active
        FROM people WHERE secret_level <= ? AND is_external = 0
    '''
    
    if category == "Bo'shaganlar":
        query = base_query + " AND is_active = 0"
    elif category == "Ta'tildagilar":
        query = base_query + " AND is_active = 1 AND vacation_end IS NOT NULL AND vacation_end >= date('now')"
    elif category == 'Jazodagilar':
        query = base_query + " AND is_active = 1 AND punishment_reason IS NOT NULL AND punishment_reason != ''"
    else:
        query = base_query + " AND is_active = 0"
        
    cursor.execute(query, (user_access_level,))
    rows = cursor.fetchall()
    conn.close()
    return rows

@rpc_enabled
def get_person_by_id(person_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, first_name, last_name, patronymic, passport, pinfl, birth_date, address, phone, position, secret_level, joined_date, left_date, vacation_start, vacation_end, punishment_start, punishment_end, punishment_reason, is_active, email, marital_status, department, languages, certifications, projects, kpi_score, meeting_status
        FROM people WHERE id = ?
    ''', (person_id,))
    row = cursor.fetchone()
    conn.close()
    return row

@rpc_enabled
def delete_person(person_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM meeting_attendees WHERE person_id = ?', (person_id,))
    cursor.execute('DELETE FROM attendance WHERE person_id = ?', (person_id,))
    cursor.execute('DELETE FROM people WHERE id = ?', (person_id,))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

# New Actions
@rpc_enabled
def activate_person(person_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''UPDATE people 
                      SET is_active = 1, left_date = NULL, 
                          vacation_start = NULL, vacation_end = NULL, 
                          punishment_start = NULL, punishment_end = NULL, punishment_reason = NULL 
                      WHERE id = ?''', (person_id,))
    conn.commit()
    conn.close()
    return person_id

@rpc_enabled
def set_left_job(person_id, left_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''UPDATE people 
                      SET is_active = 0, left_date = ?, 
                          vacation_start = NULL, vacation_end = NULL, 
                          punishment_start = NULL, punishment_end = NULL, punishment_reason = NULL 
                      WHERE id = ?''', (left_date, person_id))
    conn.commit()
    conn.close()
    return person_id

@rpc_enabled
def assign_department(person_id, department):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE people SET department = ? WHERE id = ?', (department, person_id))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def set_meeting_status(person_id, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE people SET meeting_status = ? WHERE id = ?', (status, person_id))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def set_vacation(person_id, start_date, end_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''UPDATE people 
                      SET is_active = 1, vacation_start = ?, vacation_end = ?, 
                          punishment_start = NULL, punishment_end = NULL, punishment_reason = NULL, left_date = NULL 
                      WHERE id = ?''', (start_date, end_date, person_id))
    conn.commit()
    conn.close()
    return person_id

@rpc_enabled
def clear_vacation(person_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE people SET vacation_start = NULL, vacation_end = NULL WHERE id = ?', (person_id,))
    conn.commit()
    conn.close()
    return person_id

@rpc_enabled
def set_punishment(person_id, start_date, end_date, reason):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''UPDATE people 
                      SET is_active = 1, punishment_start = ?, punishment_end = ?, punishment_reason = ?, 
                          vacation_start = NULL, vacation_end = NULL, left_date = NULL 
                      WHERE id = ?''', (start_date, end_date, reason, person_id))
    conn.commit()
    conn.close()
    return person_id

@rpc_enabled
def clear_punishment(person_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE people SET punishment_start = NULL, punishment_end = NULL, punishment_reason = NULL WHERE id = ?', (person_id,))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

# Users management
@rpc_enabled
def get_users_count():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        return count
    except:
        return 0
    finally:
        conn.close()

@rpc_enabled
def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role, access_level FROM users')
    rows = cursor.fetchall()
    conn.close()
    return rows

@rpc_enabled
def add_user(username, password, role, access_level):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, password, role, access_level)
            VALUES (?, ?, ?, ?)
        ''', (username, hash_password(password), role, access_level))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        cursor.execute('''
            UPDATE users SET password = ?, role = ?, access_level = ? WHERE username = ?
        ''', (hash_password(password), role, access_level, username))
        conn.commit()
        return True
    finally:
        conn.close()

@rpc_enabled
def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role, access_level FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

@rpc_enabled
def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def update_user_role(user_id, role, access_level):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET role = ?, access_level = ? WHERE id = ?', (role, access_level, user_id))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def get_super_owner():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE role = 'super_owner' LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row

# Notifications
@rpc_enabled
def add_notification(user_id, message):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO notifications (user_id, message) VALUES (?, ?)', (user_id, message))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def get_unread_notifications(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, message, timestamp FROM notifications WHERE user_id = ? AND is_read = 0', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

@rpc_enabled
def mark_notifications_read(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def get_person_images(person_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT photo_person, photo_passport FROM people WHERE id = ?', (person_id,))
    row = cursor.fetchone()
    conn.close()
    return row

@rpc_enabled
def update_password(user_id, old_password, new_password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE id = ? AND password = ?', (user_id, hash_password(old_password)))
    if cursor.fetchone():
        cursor.execute('UPDATE users SET password = ? WHERE id = ?', (hash_password(new_password), user_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

# Dashboard & Activities
@rpc_enabled
def add_activity(message, act_type='add'):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO activities (message, type) VALUES (?, ?)', (message, act_type))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def get_recent_activities(limit=20):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT message, type, timestamp FROM activities ORDER BY id DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

@rpc_enabled
def get_dashboard_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM people WHERE is_active=1')
    active_people = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT department) FROM people WHERE department IS NOT NULL AND department != ""')
    total_depts = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT access_level) FROM users')
    access_levels = cursor.fetchone()[0]
    
    conn.close()
    return active_people, total_users, total_depts, access_levels

@rpc_enabled
def get_department_distribution():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT department, COUNT(*) 
        FROM people 
        WHERE is_active=1 AND department IS NOT NULL AND department != ""
        GROUP BY department
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

@rpc_enabled
def get_all_people_full(user_access_level=3):
    return get_people(user_access_level, is_active=1)

@rpc_enabled
def get_attendance_for_month(month_str):
    return get_attendance(month_str)

# Organizations
@rpc_enabled
def get_organizations():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, sector, leader, phone, address FROM organizations ORDER BY name
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

@rpc_enabled
def add_organization(name, sector="", leader="", phone="", address=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO organizations (name, sector, leader, phone, address) VALUES (?, ?, ?, ?, ?)', (name, sector, leader, phone, address))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

@rpc_enabled
def update_organization(org_id, name, sector="", leader="", phone="", address=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT name FROM organizations WHERE id = ?', (org_id,))
        old_row = cursor.fetchone()
        old_name = old_row[0] if old_row else None
        
        cursor.execute('''
            UPDATE organizations 
            SET name = ?, sector = ?, leader = ?, phone = ?, address = ? 
            WHERE id = ?
        ''', (name, sector, leader, phone, address, org_id))
        
        if old_name and old_name != name:
            cursor.execute('UPDATE people SET department = ? WHERE department = ?', (name, old_name))
            
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

@rpc_enabled
def delete_organization(org_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM organizations WHERE id = ?', (org_id,))
    row = cursor.fetchone()
    if row and row[0]:
        org_name = row[0]
        cursor.execute('''
            DELETE FROM meeting_attendees 
            WHERE person_id IN (SELECT id FROM people WHERE department = ?)
        ''', (org_name,))
        cursor.execute('DELETE FROM people WHERE department = ?', (org_name,))
    cursor.execute('DELETE FROM organizations WHERE id = ?', (org_id,))
    conn.commit()
    conn.close()
    return True

@rpc_enabled
def update_external_person(person_id, first_name, last_name, position="", phone=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE people SET first_name = ?, last_name = ?, position = ?, phone = ? WHERE id = ?
    ''', (first_name, last_name, position, phone, person_id))
    conn.commit()
    conn.close()
    return person_id

@rpc_enabled
def get_internal_departments():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM internal_departments ORDER BY name')
    rows = cursor.fetchall()
    conn.close()
    return rows

@rpc_enabled
def add_internal_department(name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO internal_departments (name) VALUES (?)', (name,))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

@rpc_enabled
def delete_internal_department(dept_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM internal_departments WHERE id = ?', (dept_id,))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def get_people_by_org(org_name, user_access_level):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if org_name == "(Ichki) Barcha xodimlar":
        cursor.execute('''
            SELECT id, first_name, last_name, position, phone, meeting_status 
            FROM people 
            WHERE secret_level <= ? AND is_active = 1 AND (is_external = 0 OR is_external IS NULL)
            ORDER BY first_name, last_name
        ''', (user_access_level,))
    elif org_name.startswith("(Ichki) "):
        real_org = org_name[8:]
        cursor.execute('''
            SELECT id, first_name, last_name, position, phone, meeting_status 
            FROM people 
            WHERE department = ? AND secret_level <= ? AND is_active = 1 AND (is_external = 0 OR is_external IS NULL)
            ORDER BY first_name, last_name
        ''', (real_org, user_access_level))
    else:
        cursor.execute('''
            SELECT id, first_name, last_name, position, phone, meeting_status 
            FROM people 
            WHERE department = ? AND secret_level <= ? AND is_active = 1 AND is_external = 1
            ORDER BY first_name, last_name
        ''', (org_name, user_access_level))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Attendance
@rpc_enabled
def get_attendance(month_str):
    """month_str is 'YYYY-MM' format"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Returns (person_id, date_str, status)
    cursor.execute("SELECT person_id, date_str, status FROM attendance WHERE date_str LIKE ?", (f"{month_str}-%",))
    rows = cursor.fetchall()
    conn.close()
    return rows

@rpc_enabled
def set_attendance(person_id, date_str, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Upsert logic (requires SQLite 3.24+)
    try:
        cursor.execute('''
            INSERT INTO attendance (person_id, date_str, status) 
            VALUES (?, ?, ?)
            ON CONFLICT(person_id, date_str) DO UPDATE SET status = excluded.status
        ''', (person_id, date_str, status))
    except sqlite3.OperationalError:
        # Fallback for older SQLite versions
        cursor.execute('SELECT id FROM attendance WHERE person_id = ? AND date_str = ?', (person_id, date_str))
        if cursor.fetchone():
            cursor.execute('UPDATE attendance SET status = ? WHERE person_id = ? AND date_str = ?', (status, person_id, date_str))
        else:
            cursor.execute('INSERT INTO attendance (person_id, date_str, status) VALUES (?, ?, ?)', (person_id, date_str, status))
            
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def mark_absent_for_past_days(month_str, today_str):
    from datetime import datetime, timedelta
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM people WHERE is_active=1')
    people = cursor.fetchall()
    
    today_dt = datetime.strptime(today_str, "%Y-%m-%d")
    start_dt = datetime.strptime(month_str + "-01", "%Y-%m-%d")
    
    days_to_check = []
    curr = start_dt
    while curr < today_dt:
        if curr.weekday() < 6:
            days_to_check.append(curr.strftime("%Y-%m-%d"))
        curr += timedelta(days=1)
        
    for p in people:
        pid = p[0]
        for d in days_to_check:
            try:
                cursor.execute('''
                    INSERT INTO attendance (person_id, date_str, status) 
                    VALUES (?, ?, ?)
                    ON CONFLICT(person_id, date_str) DO NOTHING
                ''', (pid, d, '-'))
            except sqlite3.OperationalError:
                cursor.execute('SELECT id FROM attendance WHERE person_id = ? AND date_str = ?', (pid, d))
                if not cursor.fetchone():
                    cursor.execute('INSERT INTO attendance (person_id, date_str, status) VALUES (?, ?, ?)', (pid, d, '-'))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def add_meeting(title, m_type, date_time, location, chairman, agenda):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO meetings (title, type, date_time, location, chairman, agenda, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    ''', (title, m_type, date_time, location, chairman, agenda))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id
    return True

@rpc_enabled
def get_meeting(meeting_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, type, date_time, location, chairman, agenda FROM meetings WHERE id = ?', (meeting_id,))
    row = cursor.fetchone()
    conn.close()
    return row

@rpc_enabled
def get_meetings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, type, date_time, location, chairman, agenda FROM meetings WHERE is_active = 1 ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

@rpc_enabled
def delete_meeting(meeting_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE meetings SET is_active = 0 WHERE id = ?', (meeting_id,))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def add_meeting_attendee(meeting_id, person_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO meeting_attendees (meeting_id, person_id, status)
            VALUES (?, ?, '⏳ Kutilmoqda')
        ''', (meeting_id, person_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Already added
    finally:
        conn.close()

@rpc_enabled
def delete_meeting_attendee(meeting_id, person_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM meeting_attendees WHERE meeting_id = ? AND person_id = ?', (meeting_id, person_id))
    conn.commit()
    conn.close()
    return True

@rpc_enabled
def delete_all_organizations():
    target_dbs = [DB_NAME, "hokimiyat.db", os.path.join(BASE_DIR, "hokimiyat.db")]
    for db_path in set(target_dbs):
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM organizations')
                cursor.execute('DELETE FROM people WHERE is_external = 1 OR (department IS NOT NULL AND department != "")')
                cursor.execute('DELETE FROM meeting_attendees')
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error purging {db_path}: {e}")
    return True

@rpc_enabled
def add_external_person(first_name, last_name, department, position="", phone=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO people (first_name, last_name, department, phone, position, secret_level, is_active, meeting_status, passport, pinfl, is_external)
        VALUES (?, ?, ?, ?, ?, 1, 1, '⏳ Sababli', '-', '-', 1)
    ''', (first_name, last_name, department, phone, position))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def get_meeting_attendees(meeting_id, access_level=1):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, p.first_name, p.last_name, p.position, p.phone, p.department, ma.status, p.patronymic, p.is_external, org.sector
        FROM meeting_attendees ma
        JOIN people p ON ma.person_id = p.id
        LEFT JOIN organizations org ON p.department = org.name
        WHERE ma.meeting_id = ? AND p.secret_level <= ?
    ''', (meeting_id, access_level))
    rows = cursor.fetchall()
    conn.close()
    return rows

@rpc_enabled
def set_meeting_attendee_status(meeting_id, person_id, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE meeting_attendees
        SET status = ?
        WHERE meeting_id = ? AND person_id = ?
    ''', (status, meeting_id, person_id))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def seed_mock_meetings_if_empty():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM meetings')
    if cursor.fetchone()[0] == 0:
        meetings = [
            ("Haftalik Apparat Yig'ilishi", "Apparat yig'ilishi", "2026-07-15 10:00", "Katta Zal - 3-qavat", "Viloyat Hokimi", "1-yillik hisobotlar tahlili"),
            ("Navbatdagi Kengash Yig'ilishi", "Kengash", "2026-07-16 14:00", "Kichik Zal - 2-qavat", "Hokim O'rinbosari", "Yangi loyihalar muhokamasi")
        ]
        for m in meetings:
            cursor.execute('''
                INSERT INTO meetings (title, type, date_time, location, chairman, agenda, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', m)
        conn.commit()
        
        # Add random people to first meeting
        cursor.execute('SELECT id FROM meetings LIMIT 1')
        m_id = cursor.fetchone()[0]
        cursor.execute('SELECT id FROM people LIMIT 5')
        people = cursor.fetchall()
        for p in people:
            cursor.execute('''
                INSERT INTO meeting_attendees (meeting_id, person_id, status)
                VALUES (?, ?, '⏳ Kutilmoqda')
            ''', (m_id, p[0]))
        conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

@rpc_enabled
def get_person_document(person_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT original_document, original_document_ext FROM people WHERE id=?", (person_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (None, None)

@rpc_enabled
def update_person_document(person_id, doc, ext):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE people SET original_document=?, original_document_ext=? WHERE id=?", (doc, ext, person_id))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id


@rpc_enabled
def add_person_objective(data, relatives_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    passport = (data.get('passport') or '-').strip()
    if not passport: passport = '-'
    pinfl = (data.get('pinfl') or '-').strip()
    if not pinfl: pinfl = '-'
    
    photo_person = data.get('photo_person_bytes') if isinstance(data.get('photo_person_bytes'), bytes) else (data.get('photo_person') if isinstance(data.get('photo_person'), bytes) else None)
    photo_passport = data.get('photo_passport_bytes') if isinstance(data.get('photo_passport_bytes'), bytes) else (data.get('photo_passport') if isinstance(data.get('photo_passport'), bytes) else None)
    original_doc = data.get('original_document_bytes') if isinstance(data.get('original_document_bytes'), bytes) else (data.get('original_document') if isinstance(data.get('original_document'), bytes) else None)
    
    try:
        cursor.execute("""
            INSERT INTO people (
                first_name, last_name, patronymic, passport, pinfl, birth_date, address, phone, position, secret_level, 
                photo_person, photo_passport, joined_date, is_active, department, languages,
                birth_place, nationality, party_membership, education, graduated_from, education_specialty,
                academic_degree, academic_title, state_awards, deputy_status, employment_history, original_document, original_document_ext
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                ?, ?, ?, 1, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            data.get('first_name', ''), data.get('last_name', ''), data.get('patronymic', ''),
            passport, pinfl, data.get('birth_date', ''),
            data.get('address', ''), data.get('phone', ''), data.get('position', ''), int(data.get('secret_level', 1)),
            photo_person, photo_passport, data.get('joined_date', ''),
            data.get('department', ''), data.get('languages', ''),
            data.get('birth_place', ''), data.get('nationality', ''), data.get('party_membership', ''),
            data.get('education', ''), data.get('graduated_from', ''), data.get('education_specialty', ''),
            data.get('academic_degree', ''), data.get('academic_title', ''), data.get('state_awards', ''),
            data.get('deputy_status', ''), data.get('employment_history', ''),
            original_doc, data.get('original_document_ext', '.docx')
        ))
        person_id = cursor.lastrowid
        
        if relatives_data:
            for r in relatives_data:
                cursor.execute("""
                    INSERT INTO relatives (person_id, relationship, full_name, birth_info, work_info, residence)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (person_id, r.get('relationship',''), r.get('full_name',''), r.get('birth_info',''), r.get('work_info',''), r.get('residence','')))
                
        conn.commit()
        return person_id
    except Exception as e:
        print(f"Error in add_person_objective: {e}")
        return {"error": f"Saqlashda xatolik: {str(e)}"}
    finally:
        conn.close()

@rpc_enabled
def update_person_objective(person_id, data, relatives_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    passport = (data.get('passport') or '-').strip()
    if not passport: passport = '-'
    pinfl = (data.get('pinfl') or '-').strip()
    if not pinfl: pinfl = '-'
    
    update_fields = [
        "first_name=?", "last_name=?", "patronymic=?", "passport=?", "pinfl=?", "birth_date=?", "address=?", "phone=?", "position=?", 
        "secret_level=?", "joined_date=?", "department=?", "languages=?",
        "birth_place=?", "nationality=?", "party_membership=?", "education=?", "graduated_from=?", "education_specialty=?",
        "academic_degree=?", "academic_title=?", "state_awards=?", "deputy_status=?", "employment_history=?"
    ]
    
    params = [
        data.get('first_name', ''), data.get('last_name', ''), data.get('patronymic', ''),
        passport, pinfl, data.get('birth_date', ''),
        data.get('address', ''), data.get('phone', ''), data.get('position', ''), int(data.get('secret_level', 1)),
        data.get('joined_date', ''), data.get('department', ''), data.get('languages', ''),
        data.get('birth_place', ''), data.get('nationality', ''), data.get('party_membership', ''),
        data.get('education', ''), data.get('graduated_from', ''), data.get('education_specialty', ''),
        data.get('academic_degree', ''), data.get('academic_title', ''), data.get('state_awards', ''),
        data.get('deputy_status', ''), data.get('employment_history', '')
    ]
    
    photo_person = data.get('photo_person_bytes') if isinstance(data.get('photo_person_bytes'), bytes) else (data.get('photo_person') if isinstance(data.get('photo_person'), bytes) else None)
    photo_passport = data.get('photo_passport_bytes') if isinstance(data.get('photo_passport_bytes'), bytes) else (data.get('photo_passport') if isinstance(data.get('photo_passport'), bytes) else None)
    original_doc = data.get('original_document_bytes') if isinstance(data.get('original_document_bytes'), bytes) else (data.get('original_document') if isinstance(data.get('original_document'), bytes) else None)
    
    if photo_person is not None:
        update_fields.append("photo_person=?")
        params.append(photo_person)
    if photo_passport is not None:
        update_fields.append("photo_passport=?")
        params.append(photo_passport)
    if original_doc is not None:
        update_fields.append("original_document=?")
        update_fields.append("original_document_ext=?")
        params.append(original_doc)
        params.append(data.get('original_document_ext', '.docx'))
        
    params.append(person_id)
    
    try:
        query = f"UPDATE people SET {', '.join(update_fields)} WHERE id=?"
        cursor.execute(query, tuple(params))
        
        cursor.execute("DELETE FROM relatives WHERE person_id=?", (person_id,))
        if relatives_data:
            for r in relatives_data:
                cursor.execute("""
                    INSERT INTO relatives (person_id, relationship, full_name, birth_info, work_info, residence)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (person_id, r.get('relationship',''), r.get('full_name',''), r.get('birth_info',''), r.get('work_info',''), r.get('residence','')))
                
        conn.commit()
        return person_id
    except Exception as e:
        print(f"Error updating person objective: {e}")
        return {"error": f"Yangilashda xatolik: {str(e)}"}
    finally:
        conn.close()

@rpc_enabled
def get_person_objective(person_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM people WHERE id=?", (person_id,))
    row = cursor.fetchone()
    
    # Get column names
    col_names = [description[0] for description in cursor.description]
    
    conn.close()
    if row:
        return dict(zip(col_names, row))
    return None

@rpc_enabled
def get_relatives(person_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT relationship, full_name, birth_info, work_info, residence FROM relatives WHERE person_id=?", (person_id,))
    rows = cursor.fetchall()
    conn.close()
    
    relatives = []
    for row in rows:
        relatives.append({
            'relationship': row[0],
            'full_name': row[1],
            'birth_info': row[2],
            'work_info': row[3],
            'residence': row[4]
        })
    return relatives

@rpc_enabled
def get_all_positions():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT position FROM people WHERE position IS NOT NULL AND position != "" ORDER BY position')
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows if r[0]]
    except Exception as e:
        print("get_all_positions error:", e)
        return []

@rpc_enabled
def get_all_meeting_titles():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT id, title FROM meetings WHERE is_active = 1 ORDER BY title')
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print("get_all_meeting_titles error:", e)
        return []
