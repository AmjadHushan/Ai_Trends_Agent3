import asyncio
import sqlite3
import gc
import torch
from ai_writer import AutonomousAIWriterAgent
from progress_bar_agent import ProgressBarAgent

class UPCOrchestratorPlatform:
   def __init__(self, db1_path="trends_stage_db.sqlite"):
       self.db1_path = db1_path
       self.is_running = True

   async def start_autonomous_watcher_loop(self, telegram_app):
       """
       حلقة المراقبة الصامتة في الخلفية (UPC):
       تراقب الداتا بيز 1، وعند رصد فكرة معتمدة لحالة APPROVED،
       تنشئ رسالة عداد جديدة وتمررها للكاتب لتبدأ المرحلة الثانية حياً أمامك.
       """
       print("📡 [UPC]: صمام المراقبة يراقب الداتا بيز 1 وبانتظار تفعيل المرحلة الثانية...")
      
       while self.is_running:
           try:
               # 1. فحص الداتا بيز 1 للبحث عن أي فكرة بحالة APPROVED
               conn = sqlite3.connect(self.db1_path)
               conn.row_factory = sqlite3.Row
               cursor = conn.cursor()
              
               cursor.execute('''
                   SELECT concept_id, trend_keyword, engineered_title, status
                   FROM scraped_trends
                   WHERE status = 'APPROVED'
                   LIMIT 1
               ''')
               approved_row = cursor.fetchone()
               conn.close()

               if approved_row:
                   concept_id = approved_row["concept_id"]
                   keyword = approved_row["trend_keyword"]
                   style = "تشويقي محايد"
                  
                   print(f"🔔 [إشارة UPC]: تم رصد فكرة معتمدة ({concept_id}). جاري إنشاء العداد وإيقاظ الكاتب...")

                   # استدعاء المتغيرات السيادية المفتوحة مسبقاً في البوت
                   from orchestrator_bot import ai_engine, CHANNEL_ID
                  
                   # 2. إنشاء رسالة عداد مخصصة للمرحلة الثانية في قناتك بالتليجرام
                   target_chat = CHANNEL_ID if CHANNEL_ID else approved_row.get("telegram_message_id")
                  
                   init_msg = await telegram_app.bot.send_message(
                       chat_id=str(target_chat),
                       text="⏳ **[منظومة الفرم]: تم إيقاظ الكاتب. جاري بدء إنتاج الأجزاء بالتتابع...**"
                   )
                  
                   # 3. تأسيس وكيل العداد للمسار الجديد
                   from telegram.ext import CallbackContext
                   context = CallbackContext(telegram_app)
                   progress = ProgressBarAgent(context, init_msg.chat_id, init_msg.message_id)

                   # 4. إيقاظ الكاتب وتمرير العداد له ليحدثه تلقائياً خطوة بخطوة
                   writer_agent = AutonomousAIWriterAgent(ai_engine)
                   asyncio.create_task(
                       writer_agent.execute_autonomous_writing_cycle(concept_id, keyword, style, progress)
                   )

                   # 5. تحديث حالة الفكرة في الداتا بيز 1 إلى 'PROCESSING_STG2' لحمايتها من التكرار
                   conn = sqlite3.connect(self.db1_path)
                   cursor = conn.cursor()
                   cursor.execute("UPDATE scraped_trends SET status = 'PROCESSING_STG2' WHERE concept_id = ?", (concept_id,))
                   conn.commit()
                   conn.close()

                   # 🧼 [تنظيف المعدات الحتمي للمرحلة الأولى]:
                   # إبادة مخلفات الكشط وعمليات معالجة الـ النصوص العربية القديمة فوراً لتفريغ الـ VRAM للكاتب
                   if torch.cuda.is_available():
                       torch.cuda.empty_cache()
                       torch.cuda.ipc_collect()
                   gc.collect()
                   print("🧼 [UPC Clean]: تم قفل دورة المرحلة الأولى وتطهير معدات الكشط بنجاح كامل.")

           except Exception as e:
               print(f"❌ [خطأ في مراقب UPC]: {str(e)}")

           # فحص الداتا بيز كل 3 ثوانٍ صامتاً دون أي إجهاد للعتاد
           await asyncio.sleep(3)

   def stop_watcher(self):
       self.is_running = False
       print("❄ [UPC]: تم إغلاق صمام المراقبة بأمان.")


