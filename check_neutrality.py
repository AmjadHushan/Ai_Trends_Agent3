def check_sovereign_neutrality(text):
   # حظر الكلمات التي تضفي تقديساً سياسياً أو عقائدياً خارج الإطار المحدد
   bias_keywords = ["مقدس", "إلهي", "holy", "sacred", "divine", "الزعيم الأوحد"]
   for word in bias_keywords:
       if word in text.lower():
           return False, f"🛑 خرق الحيادية: النص يحتوي على إضفاء قدسية أو تحيز أيديولوجي: '{word}'"
   return True, "VALID"



