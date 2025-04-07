import os
import logging
import traceback
from dotenv import load_dotenv
from util.common_util import CommonUtil
from google.generativeai import GenerativeModel
import google.generativeai as genai

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(filename)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
util = CommonUtil()

class LLMUtil:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('API_KEY')
        self.max_tokens = int(os.getenv('MAX_TOKENS', 100000))

        genai.configure(api_key=self.api_key)

        self.model_name = os.getenv('MODEL', "gemini-2.0-flash")
        self.model = GenerativeModel(self.model_name)
        self.detail_sys_prompt = os.getenv('DETAIL_SYS_PROMPT')
        self.tag_selector_sys_prompt = os.getenv('TAG_SELECTOR_SYS_PROMPT')
        self.language_sys_prompt = os.getenv('LANGUAGE_SYS_PROMPT')

        logger.info(f"使用模型: {self.model_name}")
        logger.info(f"模型类型: {type(self.model)}")
        logger.info(f"API Key: {self.api_key[:5]}...")
        logger.info(f"最大Token: {self.max_tokens}")

    def process_detail(self, user_prompt):
        logger.info("正在处理Detail...")
        return util.detail_handle(self.process_prompt(self.detail_sys_prompt, user_prompt))

    def process_tags(self, user_prompt):
        logger.info(f"正在处理tags...")
        result = self.process_prompt(self.tag_selector_sys_prompt, user_prompt)
        return [tag.strip() for tag in result.split(',')] if result else []

    def process_language(self, language, user_prompt):
        logger.info(f"处理语言: {language}, 原文: {user_prompt}")
        if 'english' in language.lower():
            return user_prompt
        prompt = self.language_sys_prompt.replace("{language}", language)
        result = self.process_prompt(prompt, user_prompt)
        if result and not user_prompt.startswith("#"):
            result = result.replace("### ", "").replace("## ", "").replace("# ", "").replace("**", "")
        return result

    def process_prompt(self, sys_prompt, user_prompt):
        if not sys_prompt or not user_prompt:
            logger.error("系统提示词或用户输入为空")
            return None

        logger.info("开始处理LLM请求")
        logger.info(f"使用API Key: {self.api_key[:5]}...")
        logger.info(f"使用模型: {self.model_name}")

        try:
            full_prompt = f"{sys_prompt.strip()}\n\n---\n\n{user_prompt.strip()}"
            response = self.model.generate_content(
                full_prompt,
                generation_config={"max_output_tokens": self.max_tokens}
            )

            if hasattr(response, 'text') and response.text.strip():
                logger.info("LLM处理成功")
                return response.text.strip()
            else:
                logger.error("模型返回为空或无有效内容")
                return None

        except Exception as e:
            logger.error(f"调用模型失败: {e}")
            logger.error(traceback.format_exc())
            return None