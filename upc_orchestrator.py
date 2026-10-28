# upc_orchestrator.py
import os
import json
import sqlite3
import asyncio
from telegram.ext import Application

# استدعاء المايسترو كاتب القصة المستقل المعزول ستيج 2
from ai_writer import AIStoryProductionCoordinator

class UPCOrchestratorPlatform:
   def __init__(self, config_path="config.json", db_path="trends_stage_db.sqlite"):
       self.config_path = config_path
       self.db_stage1 = db_path  # الاتصال بقاعدة بيانات البوت الأصلي مباشرة
       self.config = self.load_config()
       self.writer_coordinator = AIStoryProductionCoordinator(db_stage1_path=db_path)
       self.loop_delay = 2  # فحص القرص كل ثانيتين بصمت

   def load_config(self):
       if os.path.exists(self.config_path):
           with open(self.config_path, 'r', encoding='utf-8') as f:
               return json.load(f)
       return {}

   def fetch_next_approved_ticket(self):
       """الفحص الذكي المتوازي لجدول الكشط وجدول التوجيهات البشرية لقطف حالة APPROVED"""
       conn = sqlite3.connect(self.db_stage1)
       cursor = conn.cursor()
       try:
           # 1. أولاً: التحقق من وجود ترند تلقائي معتمد
           cursor.execute(
               "SELECT concept_id, trend_keyword, telegram_message_id FROM scraped_trends WHERE status = 'APPROVED' LIMIT 1"
           )
           row = cursor.fetchone()
           if row:
               return row, "trends"

           # 2. ثانياً: التحقق من وجود توجيه بشري مباشر معتمد (حل المشكلة الحالية)
           cursor.execute(
               "SELECT command_id, command_text FROM human_commands WHERE status = 'APPROVED' LIMIT 1"
           )
           row_human = cursor.fetchone()
           if row_human:
               # توليد هيكل متوافق برمجياً ليمر بسلام لكاتب القصة
               return (row_human[0], row_human[1], 0), "human"

           return None
       except sqlite3.OperationalError:
           return None
       finally:
           conn.close()

   def update_stage1_status(self, concept_id, table_type, new_status):
       """تحديث قفل الحالة في الجدول الصحيح لمنع التكرار"""
       conn = sqlite3.connect(self.db_stage1)
       cursor = conn.cursor()
       try:
           if table_type == "trends":
               cursor.execute("UPDATE scraped_trends SET status = ? WHERE concept_id = ?", (new_status, concept_id))
           else:
               cursor.execute("UPDATE human_commands SET status = ? WHERE command_id = ?", (new_status, concept_id))
           conn.commit()
       except sqlite3.OperationalError:
           pass
       finally:
           conn.close()

   async def start_autonomous_watcher_loop(self, bot_app: Application):
       """حلقة المراقبة المركزية الصامتة المعزولة في الخلفية (Background Watcher Loop)"""
       print("🚀 [طبقة الحوكمة UPC]: تم تدشين خادم المراقبة المتوازي (كشط + بشر) حياً...")
      
       chat_id = self.config.get("telegram_chat_id")
       if not chat_id:
           print("❌ خطأ حرج: لم يتم العثور على telegram_chat_id in config.json")
           return

       while True:
           ticket_data = self.fetch_next_approved_ticket()
           if ticket_data:
               ticket, table_type = ticket_data
               concept_id, trend_kw, telegram_message_id = ticket
              
               print(f"🎯 [نبضة ملقوطة - جدول {table_type.upper()}]: جاري قفل المسار وبدء الفرم للـ ID: {concept_id}")
              
               # 1. قفل حالة التذكرة فوراً في جدولها الصحيح لمنع التداخل العشوائي
               self.update_stage1_status(concept_id, table_type, "PROCESSING_STG2")
              
               # 2. إنشاء رسالة العداد الحركية الجديدة الحتمية في التليجرام لضمان التحديث المرئي أمام عينك
               init_msg = await bot_app.bot.send_message(
                   chat_id=str(chat_id),
                   text=f"⏳ **[منظومة الفرم ستيج 2]: تم التقاط الأمر السيادي المستلم...**\n\n░░░░░░░░░░ [0%]"
               )
              
               # 3. إطلاق كاتب القصة المستقل وإعطائه السيطرة الكاملة على رسالة الـ Progress
               try:
                   await self.writer_coordinator.run_stage2_production_pipeline(
                       trend_id=concept_id,
                       bot_context=bot_app,
                       chat_id=chat_id,
                       message_id=init_msg.message_id
                   )
                  
                   # 4. وسم التذكرة بنجاح الإنتاج النصي الكامل في قاعدة البيانات ستيج 1
                   self.update_stage1_status(concept_id, table_type, "STG2_COMPLETED")
                   print(f"✅ [نجاح الحوكمة]: اكتمل طحن السيناريو للـ {concept_id} واستقر في ستيج 2.")

               except Exception as e:
                   print(f"❌ فشل داخل خط الإنتاج النصي المجهري: {e}")
                   self.update_stage1_status(concept_id, table_type, "STG2_FAILED")

           await asyncio.sleep(self.loop_delay)



