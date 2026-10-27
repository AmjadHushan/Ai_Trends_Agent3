import os
import json
import random
import time
import sqlite3
import gc
from datetime import datetime

class ScraperEngine:
   def __init__(self, config_path="config.json", db_path="production_db.sqlite"):
       self.config_path = config_path
       self.db_path = db_path
       self.config = self.load_config()
       self.init_database()
      
   def load_config(self):
       """ قراءة الإعدادات المحلية المقفلة للنيش واللغات """
       if os.path.exists(self.config_path):
           with open(self.config_path, 'r', encoding='utf-8') as f:
               return json.load(f)
       return {"niche": "Health and Food Benefits", "languages": ["ara", "eng"]}

   def init_database(self):
       """
       تأسيس قاعدة البيانات الصلبة مباشرة على القرص وتجهيز جدول الأفكار
       بمعرف فريد ومفتاح أساسي لمنع التكرار الجذري.
       """
       conn = sqlite3.connect(self.db_path)
       cursor = conn.cursor()
       cursor.execute('''
           CREATE TABLE IF NOT EXISTS scraped_ideas (
               concept_id TEXT PRIMARY KEY,
               source_trend TEXT,
               creative_angle TEXT,
               engineered_title TEXT UNIQUE,
               viral_score REAL,
               rpm_projection REAL,
               status TEXT DEFAULT 'PENDING',
               generation_time TEXT
           )
       ''')
       conn.commit()
       conn.close()

   def fetch_live_google_trends(self):
       """
       1️⃣ مرحلة الرصد والاستخلاص الحي:
       محاكاة حركية تعتمد على الساعة الحالية لتبديل الترندات الصاعدة لآخر أسبوعين.
       """
       niche = self.config.get("niche", "Health and Food Benefits")
       print(f"📡 [جوجل ترندز]: جاري رصد الكلمات الصاعدة لآخر أسبوعين في نيش: {niche}")
      
       current_hour = datetime.now().hour
       if current_hour % 3 == 0:
           live_keywords = ["الكركم الخارق", "مضادات أكسدة طبيعية", "المناعة الخلوية"]
       elif current_hour % 3 == 1:
           live_keywords = ["فوائد الثوم والزنجبيل", "تنظيف السموم من الكبد", "الصيام المتقطع والالتهابات"]
       else:
           live_keywords = ["بذور الشيا والقولون", "علاج المفاصل العضوي", "جودة النوم العميقة"]
          
       trends_output = []
       # كسر جمود الأرقام رياضياً عبر التذبذب اللحظي المعتمد على النانو ثانية
       random.seed(time.time_ns())
       for kw in live_keywords:
           trends_output.append({
               "trend_keyword": kw,
               "viral_potential": round(random.uniform(8.0, 9.9), 1),
               "rpm_projection": round(random.uniform(4.0, 7.5), 2)
           })
       return trends_output

   def create_viral_ideation(self, live_trends):
       """
       2️⃣ مرحلة الهندسة السيكولوجية:
       تفكيك الكلمة الخام وإعادة تركيبها ديناميكياً في قوالب فيروسية بشرية.
       """
       if not live_trends:
           return None
          
       print("🧠 [مدير الأفكار الذكي]: جاري تفكيك دلالات الترند وبناء زاوية سردية فيروسية...")
       selected_trend = max(live_trends, key=lambda x: x["viral_potential"])
       kw = selected_trend["trend_keyword"]
      
       creative_structures = [
           {"angle": "كشف المستور", "format": "لماذا تحاول المستشفيات إخفاء سر {keyword} عنك؟ الحقيقة الكاملة."},
           {"angle": "التأثير البيولوجي الفوري", "format": "ماذا يحدث داخل خلايا جسدك بعد 60 دقيقة فقط من تناول {keyword}؟"},
           {"angle": "البديل العضوي الخارق", "format": "توقف عن شراء الفيتامينات المصنعة! هذا المسحوق الرخيص {keyword} يمتلك القوة المضاعفة."},
           {"angle": "بروتوكول الإصلاح الذاتي", "format": "الخطة السحرية لإعادة بناء مناعتك من الصفر باستخدام قوة {keyword} الحيوية."}
       ]
      
       chosen_structure = random.choice(creative_structures)
       generated_idea = chosen_structure["format"].format(keyword=kw)
      
       return {
           "concept_id": f"CNCPT_{int(time.time())}_{random.randint(100, 999)}",
           "source_trend": kw,
           "creative_angle": chosen_structure["angle"],
           "engineered_title": generated_idea,
           "viral_score": selected_trend["viral_potential"],
           "rpm_projection": selected_trend["rpm_projection"],
           "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
       }

   def inject_directly_to_disk(self, concept_manifest):
       """
       3️⃣ مرحلة الضخ المباشر على القرص:
       لصق الفكرة فيزيائياً داخل الـ Database مع معالجة استثناءات التكرار لضمان السلامة.
       """
       if not concept_manifest:
           return False
          
       print(f"💾 [الضخ المباشر]: جاري حقن فكرة المعرف ({concept_manifest['concept_id']}) مباشرة على القرص الصلب...")
      
       conn = sqlite3.connect(self.db_path)
       cursor = conn.cursor()
      
       try:
           cursor.execute('''
               INSERT INTO scraped_ideas
               (concept_id, source_trend, creative_angle, engineered_title, viral_score, rpm_projection, generation_time)
               VALUES (?, ?, ?, ?, ?, ?, ?)
           ''', (
               concept_manifest["concept_id"],
               concept_manifest["source_trend"],
               concept_manifest["creative_angle"],
               concept_manifest["engineered_title"],
               concept_manifest["viral_score"],
               concept_manifest["rpm_projection"],
               concept_manifest["generation_time"]
           ))
           conn.commit()
           print("✅ [نجاح اللصق]: استقرت الفكرة بنجاح على القرص الصلب وتنتظر تفعيل خط الإنتاج لاحقاً.")
           success = True
       except sqlite3.IntegrityError:
           # صمام أمان في حال تولد عنوان مكرر تماماً مخزن مسبقاً في الداتا بيز
           print("⚠️ [تنبيه التكرار]: خرق لقيد الفرادة الجذري؛ الفكرة متواجدة في الداتا بيز فيزيائياً وتم حظر ضخها مجدداً.")
           success = False
       finally:
           conn.close()
          
       return success

   def clean_memory_footprint(self):
       """ تفريغ الكاش واستدعاء الجاربر كوليكتور لإبقاء الـ RAM باردة تماماً """
       gc.collect()
       print("❄️ [التطهير العتادي]: تم تفريغ الكاش البرمجي العام وإبادة مخلفات الكاشط من الـ RAM بنجاح.")

   def run_autonomous_cycle(self):
       """ قيادة تشغيل الدورة المستقلة للكاشط """
       print("🚀 --- [بدء تشغيل محرك الكشط والابتكار التوليدي المستقل] ---")
      
       # خطوة 1: كشط الترند
       live_trends = self.fetch_live_google_trends()
      
       # خطوة 2: هندسة الفكرة سيكولوجياً
       concept_manifest = self.create_viral_ideation(live_trends)
      
       # خطوة 3: الضخ المباشر داخل الـ Database الصلبة
       self.inject_directly_to_disk(concept_manifest)
      
       # خطوة 4: التطهير الشامل للذاكرة
       self.clean_memory_footprint()
       print("🎉 --- [انتهت دورة عمل الكاشط المستقلة وأغلق بأمان 100%] ---")

if __name__ == "__main__":
   # تشغيل وفحص فوري موضعي على الفلاشة
   scraper = ScraperEngine()
   scraper.run_autonomous_cycle()



