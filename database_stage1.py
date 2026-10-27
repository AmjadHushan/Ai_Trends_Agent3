import sqlite3
import os
import time

class TrendsDatabaseAgent:
   def __init__(self, db_path="trends_stage_db.sqlite"):
       self.db_path = db_path
       self.init_database()

   def init_database(self):
       """تأسيس الجداول المنفصلة وتفعيل وضع WAL لمنع التجميد"""
       conn = sqlite3.connect(self.db_path, check_same_thread=False)
       cursor = conn.cursor()
       cursor.execute("PRAGMA journal_mode=WAL;")
      
       # 1. قائمة نتائج الكشط التلقائي
       cursor.execute('''
           CREATE TABLE IF NOT EXISTS scraped_trends (
               concept_id TEXT PRIMARY KEY,
               trend_keyword TEXT,
               engineered_title TEXT UNIQUE,
               status TEXT DEFAULT 'PENDING',
               telegram_message_id INTEGER DEFAULT NULL
           )''')
          
       # 2. قائمة التوجيهات والأوامر البشرية المباشرة
       cursor.execute('''
           CREATE TABLE IF NOT EXISTS human_commands (
               command_id TEXT PRIMARY KEY,
               user_prompt TEXT,
               status TEXT DEFAULT 'PENDING',
               telegram_message_id INTEGER DEFAULT NULL
           )''')
          
       conn.commit()
       conn.close()

   def insert_scraped_trend(self, concept_id, keyword, title):
       """حقن نتائج الكشط في الجدول الخاص بها بحالة PENDING"""
       conn = sqlite3.connect(self.db_path, check_same_thread=False)
       cursor = conn.cursor()
       try:
           cursor.execute('''
               INSERT INTO scraped_trends (concept_id, trend_keyword, engineered_title)
               VALUES (?, ?, ?)''', (concept_id, keyword, title))
           conn.commit()
           return True
       except sqlite3.IntegrityError:
           return False
       finally:
           conn.close()

   def insert_human_command(self, command_id, user_text):
       """حقن الأوامر والتوجيهات البشرية المباشرة في الجدول الخاص بها بحالة PENDING"""
       conn = sqlite3.connect(self.db_path, check_same_thread=False)
       cursor = conn.cursor()
       try:
           cursor.execute('''
               INSERT INTO human_commands (command_id, user_prompt)
               VALUES (?, ?)''', (command_id, user_text))
           conn.commit()
           print(f"💾 [جدول البشر]: تم حفظ التوجيه البشري على القرص: {user_text}")
           return True
       except sqlite3.IntegrityError:
           return False
       finally:
           conn.close()

   def update_trend_status(self, concept_id, new_status):
       """تغيير قيمة وحالة موضوع الكشط عند الاختيار"""
       conn = sqlite3.connect(self.db_path, check_same_thread=False)
       cursor = conn.cursor()
       cursor.execute("UPDATE scraped_trends SET status = ? WHERE concept_id = ?", (new_status, concept_id))
       conn.commit()
       conn.close()

   def update_command_status(self, command_id, new_status):
       """تغيير قيمة وحالة الأمر البشري عند الاختيار والتنفيذ"""
       conn = sqlite3.connect(self.db_path, check_same_thread=False)
       cursor = conn.cursor()
       cursor.execute("UPDATE human_commands SET status = ? WHERE command_id = ?", (new_status, command_id))
       conn.commit()
       conn.close()



