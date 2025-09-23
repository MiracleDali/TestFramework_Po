"""
# file:     Base/baseAiAnalyse.py
"""

import sys
from pathlib import Path
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from Base.baseData import DataBase
from Base.baseLogger import Logger
from Base.basePath import BasePath as Bp
from openai import OpenAI

logger = Logger('Base/baseAiAnalyse.py').getLogger()


class StreamChat:
    """封装流式 ChatCompletion """
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def chat_stream(self, messages: list, extra_body: dict = None):
        """
        发送消息并流式接收回复（包含思考过程 + 最终回复）
        """
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            extra_body=extra_body or {},
            stream=True
        )
        self._process_stream(completion)

    def _process_stream(self, completion):
        """处理流数据，分别打印思考过程和完整回复"""
        is_answering = False
        print("\n" + "=" * 20 + " 思考过程 " + "=" * 20)
        for chunk in completion:
            delta = chunk.choices[0].delta
            # 输出思考过程
            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                if not is_answering:
                    print(delta.reasoning_content, end="", flush=True)
            # 输出最终回答
            if hasattr(delta, "content") and delta.content:
                if not is_answering:
                    print("\n" + "=" * 20 + " 完整回复 " + "=" * 20)
                    is_answering = True
                print(delta.content, end="", flush=True)


if __name__ == "__main__":
    client = StreamChat(
        api_key="sk-",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-plus-2025-07-28"
    )

    messages = [{"role": "user", "content": "你是谁"}]
    client.chat_stream(messages, extra_body={"enable_thinking": True})


