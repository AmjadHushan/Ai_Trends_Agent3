def check_sharia_compliance(text):
   # قائمة الفلترة الصارمة للمحظورات الشرعية أو العقدية
   forbidden_keywords = ["موسيقى", "صنم", "الهة", "أصنام", "خمر", "ميسر", "magic", "idol", "pagan"]
   for word in forbidden_keywords:
       if word in text.lower():
           return False, f"🚫 مخالفة شرعية: تم رصد كلمة محظورة عقديًا أو شرعيًا: '{word}'"
   return True, "VALID"



