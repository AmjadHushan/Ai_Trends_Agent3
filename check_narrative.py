def check_story_quality(text, lang_code):
   # فحص وجود علامات التشويق أو الكلمات المفتاحية التفاعلية بحسب اللغة
   hook_triggers = ["سر", "سرًا", "secret", "wahrheit", "geheimnis", "oculto", "रहस्य"]
   has_hook = any(trigger in text.lower() for trigger in hook_triggers)
  
   if not has_hook and len(text) < 20:
       return False, "⚠️ النص يفتقر إلى الخطاف النفسي (Viral Hook) أو عناصر الجذب."
   return True, "VALID"



