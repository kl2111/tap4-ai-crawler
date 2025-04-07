import os
import time
from dotenv import load_dotenv
import logging
from io import BytesIO
import requests
import oss2
from datetime import datetime
import random
from PIL import Image
from util.common_util import CommonUtil

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(filename)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OSSUtil:
    def __init__(self):
        load_dotenv()
        self.OSS_ENDPOINT = os.getenv('OSS_ENDPOINT_URL')
        self.OSS_ACCESS_KEY_ID = os.getenv('OSS_ACCESS_KEY_ID')
        self.OSS_ACCESS_KEY_SECRET = os.getenv('OSS_ACCESS_KEY_SECRET')
        self.OSS_BUCKET_NAME = os.getenv('OSS_BUCKET_NAME')
        self.OSS_CUSTOM_DOMAIN = os.getenv('OSS_CUSTOM_DOMAIN', '')

        # 创建阿里云OSS Bucket实例
        auth = oss2.Auth(self.OSS_ACCESS_KEY_ID, self.OSS_ACCESS_KEY_SECRET)
        self.bucket = oss2.Bucket(auth, self.OSS_ENDPOINT, self.OSS_BUCKET_NAME)

    def default_file_key(self, url, is_thumbnail=False):  # 修改方法名
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        
        # 根据url生成名字
        image_name = None
        if url:
            image_name = CommonUtil.get_name_by_url(url)
        else:
            image_name = random.randint(1, 1000)  # 生成随机值，范围可根据需求调整
        
        # 如果is_thumbnail True，则添加"thumbnail-"前缀
        if is_thumbnail:
            image_name = f"{image_name}-thumbnail"

        # 生成时间戳
        timestamp = int(time.time())
        # 构建默认的 file_key
        return f"tools/{year}/{month}/{day}/{image_name}-{timestamp}.png"
        
        logger.info(f"生成的文件key: {file_key}")
        return file_key

    def compress_image_to_webp(self, image_data, quality=85):
        image = Image.open(BytesIO(image_data))
        buffer = BytesIO()
        image.save(buffer, format='WEBP', quality=quality)
        buffer.seek(0)
        return buffer.getvalue()

    def upload_file_to_r2(self, file_path, file_key):
        try:
            # 上传文件
            if file_path and 'http' in file_path:
                # 如果文件路径是URL
                response = requests.get(file_path, headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
                })
                image_data = response.content
                # 压缩图片为WebP格式
                compressed_image_data = self.compress_image_to_webp(image_data)
                # 使用阿里云OSS上传
                self.bucket.put_object(file_key, compressed_image_data)
            else:
                with open(file_path, 'rb') as f:
                    image_data = f.read()
                    # 压缩图片为WebP格式
                    compressed_image_data = self.compress_image_to_webp(image_data)
                    # 使用阿里云OSS上传
                    self.bucket.put_object(file_key, compressed_image_data)

            logger.info(f"文件 '{file_path}' 成功上传到 '{self.OSS_BUCKET_NAME}/{file_key}'")
            if os.path.exists(file_path):
                os.remove(file_path)

            # 如果提供了自定义域名
            if self.OSS_CUSTOM_DOMAIN:
                file_url = f"https://{self.OSS_CUSTOM_DOMAIN}/{file_key}"
            else:
                file_url = f"https://{self.OSS_BUCKET_NAME}.{self.OSS_ENDPOINT}/{file_key}"

            logger.info(f"文件URL: {file_url}")
            return file_url
        except Exception as e:
            logger.error(f"上传文件过程中发生错误: {e}")
            return None
    def get_default_file_key(self, url: str, is_thumbnail: bool = False) -> str:
        from urllib.parse import urlparse
        import hashlib
        parsed_url = urlparse(url)
        base_name = parsed_url.netloc + parsed_url.path
        key_hash = hashlib.md5(base_name.encode()).hexdigest()
        suffix = "_thumb.webp" if is_thumbnail else ".webp"
        return f"images/{key_hash}{suffix}"
    
    def generate_thumbnail_image(self, url, image_key):
        try:
            # 下载图像文件
            image_data = self.bucket.get_object(image_key).read()

            # 使用Pillow库打开图像
            image = Image.open(BytesIO(image_data))

            # 将图像缩放为50%
            width, height = image.size
            new_width = int(width * 0.5)
            new_height = int(height * 0.5)
            resized_image = image.resize((new_width, new_height))

            # 创建一个BytesIO对象来保存缩略图
            thumbnail_buffer = BytesIO()
            resized_image.save(thumbnail_buffer, format='PNG')
            thumbnail_buffer.seek(0)

            # 压缩缩略图为WebP格式
            compressed_thumbnail_data = self.compress_image_to_webp(thumbnail_buffer.getvalue())

            # 将缩略图上传到阿里云OSS
            thumbnail_key = self.get_default_file_key(url, is_thumbnail=True)
            self.bucket.put_object(thumbnail_key, compressed_thumbnail_data)

            # 如果提供了自定义域名
            if self.OSS_CUSTOM_DOMAIN:
                file_url = f"https://{self.OSS_CUSTOM_DOMAIN}/{thumbnail_key}"
            else:
                file_url = f"https://{self.OSS_BUCKET_NAME}.{self.OSS_ENDPOINT}/{thumbnail_key}"
            
            logger.info(f"缩略图文件URL: {file_url}")
            return file_url
        except Exception as e:
            logger.error(f"生成缩略图过程中发生错误: {e}")
            return None