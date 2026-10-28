# database_stage2_txt.py
import sqlite3
import os

class ProductionTextDatabaseAgent:
   def __init__(self, db_path="production_manifest_db.sqlite"):
       self.db_path = db_path
       self.init_database()

   def init_database(self):
       """تأسيس الجداول التشغيلية لحقن المقاطع النصية وسجل المراجعات بوضع WAL"""
       conn = sqlite3.connect(self.db_path)
       cursor = conn.cursor()
       cursor.execute("PRAGMA journal_mode=WAL;")
      
       # 1. جدول تذاكر الإنتاج (الحالة الافتراضية تكون PROCESSING لحين اكتمال طحن كافة المقاطع)
       cursor.execute('''
           CREATE TABLE IF NOT EXISTS production_tickets (
               trend_id TEXT PRIMARY KEY,
               cinematic_style TEXT,
               content_genre TEXT,
               target_duration_minutes INTEGER,
               voice_gender TEXT,
               voice_tone TEXT,
               status TEXT DEFAULT 'PROCESSING',
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
           )
       ''')
      
       # 2. جدول حفظ المقاطع السردية لكل لغة وثقافة على حدة بالتوازي
       cursor.execute('''
           CREATE TABLE IF NOT EXISTS story_segments (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               trend_id TEXT,
               segment_id TEXT,
               lang_code TEXT,
               time_window TEXT,
               is_hook INTEGER,
               validated_text TEXT,
               FOREIGN KEY(trend_id) REFERENCES production_tickets(trend_id),
               UNIQUE(trend_id, segment_id, lang_code)
           )
       ''')

       # 3. جدول ذاكرة المراجعات والرفض التراكمي لرفع الـ RPM
       cursor.execute('''
           CREATE TABLE IF NOT EXISTS patching_revision_history (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               trend_id TEXT,
               segment_id TEXT,
               lang_code TEXT,
               rejected_text TEXT,
               correction_note TEXT,
               rejected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
           )
       ''')
       conn.commit()
       conn.close()

   def create_production_ticket(self, trend_id, style, genre, duration, gender, tone):
       """فتح تذكرة إنتاج جديدة وحفظ بطاقة الشخصية والنبرة والجنس على القرص بحالة PROCESSING"""
       conn = sqlite3.connect(self.db_path)
       cursor = conn.cursor()
       try:
           cursor.execute('''
               INSERT OR REPLACE INTO production_tickets
               (trend_id, cinematic_style, content_genre, target_duration_minutes, voice_gender, voice_tone, status)
               VALUES (?, ?, ?, ?, ?, ?, 'PROCESSING')
           ''', (trend_id, style, genre, duration, gender, tone))
           conn.commit()
       finally:
           conn.close()

   def inject_segment_safely(self, trend_id, segment_id, lang_code, time_window, is_hook, text):
       """حقن المقطع المصحح والمطهر مباشرة على القرص بالتوازي مع التوليد لحماية الـ RAM"""
       conn = sqlite3.connect(self.db_path)
       cursor = conn.cursor()
       try:
           cursor.execute('''
               INSERT OR REPLACE INTO story_segments
               (trend_id, segment_id, lang_code, time_window, is_hook, validated_text)
               VALUES (?, ?, ?, ?, ?, ?)
           ''', (trend_id, segment_id, lang_code, time_window, int(is_hook), text))
           conn.commit()
       finally:
           conn.close()

   def update_ticket_status(self, trend_id, status):
       """تحديث الحالة النهائية للتذكرة (تحويلها إلى APPROVED فور اكتمال طحن كافة السطور)"""
       conn = sqlite3.connect(self.db_path)
       cursor = conn.cursor()
       try:
           cursor.execute("UPDATE production_tickets SET status = ? WHERE trend_id = ?", (status, trend_id))
           conn.commit()
           print(f"💾 [حالة القرص الصلب ستيج 2]: تحولت التذكرة ({trend_id}) بنجاح إلى حالة: [{status}]")
       finally:
           conn.close()

   def check_blacklisted_phrases(self, lang_code, text):
       """التحقق مما إذا كان النص يحتوي على جمل تم رفضها سابقاً في جولات المراجعة"""
       conn = sqlite3.connect(self.db_path)
       cursor = conn.cursor()
       try:
           cursor.execute("SELECT rejected_text FROM patching_revision_history WHERE lang_code = ?", (lang_code,))
           rows = cursor.fetchall()
           for row in rows:
               if row[0] in text:
                   return True, row[0]
           return False, None
       finally:
           conn.close()


