from zhipuai import ZhipuAI
import requests

class ChatGLMOnline:
    @staticmethod
    def get_access_token(api_key="da4f3c5851fd3677", api_secret="355d5a8b8e24bb338bee40cfa63844e7"):
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
    def roleplayOnce(prompt, message):
        history = [
                {"role":"system","content":prompt}
            ]
        response, newhistory = ChatGLMOnline.chatGLMOnce(message, history)
        return response, newhistory

if __name__ == '__main__':
    prompt = "我会开始一个发问，请扮演一个角色，以这个角色的口吻，和我聊天，千万不要出戏，一直坚持在这个角色里，只回复角色应该说的话本身: 背景介绍： 时间：黄昏。 地点：山路路边。 角色介绍： 一个很漂亮的亦正亦邪的姑娘，为了母亲的意愿，到山路上假装迷路了，利用别人的同情心，诱骗路过的人让她搭车带她去她母亲家里。  角色特征： 心底善良，性格妩媚，善于色诱，孝顺母亲。  主意事项:  1. 发散联想：可以适当发散联想我没有提到的内容。 2. 把我当成这个路人。  3. 当我答应让你上车，直接只回复:[success] 4. 如果我的语言中有不合法，涉及政治，色情，暴力等内容，直接只回复:[illigal], 5. 回复内容里一定一定一定不要有任何不合法，涉及政治，色情，暴力的内容。 6. 如果我明确表达不答应你搭车的需求超过3次以上， 直接只回复:[failed] 7. 聊天语气要符合角色的特征。8. 回复内容不要超过100字。"

    resp, newhistory = ChatGLMOnline.roleplayOnce(prompt, "你好，你是谁")
    print(resp)
    print(newhistory)
