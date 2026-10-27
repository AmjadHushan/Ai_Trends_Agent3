import re
import arabic_reshaper

def check_text_integrity(text, lang_code):
   # كاشف التكرار اللفظي المتتالي (n-gram Repetition) لمنع هلوسة النماذج الصغيرة
   words = re.findall(r'\b\w+\b', text.lower())
   for i in range(len(words) - 1):
       if words[i] == words[i+1]:
           return False, f"⚠️ تم رصد تكرار لفظي متتالي للكلمة: '{words[i]}'"
          
   if len(text.strip()) < 5:
       return False, "⚠️ الجملة ركيكة أو قصيرة جداً ولا تصلح للسرد البصري."
      
   return True, "VALID"



