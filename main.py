import os
import subprocess
import shutil
import tempfile
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("jmcomic", "YourName", "从JMComic下载漫画", "1.0.0")
class JMComicPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.jmcomic_path = os.path.abspath("./JMComic-Crawler-Python")

    async def initialize(self):
        logger.info("JMComic插件初始化完成")

    @filter.command("jm")
    async def jmcomic(self, event: AstrMessageEvent):
        """输入 /jm <漫画ID> 下载漫画并返回压缩文件"""
        args = event.args
        if not args:
            yield event.plain_result("请提供漫画 ID，例如 /jmcomic 350234")
            return

        # 拼接命令
        cmd = ["jmcomic"] + args
        logger.info(f"执行命令: {' '.join(cmd)}")

        try:
            # 临时目录，用于压缩结果
            temp_dir = tempfile.mkdtemp()
            old_cwd = os.getcwd()
            os.chdir(temp_dir)  # 将下载路径改为临时目录

            # 调用命令行
            result = subprocess.run(cmd, cwd=self.jmcomic_path, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(result.stderr)
                yield event.plain_result(f"下载失败: {result.stderr.strip()}")
                return

            # 查找下载后的目录
            files = os.listdir(temp_dir)
            if not files:
                yield event.plain_result("下载完成，但未发现任何文件。")
                return

            # 将目录压缩为 zip
            zip_name = os.path.join(temp_dir, "comic.zip")
            shutil.make_archive(zip_name[:-4], 'zip', temp_dir)

            # 发送压缩包
            yield event.file_result(zip_name)

        except Exception as e:
            logger.exception("执行 jmcomic 时出错")
            yield event.plain_result(f"下载过程中出现错误: {str(e)}")

        finally:
            os.chdir(old_cwd)
            shutil.rmtree(temp_dir, ignore_errors=True)

    async def terminate(self):
        logger.info("JMComic 插件被卸载")
