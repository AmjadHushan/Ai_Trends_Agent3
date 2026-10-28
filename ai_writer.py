# ai_writer.py
import os
import json
import sqlite3
import asyncio
from database_stage2_txt import ProductionTextDatabaseAgent
from persona_agent import CinematicPersonaAgent
from cultural_qwen_engine import CulturalQwenEngine
from style_rules_agent import StyleRulesAgent
from progress_bar_agent import ProgressBarAgent

# استدعاء صمامات الفحص الخمسة الصارمة التي قمت أنت ببنائها
from check_stutter import check_text_integrity
from check_eu_law import check_legal_compliance
from check_islamic import check_sharia_compliance
from check_neutrality import check_sovereign_neutrality
from check_narrative import check_story_quality

# استدعاء صمام التصحيح الجغرافي المطور والمشترك من الأوركسترا
from orchestrator_bot import geo_fact_checker_chain

class AIStoryProductionCoordinator:
   def __init__(self, db_stage1_path="trends_stage_db.sqlite"):
       self.db_stage1_path = db_stage1_path
       self.db_stage2 = ProductionTextDatabaseAgent()
       self.persona_agent = CinematicPersonaAgent()
       self.qwen_engine = CulturalQwenEngine()
       self.rules_agent = StyleRulesAgent()

   def fetch_approved_manifest_from_stage1(self, trend_id):
       """تطهير ومطابقة ميكانيكية شاملة لجميع الأنماط المحتملة للمعرّف النصي في ستيج 1"""
       conn = sqlite3.connect(self.db_stage1_path)
       cursor = conn.cursor()
      
       # توليد كافة الأشكال النصية المحتملة للمعرّف لقطع الطريق أمام أي تضارب أسماء
       id_variants = [trend_id]
      
       # إذا كان المعرف مضغوطاً مثل SCRPA1793202596 يتم تفكيكه إلى SCRP_A_1793202596
       if "SCRPA" in trend_id and "SCRP_A_" not in trend_id:
           id_variants.append(trend_id.replace("SCRPA", "SCRP_A_"))
          
       # إضافة احتمال وجود الشرطة في نهاية المقطع المكتوب
       if "SCRP_A" in trend_id:
           id_variants.append(trend_id.replace("SCRP_A_", "SCRPA"))

       try:
           for v_id in id_variants:
               # 1. البحث في جدول الكشط التلقائي للبوت الأصلي
               cursor.execute(
                   "SELECT trend_keyword, marketing_style FROM scraped_trends WHERE c_id = ? OR concept_id = ?",
                   (v_id, v_id)
               )
               row = cursor.fetchone()
               if row:
                   return {
                       "keyword": row[0],
                       "style": row[1],
                       "approved_manifest_text": f"الترند: {row[0]} | النمط السيكولوجي: {row[1]}"
                   }
              
               # 2. البحث التبادلي في جدول التوجيهات البشرية
               cursor.execute(
                   "SELECT command_text, style FROM human_commands WHERE command_id = ?",
                   (v_id,)
               )
               row_human = cursor.fetchone()
               if row_human:
                   return {
                       "keyword": row_human[0],
                       "style": row_human[1],
                       "approved_manifest_text": f"التوجيه البشري: {row_human[0]} | النمط: {row_human[1]}"
                   }
           return None
       except sqlite3.OperationalError as e:
           print(f"⚠️ تنبيه فحص الأعمدة الميكانيكي: {e}")
           return None
       finally:
           conn.close()

   async def run_stage2_production_pipeline(self, trend_id, bot_context, chat_id, message_id):
       """قيادة وإدارة طابور المعالجة المتتالية للغات الخمس مع التحكم الكامل والمستقل بملف التحميل"""
       progress = ProgressBarAgent(bot_context, chat_id, message_id)
       await progress.update_progress(5, "⏳ جاري استدعاء مستند الفكرة من ستيج 1 وفحص الطراز...")

       base_manifest = self.fetch_approved_manifest_from_stage1(trend_id)
       if not base_manifest:
           await progress.update_progress(0, f"❌ خطأ حرج: المعرف ({trend_id}) غير متطابق مع سطور الداتا بيز.")
           return

       # استدعاء الوكيل المجهري الذكي لاتخاذ قرار المدة والنوع أوتوماتيكياً
       specs = self.rules_agent.get_production_specs(base_manifest["style"])
       content_genre = specs["genre"]
       duration_minutes = specs["duration"]

       await progress.update_progress(12, f"🎬 القرار الذكي: [{content_genre}] لـ {duration_minutes} دقائق. جاري قفل الجندر...")
      
       persona_card = self.persona_agent.analyze_and_lock_persona(base_manifest["approved_manifest_text"], base_manifest["style"])
       self.db_stage2.create_production_ticket(trend_id, base_manifest["style"], content_genre, duration_minutes, persona_card["voice_gender"], persona_card["voice_tone"])

       segment_chunk_minutes = 3 if duration_minutes > 3 else duration_minutes
       total_segments = (duration_minutes + segment_chunk_minutes - 1) // segment_chunk_minutes
       words_per_minute = self.qwen_engine.genre_rules.get(content_genre, {"words_per_minute": 130})["words_per_minute"]
       words_per_segment = words_per_minute * segment_chunk_minutes
      
       target_languages = ["ara", "eng", "deu", "spa", "hin"]
       total_steps = len(target_languages) * total_segments
       current_step = 0

       for lang in target_languages:
           prev_segment_context = "بداية تدفق السيناريو السينمائي الصافي."
           for seg_idx in range(1, total_segments + 1):
               current_step += 1
               calc_percentage = int(15 + (current_step / total_steps) * 75)
               segment_id = f"SEG_{seg_idx:02d}"
               time_window = f"{(seg_idx - 1) * segment_chunk_minutes:02d}:00 - {min(seg_idx * segment_chunk_minutes, duration_minutes):02d}:00"
              
               stage_text = f"جاري صياغة قصة لغة: [{lang.upper()}] | {segment_id}"
               await progress.update_progress(calc_percentage, stage_text)
              
               raw_text = await asyncio.to_thread(self.qwen_engine.generate_segment_text, lang, base_manifest, content_genre, words_per_segment, seg_idx, prev_segment_context)
              
               # طابور الفحوصات الخمسة الميكانيكية الصارمة
               v1, _ = check_text_integrity(raw_text, lang)
               v2, _ = check_legal_compliance(raw_text)
               v3, _ = check_sharia_compliance(raw_text)
               v4, _ = check_sovereign_neutrality(raw_text)
               v5, _ = check_story_quality(raw_text, lang)
              
               clean_cinematic_text = geo_fact_checker_chain(raw_text)
              
               # فحص سجل المراجعات في ستيج 2 لمنع التكرار
               is_bl, _ = self.db_stage2.check_blacklisted_phrases(lang, clean_cinematic_text)
              
               self.db_stage2.inject_segment_safely(trend_id, segment_id, lang, time_window, (seg_idx == 1), clean_cinematic_text)
               prev_segment_context = clean_cinematic_text[:250]
          
           await asyncio.to_thread(self.qwen_engine.unload_brain)
          
       await progress.update_progress(95, "💾 جاري قفل السطور على القرص الصلب وتصدير تذكرة الجيسون...")
       self.db_stage2.update_ticket_status(trend_id, "APPROVED")
       self.export_final_manifest_json(trend_id)
       await progress.update_progress(100, "🎉 اكتمل إنتاج السرد الثقافي لجميع اللغات واستقر على القرص بنجاح 100%!")

   def export_final_manifest_json(self, trend_id):
       """سحب كافة السطور المصححة من قاعدة البيانات وإصدار تذكرة الجيسون الخفيفة"""
       conn = sqlite3.connect(self.db_stage2.db_path)
       cursor = conn.cursor()
       cursor.execute("SELECT * FROM production_tickets WHERE trend_id = ?", (trend_id,))
       ticket = cursor.fetchone()
       cursor.execute("SELECT segment_id, lang_code, time_window, is_hook, validated_text FROM story_segments WHERE trend_id = ?", (trend_id,))
       rows = cursor.fetchall()
       conn.close()
      
       if not ticket: return
       manifest = {"production_ticket": {"trend_id": ticket, "cinematic_style": ticket, "content_genre": ticket, "target_duration_minutes": ticket, "voice_gender": ticket, "voice_tone": ticket, "status": ticket}, "story_segments": {}}
       for r in rows:
           seg_id, lang, window, is_hook, text = r
           if seg_id not in manifest["story_segments"]:
               manifest["story_segments"][seg_id] = {"time_window": window, "is_hook": bool(is_hook), "languages": {}}
           manifest["story_segments"][seg_id]["languages"][lang] = text
          
       with open("manifest_output.json", "w", encoding="utf-8") as f:
           json.dump(manifest, f, ensure_ascii=False, indent=2)



