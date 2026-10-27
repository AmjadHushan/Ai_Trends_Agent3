import asyncio

class ProgressBarAgent:
   def __init__(self, bot_context, chat_id, message_id):
       self.bot = bot_context.bot
       self.chat_id = chat_id
       self.message_id = message_id

   def build_visual_bar(self, percentage):
       """بناء شكل خط التعبئة البصري السينمائي بناءً على النسبة"""
       total_blocks = 10
       filled_blocks = int(percentage / 10)
       empty_blocks = total_blocks - filled_blocks
       return "█" * filled_blocks + "░" * empty_blocks

   async def update_progress(self, percentage, stage_text):
       """
       تحديث العداد حياً وتفصيلياً أمام عينك في التليجرام.
       يتحرك الكود بالمليمتر والنسبة المئوية ليعطيك إيقاعاً حياً خارقاً.
       """
       bar_visual = self.build_visual_bar(percentage)
       full_text = f"⏳ **[منظومة الفرم]: {stage_text}**\n\n{bar_visual} [{percentage}%]"
       try:
           await self.bot.edit_message_text(
               chat_id=self.chat_id,
               message_id=self.message_id,
               text=full_text,
               parse_mode="Markdown"
           )
           # إعطاء نافذة تنفس خفيفة للشبكة لمنع الحظر التلقائي (Flood Control)
           await asyncio.sleep(0.4)
       except Exception:
           pass



