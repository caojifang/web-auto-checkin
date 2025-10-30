import aiohttp
import asyncio
import logging
from typing import Dict, Any
from plugins.base_plugin import BasePlugin

class GladosPlugin(BasePlugin):
    def __init__(self, global_config, site_config):
        super().__init__(global_config, site_config)
        self.base_url = "https://glados.rocks"
        self.cookie = site_config.get('config', {}).get('cookies', {}).get('cookie', '')
        if not self.cookie:
            logging.warning(f"{self.name} 未检测到cookie，请检查配置文件")

    async def login(self) -> bool:
        """GLaDOS 不需要登录，只需通过 cookie 访问接口验证有效性"""
        try:
            status_url = f"{self.base_url}/api/user/status"
            headers = {
                "cookie": self.cookie,
                "content-type": "application/json;charset=UTF-8",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }

            async with self.session.get(status_url, headers=headers) as response:
                if response.status != 200:
                    logging.error(f"{self.name} 登录验证失败，状态码: {response.status}")
                    return False
                result = await response.json()
                if result.get("code") == 0:
                    logging.info(f"{self.name} cookie 有效，登录验证成功")
                    return True
                else:
                    logging.error(f"{self.name} 登录验证失败: {result}")
                    return False

        except Exception as e:
            logging.error(f"{self.name} 登录异常: {str(e)}")
            return False

    async def checkin(self) -> Dict[str, Any]:
        """执行 GLaDOS 签到操作"""
        try:
            checkin_url = f"{self.base_url}/api/user/checkin"
            headers = {
                "cookie": self.cookie,
                "content-type": "application/json;charset=UTF-8",
                "referer": f"{self.base_url}/console/checkin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }

            data = {"token": "glados.network"}

            async with self.session.post(checkin_url, headers=headers, json=data) as response:
                if response.status != 200:
                    raise Exception(f"签到请求失败，状态码: {response.status}")

                result = await response.json()
                message = result.get("message", "")
                logging.info(f"{self.name} 签到响应: {result}")

                # 判断成功或失败
                if "success" in message.lower() or "checkin" in message.lower():
                    return {"success": True, "message": message or "签到成功"}
                else:
                    return {"success": False, "message": message or "签到失败"}

        except Exception as e:
            logging.error(f"{self.name} 签到异常: {str(e)}")
            return {"success": False, "message": f"签到异常: {str(e)}"}

def register_plugin():
    """注册插件"""
    return GladosPlugin
