# database_stage2_txt.py
import sqlite3
import os

class DatabaseStage2Txt:
   def __init__(self, db_path="production_stage2.sqlite"):
       self.db_path = db_path
       self.init_database()

   def init_database(self):
       """
       تأسيس جدول النصوص المجزأة مع مصفوفة الـ 25 Check (5 لغات × 5 فحوصات)
       وتفعيل وضع WAL لمنع التجميد العتادي أثناء الكتابة والفحص المستمر.
       """
       conn = sqlite3.connect(self.db_path, check_same_thread=False)
       cursor = conn.cursor()
       cursor.execute("PRAGMA journal_mode=WAL;")
      
       # إنشاء جدول النصوص
       cursor.execute('''
       CREATE TABLE IF NOT EXISTS language_scripts (
           concept_id TEXT,
           language_code TEXT,
           script_hook TEXT DEFAULT '',
           script_body TEXT DEFAULT '',
           status TEXT DEFAULT 'WRITING',
           -- مصفوفة الـ 25 Check (5 فلاتر فحص × 5 لغات، تسجل كـ 1 للناجح و 0 للمنتظر)
           check_stutter INTEGER DEFAULT 0,
           check_neutrality INTEGER DEFAULT 0,
           check_narrative INTEGER DEFAULT 0,
           check_islamic INTEGER DEFAULT 0,
           check_eu_law INTEGER DEFAULT 0,
           PRIMARY KEY (concept_id, language_code)
       )''')
       conn.commit()
       conn.close()

   def save_script_part(self, concept_id, lang_code, part_type, text_content):
       """
       حقن وتحديث أجزاء النص (Hook أو Body) لغة تلو الأخرى بشكل مجزأ
       لمنع امتلاء الذاكرة العشوائية وتوفير سياق القراءة التراكمي.
       """
       conn = sqlite3.connect(self.db_path, check_same_thread=False)
       cursor = conn.cursor()
      
       # التأكد من وجود السطر أولاً للغة المحددة
       cursor.execute('''
       INSERT OR IGNORE INTO language_scripts (concept_id, language_code)
       VALUES (?, ?)''', (concept_id, lang_code))
      
       # تحديث الجزء المحدد ديناميكياً (سواء الخطاف أو صلب الموضوع)
       if part_type == "hook":
           cursor.execute('''
           UPDATE language_scripts SET script_hook = ?, status = 'WRITING'
           WHERE concept_id = ? AND language_code = ?''', (text_content, concept_id, lang_code))
       elif part_type == "body":
           cursor.execute('''
           UPDATE language_scripts SET script_body = ?, status = 'WRITING'
           WHERE concept_id = ? AND language_code = ?''', (text_content, concept_id, lang_code))
          
       conn.commit()
       conn.close()

   def get_accumulated_context(self, concept_id, lang_code):
       """
       قراءة الذاكرة التراكمية المتحركة للنص الحالي (ما تم كتابته حتى الآن)
       لتمريره للكاتب الذكي لمنع التكرار والحفاظ على السياق.
       """
       conn = sqlite3.connect(self.db_path, check_same_thread=False)
       cursor = conn.cursor()
       cursor.execute('''
       SELECT script_hook, script_body FROM language_scripts
       WHERE concept_id = ? AND language_code = ?''', (concept_id, lang_code))
       row = cursor.fetchone()
       conn.close()
      
       if row:
           return {"hook": row[0], "body": row[1]}
       return {"hook": "", "body": ""}

   def update_status_to_ready_for_check(self, concept_id):
       """
       تحويل النصوص بالكامل لحالة الجاهزية الفورية للفحص بعد انتهاء الكتابة.
       """
       conn = sqlite3.connect(self.db_path, check_same_thread=False)
       cursor = conn.cursor()
       cursor.execute('''
       UPDATE language_scripts SET status = 'READY_FOR_CHECK'
       WHERE concept_id = ? AND status = 'WRITING'
       ''', (concept_id,))
       conn.commit()
       conn.close()

   def get_all_scripts_for_checking(self, concept_id):
       """
       استدعاء جميع نصوص اللغات المرتبطة بالمعرف لتمريرها على وكلاء الفحص بالتتابع.
       """
       conn = sqlite3.connect(self.db_path, check_same_thread=False)
       cursor = conn.cursor()
       cursor.execute('''
       SELECT language_code, script_hook, script_body FROM language_scripts
       WHERE concept_id = ?''', (concept_id,))
       rows = cursor.fetchall()
       conn.close()
       return rows

   def apply_immediate_correction(self, concept_id, lang_code, part_type, corrected_text, check_column):
       """
       تحديث النص المصحح فوراً على القرص وتفعيل الـ Check الخاص بالوكيل الحالي
       لبناء مصفوفة الـ 25 Check بالتتابع.
       """
       conn = sqlite3.connect(self.db_path, check_same_thread=False)
       cursor = conn.cursor()
      
       # تصحيح الجزء التالف في النص فوراً
       if part_type == "hook":
           cursor.execute(f'''
           UPDATE language_scripts SET script_hook = ?, {check_column} = 1
           WHERE concept_id = ? AND language_code = ?''', (corrected_text, concept_id, lang_code))
       elif part_type == "body":
           cursor.execute(f'''
           UPDATE language_scripts SET script_body = ?, {check_column} = 1
           WHERE concept_id = ? AND language_code = ?''', (corrected_text, concept_id, lang_code))
          
       conn.commit()
       conn.close()

   def verify_and_finalize_checks(self, concept_id):
       """
       الفحص النهائي للمصفوفة: إذا كانت جميع الفحوصات الخمسة لجميع اللغات تساوي 1 (أي 25 Check مكتمل)،
       يتم ترقية حالة النصوص فوراً إلى Approved to Audio.
       """
       conn = sqlite3.connect(self.db_path, check_same_thread=False)
       cursor = conn.cursor()
      
       # حساب عدد الفحوصات المكتملة (المجموع الكلي يجب أن يكون 25)
       cursor.execute('''
       SELECT SUM(check_stutter + check_neutrality + check_narrative + check_islamic + check_eu_law)
       FROM language_scripts WHERE concept_id = ?''', (concept_id,))
       total_checks = cursor.fetchone()[0]
      
       if total_checks and total_checks == 25:
           cursor.execute('''
           UPDATE language_scripts SET status = 'Approved to Audio'
           WHERE concept_id = ?''', (concept_id,))
           conn.commit()
           success = True
       else:
           success = False
          
       conn.close()
       return success



