import os
from dotenv import load_dotenv
import logging
import google.generativeai as genai
from transformers import LlamaTokenizer
from util.common_util import CommonUtil

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(filename)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
util = CommonUtil()
# 不使用LlamaTokenizer，而是用字符长度作为简单估计
if len(user_prompt) > 100000:  # 简单限制为10万字符
    logger.info(f"用户输入长度超过100000字符，进行截取")
    user_prompt = user_prompt[:100000]

class LLMUtil:
    def __init__(self):
        load_dotenv()
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        logger.info(f"Gemini API Key:{self.gemini_api_key}")
        self.detail_sys_prompt = os.getenv('DETAIL_SYS_PROMPT')
        self.tag_selector_sys_prompt = os.getenv('TAG_SELECTOR_SYS_PROMPT')
        self.language_sys_prompt = os.getenv('LANGUAGE_SYS_PROMPT')
        self.gemini_model = "gemini-2.5-pro-exp-03-25"
        self.gemini_max_tokens = int(os.getenv('GEMINI_MAX_TOKENS', 5000))
        
        # 初始化Gemini客户端
        genai.configure(api_key=self.gemini_api_key)
        
    def process_detail(self, user_prompt):
        logger.info("正在处理Detail...")
        return util.detail_handle(self.process_prompt(self.detail_sys_prompt, user_prompt))

    def process_tags(self, user_prompt):
        logger.info(f"正在处理tags...")
        result = self.process_prompt(self.tag_selector_sys_prompt, user_prompt)
        # 将result（逗号分割的字符串）转为数组
        if result:
            tags = [element.strip() for element in result.split(',')]
        else:
            tags = []
        logger.info(f"tags处理结果:{tags}")
        return tags

    def process_language(self, language, user_prompt):
        logger.info(f"正在处理多语言:{language}, user_prompt:{user_prompt}")
        # 如果language 包含 English字符，则直接返回
        if 'english'.lower() in language.lower():
            result = user_prompt
        else:
            result = self.process_prompt(self.language_sys_prompt.replace("{language}", language), user_prompt)
            if result and not user_prompt.startswith("#"):
                # 如果原始输入没有包含###开头的markdown标记，则去掉markdown标记
                result = result.replace("### ", "").replace("## ", "").replace("# ", "").replace("**", "")
        logger.info(f"多语言:{language}, 处理结果:{result}")
        return result

    def process_prompt(self, sys_prompt, user_prompt):
        if not sys_prompt:
            logger.info(f"LLM无需处理，sys_prompt为空:{sys_prompt}")
            return None
        if not user_prompt:
            logger.info(f"LLM无需处理，user_prompt为空:{user_prompt}")
            return None

        logger.info("LLM正在处理")
        try:
            tokens = tokenizer.encode(user_prompt)
            if len(tokens) > self.gemini_max_tokens:
                logger.info(f"用户输入长度超过{self.gemini_max_tokens}，进行截取")
                truncated_tokens = tokens[:self.gemini_max_tokens]
                user_prompt = tokenizer.decode(truncated_tokens)
            
            # 创建Gemini模型实例
            model = genai.GenerativeModel(self.gemini_model)
            
            # 构建消息结构
            prompt = f"{sys_prompt}\n\n{user_prompt}"
            
            # 获取生成结果
            response = model.generate_content(prompt, generation_config={
                "temperature": 0.2,
                "top_p": 0.95,
                "top_k": 64,
            })
            
            if response and response.text:
                logger.info(f"LLM完成处理，成功响应!")
                return response.text
            else:
                logger.info("LLM完成处理，处理结果为空")
                return None
        except Exception as e:
            logger.error(f"LLM处理失败", e)
            return None
