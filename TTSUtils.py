import json
import os.path,shutil
import sys
import requests
from pydub import AudioSegment
from gradio_client import Client, handle_file
from .OllamaCli import OllamaCli
from .DBUtils import DBUtils
from .ChatOnlineCli import ChatGLMOnline
from .config import ImmortalConfig

#
# script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(script_path)
# sys.path.append("")
# sys.path.append(script_path)
# from Utils import Utils
from .Utils import Utils

class TTSUtils:

    regularFemale=9245

    @staticmethod
    def ChatTTS(text, to, speed=1, voiceid=9245):
        headers = {"Content-Type": "application/json"}
        text = {"text": text, "seed": voiceid, "speed": speed}
        response = requests.post(ImmortalConfig.cosyvoiceurl, data=json.dumps(text), headers=headers)
        data = response.content
        Utils.mkdir(to)
        with open(to, mode='wb') as f:
            f.write(data)
        return to
        pass

    @staticmethod
    def ChatTTS_with_break(text, to, speed=5, voiceid=1342):
        pieces = TTSUtils.breakdownText(text)
        print(f"tts pieces: {pieces}")
        sound = None
        for piece in pieces:
            type = piece[0]
            value = piece[1]
            if type == 'str':
                # text path
                id, path = Utils.generatePathId(namespace="tts", exten="wav")
                dir = os.path.dirname(path)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                TTSUtils.ChatTTS(value, path, speed=speed, voiceid=voiceid)
                # TTSUtils.cosvoiceTTS_without_break(value, path, speakerID=speakerID)
                clip = AudioSegment.from_file(path, format='wav')
            elif type == 'audio':
                minsec = 2
                maxsec = 10
                splited = value.split('|')
                if len(splited) > 1:
                    minsec = int(splited[1])
                    if len(splited) > 2:
                        maxsec = int(splited[2])
                audiofile = TTSUtils.audio_gen(prompt=value, minduration=minsec, maxduration=maxsec)
                clip = AudioSegment.from_file(audiofile)
            else:
                clip = AudioSegment.silent(duration=int(value * 1000))

            if sound is None:
                sound = clip
            else:
                sound = sound + clip
        sound.export(to,format='wav')

    @staticmethod
    def getAudioFileByPrompt(prompt, negprompt, minduration):
        promptkey = f"{prompt}_{negprompt}_{minduration}"
        db = DBUtils()
        dt = db.doQuery(f"SELECT audiofile FROM immortal.audiostore where text='{promptkey}' order by time desc limit 1")
        if len(dt) > 0:
            path = Utils.getPathById(id=dt[0][0])
            return path
        return None

    @staticmethod
    def setAudioFileByPrompt(prompt, negprompt, filepath, minduration):
        promptkey = f"{prompt}_{negprompt}_{minduration}"
        id, path = Utils.generatePathId(namespace="ImmortalAudio", exten='wav')
        Utils.mkdir(path)
        shutil.move(filepath, path)
        db = DBUtils()
        db.doCommand(f"INSERT INTO `immortal`.`audiostore`(`text`,`audiofile`) VALUES ('{promptkey}', '{id}');")
        return path

    @staticmethod
    def audio_gen(prompt, negprompt=None, minduration=2, maxduration = 10):
        wavfile = TTSUtils.getAudioFileByPrompt(prompt, negprompt, minduration)
        if wavfile is None:
            wavfile = TTSUtils.stable_audio_tools(prompt, negprompt)
            wavfile = Utils.split_wav(wavfile, minsec=minduration, maxssec=maxduration, silentthresholdpercent=40)
            wavfile = TTSUtils.setAudioFileByPrompt(prompt, negprompt, wavfile, minduration)
        return wavfile

    @staticmethod
    def stable_audio_tools(prompt, negprompt=None):
        client = Client("http://127.0.0.1:7861/")
        translatedprompt, _ = ChatGLMOnline.roleplayDeepseekOnce("帮我我给出的中文翻译成英文，不要给任何其他回复信息", prompt)
        result = client.predict(
            prompt=translatedprompt,
            negative_prompt=negprompt,
            trans=False,
            seconds_start=0,
            seconds_total=47,
            cfg_scale=7,
            steps=100,
            preview_every=0,
            seed="-1",
            sampler_type="dpmpp-3m-sde",
            sigma_min=0.03,
            sigma_max=500,
            cfg_rescale=0,
            use_init=False,
            init_audio=None,
            init_noise_level=0.1,
            api_name="/generate"
        )
        return result[0]

    @staticmethod
    def cosvoiceTTS(text, to, speakerID='dushuai', instruct=""):
        pieces = TTSUtils.breakdownText(text)
        print(f"tts pieces: {pieces}")
        sound = None
        for piece in pieces:
            type = piece[0]
            value = piece[1]
            if type == 'str':
                # text path
                id, path = Utils.generatePathId(namespace="tts", exten="wav")
                dir = os.path.dirname(path)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                TTSUtils.cosvoiceTTS_without_break(value, path, speakerID=speakerID, instruct=instruct)
                clip = AudioSegment.from_file(path, format='wav')
            elif type == 'audio':
                minsec = 2
                maxsec = 10
                splited = value.split('|')
                if len(splited) > 1:
                    minsec = int(splited[1])
                    if len(splited) > 2:
                        maxsec = int(splited[2])
                audiofile = TTSUtils.audio_gen(prompt=value, minduration=minsec, maxduration=maxsec)
                clip = AudioSegment.from_file(audiofile)
            else:
                clip = AudioSegment.silent(duration=int(value * 1000))

            if sound is None:
                sound = clip
            else:
                sound = sound + clip
        Utils.mkdir(to)
        sound.export(to,format='wav')

    @staticmethod
    def cosvoiceTTS_with_subtitle(text, to=None, speakerID='dushuai', instruct=""):
        pieces = TTSUtils.breakdownText(text)
        print(f"tts pieces: {pieces}")
        sound = None
        subtitlesequence = []
        offset = 0
        for piece in pieces:
            type = piece[0]
            value = piece[1]
            if type == 'str':
                # text path
                id, path = Utils.generatePathId(namespace="tts", exten="wav")
                dir = os.path.dirname(path)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                TTSUtils.cosvoiceTTS_without_break(value, path, speakerID=speakerID, instruct=instruct)
                clip = AudioSegment.from_file(path, format='wav')
                duration = clip.duration_seconds
                subtitlesequence.append((offset, duration, value))
                offset += duration
            elif type == 'audio':
                minsec = 2
                maxsec = 10
                splited = value.split('|')
                if len(splited) > 1:
                    minsec = int(splited[1])
                    if len(splited) > 2:
                        maxsec = int(splited[2])
                audiofile = TTSUtils.audio_gen(prompt=value, minduration=minsec, maxduration=maxsec)
                clip = AudioSegment.from_file(audiofile)
                duration = clip.duration_seconds
                offset += duration
            else:
                clip = AudioSegment.silent(duration=int(value * 1000))
                duration = clip.duration_seconds
                offset += duration

            if sound is None:
                sound = clip
            else:
                sound = sound + clip
        if to is None:
            id, path = Utils.generatePathId(namespace='temp', exten='wav')
            to = path
        Utils.mkdir(to)
        sound.export(to,format='wav')
        return to, subtitlesequence

    @staticmethod
    def cosvoiceTTS_without_break(text, to, speakerID='dushuai', instruct=""):
        headers = {"Content-Type": "application/json"}
        text = {"text": text, "speaker": speakerID, "new": 1}
        if len(instruct) > 0:
            text["instruct"] = instruct
        response = requests.post(ImmortalConfig.cosyvoiceurl, data=json.dumps(text), headers=headers)
        data = response.content
        Utils.mkdir(to)
        with open(to, mode='wb') as f:
            f.write(data)
        return to
        pass

    @staticmethod
    def cosvoiceTTS_buildin_speaker(text, to=None):
        speakerTextList = TTSUtils.extractSpeakerFromText(text)
        sound = None
        for piece in speakerTextList:
            speakerid = piece[0]
            instruct = piece[1]
            content = piece[2]
            id, path = Utils.generatePathId(namespace="temp",exten="wav")
            Utils.mkdir(path)
            TTSUtils.cosvoiceTTS(content, path, speakerid, instruct)
            clip = AudioSegment.from_file(path, format='wav')
            if sound is None:
                sound = clip
            else:
                sound = sound + clip
        if to is None:
            _, to = Utils.generatePathId(namespace="temp",exten="wav")
            Utils.mkdir(to)
        sound.export(to, format='wav')
        return to

    @staticmethod
    def cosyvoiceTTS_buildin_speaker_with_subtitle(text, to=None):
        speakerTextList = TTSUtils.extractSpeakerFromText(text)
        sound = None
        subtitle = []
        offset = 0
        for piece in speakerTextList:
            speakerid = piece[0]
            instruct = piece[1]
            content = piece[2]
            id, path = Utils.generatePathId(namespace="temp",exten="wav")
            Utils.mkdir(path)
            path, subtitlechunk = TTSUtils.cosvoiceTTS_with_subtitle(content, path, speakerid, instruct)

            # update offset
            updated = []
            for ck in subtitlechunk:
                updated.append(((ck[0] + offset), ck[1], ck[2]))
            subtitle += updated
            if len(subtitlechunk) > 0:
                offset += subtitlechunk[-1][0] + subtitlechunk[-1][1]

            clip = AudioSegment.from_file(path, format='wav')
            if sound is None:
                sound = clip
            else:
                sound = sound + clip
        if to is None:
            _, to = Utils.generatePathId(namespace="temp",exten="wav")
            Utils.mkdir(to)
        sound.export(to, format='wav')
        return to, subtitle

    @staticmethod
    def extractSpeakerFromText(text:str)->list:
        speakerToken = "[speaker:"
        pieces = text.split(speakerToken)
        resultlist = []
        for p in pieces:
            txt = p.strip()
            if len(txt) == 0:
                continue

            splitchar = txt.index(']')
            speakerid = txt[0:splitchar]
            instruct = ""
            tk = speakerid.split('|')
            if len(tk) > 1:
                speakerid = tk[0]
                instruct = tk[1]
            rest = txt[splitchar+1:]
            resultlist.append((speakerid, instruct, rest))
        return resultlist
    @staticmethod
    def breakdownText(text:str):
        muteMode = False
        result = []
        temp = ""
        for char in text:
            if char == "[":
                muteMode = True
                if len(temp) > 0:
                    result.append(['str',temp])
                    temp = ""
                continue
            if char == "]":
                muteMode = False
                if len(temp) > 0:
                    result.append(['int', f'[{temp}]'])
                    temp = ""
                continue
            temp += char
        if len(temp) > 0:
            if muteMode:
                result.append(['int', f'[{temp}]'])
            else:
                result.append(['str', temp])


        for t in result:
            if t[0] == 'int':
                if not Utils.is_float(t[1][1:-1]):
                    if not t[1].__contains__(':'):
                        t[0] = 'str'
                    else:
                        tokens = t[1][1:-1].split(':')
                        type = tokens[0]
                        value = tokens[1]
                        t[0] = type
                        t[1] = value
                else:
                    t[1] = float(t[1][1:-1])

        temptype = None
        mergedresult = []
        for i in range(0,len(result)):
            r = result[i]
            if temptype is None:
                temptype = r[0]
                mergedresult.append(r)
                continue
            if temptype == 'str' and r[0] == 'str':
                lastmerge = mergedresult[-1]
                mergedresult[-1][1] = lastmerge[1] + f'{r[1]}'
            else:
                temptype = r[0]
                mergedresult.append(r)

        # final = []
        # for m in mergedresult:
        #     type = m[0]
        #     if type == 'str':
        #         final.append(m[1])
        #     elif type == 'int':
        #         final.append(float(m[1][1:-1]))
        return mergedresult


if __name__ == "__main__":
    textlist = \
        ["[speaker:dushuaiv2]宝贝，小朋友们不跟你玩，并不一定意味着他们不喜欢你。你知道吗？每个人都有自己的心情和想法，就像你有时候想在家里玩玩具，不想出门和其他小朋友玩一样。小朋友们不跟你玩的原因有很多：比如：小朋友们正在忙着自己的事情，他们可能在做一个特别有趣的游戏，没有注意到你想要加入。 还可能是小朋友比较害羞，不知道怎么邀请你一起玩。也可能他们不知道你也想和他们一起玩，因为有时候我们不容易看出别人是怎么想的。记住，事情的原因有很多，并不总是关于你。如果你想要和小朋友们一起玩，你可以试试主动一点，告诉他们你也想加入。如果你觉得还是有点难过，那也没关系，妈妈可以陪你一起想办法，让你能更容易地和小朋友们一起玩。 但是，请记得，你的价值不是由其他小朋友是否和你玩来决定的，你是一个很棒的孩子，不管别人怎么做，我们都非常爱你。"]
    result = []

    for txt in textlist:
        wavfile = TTSUtils.cosvoiceTTS_buildin_speaker(txt)
        result.append(wavfile)
    print(result)