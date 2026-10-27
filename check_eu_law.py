def check_legal_compliance(text):
   # فحص حظر الكراهية، العنف، أو خرق حقوق الملكية الرقمية
   illegal_keywords = ["اقتل", "عنف", "hate", "kill", "violence", "racist", "عنصري"]
   for word in illegal_keywords:
       if word in text.lower():
           return False, f"⚖️ مخالفة قانونية: النص يحتوي على محتوى يحث على العنف أو الكراهية: '{word}'"
   return True, "VALID"



