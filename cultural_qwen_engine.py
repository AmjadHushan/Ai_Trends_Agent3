# cultural_qwen_engine.py
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import gc

class CulturalQwenEngine:
   def __init__(self, model_path="Qwen/Qwen2.5-0.5B-Instruct"):
       self.model_path = model_path
       self.tokenizer = None
       self.model = None
      
       # قواعد الكثافة اللفظية المعتمدة بناءً على نوع المحتوى (Genre-Based Word Density)
       self.genre_rules = {
           "روبورتاج عميق": {"words_per_minute": 155, "style_guide": "اعتمد على الأرقام، الدقة الصارمة، التحقيق الاستقصائي الصادم، وزخم المعلومات اللحظي السريع."},
           "قصة أطفال": {"words_per_minute": 100, "style_guide": "اعتمد على السرد الهادئ، العبارات العاطفية والمبسطة، التعبيرات المشوقة للغاية، وترك هوامش للوقفات الدرامية."},
           "فيلم درامي وثائقي": {"words_per_minute": 130, "style_guide": "امزج بين الحقائق العلمية والعمق الإنساني الفلسفي، وابنِ حبكة تصاعدية مثيرة تشد المشاهد لآخر ثانية."}
       }

   def load_brain(self):
       """شحن خلايا النموذج في الذاكرة العتبية لكارت الشاشة"""
       if self.model is None:
           print("⏳ [محرك Qwen]: جاري فتح وتهيئة عتاد الذاكرة العتادية وشحن كوين محلياً...")
           self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, local_files_only=True)
           self.model = AutoModelForCausalLM.from_pretrained(
               self.model_path,
               torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
               device_map="auto",
               local_files_only=True
           )

   def unload_brain(self):
       """بروتوكول التطهير العتادي والسبات البارد لتفريغ كاش CUDA لحماية الـ VRAM"""
       self.model = None
       self.tokenizer = None
       if torch.cuda.is_available():
           torch.cuda.empty_cache()
       gc.collect()
       print("❄ [تطهير العتاد]: تم إخلاء الـ VRAM بنجاح ودخول نافذة التبريد الحتمي لكارت الـ RTX.")

   def get_prompt_template(self, lang_code, base_manifest, genre, words_count, segment_num, prev_context):
       """هندسة الأوامر الثقافية بشكل منفصل تماماً لكل مجتمع مستهدف لمنع مشاكل الترجمة الحرفية"""
       cultural_guides = {
           "ara": "اكتب بلغة عربية فصحى بيضاء بليغة ومبسطة، مفهومة لكل الدول العربية عالمياً، خالية من التعقيد اللفظي أو الكلمات الهجينة.",
           "eng": "Write in premium global English, high impact, data-driven, urgent tone, and highly engaging for western corporate and modern audiences.",
           "deu": "Schreiben Sie auf Deutsch. Nutzen Sie präzise Fakten, logische Strukturen und eine tiefgründige, seriöse und packende Tonalität.",
           "spa": "Escriba en español. Use un tono narrativo apasionado, fluido, altamente cinematográfico, emocional y muy expresivo.",
           "hin": "हिंदी में लिखें। भारतीय उपद्वीप की सांस्कृतिक समझ, स्थानीय संवेदनाओं और भावनात्मक जुड़ाव को ध्यान में रखते हुए सिनेमाई शैली का उपयोग करें।"
       }

       prompt = (
           f"<|im_start|>system\n"
           f"أنت كاتب سيناريو محترف وعالم في سيكولوجية الجماهير وثقافة المجتمعات المستهدفة.\n"
           f"مهمتك المقفلة: صياغة وتوسيع المقطع رقم ({segment_num}) للسيناريو السينمائي بناءً على معطيات بطاقة الكاشط المعتمدة التالية:\n"
           f"📋 العنوان والأساس المعتمد: ({base_manifest['approved_manifest_text']})\n"
           f"🎭 الطراز السيكولوجي المقيد: [{base_manifest['style']}]\n"
           f"🎬 نوع المحتوى المستهدف: [{genre}]. دليل التوجيه الهيكلي: {self.genre_rules.get(genre, {}).get('style_guide', '')}\n"
           f"🌍 التوجيه الثقافي الصارم لمجتمع هذه اللغة: {cultural_guides.get(lang_code, cultural_guides['eng'])}\n"
           f"📏 الطول المطلوب والمستهدف لهذا المقطع: {words_count} كلمة تقريباً.\n"
           f"🔄 السياق السابق للمقطع الماضي (لمنع الانفصال السردي): {prev_context}\n"
           f"🚨 تنبيه صارم: اكتب النص السردي الصافي والمباشر الذي سينطقه المعلق فوراً، ويُمنع منعاً باتاً كتابة أي مقدمات مثل 'إليك المقطع' أو هوامش أو تعقيبات جانبية.<|im_end|>\n"
           f"<|im_start|>user\nانطلق بصياغة النص السردي الصافي للمقطع الآن:<|im_end|>\n"
           f"<|im_start|>assistant\n"
       )
       return prompt

   def generate_segment_text(self, lang_code, base_manifest, genre, words_count, segment_num, prev_context):
       """توليد النص الصافي للمقطع من كارت الشاشة مباشرة"""
       self.load_brain()
       prompt = self.get_prompt_template(lang_code, base_manifest, genre, words_count, segment_num, prev_context)
       inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
       with torch.no_grad():
           outputs = self.model.generate(
               **inputs, max_new_tokens=words_count + 120, temperature=0.65, do_sample=True, pad_token_id=self.tokenizer.eos_token_id
           )
       return self.tokenizer.decode(outputs[len(inputs.input_ids):], skip_special_tokens=True).strip()



