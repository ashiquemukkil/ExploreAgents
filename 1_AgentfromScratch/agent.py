from typing import Any

from open_ai import client,AZURE_CHAT_DEPLOYMENT_NAME

class Agent:
    def __init__(self,system="") -> None:
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role":"system","content":system})

    def __call__(self,message, *args: Any, **kwds: Any) -> Any:
        self.messages.append({"role":"user","content":message})
        result = self.run()
        self.messages.append({"role":"assistant","content":result})
        return result

    def run(self):
        response = client.chat.completions.create(
            model=AZURE_CHAT_DEPLOYMENT_NAME,
            messages=self.messages
        )
        return response.choices[0].message.content