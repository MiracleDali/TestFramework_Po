"""
# file:     Base/baseAiAnalyse.py
"""

import sys
from pathlib import Path
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)
sys.path.append(str(BASE_DIR))
from Base.baseLogger import Logger
from Base.basePath import BasePath as BP
from Base.utils import read_config_ini
from openai import OpenAI

logger = Logger('Base/baseAiAnalyse.py').getLogger()



class AiAnalyse():
    """
    AI分析类
    """
    def __init__(self):
        self.config = read_config_ini(BP.CONFIG_FILE)
        self.run_config = self.config['AI配置']

        self.client = OpenAI(
            api_key = self.run_config['API_KEY'],
            base_url = self.run_config['BASE_URL']
            )
        self.model = self.run_config['MODEL']
        self.system_prompt = self.run_config['SYSTEM_PROMPT']
        self.enable_thinking = self.run_config.getboolean('ENABLE_THINKING')
        # print('====================================')
        # print(self.run_config['BASE_URL'])
        # print(self.run_config['MODEL'])
        # print(self.run_config['SYSTEM_PROMPT'])
        # print(self.run_config['ENABLE_THINKING'])
        # print('====================================')

    def chat(self, user_message: str, system_prompt: str = None) -> str:
        """
        发送消息并返回完整回复
        Args:
            user_message: 用户消息
            system_prompt: 可选的系统提示词，默认使用配置文件中的
        Returns:
            str: 完整的回复内容
        """

        try: 
            # 构建会话
            system_prompt = system_prompt or self.system_prompt
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ]

            # 构建其他参数
            extra_body = {
                "enable_thinking": self.enable_thinking,
                "thinking_budget": 50
            }

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                # **extra_body
            )
            return response.choices[0].message.content  # 返回完整回复

        except Exception as e:
            logger.exception(f"AI分析错误: {e}")

# 创建实例
_ai_chat = AiAnalyse()

# 外部调用
def ai_chat(user_message: str, system_prompt: str = None) -> str:
    """
    外部调用AI分析
    Args:
        user_message: 报错消息
        system_prompt: 可选的系统提示词，默认使用配置文件中的
    Returns:
        str: 完整的回复内容
    """
    return _ai_chat.chat(user_message, system_prompt)


if __name__ == "__main__":
    # 测试代码
    response = ai_chat("你是谁")
    print(response)



