# style_rules_agent.py

class StyleRulesAgent:
   def __init__(self):
       # مصفوفة اتخاذ القرار الذكي لنوع المحتوى والمدة بناءً على طراز الكاشط لضمان ثبات الحبكة وثقافة المجتمع
       self.rules = {
           "وثائقي غامض": {"genre": "روبورتاج عميق", "duration": 10},
           "إثارة علمية": {"genre": "فيلم درامي وثائقي", "duration": 5},
           "تحقيق درامي واقعي": {"genre": "روبورتاج عميق", "duration": 8},
           "تشويقي محايد": {"genre": "قصة أطفال", "duration": 3}
       }

   def get_production_specs(self, psychological_style):
       """تحليل الطراز وإرجاع المدة الدقيقة ونوع المحتوى المعتمد للفيديو تلقائياً"""
       style_clean = psychological_style.strip()
       return self.rules.get(style_clean, {"genre": "فيلم درامي وثائقي", "duration": 5})


