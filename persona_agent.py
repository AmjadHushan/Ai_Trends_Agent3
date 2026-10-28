# persona_agent.py

class CinematicPersonaAgent:
   def __init__(self):
       # مصفوفة ربط الأنماط السيكولوجية التسويقية بنبرات الصوت السينمائية الصارمة
       self.tone_mapping = {
           "وثائقي غامض": "Dramatically Deep & Whispering (عميق، غامض وجهير)",
           "إثارة علمية": "Energetic, Fast-Paced & Intense (سريع، حماسي وقوي الإيقاع)",
           "تحقيق درامي واقعي": "Serious, Authoritative & Grounded (جاد، سلطوي وواقعي الثبات)",
           "تشويقي محايد": "Suspenseful, Moderate & Captivating (تشويقي، معتدل وجاذب للانتباه)"
       }

   def analyze_and_lock_persona(self, engineered_title, psychological_style):
       """تحليل بنية العنوان لقفل الهوية الصوتية والجنس قبل بدء التوليد النصي"""
       clean_title = engineered_title.lower()
       clean_style = psychological_style.strip()

       selected_tone = self.tone_mapping.get(clean_style, "Suspenseful, Moderate & Captivating (تشويقي، معتدل)")

       # الهندسة السيكولوجية لاختيار الجنس (ذكر/أنثى) بناءً على دلالات الكلمات والنيش الحالي
       if any(word in clean_title for word in ["محرك", "سيارات", "بطاريات", "ليثيوم", "تكنولوجيا", "صناعة", "المستقبل"]):
           locked_gender = "Male"
       elif any(word in clean_title for word in ["مناعة", "خلايا", "علاج", "بذور", "صحة", "أطفال", "الكركم", "الكبد"]):
           locked_gender = "Female"
       else:
           locked_gender = "Male"

       print(f"🎭 [Persona Agent]: Locked Gender: [{locked_gender}] | Tone Curve: [{selected_tone}]")
       return {
           "voice_gender": locked_gender,
           "voice_tone": selected_tone
       }



