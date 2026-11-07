# ai_writer.py
import os
import sys
import gc
import json
import time
import torch
import asyncio
from concurrent.futures import ThreadPoolExecutor

# استدعاء بنية القرص الصلب للداتا بيز الثانية ومصفوفة الـ 25 Check
from database_stage2_txt import DatabaseStage2Txt

# استدعاء صمامات الفحص الخمسة المستقلة المصقولة من ملفاتها الأصلية
from check_stutter import check_text_integrity
from check_neutrality import check_sovereign_neutrality
from check_narrative import check_story_quality
from check_eu_law import check_legal_compliance
from check_islamic import check_sharia_compliance

# تأسيس منفذ الخيوط المعزول لحماية المعالج والـ RAM من التجميد
ai_writer_executor = ThreadPoolExecutor(max_workers=1)
db2 = DatabaseStage2Txt()

class AutonomousAIWriterAgent:
   def __init__(self, ai_engine_instance):
       """
       تمرير محرك كوين المحلي المشترك لعدم تكرار تحميل الأوزان في الذاكرة
       """
       self.ai_engine = ai_engine_instance
       self.languages = ["ara", "eng", "ger", "fre", "spa"]

   async def execute_autonomous_writing_cycle(self, concept_id, trend_keyword, marketing_style, telegram_progress_agent=None):
       """
       بروتوكول الإنتاج بالتتابع الحركي (لغة تلو الأخرى، جزء تلو الآخر)
       يتم قراءة الهوية من داتا بيز 1 والربط مع الذاكرة التراكمية في داتا بيز 2.
       """
       try:
           if telegram_progress_agent:
               await telegram_progress_agent.update_progress(5, "🎬 الـ UPC يوقظ الكاتب: جاري شحن الذاكرة التراكمية وتحليل أبعاد السياق...")

           # =================================================================
           # 1⃣ مرحلة الكتابة المجزأة بالتتابع التام (حجم ديناميكي غير ممل)
           # =================================================================
           for index, lang in enumerate(self.languages):
               if telegram_progress_agent:
                   current_percent = int(5 + (index / len(self.languages)) * 35)
                   await telegram_progress_agent.update_progress(current_percent, f"✍ جاري صياغة أجزاء السيناريو للغة: [{lang}]...")

               # --- الجزء الأول: صياغة الخطاف (Hook) بسطر واحد من كوين ---
               prompt_hook = (
                   f"الموضوع الرئيسي: ({trend_keyword}) والنمط السيكولوجي: [{marketing_style}]. "
                   f"اكتب خطافاً سينمائياً مشوقاً جداً وفيروسياً يتكون من سطر واحد فقط بلغة رمزها ({lang}). "
                   f"اكتب النص المطلوب مباشرة دون أي مقدمات أو هوامش."
               )
              
               # التوليد الخيطي المعزول لحماية الـ Event Loop
               hook_text = await asyncio.to_thread(self.ai_engine.generate_text_sync, prompt_hook, 40)
               db2.save_script_part(concept_id, lang, "hook", hook_text)

               # تطهير عتادي لحظي بين الأجزاء
               if torch.cuda.is_available(): torch.cuda.empty_cache()
               gc.collect()

               # --- الجزء الثاني: صياغة صلب الموضوع (Body) بناءً على الذاكرة التراكمية والطول الديناميكي المشوق ---
               accumulated_context = db2.get_accumulated_context(concept_id, lang)
               last_hook_written = accumulated_context.get("hook", "")

               prompt_body = (
                   f"أنت مخرج وثائقي ومدير إبداعي محترف. الموضوع الرئيسي هو ({trend_keyword}) والنمط السيكولوجي هو [{marketing_style}]. "
                   f"لقد قمت بكتابة الخطاف التالي سابقاً: ({last_hook_written}). "
                   f"بناءً على هذا الخطاف وحفاظاً على صلب الموضوع وعدم التكرار, اقرأ النص السابق جيداً ثم صغ صلب السيناريو (Body) كاملاً "
                   f"باللغة ذات الرمز ({lang}) وبحجم ممتد، مرن، ومتناسب تلقائياً يعطي مادة غنية، مشوقة، وغير مملة تليق بأبعاد هذا السياق وطبيعته الزمنية. "
                   f"اكتب النص الإبداعي المطلوب فوراً دون أي مقدمات أو شرح جانبي."
               )
              
               body_text = await asyncio.to_thread(self.ai_engine.generate_text_sync, prompt_body, 350)
               db2.save_script_part(concept_id, lang, "body", body_text)

               # تنظيف الكاش وإبقاء الـ RAM باردة تماماً قبل الانتقال للغة التالية
               if torch.cuda.is_available(): torch.cuda.empty_cache()
               gc.collect()

           # قفل مرحلة الكتابة والتحول التلقائي للجاهزية الفورية للفحص
           db2.update_status_to_ready_for_check(concept_id)
          
           # 🔥 استدعاء تنظيف المعدات حتمياً فور انتهاء مرحلة الكتابة وضخها على القرص
           self.purge_hardware_equipment()
          
           if telegram_progress_agent:
               await telegram_progress_agent.update_progress(45, "💾 استقرت النصوص في الداتا بيز 2. الحالة: READY_FOR_CHECK. تم غسل الذاكرة.")
               await asyncio.sleep(0.5)

           # =================================================================
           # 2⃣ مرحلة الفحص الممنهج المتتابع وتوثيق الـ 25 Check
           # =================================================================
           validators = [
               {"column": "check_stutter", "name": "كاشف التكرار والهلوسة", "func": lambda t, l: check_text_integrity(t, l)},
               {"column": "check_neutrality", "name": "صمام الحيادية السياسية", "func": lambda t, l: check_sovereign_neutrality(t)},
               {"column": "check_narrative", "name": "مقياس الخطاف النفسي والجذب", "func": lambda t, l: check_story_quality(t, l)},
               {"column": "check_islamic", "name": "فلتر المحظورات الشرعية", "func": lambda t, l: check_sharia_compliance(t)},
               {"column": "check_eu_law", "name": "مراقب القوانين الرقمية", "func": lambda t, l: check_legal_compliance(t)}
           ]

           for v_index, validator in enumerate(validators):
               if telegram_progress_agent:
                   base_progress = 45 + (v_index * 10)
                   await telegram_progress_agent.update_progress(base_progress, f"👁 إيقاظ الوكيل: [{validator['name']}] لفحص اللغات الخمس بالتتابع...")

               scripts_to_check = db2.get_all_scripts_for_checking(concept_id)

               for lang_code, hook, body in scripts_to_check:
                   is_valid_hook, hook_feedback = validator["func"](hook, lang_code)
                   corrected_hook = hook
                   if not is_valid_hook:
                       fix_prompt_hook = f"أعد صياغة وتصحيح هذه الجملة لتتفادى الخطأ البرمجي البنيوي ({hook_feedback}). الجملة: ({hook}). صغها بسطر واحد وبنفس اللغة."
                       corrected_hook = await asyncio.to_thread(self.ai_engine.generate_text_sync, fix_prompt_hook, 40)

                   is_valid_body, body_feedback = validator["func"](body, lang_code)
                   corrected_body = body
                   if not is_valid_body:
                       fix_prompt_body = f"أنت مصحح ومدقق نصوص محترف. أعد صياغة وتصحيح هذا النص الإبداعي بالكامل لتتفادى الخرق والمخالفة المذكورة هنا ({body_feedback}). النص الأصلي: ({body}). حافظ على الطول والسياق المشوق وصححه بنفس اللغة فوراً دون مقدمات."
                       corrected_body = await asyncio.to_thread(self.ai_engine.generate_text_sync, fix_prompt_body, 350)

                   db2.apply_immediate_correction(concept_id, lang_code, "hook", corrected_hook, validator["column"])
                   db2.apply_immediate_correction(concept_id, lang_code, "body", corrected_body, validator["column"])

                   if torch.cuda.is_available(): torch.cuda.empty_cache()
                   gc.collect()

           # =================================================================
           # 3⃣ تقفيل مصفوفة الـ 25 علامة بنجاح وبث النتائج للقرص والشات
           # =================================================================
           if telegram_progress_agent:
               await telegram_progress_agent.update_progress(95, "⚖ جاري مطابقة وتقفيل مصفوفة الـ 25 Check السيادية...")

           is_matrix_complete = db2.verify_and_finalize_checks(concept_id)
           if is_matrix_complete:
               if telegram_progress_agent:
                   await telegram_progress_agent.update_progress(100, "🎉 اكتمل الفرم بنجاح! الحالة الحالية: Approved to Audio.")
              
               all_final_texts = db2.get_all_scripts_for_checking(concept_id)
               texts_broadcast = f"🎬 **[حصاد منظومة الفرم]: النصوص المصقولة 25/25 APPROVED**\n\n"
              
               for lang_code, hook, body in all_final_texts:
                   texts_broadcast += f"🌍 **اللغة: [{lang_code.upper()}]**\n"
                   texts_broadcast += f"🪝 **الخطاف:** `{hook}`\n"
                   texts_broadcast += f"📝 **الموضوع:** {body}\n"
                   texts_broadcast += f"----------------------------------------\n"
              
               if telegram_progress_agent:
                   try:
                       await telegram_progress_agent.bot.send_message(
                           chat_id=str(telegram_progress_agent.chat_id),
                           text=texts_broadcast,
                           parse_mode="Markdown"
                       )
                   except Exception:
                       pass
              
               # 🔥 استدعاء تنظيف المعدات الحتمي والأخير للمرحلة الثانية لتفريغ الـ VRAM تماماً للخطوات المستقبلية
               self.purge_hardware_equipment()
              
               print(f"✅ [UPC PIPELINE SUCCESS]: المعرف {concept_id} قفل مصفوفة الـ 25 Check بنجاح وبث النصوص وتطهر العتاد.")
               return True
           else:
               if telegram_progress_agent:
                   await telegram_progress_agent.update_progress(0, "⚠ خرق في جودة المصفوفة: لم يتم إغلاق الـ 25 Check بالكامل بنجاح.")
               return False

       except Exception as e:
           print(f"❌ انهيار خط الإنتاج الداخلي لوكيل الكتابة: {str(e)}")
           if telegram_progress_agent:
               await telegram_progress_agent.update_progress(0, "❌ فشل حرج عتادي أثناء الكتابة أو الفحص المتتابع.")
           return False




