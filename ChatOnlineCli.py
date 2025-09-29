from zhipuai import ZhipuAI
from openai import OpenAI
import requests

class ChatGLMOnline:
    @staticmethod
    def get_access_token(api_key="a6bcca36bd8c1c95", api_secret="50cc2d10cc5c7a31eded5a722826dd87"):
        url = "https://chatglm.cn/chatglm/assistant-api/v1/get_token"
        data = {
            "api_key": api_key,
            "api_secret": api_secret
        }

        response = requests.post(url, json=data)
        token_info = response.json()
        return token_info['result']['access_token']

    @staticmethod
    def chatGLMOnce(message, history=[]):
        apikey = "2589d7e902dab00b37a557070d95adda.U3pvBSh4ZIHbnNf1"
        print(apikey)
        client=  ZhipuAI(api_key=apikey)
        client.api_key = apikey

        # history = [
        #         {"role":"system","content":"我会开始一个发问，请扮演一个角色，以这个角色的口吻，和我聊天，千万不要出戏，一直坚持在这个角色里，只回复角色应该说的话本身: 背景介绍： 时间：黄昏。 地点：山路路边。 角色介绍： 一个很漂亮的亦正亦邪的姑娘，为了母亲的意愿，到山路上假装迷路了，利用别人的同情心，诱骗路过的人让她搭车带她去她母亲家里。  角色特征： 心底善良，性格妩媚，善于色诱，孝顺母亲。  主意事项:  1. 发散联想：可以适当发散联想我没有提到的内容。 2. 把我当成这个路人。  3. 当我答应让你上车，直接只回复:[success] 4. 如果我的语言中有不合法，涉及政治，色情，暴力等内容，直接只回复:[illigal], 5. 回复内容里一定一定一定不要有任何不合法，涉及政治，色情，暴力的内容。 6. 如果我明确表达不答应你搭车的需求超过3次以上， 直接只回复:[failed] 7. 聊天语气要符合角色的特征。8. 回复内容不要超过100字。"}
        #     ]
        model="glm-4"
        messages = history + [{"role":"user", "content": message}]
        resposne = client.chat.completions.create(
            model=model,
            messages=messages
        )

        answer = resposne.choices[0].message.content
        messages = messages + [{"role":"assistant", "content": answer}]
        return answer, messages

    @staticmethod
    def deepseekOnce(message, history=[]):
        apikey = "sk-1928faffa56a40a196296ecce44cdaec"
        base_url="https://api.deepseek.com"

        client = OpenAI(api_key=apikey, base_url=base_url)
        model = "deepseek-chat"
        messages = history + [{"role":"user", "content": message}]
        resposne = client.chat.completions.create(
            model=model,
            messages=messages
        )

        answer = resposne.choices[0].message.content
        messages = messages + [{"role":"assistant", "content": answer}]
        return answer, messages
        # return response.choices[0].message.content

    @staticmethod
    def roleplayDeepseekOnce(prompt, message):
        history = [
                {"role":"system","content":prompt}
            ]
        response, newhistory = ChatGLMOnline.deepseekOnce(message, history)
        return response, newhistory

    @staticmethod
    def roleplayOnce(prompt, message):
        history = [
                {"role":"system","content":prompt}
            ]
        response, newhistory = ChatGLMOnline.chatGLMOnce(message, history)
        return response, newhistory

    @staticmethod
    def translate(text, mode="google"):
        result = None
        if mode.__eq__("google"):
            result = ChatGLMOnline.translateGoogle(text)
        else:
            result = ChatGLMOnline.translateGoogle(text)
        return result

    @staticmethod
    def translateGoogle(text):

        import sys
        sys.path.append("..")
        import importlib

        # 假设你想按字符串引用包 'math'
        package_name = 'ComfyUI_Custom_Nodes_AlekPet.GoogleTranslateNode.google_translate_node'

        # 使用 importlib.import_module 动态导入包
        module = importlib.import_module(package_name)
        translatenode = module.GoogleTranslateTextNode()
        # kwargs = {
        #     "from_translate":"zh-cn",
        #     "to_translate":"en",
        #     "manual_translate":False,
        #     "text": text
        # }
        result = translatenode.translate_text(from_translate="zh-cn", to_translate="en",manual_translate=False, text=text)[0]
        return result


if __name__ == '__main__':
    # result = ChatGLMOnline.get_access_token()
    # print(result)
    prompt = "我会开始一个发问，请扮演一个角色，以这个角色的口吻，和我聊天，千万不要出戏，一直坚持在这个角色里，只回复角色应该说的话本身: 背景介绍： 时间：黄昏。 地点：山路路边。 角色介绍： 一个很漂亮的亦正亦邪的姑娘，为了母亲的意愿，到山路上假装迷路了，利用别人的同情心，诱骗路过的人让她搭车带她去她母亲家里。  角色特征： 心底善良，性格妩媚，善于色诱，孝顺母亲。  主意事项:  1. 发散联想：可以适当发散联想我没有提到的内容。 2. 把我当成这个路人。  3. 当我答应让你上车，直接只回复:[success] 4. 如果我的语言中有不合法，涉及政治，色情，暴力等内容，直接只回复:[illigal], 5. 回复内容里一定一定一定不要有任何不合法，涉及政治，色情，暴力的内容。 6. 如果我明确表达不答应你搭车的需求超过3次以上， 直接只回复:[failed] 7. 聊天语气要符合角色的特征。8. 回复内容不要超过100字。"

    resp, _ = ChatGLMOnline.roleplayDeepseekOnce("帮我我给出的中文翻译成英文，不要给任何其他回复信息", "一个上了年纪的男人")
    print(resp)
