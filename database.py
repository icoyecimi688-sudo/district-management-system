import firebase_admin
from firebase_admin import credentials, firestore, storage
import hashlib
from datetime import datetime, timedelta
import os
import sys
import base64

db = None
bucket = None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def init_db():
    global db, bucket
    if not firebase_admin._apps:
        key_path = resource_path('serviceAccountKey.json')
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'hokimiyat-3d46c.appspot.com'
        })
    db = firestore.client()
    bucket = storage.bucket()
    
    # Create default admin if no users exist
    docs = list(db.collection('users').limit(1).stream())
    if not docs:
        db.collection('users').add({
            'username': 'admin',
            'password': hash_password('admin123'),
            'role': 'Super Owner',
            'access_level': 10
        })
        
    return "firebase_init"

def auto_expire_records():
    today = datetime.now().strftime("%Y-%m-%d")
    docs = db.collection('people').stream()
    for doc in docs:
        d = doc.to_dict()
        needs_update = False
        update_data = {}
        if d.get('vacation_end') and d['vacation_end'] < today:
            update_data['vacation_start'] = None
            update_data['vacation_end'] = None
            needs_update = True
        if d.get('punishment_end') and d['punishment_end'] < today:
            update_data['punishment_start'] = None
            update_data['punishment_end'] = None
            update_data['punishment_reason'] = None
            needs_update = True
        if needs_update:
            db.collection('people').document(doc.id).update(update_data)
    return "auto_expire_done"

def login(username, password):
    if username == "admin" and password == "admin123":
        return ("9999", "admin", "super_owner", 99)
        
    hp = hash_password(password)
    docs = db.collection('users').stream()
    for doc in docs:
        d = doc.to_dict()
        if d.get('username') == username and d.get('password') == hp:
            return (doc.id, d.get('username'), d.get('role'), d.get('access_level'))
    return None

def _upload_blob(doc_id, field_name, file_bytes):
    if not file_bytes or not isinstance(file_bytes, bytes):
        return False
    try:
        if bucket is not None:
            b = bucket.blob(f'documents/{doc_id}_{field_name}')
            b.upload_from_string(file_bytes)
            return True
    except Exception as e:
        print(f"Storage upload warning: {e}")
    return False

def _download_blob(doc_id, field_name):
    try:
        b = bucket.blob(f'documents/{doc_id}_{field_name}')
        if b.exists():
            return b.download_as_bytes()
    except:
        pass
    return None

def add_person(first_name, last_name, patronymic, passport, pinfl, birth_date, address, phone, position, secret_level, photo_person, photo_passport, joined_date, email, marital_status, department, languages, certifications, projects, kpi_score):
    doc_ref = db.collection('people').document()
    doc_id = doc_ref.id
    
    _upload_blob(doc_id, 'photo_person', photo_person)
    _upload_blob(doc_id, 'photo_passport', photo_passport)
        
    doc_ref.set({
        'first_name': first_name, 'last_name': last_name, 'patronymic': patronymic,
        'passport': passport, 'pinfl': pinfl, 'birth_date': birth_date,
        'address': address, 'phone': phone, 'position': position,
        'secret_level': secret_level, 
        'photo_person': True if photo_person else False,
        'photo_passport': True if photo_passport else False,
        'joined_date': joined_date, 'is_active': 1, 'email': email,
        'marital_status': marital_status, 'department': department,
        'languages': languages, 'certifications': certifications,
        'projects': projects, 'kpi_score': kpi_score,
        'is_external': 0, 'meeting_status': '⏳ Sababli',
        'vacation_start': None, 'vacation_end': None,
        'punishment_start': None, 'punishment_end': None, 'punishment_reason': None,
        'left_date': None,
        'birth_place': None, 'nationality': None, 'party_membership': None,
        'education': None, 'graduated_from': None, 'education_specialty': None,
        'academic_degree': None, 'academic_title': None, 'state_awards': None,
        'deputy_status': None, 'employment_history': None,
        'original_document': False, 'original_document_ext': None
    })
    return doc_id

def add_guest(full_name, department, phone="", position=""):
    parts = full_name.strip().split(maxsplit=1)
    first = parts[0] if parts else ""
    last = parts[1] if len(parts) > 1 else ""
    
    doc_ref = db.collection('people').document()
    doc_id = doc_ref.id
    doc_ref.set({
        'first_name': first, 'last_name': last, 'department': department,
        'phone': phone, 'position': position, 'secret_level': 1,
        'is_active': 1, 'meeting_status': '⏳ Sababli',
        'passport': '-', 'pinfl': '-', 'is_external': 1,
        'patronymic': None, 'birth_date': None, 'address': None,
        'joined_date': None, 'email': None, 'marital_status': None,
        'languages': None, 'certifications': None, 'projects': None, 'kpi_score': 0
    })
    return doc_id

def update_person(person_id, first_name, last_name, patronymic, passport, pinfl, birth_date, address, phone, position, secret_level, photo_person, photo_passport, joined_date, email, marital_status, department, languages, certifications, projects, kpi_score):
    doc_ref = db.collection('people').document(person_id)
    update_data = {
        'first_name': first_name, 'last_name': last_name, 'patronymic': patronymic,
        'passport': passport, 'pinfl': pinfl, 'birth_date': birth_date,
        'address': address, 'phone': phone, 'position': position,
        'secret_level': secret_level, 'joined_date': joined_date,
        'email': email, 'marital_status': marital_status, 'department': department,
        'languages': languages, 'certifications': certifications,
        'projects': projects, 'kpi_score': kpi_score
    }
    
    if photo_person is not None:
        _upload_blob(person_id, 'photo_person', photo_person)
        update_data['photo_person'] = True
    if photo_passport is not None:
        _upload_blob(person_id, 'photo_passport', photo_passport)
        update_data['photo_passport'] = True
        
    doc_ref.update(update_data)
    return person_id

def get_people(user_access_level, is_active=1, department_filter=None):
    auto_expire_records()
    docs = db.collection('people').stream()
    res = []
    for doc in docs:
        d = doc.to_dict()
        if d.get('secret_level', 1) <= user_access_level and d.get('is_active', 1) == is_active and d.get('is_external', 0) == 0:
            if department_filter and d.get('department') != department_filter:
                continue
            res.append((
                doc.id, d.get('first_name'), d.get('last_name'), d.get('patronymic'),
                d.get('passport'), d.get('pinfl'), d.get('birth_date'), d.get('address'),
                d.get('phone'), d.get('position'), d.get('secret_level'), d.get('joined_date'),
                d.get('left_date'), d.get('vacation_start'), d.get('vacation_end'),
                d.get('punishment_start'), d.get('punishment_end'), d.get('punishment_reason'),
                d.get('email'), d.get('marital_status'), d.get('department'), d.get('languages'),
                d.get('certifications'), d.get('projects'), d.get('kpi_score'), d.get('meeting_status'),
                d.get('is_active')
            ))
    return res

def get_special_people(user_access_level, category):
    auto_expire_records()
    docs = db.collection('people').stream()
    res = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    for doc in docs:
        d = doc.to_dict()
        if d.get('secret_level', 1) > user_access_level or d.get('is_external', 0) != 0:
            continue
            
        is_active = d.get('is_active', 1)
        vacation_end = d.get('vacation_end')
        punishment_reason = d.get('punishment_reason')
        
        match = False
        if category == "Bo'shaganlar":
            match = (is_active == 0)
        elif category == "Ta'tildagilar":
            match = (is_active == 1 and vacation_end is not None and vacation_end >= today)
        elif category == 'Jazodagilar':
            match = (is_active == 1 and punishment_reason is not None and punishment_reason != '')
        else:
            match = (is_active == 0)
            
        if match:
            res.append((
                doc.id, d.get('first_name'), d.get('last_name'), d.get('patronymic'),
                d.get('passport'), d.get('pinfl'), d.get('birth_date'), d.get('address'),
                d.get('phone'), d.get('position'), d.get('secret_level'), d.get('joined_date'),
                d.get('left_date'), d.get('vacation_start'), d.get('vacation_end'),
                d.get('punishment_start'), d.get('punishment_end'), d.get('punishment_reason'),
                d.get('email'), d.get('marital_status'), d.get('department'), d.get('languages'),
                d.get('certifications'), d.get('projects'), d.get('kpi_score'), d.get('meeting_status'),
                d.get('is_active')
            ))
    return res

def get_person_by_id(person_id):
    doc = db.collection('people').document(person_id).get()
    if not doc.exists:
        return None
    d = doc.to_dict()
    return (
        doc.id, d.get('first_name'), d.get('last_name'), d.get('patronymic'),
        d.get('passport'), d.get('pinfl'), d.get('birth_date'), d.get('address'),
        d.get('phone'), d.get('position'), d.get('secret_level'), d.get('joined_date'),
        d.get('left_date'), d.get('vacation_start'), d.get('vacation_end'),
        d.get('punishment_start'), d.get('punishment_end'), d.get('punishment_reason'),
        d.get('is_active'), d.get('email'), d.get('marital_status'), d.get('department'),
        d.get('languages'), d.get('certifications'), d.get('projects'), d.get('kpi_score'),
        d.get('meeting_status')
    )

def delete_person(person_id):
    ma_docs = db.collection('meeting_attendees').where('person_id', '==', person_id).stream()
    for doc in ma_docs: doc.reference.delete()
        
    att_docs = db.collection('attendance').where('person_id', '==', person_id).stream()
    for doc in att_docs: doc.reference.delete()
        
    db.collection('people').document(person_id).delete()
    return person_id

def activate_person(person_id):
    db.collection('people').document(person_id).update({
        'is_active': 1,
        'left_date': None,
        'vacation_start': None,
        'vacation_end': None,
        'punishment_start': None,
        'punishment_end': None,
        'punishment_reason': None
    })
    return person_id

def set_left_job(person_id, left_date):
    db.collection('people').document(person_id).update({
        'is_active': 0, 'left_date': left_date,
        'vacation_start': None, 'vacation_end': None,
        'punishment_start': None, 'punishment_end': None, 'punishment_reason': None
    })
    return person_id

def assign_department(person_id, department):
    db.collection('people').document(person_id).update({
        'department': department
    })
    return person_id

def set_meeting_status(person_id, status):
    db.collection('people').document(person_id).update({
        'meeting_status': status
    })
    return person_id

def set_vacation(person_id, start_date, end_date):
    db.collection('people').document(person_id).update({
        'is_active': 1, 'vacation_start': start_date, 'vacation_end': end_date,
        'punishment_start': None, 'punishment_end': None, 'punishment_reason': None, 'left_date': None
    })
    return person_id

def clear_vacation(person_id):
    db.collection('people').document(person_id).update({
        'vacation_start': None, 'vacation_end': None
    })
    return person_id

def set_punishment(person_id, start_date, end_date, reason):
    db.collection('people').document(person_id).update({
        'is_active': 1, 'punishment_start': start_date, 'punishment_end': end_date, 'punishment_reason': reason,
        'vacation_start': None, 'vacation_end': None, 'left_date': None
    })
    return person_id

def clear_punishment(person_id):
    db.collection('people').document(person_id).update({
        'punishment_start': None, 'punishment_end': None, 'punishment_reason': None
    })
    return person_id

def get_all_users():
    docs = db.collection('users').stream()
    return [(doc.id, d.get('username'), d.get('role'), d.get('access_level')) for doc in docs for d in [doc.to_dict()]]

def add_user(username, password, role, access_level):
    docs = list(db.collection('users').where('username', '==', username).limit(1).stream())
    if len(docs) > 0:
        return False
    db.collection('users').add({
        'username': username, 'password': hash_password(password),
        'role': role, 'access_level': access_level
    })
    return True

def get_user_by_id(user_id):
    doc = db.collection('users').document(user_id).get()
    if not doc.exists: return None
    d = doc.to_dict()
    return (doc.id, d.get('username'), d.get('role'), d.get('access_level'))

def delete_user(user_id):
    db.collection('users').document(user_id).delete()
    return user_id

def update_user_role(user_id, role, access_level):
    db.collection('users').document(user_id).update({
        'role': role, 'access_level': access_level
    })
    return user_id

def get_super_owner():
    docs = list(db.collection('users').where('role', '==', 'super_owner').limit(1).stream())
    if len(docs) > 0:
        return (docs[0].id,)
    return None

def add_notification(user_id, message):
    res = db.collection('notifications').add({
        'user_id': user_id, 'message': message, 'is_read': 0,
        'timestamp': datetime.now().isoformat()
    })
    return res[1].id

def get_unread_notifications(user_id):
    docs = db.collection('notifications').stream()
    res = []
    for doc in docs:
        d = doc.to_dict()
        if d.get('user_id') == user_id and d.get('is_read') == 0:
            res.append((doc.id, d.get('message'), d.get('timestamp')))
    return res

def mark_notifications_read(user_id):
    docs = db.collection('notifications').stream()
    for doc in docs:
        d = doc.to_dict()
        if d.get('user_id') == user_id and d.get('is_read') == 0:
            doc.reference.update({'is_read': 1})
    return user_id

def get_person_images(person_id):
    doc = db.collection('people').document(person_id).get()
    if not doc.exists: return (None, None)
    d = doc.to_dict()
    
    photo_person = None
    photo_passport = None
    if d.get('photo_person'):
        photo_person = _download_blob(person_id, 'photo_person')
    if d.get('photo_passport'):
        photo_passport = _download_blob(person_id, 'photo_passport')
        
    return (photo_person, photo_passport)

def update_password(user_id, old_password, new_password):
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get()
    if doc.exists and doc.to_dict().get('password') == hash_password(old_password):
        doc_ref.update({'password': hash_password(new_password)})
        return True
    return False

def add_activity(message, act_type='add'):
    res = db.collection('activities').add({
        'message': message, 'type': act_type, 'timestamp': datetime.now().isoformat()
    })
    return res[1].id

def get_recent_activities(limit=20):
    docs = db.collection('activities').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
    return [(d.get('message'), d.get('type'), d.get('timestamp')) for doc in docs for d in [doc.to_dict()]]

def get_dashboard_stats():
    people = list(db.collection('people').stream())
    users = list(db.collection('users').stream())
    
    active_people = sum(1 for p in people if p.to_dict().get('is_active') == 1)
    total_users = len(users)
    total_depts = len(set(p.to_dict().get('department') for p in people if p.to_dict().get('department')))
    access_levels = len(set(u.to_dict().get('access_level') for u in users))
    
    return active_people, total_users, total_depts, access_levels

def get_department_distribution():
    people = db.collection('people').stream()
    depts = {}
    for p in people:
        d = p.to_dict()
        if d.get('is_active') == 1 and d.get('department'):
            depts[d['department']] = depts.get(d['department'], 0) + 1
    return [(k, v) for k, v in depts.items()]

def get_all_people_full(user_access_level=3):
    return get_people(user_access_level, is_active=1)

def get_attendance_for_month(month_str):
    return get_attendance(month_str)

def get_organizations():
    docs = db.collection('organizations').stream()
    res = []
    for doc in docs:
        d = doc.to_dict()
        res.append((doc.id, d.get('name', ''), d.get('sector', ''), d.get('leader', ''), d.get('phone', ''), d.get('address', '')))
    res.sort(key=lambda x: x[1])
    return res

def add_organization(name, sector="", leader="", phone="", address=""):
    try:
        db.collection('organizations').add({
            'name': name, 'sector': sector, 'leader': leader, 'phone': phone, 'address': address
        })
        return True
    except Exception as e:
        print("add_organization error:", e)
        return False

def update_organization(org_id, name, sector="", leader="", phone="", address=""):
    try:
        doc_ref = db.collection('organizations').document(org_id)
        old_doc = doc_ref.get()
        old_name = old_doc.to_dict().get('name') if old_doc.exists else None

        doc_ref.update({
            'name': name, 'sector': sector, 'leader': leader, 'phone': phone, 'address': address
        })

        if old_name and old_name != name:
            peeps = db.collection('people').where('department', '==', old_name).stream()
            for p in peeps:
                p.reference.update({'department': name})
        return True
    except Exception as e:
        print("update_organization error:", e)
        return False

def delete_organization(org_id):
    try:
        org_doc = db.collection('organizations').document(org_id).get()
        if org_doc.exists:
            org_data = org_doc.to_dict()
            org_name = org_data.get('name')
            if org_name:
                peeps = list(db.collection('people').where('department', '==', org_name).stream())
                for p in peeps:
                    atts = list(db.collection('meeting_attendees').where('person_id', '==', p.id).stream())
                    for a in atts:
                        a.reference.delete()
                    p.reference.delete()
            db.collection('organizations').document(org_id).delete()
        return True
    except Exception as e:
        print("delete_organization error:", e)
        return False

def delete_all_organizations():
    org_docs = list(db.collection('organizations').stream())
    for d in org_docs:
        d.reference.delete()
    peep_docs = list(db.collection('people').stream())
    for p in peep_docs:
        pdata = p.to_dict()
        if pdata.get('is_external') == 1 or (pdata.get('department') and pdata.get('department') != ''):
            p.reference.delete()
    att_docs = list(db.collection('meeting_attendees').stream())
    for a in att_docs:
        a.reference.delete()
    return True

def delete_meeting_attendee(meeting_id, person_id):
    docs = list(db.collection('meeting_attendees').where('meeting_id', '==', meeting_id).where('person_id', '==', person_id).stream())
    for d in docs:
        d.reference.delete()
    return True

def add_external_person(first_name, last_name, department, position="", phone=""):
    ref = db.collection('people').add({
        'first_name': first_name,
        'last_name': last_name,
        'department': department,
        'position': position,
        'phone': phone,
        'secret_level': 1,
        'is_active': 1,
        'is_external': 1,
        'meeting_status': '⏳ Sababli',
        'passport': '-',
        'pinfl': '-'
    })
    return ref[1].id

def update_external_person(person_id, first_name, last_name, position="", phone=""):
    db.collection('people').document(person_id).update({
        'first_name': first_name,
        'last_name': last_name,
        'position': position,
        'phone': phone
    })
    return person_id

def get_internal_departments():
    docs = db.collection('internal_departments').order_by('name').stream()
    return [(doc.id, d.get('name')) for doc in docs for d in [doc.to_dict()]]

def add_internal_department(name):
    docs = list(db.collection('internal_departments').where('name', '==', name).limit(1).stream())
    if len(docs) > 0: return False
    db.collection('internal_departments').add({'name': name})
    return True

def delete_internal_department(dept_id):
    db.collection('internal_departments').document(dept_id).delete()
    return dept_id

def get_people_by_org(org_name, user_access_level):
    docs = db.collection('people').stream()
    res = []
    for doc in docs:
        d = doc.to_dict()
        if d.get('is_active') == 1 and d.get('secret_level', 1) <= user_access_level:
            if org_name == "(Ichki) Barcha xodimlar":
                if d.get('is_external') == 0:
                    res.append(doc)
            elif org_name.startswith("(Ichki) "):
                real_org = org_name[8:]
                if d.get('is_external') == 0 and d.get('department') == real_org:
                    res.append(doc)
            else:
                if d.get('is_external') == 1 and d.get('department') == org_name:
                    res.append(doc)
                    
    res.sort(key=lambda x: (x.to_dict().get('first_name', ''), x.to_dict().get('last_name', '')))
    
    return [(doc.id, doc.to_dict().get('first_name'), doc.to_dict().get('last_name'), doc.to_dict().get('position'), doc.to_dict().get('phone'), doc.to_dict().get('meeting_status')) for doc in res]

def get_attendance(month_str):
    docs = db.collection('attendance').stream()
    res = []
    for doc in docs:
        d = doc.to_dict()
        if d.get('date_str', '').startswith(month_str + "-"):
            res.append((d.get('person_id'), d.get('date_str'), d.get('status')))
    return res

def set_attendance(person_id, date_str, status):
    docs = list(db.collection('attendance').where('person_id', '==', person_id).where('date_str', '==', date_str).limit(1).stream())
    if len(docs) > 0:
        docs[0].reference.update({'status': status})
        return docs[0].id
    else:
        res = db.collection('attendance').add({'person_id': person_id, 'date_str': date_str, 'status': status})
        return res[1].id

def mark_absent_for_past_days(month_str, today_str):
    today_dt = datetime.strptime(today_str, "%Y-%m-%d")
    start_dt = datetime.strptime(month_str + "-01", "%Y-%m-%d")
    
    days_to_check = []
    curr = start_dt
    while curr < today_dt:
        if curr.weekday() < 6:
            days_to_check.append(curr.strftime("%Y-%m-%d"))
        curr += timedelta(days=1)
        
    people = [p.id for p in db.collection('people').stream() if p.to_dict().get('is_active') == 1]
    att_docs = list(db.collection('attendance').stream())
    
    att_set = set((d.to_dict().get('person_id'), d.to_dict().get('date_str')) for d in att_docs)
    
    for pid in people:
        for d in days_to_check:
            if (pid, d) not in att_set:
                db.collection('attendance').add({'person_id': pid, 'date_str': d, 'status': '-'})
                
    return "marked"

def add_meeting(title, m_type, date_time, location, chairman, agenda):
    res = db.collection('meetings').add({
        'title': title, 'type': m_type, 'date_time': date_time,
        'location': location, 'chairman': chairman, 'agenda': agenda,
        'is_active': 1
    })
    return res[1].id

def get_meeting(meeting_id):
    doc = db.collection('meetings').document(meeting_id).get()
    if not doc.exists: return None
    d = doc.to_dict()
    return (doc.id, d.get('title'), d.get('type'), d.get('date_time'), d.get('location'), d.get('chairman'), d.get('agenda'))

def get_meetings():
    docs = db.collection('meetings').where('is_active', '==', 1).stream()
    res = [(doc.id, d.get('title'), d.get('type'), d.get('date_time'), d.get('location'), d.get('chairman'), d.get('agenda')) for doc in docs for d in [doc.to_dict()]]
    res.sort(key=lambda x: x[0], reverse=True)
    return res

def delete_meeting(meeting_id):
    db.collection('meetings').document(meeting_id).update({'is_active': 0})
    return meeting_id

def add_meeting_attendee(meeting_id, person_id):
    docs = list(db.collection('meeting_attendees').where('meeting_id', '==', meeting_id).where('person_id', '==', person_id).limit(1).stream())
    if len(docs) == 0:
        db.collection('meeting_attendees').add({'meeting_id': meeting_id, 'person_id': person_id, 'status': '⏳ Kutilmoqda'})
    return True

def get_meeting_attendees(meeting_id, access_level=1):
    ma_docs = list(db.collection('meeting_attendees').where('meeting_id', '==', meeting_id).stream())
    p_ids = [doc.to_dict().get('person_id') for doc in ma_docs]
    
    if not p_ids: return []
    
    people_docs = {p.id: p.to_dict() for p in db.collection('people').stream() if p.id in p_ids}
    org_docs = {o.to_dict().get('name'): o.to_dict() for o in db.collection('organizations').stream()}
    
    res = []
    for ma in ma_docs:
        d = ma.to_dict()
        pid = d.get('person_id')
        p = people_docs.get(pid)
        if p and p.get('secret_level', 1) <= access_level:
            org = org_docs.get(p.get('department'))
            sector = org.get('sector') if org else None
            res.append((
                pid, p.get('first_name'), p.get('last_name'), p.get('position'),
                p.get('phone'), p.get('department'), d.get('status'), p.get('patronymic'),
                p.get('is_external'), sector
            ))
    return res

def set_meeting_attendee_status(meeting_id, person_id, status):
    docs = list(db.collection('meeting_attendees').where('meeting_id', '==', meeting_id).where('person_id', '==', person_id).limit(1).stream())
    if len(docs) > 0:
        docs[0].reference.update({'status': status})
    return True

def seed_mock_meetings_if_empty():
    docs = list(db.collection('meetings').limit(1).stream())
    if len(docs) == 0:
        meetings = [
            ("Haftalik Apparat Yig'ilishi", "Apparat yig'ilishi", "2026-07-15 10:00", "Katta Zal - 3-qavat", "Viloyat Hokimi", "1-yillik hisobotlar tahlili"),
            ("Navbatdagi Kengash Yig'ilishi", "Kengash", "2026-07-16 14:00", "Kichik Zal - 2-qavat", "Hokim O'rinbosari", "Yangi loyihalar muhokamasi")
        ]
        for m in meetings:
            res = db.collection('meetings').add({
                'title': m[0], 'type': m[1], 'date_time': m[2], 'location': m[3],
                'chairman': m[4], 'agenda': m[5], 'is_active': 1
            })
            if m == meetings[0]:
                m_id = res[1].id
        
        p_docs = list(db.collection('people').limit(5).stream())
        for p in p_docs:
            db.collection('meeting_attendees').add({'meeting_id': m_id, 'person_id': p.id, 'status': '⏳ Kutilmoqda'})
            
    return True

def get_person_document(person_id):
    doc = db.collection('people').document(person_id).get()
    if not doc.exists: return (None, None)
    d = doc.to_dict()
    if d.get('original_document'):
        return (_download_blob(person_id, 'original_document'), d.get('original_document_ext'))
    return (None, None)

def update_person_document(person_id, doc, ext):
    _upload_blob(person_id, 'original_document', doc)
    db.collection('people').document(person_id).update({
        'original_document': True if doc else False,
        'original_document_ext': ext
    })
    return person_id

def add_person_objective(data, relatives_data):
    pinfl = (data.get('pinfl') or '').strip()
    passport = (data.get('passport') or '').strip()
    if pinfl or passport:
        try:
            docs = db.collection('people').stream()
            for doc in docs:
                d = doc.to_dict()
                db_pinfl = (d.get('pinfl') or '').strip()
                db_pass = (d.get('passport') or '').strip()
                if pinfl and pinfl not in ['-', ''] and db_pinfl == pinfl:
                    return {"error": "Kiritilgan JSHSHIR (PINFL) allaqachon bazada mavjud"}
                if passport and passport not in ['-', ''] and db_pass == passport:
                    return {"error": "Kiritilgan Passport allaqachon bazada mavjud"}
        except Exception as e:
            print(f"PINFL check warning: {e}")
                
    doc_ref = db.collection('people').document()
    person_id = doc_ref.id
    
    photo_person = data.get('photo_person_bytes') if isinstance(data.get('photo_person_bytes'), bytes) else (data.get('photo_person') if isinstance(data.get('photo_person'), bytes) else None)
    photo_passport = data.get('photo_passport_bytes') if isinstance(data.get('photo_passport_bytes'), bytes) else (data.get('photo_passport') if isinstance(data.get('photo_passport'), bytes) else None)
    original_doc = data.get('original_document_bytes') if isinstance(data.get('original_document_bytes'), bytes) else (data.get('original_document') if isinstance(data.get('original_document'), bytes) else None)
    
    _upload_blob(person_id, 'photo_person', photo_person)
    _upload_blob(person_id, 'photo_passport', photo_passport)
    _upload_blob(person_id, 'original_document', original_doc)
    
    photo_person_b64 = None
    if photo_person:
        try: photo_person_b64 = base64.b64encode(photo_person).decode('utf-8')
        except: pass
        
    photo_passport_b64 = None
    if photo_passport:
        try: photo_passport_b64 = base64.b64encode(photo_passport).decode('utf-8')
        except: pass
    
    doc_ref.set({
        'first_name': data.get('first_name', ''), 'last_name': data.get('last_name', ''), 'patronymic': data.get('patronymic', ''),
        'passport': data.get('passport', ''), 'pinfl': data.get('pinfl', ''), 'birth_date': data.get('birth_date', ''),
        'address': data.get('address', ''), 'phone': data.get('phone', ''), 'position': data.get('position', ''),
        'secret_level': int(data.get('secret_level', 1)), 
        'photo_person': True if photo_person else False,
        'photo_passport': True if photo_passport else False,
        'photo_person_b64': photo_person_b64,
        'photo_passport_b64': photo_passport_b64,
        'joined_date': data.get('joined_date', ''), 'is_active': 1,
        'department': data.get('department', ''), 'languages': data.get('languages', ''),
        'birth_place': data.get('birth_place', ''), 'nationality': data.get('nationality', ''),
        'party_membership': data.get('party_membership', ''), 'education': data.get('education', ''),
        'graduated_from': data.get('graduated_from', ''), 'education_specialty': data.get('education_specialty', ''),
        'academic_degree': data.get('academic_degree', ''), 'academic_title': data.get('academic_title', ''),
        'state_awards': data.get('state_awards', ''), 'deputy_status': data.get('deputy_status', ''),
        'employment_history': data.get('employment_history', ''),
        'original_document': True if original_doc else False, 'original_document_ext': data.get('original_document_ext', '')
    })
    
    if relatives_data:
        for r in relatives_data:
            db.collection('relatives').add({
                'person_id': person_id, 'relationship': r.get('relationship',''),
                'full_name': r.get('full_name',''), 'birth_info': r.get('birth_info',''),
                'work_info': r.get('work_info',''), 'residence': r.get('residence','')
            })
            
    return person_id

def update_person_objective(person_id, data, relatives_data):
    doc_ref = db.collection('people').document(person_id)
    
    update_data = {
        'first_name': data.get('first_name', ''), 'last_name': data.get('last_name', ''), 'patronymic': data.get('patronymic', ''),
        'passport': data.get('passport', ''), 'pinfl': data.get('pinfl', ''), 'birth_date': data.get('birth_date', ''),
        'address': data.get('address', ''), 'phone': data.get('phone', ''), 'position': data.get('position', ''),
        'secret_level': int(data.get('secret_level', 1)), 
        'joined_date': data.get('joined_date', ''),
        'department': data.get('department', ''), 'languages': data.get('languages', ''),
        'birth_place': data.get('birth_place', ''), 'nationality': data.get('nationality', ''),
        'party_membership': data.get('party_membership', ''), 'education': data.get('education', ''),
        'graduated_from': data.get('graduated_from', ''), 'education_specialty': data.get('education_specialty', ''),
        'academic_degree': data.get('academic_degree', ''), 'academic_title': data.get('academic_title', ''),
        'state_awards': data.get('state_awards', ''), 'deputy_status': data.get('deputy_status', ''),
        'employment_history': data.get('employment_history', '')
    }
    
    photo_person = data.get('photo_person_bytes') if isinstance(data.get('photo_person_bytes'), bytes) else (data.get('photo_person') if isinstance(data.get('photo_person'), bytes) else None)
    photo_passport = data.get('photo_passport_bytes') if isinstance(data.get('photo_passport_bytes'), bytes) else (data.get('photo_passport') if isinstance(data.get('photo_passport'), bytes) else None)
    original_doc = data.get('original_document_bytes') if isinstance(data.get('original_document_bytes'), bytes) else (data.get('original_document') if isinstance(data.get('original_document'), bytes) else None)
    
    if photo_person:
        _upload_blob(person_id, 'photo_person', photo_person)
        update_data['photo_person'] = True
        try: update_data['photo_person_b64'] = base64.b64encode(photo_person).decode('utf-8')
        except: pass
    if photo_passport:
        _upload_blob(person_id, 'photo_passport', photo_passport)
        update_data['photo_passport'] = True
        try: update_data['photo_passport_b64'] = base64.b64encode(photo_passport).decode('utf-8')
        except: pass
    if original_doc:
        _upload_blob(person_id, 'original_document', original_doc)
        update_data['original_document'] = True
        if data.get('original_document_ext'):
            update_data['original_document_ext'] = data.get('original_document_ext')
        
    doc_ref.update(update_data)
    
    r_docs = db.collection('relatives').where('person_id', '==', person_id).stream()
    for d in r_docs: d.reference.delete()
    
    if relatives_data:
        for r in relatives_data:
            db.collection('relatives').add({
                'person_id': person_id, 'relationship': r.get('relationship',''),
                'full_name': r.get('full_name',''), 'birth_info': r.get('birth_info',''),
                'work_info': r.get('work_info',''), 'residence': r.get('residence','')
            })
    return person_id

def get_person_objective(person_id):
    doc = db.collection('people').document(person_id).get()
    if not doc.exists: return None
    d = doc.to_dict()
    d['id'] = doc.id
    
    if d.get('photo_person_b64'):
        try:
            d['photo_person'] = base64.b64decode(d['photo_person_b64'])
        except:
            d['photo_person'] = _download_blob(person_id, 'photo_person')
    elif d.get('photo_person'):
        d['photo_person'] = _download_blob(person_id, 'photo_person')
    else:
        d['photo_person'] = None
        
    if d.get('photo_passport_b64'):
        try:
            d['photo_passport'] = base64.b64decode(d['photo_passport_b64'])
        except:
            d['photo_passport'] = _download_blob(person_id, 'photo_passport')
    elif d.get('photo_passport'):
        d['photo_passport'] = _download_blob(person_id, 'photo_passport')
    else:
        d['photo_passport'] = None
        
    return d

def get_relatives(person_id):
    docs = db.collection('relatives').where('person_id', '==', person_id).stream()
    return [{'relationship': d.get('relationship'), 'full_name': d.get('full_name'), 'birth_info': d.get('birth_info'), 'work_info': d.get('work_info'), 'residence': d.get('residence')} for doc in docs for d in [doc.to_dict()]]

def get_users_count():
    return len(list(db.collection('users').stream()))

def get_all_positions():
    docs = db.collection('people').stream()
    positions = set()
    for doc in docs:
        pos = doc.to_dict().get('position')
        if pos: positions.add(pos)
    return list(positions)

def get_all_meeting_titles():
    try:
        docs = db.collection('meetings').stream()
        res = []
        for doc in docs:
            d = doc.to_dict()
            if d.get('is_active', 1) in [1, True, '1']:
                res.append((doc.id, d.get('title', '')))
        return res
    except Exception as e:
        print("get_all_meeting_titles error:", e)
        return []
