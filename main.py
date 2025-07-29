from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import File
from astrbot.api import logger

import jmcomic
import asyncio
import os

@register("jm_downloader", "Tsukimiya", "一个下载禁漫本子的小插件", "1.0.0", "https://github.com/tanzhanbo/astrbot_plugin_jm")
class JMDownloaderPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.option_path = os.path.join("data/plugins/astrbot_plugin_jm/option.yml")

    @filter.command("jm")
    async def jm(self, event: AstrMessageEvent):
        message_str = event.message_str.strip()
        parts = message_str.split()

        if len(parts) < 2:
            yield event.plain_result(f"@{user_name} 请提供本子编号，例如：/jm 350234")
            return

        album_id = parts[1]
        user_name = event.get_sender_name()
        yield event.plain_result(f"@{user_name} 请求下载本子 ID: {album_id}")
        
        # 构造 pdf 路径
        path = os.path.abspath(os.path.dirname(__file__))
        pdf_path = f"{path}/pdf/{album_id}.pdf"

        # 如果文件已经存在，直接发送
        if os.path.exists(pdf_path):
            yield event.plain_result(f"@{user_name} 本子 {album_id} 已存在，正在发送 PDF...")
            yield event.chain_result([File(name=f"{album_id}.pdf", file=pdf_path)])
            return

        try:
            def download():
                option = jmcomic.create_option_by_file(self.option_path)
                option.download_album(album_id)

            await asyncio.get_event_loop().run_in_executor(None, download)

            if os.path.exists(pdf_path):
                yield event.plain_result(f"@{user_name} ✅ 下载完成，发送 PDF 文件：")
                yield event.chain_result([File(name=f"{album_id}.pdf", file=pdf_path)])
            else:
                yield event.plain_result(f"@{user_name} ❌ 本子 {album_id} 下载完成，但未找到 PDF 文件，请更换ID后重试。")
        except Exception as e:
            logger.error(f"@{user_name} 下载出错: {str(e)}")
            yield event.plain_result(f"@{user_name} ❌ 下载失败：{str(e)}")

    async def terminate(self):
        logger.info("JMDownloader 插件已卸载")
