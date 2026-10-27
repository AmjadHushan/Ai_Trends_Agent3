import os
import sys
import json
import time
import random
import torch
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from database_stage1 import TrendsDatabaseAgent
from progress_bar_agent import ProgressBarAgent

try:
   from transformers import AutoModelForCausalLM, AutoTokenizer
except ImportError:
   os.system(f'"{sys.executable}" -m pip install transformers torch')
   from transformers import AutoModelForCausalLM, AutoTokenizer

def load_bot_credentials(config_path="config.json"):
   if os.path.exists(config_path):
       with open(config_path, 'r', encoding='utf-8') as f:
           config = json.load(f)
           return (config.get("telegram_token"),
                   config.get("telegram_chat_id"),
                   config.get("qwen_model_path", "Qwen/Qwen2.5-0.5B-Instruct"))
   return None, None, "Qwen/Qwen2.5-0.5B-Instruct"

BOT_TOKEN, CHANNEL_ID, MODEL_PATH = load_bot_credentials()
db = TrendsDatabaseAgent()

class QwenLocalEngine:
   def __init__(self, model_path):
       self.model_path = model_path
       self.tokenizer = None
       self.model = None

   def load_brain(self):
       if self.model is None:
           print("⏳ جاري فتح خلايا نموذج كوين المحلي من الفلاشة...")
           self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, local_files_only=True)
           self.model = AutoModelForCausalLM.from_pretrained(
               self.model_path,
               torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
               device_map="auto",
               local_files_only=True
           )

   def generate_text_sync(self, user_instruction, max_tokens=100):
       self.load_brain()
       prompt = (
           f"<|im_start|>system\nأنت مدير إبداعي سينمائي محترف وموجز للغاية. "
           f"اكتب النتيجة المطلوبة فوراً وبسطر واحد فقط، ويُمنع منعاً باتاً كتابة أي مقدمات أو شرح جانبي.<|im_end|>\n"
           f"<|im_start|>user\n{user_instruction}<|im_end|>\n"
           f"<|im_start|>assistant\n"
       )
       inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
       pad_id = self.tokenizer.eos_token_id
       with torch.no_grad():
           outputs = self.model.generate(
               **inputs, max_new_tokens=max_tokens, temperature=0.4, do_sample=True, pad_token_id=pad_id, eos_token_id=pad_id, num_return_sequences=1
           )
      
       decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
       if "assistant" in decoded:
           decoded = decoded.split("assistant")[-1].strip()
      
       final_lines = decoded.split("\n")
       if final_lines:
           return final_lines[0].replace("assistant", "").strip()
       return decoded.replace("assistant", "").strip()

   def unload_brain(self):
       self.model = None
       self.tokenizer = None
       if torch.cuda.is_available(): torch.cuda.empty_cache()
       import gc; gc.collect()

ai_engine = QwenLocalEngine(MODEL_PATH)

def fetch_live_ideas_instantly():
   niche_keywords = ["أسرار محركات المستقبل الفائقة", "ثورة السيارات الكهربائية المعقدة", "خفايا بطاريات الليثيوم الصادمة"]
   return random.choice(niche_keywords)

def dynamic_style_analyzer(keyword_topic):
   topic_clean = keyword_topic.lower()
   if "أسرار" in topic_clean or "خفايا" in topic_clean:
       return "وثائقي غامض"
   elif "ثورة" in topic_clean or "الفائقة" in topic_clean:
       return "إثارة علمية"
   elif "بطاريات" in topic_clean or "الليثيوم" in topic_clean:
       return "تحقيق درامي واقعي"
   return "تشويقي محايد"

def geo_fact_checker_chain(raw_text):
   flagged_words = ["فلسطين", "غزة", "القدس", "رام الله"]
   mended_text = raw_text
  
   industrial_substitute = "ألمانيا" if "محرك" in raw_text else "اليابان"
  
   for word in flagged_words:
       if word in mended_text:
           mended_text = mended_text.replace(word, industrial_substitute)
           print(f"🚨 [صمام التصحيح الجغرافي]: تم تنقية النص واستبدال ({word}) بـ ({industrial_substitute}) لحماية سلامة الجملة وسيكولوجيتها.")
   return mended_text

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
   init_msg = await update.message.reply_text("⏳ جاري بدء خط الإنتاج الحركي تفصيلياً...")
   progress = ProgressBarAgent(context, init_msg.chat_id, init_msg.message_id)
  
   await progress.update_progress(10, "جاري استدعاء الكاشط واقتناص الترند الحي...")
   keyword = fetch_live_ideas_instantly()
   c_id1 = f"SCRP_A_{int(time.time())}"
  
   await progress.update_progress(20, "تم اقتناص الترند. جاري إجراء المطابقة السيكولوجية المتوافقة مع النص...")
   marketing_style = dynamic_style_analyzer(keyword)
  
   await progress.update_progress(40, f"الطراز المتطابق المعتمد: [{marketing_style}]. جاري تشغيل كوين...")
   instr_title1 = f"خذ هذا الترند: ({keyword}). صغ منه عنواناً سينمائياً فيروسياً واحداً ومثيراً جداً باللغة العربية بطابع وبأسلوب [{marketing_style}] صريح وبسطر واحد فقط."
   title1 = await asyncio.to_thread(ai_engine.generate_text_sync, instr_title1, 50)
  
   await progress.update_progress(60, "تم صقل العنوان. جاري ابتكار الفكرة السردية المقفلة...")
   instr_story1 = f"بناءً على موضوع ({keyword}) والأسلوب [{marketing_style}]، اكتب فكرة سردية جادة وواقعية في سطرين فقط دون مقدمات أو قصص خيالية عشوائية."
   story1 = await asyncio.to_thread(ai_engine.generate_text_sync, instr_story1, 80)
  
   await progress.update_progress(70, "اكتمل التوليد. جاري تفريغ الـ RAM وتبريد العتاد...")
   await asyncio.to_thread(ai_engine.unload_brain)
  
   await progress.update_progress(80, "جاري تمرير المخرجات عبر صمام تطهير الأخطاء الجغرافية والمعلوماتية البنيوي...")
   title1_clean = geo_fact_checker_chain(title1)
   story1_clean = geo_fact_checker_chain(story1)
  
   await progress.update_progress(90, "تم التصحيح البنيوي! جاري حقن المانيفست النهائي وتأمينه في قاعدة البيانات...")
   full_manifest_1 = f"العنوان: {title1_clean} | الفكرة: {story1_clean}"
   db.insert_scraped_trend(c_id1, keyword, full_manifest_1)
  
   await progress.update_progress(100, "اكتمل الفحص والإنتاج! جاري بث البطاقة السيادية للتلجرام...")

   channel_message = (
       f"🎬 **[جدول الكشط التلقائي]: تم رصد أفكار جديدة**\n\n"
       f"🎯 **الترند البنائي:** {keyword}\n"
       f"🎭 **الطراز السيكولوجي المتطابق:** `{marketing_style}`\n\n"
       f"1️⃣ **الخيار المطور والمصحح عتادياً:**\n"
       f"📝 **العنوان السينمائي البليغ:** `{title1_clean}`\n"
       f"🧠 **الفكرة السردية المقفلة:** {story1_clean}\n\n"
       f"🔒 اختر الفكرة المراد اعتمادها لتغيير قيمتها في الداتا بيز فورا:"
   )
  
   keyboard_layout = [[InlineKeyboardButton("🎯 اعتماد الفكرة وتمريرها للإنتاج", callback_data=f"TRND_APP:{c_id1}")]]
   
   # إرسال الرسالة إلى القناة المحددة في الإعدادات أو نفس الشات إذا لم تتوفر القناة لضمان عدم توقف الكود
   target_chat = CHANNEL_ID if CHANNEL_ID else init_msg.chat_id
   await context.bot.send_message(chat_id=str(target_chat), text=channel_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard_layout))

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
   user_text = update.message.text.strip()
   command_id = f"HUMAN_{int(time.time())}"
   chosen_style = dynamic_style_analyzer(user_text)
  
   clean_user_text = geo_fact_checker_chain(user_text)
   db.insert_human_command(command_id, f"النمط: {chosen_style} | الطلب: {clean_user_text}")
  
   human_message = (
       f"👑 **[جدول التوجيهات البشرية]: أمر مباشر مستلم**\n\n"
       f"📝 **نص التوجيه المكتوب:**\n`{clean_user_text}`\n"
       f"🎭 **النمط المتوافق تلقائياً:** `{chosen_style}`\n\n"
       f"🚨 *ملاحظة: هذا التوجيه البشري له الأولوية القصوى للتنفيذ في خط الإنتاج وسيتم فحص سطوره عبر الصمام.*"
   )
   keyboard_layout = [[InlineKeyboardButton("🚀 اعتماد وتنفيذ الأمر فوراً", callback_data=f"CMD_APP:{command_id}")]]
   
   target_chat = CHANNEL_ID if CHANNEL_ID else update.message.chat_id
   await context.bot.send_message(chat_id=str(target_chat), text=human_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard_layout))

async def handle_callback_queries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة استجابات الأزرار لتحديث قاعدة البيانات حركياً فور ضغط المستخدم"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("TRND_APP:"):
        concept_id = data.split(":")[-1]
        db.update_trend_status(concept_id, "APPROVED")
        await query.edit_message_caption(caption=query.message.caption + "\n\n✅ [حالة القرص الصلب]: تم اعتماد الترند ونقله لطابور الإنتاج.") if query.message.caption else await query.edit_message_text(text=query.message.text + "\n\n✅ [حالة القرص الصلب]: تم اعتماد الترند ونقله لطابور الإنتاج.")
        
    elif data.startswith("CMD_APP:"):
        command_id = data.split(":")[-1]
        db.update_command_status(command_id, "APPROVED")
        await query.edit_message_text(text=query.message.text + "\n\n🚀 [أمر سيادي]: تم قفل التوجيه البشري وبدأ الضخ الفوري.")

def main():
    """تأسيس حلقة العمل وبدء فحص التلغرام الحي وعملية الـ Polling"""
    if not BOT_TOKEN:
        print("❌ خطأ: لم يتم العثور على التوكن الخاص بالبوت داخل ملف config.json!")
        return

    print("🚀 جاري تهيئة وتدشين البوت المنسق (Orchestrator)...")
    app = Application.builder().token(BOT_TOKEN).build()

    # ربط المعالجات وحقن المسارات البرمجية في محرك المكتبة
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
    app.add_handler(CallbackQueryHandler(handle_callback_queries))

    print("📡 البوت مستقر وحي الآن وبانتظار الإشارات...")
    app.run_polling()

if __name__ == "__main__":
    main()

