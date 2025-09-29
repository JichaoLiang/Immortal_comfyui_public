import os
import re
import random
import shutil
from pathlib import Path
from typing import Literal

import librosa
import moviepy
from moviepy import *
from moviepy import CompositeVideoClip
from moviepy import CompositeAudioClip
import soundfile as sf
from . import config
from .Utils import Utils
from .TTSUtils import TTSUtils
from .config import ImmortalConfig
from . import MovieEffect
# from moviepy.video.compositing import *
from moviepy.video.VideoClip import TextClip
#
# import Config.Config
# from MovieMaker.TTSAgent import TTSAgent
# from Utils.DataStorageUtils import DataStorageUtils
import wave
# from .. import Utils


class MovieMakerUtils:
    @staticmethod
    def enlargeFullScreen(clip: VideoClip, fullscreensize, inseconds: int):
        wdivh = clip.size[0] / clip.size[1]

        return MovieMakerUtils.animationTo(clip, (0, 0), fullscreensize, inseconds)
        pass

    @staticmethod
    def getTickStampsByInsecondsArray(inseconsArray):
        result = []
        tempTimestamp = 0
        for i in range(0, len(inseconsArray)):
            time = inseconsArray[i]
            tempTimestamp += time
            result.append(tempTimestamp)
        return result
        pass

    @staticmethod
    def normalizeWH(w, h, w_h_div):
        whdiv = w/h
        if whdiv > w_h_div:
            return h * w_h_div, h
        else:
            return w, w / w_h_div
        pass

    @staticmethod
    def animationsTo(clip: VideoClip|ImageClip, offsetArray, sizeArray, inseconsArray) -> VideoClip:
        posfuncArray = []
        sizefuncArray = []
        w_h_div = clip.size[0] / clip.size[1]
        targetDivOriginWidth = sizeArray[-1][0] / clip.size[0]
        for i in range(0, len(offsetArray)):
            def posFunc(t: int, iter = i):
                targetOffset = offsetArray[iter]
                inseconds = inseconsArray[iter]
                if iter == 0:
                    l, tp = clip.pos(0)
                else:
                    l, tp = offsetArray[iter - 1]

                movSpeed = (targetOffset[0] - l) / inseconds
                movSpeed2 = (targetOffset[1] - tp) / inseconds

                left = l + movSpeed * t
                # if left <= 0:
                #     left = 0
                top = tp + movSpeed2 * t
                # if top <= 0:
                #     top = 0
                if movSpeed > 0 and left > targetOffset[0] \
                        or movSpeed < 0 and left < targetOffset[0]:
                    left = targetOffset[0]
                if movSpeed2 > 0 and top > targetOffset[1] \
                        or movSpeed2 < 0 and top < targetOffset[1]:
                    top = targetOffset[1]
                # print(f'{left},{top},{t}')
                return (left, top)
                pass

            def sizeFunc(t: int, iter = i):
                inseconds = inseconsArray[iter]
                targetSize = sizeArray[iter]
                if iter == 0:
                    w, h = clip.size
                else:
                    w, h = sizeArray[iter -1]
                w, h = MovieMakerUtils.normalizeWH(w, h, w_h_div)

                nw = targetSize[0]
                nh = targetSize[1]

                speed = (nw - w) / w / inseconds

                neww = w + w * speed * t
                newh = h + h * speed * t

                # print(f'{neww},{newh}')
                if speed > 0:
                    if neww > targetSize[0]:
                        return (neww, newh)
                if speed < 0:
                    if neww < targetSize[0]:
                        return (neww, newh)
                return (neww, newh)
                pass

            posfuncArray.append(posFunc)
            sizefuncArray.append(sizeFunc)
        tickStamp = MovieMakerUtils.getTickStampsByInsecondsArray(inseconsArray)

        def posf(t):
            ts = 0
            for i in range(0, len(tickStamp)):
                if t < tickStamp[i]:
                    return posfuncArray[i](t - ts)
                ts = tickStamp[i]
            return posfuncArray[-1](t - ts)
            pass

        def sizef(t):
            ts = 0
            for i in range(0, len(tickStamp)):
                # print(tickStamp[i])
                if t < tickStamp[i]:
                    return sizefuncArray[i](t - ts)
                ts = tickStamp[i]
            return targetDivOriginWidth
            pass

        result = clip.with_position(lambda t: posf(t)).resized(lambda t: (sizef(t)))
        return result
        pass

    @staticmethod
    def animationTo(clip: VideoClip|ImageClip, targetOffset, targetSize, inseconds):
        w, h = clip.size
        wdivh = w / h
        nw = targetSize[0]
        nh = targetSize[1]
        targetwdivh = nw / nh
        if wdivh > targetwdivh:
            nh = nw / wdivh
        else:
            nw = nh * wdivh
        speed = (nw - w) / w / inseconds
        l, tp = clip.pos(0)
        movSpeed = (targetOffset[0] - l) / inseconds
        movSpeed2 = (targetOffset[1] - tp) / inseconds

        def posFunc(t: int):
            left = l + movSpeed * t
            if left <= 0:
                left = 0
            top = tp + movSpeed2 * t
            if top <= 0:
                top = 0

            # print(f'{left},{top},{t}')
            return (left, top)
            pass

        def sizeFunc(t: int):
            neww = w + w * speed * t
            newh = h + h * speed * t

            # print(f'{nw},{nh}')
            if speed > 0:
                if neww > targetSize[0]:
                    return (nw, nh)
            if speed < 0:
                if neww < targetSize[0]:
                    return (nw, nh)
            return (neww, newh)
            pass

        result = clip.with_position(lambda t: posFunc(t)).resized(lambda t: (sizeFunc(t)))
        return result
        pass

    @staticmethod
    def concatevideo():
        vpath = 'D:/BaiduNetdiskDownload/clip.mp4'
        vpath2 = 'D:/BaiduNetdiskDownload/clip2.mp4'
        toPath = 'D:/BaiduNetdiskDownload/clip3.mp4'
        video1 = VideoFileClip(vpath).subclipped(0, 10)

        video2 = VideoFileClip(vpath2).subclipped(0, 10)
        resized = video2.resized(0.3).with_position((50, 50)).with_start(2)
        moving = resized.with_position(lambda t: (50 + 10 * t, 50 + 10 * t)).resized(lambda t: 1 + 0.1 * t)
        # txtClip = TextClip('Cool effect', color='white', font="Amiri-Bold",
        #                    kerning=5, fontsize=100)
        # video1.fx(vfx.mirror_y)
        composited = CompositeVideoClip([video1, moving])
        # concatenated = concatenate_videoclips([video1,video2],method='chain') # method: chain compose
        if Path(toPath).exists():
            os.remove(toPath)
        composited.write_videofile(toPath)
        pass

    @staticmethod
    def setBGM(video:VideoClip, audio:AudioClip, vol=0.8):
        audio1 = video.audio
        looped = audio.with_volume_scaled(vol).with_effects([afx.AudioLoop(duration=video.duration)])

        print(f"audio1:{audio1}")
        print(f"audio2:{looped}")

        if audio1 is None:
            mixed = looped
        else:
            mixed = CompositeAudioClip([audio1, looped])
        return video.with_audio(mixed)
        pass

    def extendRotateDurationAudio(clip: AudioClip, durationSec, muteExtended = False):
        duration = clip.duration
        concatelist = [clip]
        while durationSec - duration > clip.duration:
            copy = clip.copy()
            if muteExtended:
                copy = copy.without_audio()
            concatelist.append(copy)
            duration += clip.duration
        if durationSec > duration:
            lastSec = clip.subclipped(0, durationSec - duration)
            if muteExtended:
                lastSec = lastSec.without_audio()
            concatelist.append(lastSec)
        return concatenate_audioclips(concatelist)
        pass

    @staticmethod
    def extendRotateDuration(clip: VideoClip, durationSec, muteExtended = False):
        duration = 0
        concatelist = []
        while durationSec - duration > clip.duration:
            copy = clip.copy()
            if len(concatelist) > 0 and muteExtended:
                copy = copy.without_audio()
            concatelist.append(copy)
            duration += clip.duration
        if durationSec > duration:
            lastSec = clip.subclipped(0, durationSec - duration)
            if len(concatelist) > 0 and muteExtended:
                lastSec = lastSec.without_audio()
            concatelist.append(lastSec)
        return concatenate_videoclips(concatelist)
        pass


    @staticmethod
    def seperatetextbynewline(question, sizewidth=1920, fontsize=80, charcount=20):
        result = ''
        for i in range(0, len(question)):
            result += question[i]
            if i > 0 and i % charcount == 0:
                result += '\n'
        return result
        pass
    # @staticmethod
    # def captionTextToVideoClip(clip:VideoClip, captionText: str):
    #     enlarged = clip.resized((1920, 1080))
    #     pieces = TTSAgent.splitText(captionText)
    #     offsetduration = 0
    #     textsubtitlecliplist = []
    #     for piece in pieces:
    #         rows = len(piece) / 20
    #         question = MovieMakerUtils.seperatetextbynewline(piece,1920,80)
    #         if rows > 4:
    #             question = MovieMakerUtils.seperatetextbynewline(piece, 1920, 28)
    #             rows = len(piece) / 28
    #         duration = clip.duration * len(piece) / len(captionText)
    #         fontsize = 65
    #         if rows > 3: # 三行以上,太高了
    #             fontsize = 48
    #         titleClip: TextClip = TextClip(question, font=Config.Config.Config.subtitlefont, color='white',
    #                                        align='center', stroke_color='black', fontsize=fontsize, bg_color='black', size=(1920, 290 - 54))
    #         if titleClip.size[0] > 1920 * 0.9:
    #             titleClip = titleClip.resized(1920 * 0.9 / titleClip.size[0]).with_position((96, 54 + 790))
    #
    #         titleClip = titleClip.with_duration(duration).with_start(offsetduration)
    #
    #         offsetduration += duration
    #         textsubtitlecliplist.append(titleClip)
    #     textsubtitlecliplist.insert(0,enlarged)
    #     composited = CompositeVideoClip(textsubtitlecliplist).resized(clip.size)
    #     return composited

    @staticmethod
    def getCaptureFile(videoPath, to, momentSec=1):
        clip = VideoFileClip(videoPath)
        clip.save_frame(to, t=momentSec)
        return to
        pass

    @staticmethod
    def regularchineseABCabc(temp):
        # re.compile(r'[\u4e00-\u9fa5_a-zA-Z0-9]+')
        group = re.search(r'[\u4e00-\u9fa5_a-zA-Z0-9]+', temp)
        return group is not None
        pass

    @staticmethod
    def cutTextSentence(text: str) -> list:
        splitor = [',', '。', '，', '?', '？', '?', '!', '！', ';', '；', ':', '：']
        result = []
        temp = ''
        for i in range(0, len(text)):
            char = text[i]
            temp += char
            if char in splitor:
                if not MovieMakerUtils.regularchineseABCabc(temp):
                    if len(result) > 0:
                        result[-1] = result[-1] + temp
                else:
                    if len(temp) > 400:
                        splited = []
                        for j in range(0, len(temp), 400):
                            if j + 400 > len(temp):
                                splited.append(temp[j:])
                            else:
                                splited.append(temp[j:j+400])
                        for s in splited:
                            result.append(s)
                    else:
                        result.append(temp)
                temp = ''
        if temp != '':
            if not MovieMakerUtils.regularchineseABCabc(temp):
                if len(result) > 0:
                    result[-1] = result[-1] + temp
            else:
                if len(temp) > 400:
                    splited = []
                    for j in range(0, len(temp), 400):
                        if j + 400 > len(temp):
                            splited.append(temp[j:])
                        else:
                            splited.append(temp[j:j+400])
                    for s in splited:
                        result.append(s)
                else:
                    result.append(temp)
        return result
        pass

    @staticmethod
    def splitText(text: str):
        cutted = MovieMakerUtils.cutTextSentence(text)
        maxpiecelength = 10
        minpiecelength = 40

        stopflag = ['。', '?', '？', '!', '！']

        resultparagraph = []

        temp = ''
        for i in range(0, len(cutted)):
            piece = cutted[i]
            temp += piece
            if len(temp) > maxpiecelength:
                resultparagraph.append(temp)
                temp = ''
            elif len(temp) < minpiecelength:
                continue
            else:
                lastChar = temp[-1]
                if lastChar in stopflag:
                    resultparagraph.append(temp)
                    temp = ''
        if len(temp) > 0:
            resultparagraph.append(temp)
        return resultparagraph
        pass

    @staticmethod
    def captionTextToVideoClip(clip:VideoClip, text, offsetSec=0, durationSec=None):
        if durationSec is None:
            durationSec = clip.duration

        # remove breath and laughter
        text = text.replace('[breath]', '$$').replace('[laughter]', '$$')
        enlarged = clip.resized((720, 1280))
        pieces = MovieMakerUtils.splitText(text)
        offsetduration = offsetSec
        textsubtitlecliplist = []
        for piec in pieces:
            rows = len(piec) / 20
            piece = piec.replace('$', '')
            question = MovieMakerUtils.seperatetextbynewline(piece,1920,80, charcount=8)
            if rows > 4:
                question = MovieMakerUtils.seperatetextbynewline(piece, 1920, 28, charcount=8)
                rows = len(piec) / 28
            duration = durationSec * len(piece) / len(text)
            fontsize = 65
            if rows > 3: # 三行以上,太高了
                fontsize = 48
            print(ImmortalConfig.subtitlefont)
            titleClip: TextClip = TextClip(text=question, font=ImmortalConfig.subtitlefont, horizontal_align='center', color='white', stroke_color='black', stroke_width=2, font_size=fontsize, size=(720 - 60, 480))
            # margin 30
            titleClip = titleClip.with_position((30, 800 - 30))
            # if titleClip.size[0] > 1920 * 0.9:
            #     titleClip = titleClip.resized(1920 * 0.9 / titleClip.size[0]).with_position((96, 54 + 790))
            print(f"with start: {offsetduration}, text: {piece}")
            titleClip = titleClip.with_duration(duration).with_start(offsetduration)

            offsetduration += duration
            textsubtitlecliplist.append(titleClip)
        textsubtitlecliplist.insert(0,enlarged)
        composited = CompositeVideoClip(textsubtitlecliplist).resized(clip.size)
        return composited
        pass

    @staticmethod
    def concateVideoWithEffect(videolist:list, effect:Literal[None,'none','fade','zoom','rotate','slide']='fade', to=None):
        clips = [VideoFileClip(v) for v in videolist]
        concated = MovieEffect.concateClipList(clips, effect=effect)
        if to is None:
            id, path = Utils.generatePathId(namespace='temp', exten='mp4')
            Utils.mkdir(path)
            to = path
        concated.write_videofile(to)
        return to

    @staticmethod
    def captionTextlistToVideoClip(clip:VideoClip, subtitlelist: list, to=None, returnclip=False):
        clipoutput = clip
        for subtitile in subtitlelist:
            clipoutput = MovieMakerUtils.captionTextToVideoClip(clipoutput, subtitile[2], subtitile[0], subtitile[1])
        if returnclip:
            return clipoutput
        else:
            if to is None:
                _, to = Utils.generatePathId(namespace='temp', exten='mp4')
            Utils.mkdir(to)
            clipoutput.write_videofile(to, fps=25)
            return to
    #
    # @staticmethod
    # def imageToVideo(imgPath, duration, to, resize=(920, 1480)):
    #     clip = ImageClip(imgPath, duration=duration)
    #     if resize is not None:
    #         clip = clip.resized(resize)
    #
    #     bg = ColorClip((resize[0] - 200, resize[1]-200), color=(255,255,255))
    #     bg = bg.with_duration(duration)
    #
    #     piecelength = 8
    #     pieces = []
    #     temp = duration
    #     while temp > piecelength:
    #         pieces.append(piecelength)
    #         temp -= piecelength
    #     if temp > 0:
    #         pieces.append(temp)
    #
    #     randPick = MovieMakerUtils.randomPick(2)
    #
    #     if randPick == 0:
    #         clip = clip.with_position((-200, 0))
    #         clip = MovieMakerUtils.animationsTo(clip, [(0, 0)], [resize], [pieces[0]])
    #     if randPick == 1:
    #         enlarged = (resize[0] * 1.2, resize[1] * 1.2)
    #         clip = clip.resized(enlarged).with_position((-100 * 1.2, 0))
    #         clip = MovieMakerUtils.animationsTo(clip, [(-100, 0)], [resize], [pieces[0]])
    #     sequence = [bg, clip]
    #     composited = CompositeVideoClip(sequence)
    #
    #     dir = os.path.dirname(to)
    #     if not os.path.exists(dir):
    #         os.makedirs(dir)
    #     composited.write_videofile(to,fps=24)
    #     return to

    @staticmethod
    def breakcandidateInText(start, length, text):
        breaktext = [',', '。', '!', '?', '！', '？']
        result = []
        idx = 0
        lastduration = 0
        for chr in text:
            if chr in breaktext:
                duration = idx / len(text) * length
                offset = start + duration
                if duration - lastduration > 5:
                    # piece too long, insert another breakpoint
                    extra = (duration + lastduration)/2 + start
                    result.append(extra)
                result.append(offset)
                lastduration = duration
            idx += 1
        return result

    @staticmethod
    def searchNearest(list, val, startfromidx=0):
        for i in range(startfromidx, len(list)):
            currentval = list[i]
            #last
            if i == len(list) - 1:
                return i
            else:
                nextval = list[i + 1]
                if nextval >= val:
                    if currentval <= val:
                        gap1 = val - currentval
                        gap2 = nextval - val
                        if gap1 < gap2:
                            return i
                        else:
                            return i + 1
                    else:
                        return i
        raise 'unexpected list'

    @staticmethod
    def replaceAudio(video, audio):
        id, path = Utils.generatePathId(namespace="replaceaudio", exten='mp4')
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        videoClip = VideoFileClip(video)
        audioClip = AudioFileClip(audio)
        print(f"video clip duration:{videoClip.duration} , audio duration: {audioClip.duration}")
        videoClip = videoClip.with_duration(audioClip.duration)
        print(f"after process: video duration: {videoClip.duration}")
        clip = videoClip.with_audio(audioClip)
        # clip = MovieMakerUtils.setBGM(videoClip, audioClip, 1.0)
        clip.write_videofile(path)
        return id, path
        pass

    @staticmethod
    def imagestextToVideo(imgPathList, TTSText):
        voicePath, subtitlelist = TTSUtils.cosyvoiceTTS_buildin_speaker_with_subtitle(TTSText)
        MovieMakerUtils.resamplewav(voicePath, 22050)
        audioclip = AudioFileClip(voicePath)
        duration = audioclip.duration

        breakpointCandidate = []
        for subtitle in subtitlelist:
            start = subtitle[0]
            end = start + subtitle[1]
            inTextBreakpoint = MovieMakerUtils.breakcandidateInText(start, end - start, subtitle[2])
            totallist = [start] + [end] + inTextBreakpoint
            for l in totallist:
                if not breakpointCandidate.__contains__(l):
                    breakpointCandidate.append(l)
        breakpointCandidate.sort()
        fromstart = 0
        stepindex = duration / len(imgPathList)
        offsetlist = []
        for i in range(1, len(imgPathList)):
            if i == len(imgPathList) - 1:
                break
            if fromstart >= len(breakpointCandidate):
                break
            currentoffset = i * stepindex
            nearestIndex = MovieMakerUtils.searchNearest(breakpointCandidate, currentoffset, fromstart)
            offsetlist.append(breakpointCandidate[nearestIndex])
            fromstart = nearestIndex + 1

        vid_without_audio = MovieMakerUtils.imagesToVideo(imgPathlist=imgPathList,duration=duration,breakpoints=offsetlist, returnclip=True)
        vid_with_subtitle = MovieMakerUtils.captionTextlistToVideoClip(vid_without_audio, subtitlelist)
        id, topath = MovieMakerUtils.replaceAudio(vid_with_subtitle, voicePath)
        return id, topath
        pass

    @staticmethod
    def imagesToVideo(imgPathlist, duration, to=None, breakpoints=None, resize=(920,1480), returnclip=False):
        if to is None:
            _, path = Utils.generatePathId(namespace='temp', exten='mp4')
            Utils.mkdir(path)
            to = path
        if breakpoints is None:
            breakpoints = []
        breakpoints.sort()
        start = 0
        if len(breakpoints) > 0:
            start = breakpoints[-1]
        if start > duration:
            raise "invalid break points"

        # fill with auto-generated breakpoint
        imglen = len(imgPathlist)
        if imglen > len(breakpoints) + 1:
            imgnotspecified = imglen - len(breakpoints)
            step = (duration - start) / imgnotspecified
            offset = start
            for i in range(0, imgnotspecified - 1):
                offset += step
                breakpoints.append(offset)
        videolist = []
        for i in range(0, len(imgPathlist)):
            img = imgPathlist[i]
            if i == len(breakpoints):
                breakpoint = duration
            else:
                breakpoint = breakpoints[i]
            if i == 0:
                lastbreakpoint = 0
            else:
                lastbreakpoint = breakpoints[i-1]
            pieceduration = breakpoint - lastbreakpoint
            if pieceduration > 0:
                pieceVideo = MovieMakerUtils.imageToVideo(img, pieceduration)
                videolist.append(pieceVideo)
        cliplist = [VideoFileClip(v) for v in videolist]
        if len(cliplist) < 2:
            concated = cliplist[0]
        else:
            concated = MovieEffect.concateClipList(cliplist) # concatenate_videoclips(cliplist)
        for clip in cliplist:
            clip.reader.close()
            # clip.audio.reader.close()
            # clip.audio.reader.close_proc()
        # time.sleep(15)
        if not returnclip:
            concated.write_videofile(to, fps=25)
            concated.close()
            # CompositeVideoClip(videolist)
            return to
        else:
            return concated

    @staticmethod
    def imageToVideo(imgPath, duration, to=None, resize=(920, 1480)):
        if to is None:
            _, path = Utils.generatePathId(namespace='temp', exten='mp4')
            Utils.mkdir(path)
            to = path
        clip = ImageClip(imgPath, duration=duration)
        if resize is not None:
            clip = clip.resized(resize)

        bg = ColorClip((resize[0] - 200, resize[1]-200), color=(255,255,255))
        bg = bg.with_duration(duration)

        piecelength = 8
        pieces = []
        temp = duration
        while temp > piecelength:
            pieces.append(piecelength)
            temp -= piecelength
        if temp > 0:
            pieces.append(temp)
        lastpieceratio = pieces[-1]/piecelength

        randPick = MovieMakerUtils.randomPick(2)

        if randPick == 0:
            initoffset = (-200, 0)

            offsetarray = []
            resizearray = []
            durationarray = []
            for i in range(0,len(pieces)):
                if i % 2 == 0:
                    if i == len(pieces) - 1:
                        ofst = (initoffset[0] - lastpieceratio*initoffset[0], initoffset[1] - lastpieceratio*initoffset[1])
                    else:
                        ofst = (0,0)
                    offsetarray.append(ofst)
                else:
                    if i == len(pieces) - 1:
                        ofst = (lastpieceratio*initoffset[0], lastpieceratio*initoffset[1])
                    else:
                        ofst = initoffset
                    offsetarray.append(ofst)
                resizearray.append(resize)
                durationarray.append(pieces[i])
            clip = clip.with_position(initoffset)
            clip = MovieMakerUtils.animationsTo(clip, offsetarray, resizearray, durationarray)
        if randPick == 1:
            enlarged = (resize[0] * 1.2, resize[1] * 1.2)
            initoffset = (-100 * 1.2, 0)
            tooffset = (-100,0)

            offsetarray = []
            resizearray = []
            durationarray = []
            for i in range(0,len(pieces)):
                if i % 2 == 0:
                    sfst = tooffset
                    rsz = resize
                    if i == len(pieces) - 1:
                        sfst = (lastpieceratio * tooffset[0] + (1-lastpieceratio) * initoffset[0], lastpieceratio * tooffset[1] + (1-lastpieceratio) * initoffset[1])
                        rsz = (lastpieceratio * resize[0] + (1-lastpieceratio) * enlarged[0], lastpieceratio * resize[1] + (1-lastpieceratio) * enlarged[1])
                    offsetarray.append(sfst)
                    resizearray.append(rsz)
                else:
                    sfst = initoffset
                    rsz = enlarged
                    if i == len(pieces) - 1:
                        sfst = (lastpieceratio * initoffset[0] + (1-lastpieceratio) * tooffset[0], lastpieceratio * initoffset[1] + (1-lastpieceratio) * tooffset[1])
                        rsz = (lastpieceratio * enlarged[0] + (1-lastpieceratio) * resize[0], lastpieceratio * enlarged[1] + (1-lastpieceratio) * resize[1])
                    offsetarray.append(sfst)
                    resizearray.append(rsz)
                durationarray.append(pieces[i])

            clip = clip.resized(enlarged).with_position(initoffset)
            clip = MovieMakerUtils.animationsTo(clip, offsetarray, resizearray, durationarray)
        sequence = [bg, clip]
        composited = CompositeVideoClip(sequence)

        dir = os.path.dirname(to)
        if not os.path.exists(dir):
            os.makedirs(dir)
        composited.write_videofile(to,fps=30)
        composited.close()
        return to


    @staticmethod
    def get_wav_duration(file_path):
        with wave.open(file_path, 'r') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration = frames / float(rate)
            return duration

    @staticmethod
    def resamplewav(path, resamplerate=22050):
        temp = path + '.temp.wav'
        MovieMakerUtils.resample4wavs(path, temp, resamplerate)
        os.remove(path)
        shutil.move(temp, path)

    @staticmethod
    def resample4wavs(frompath, topath, resamplerate=22050):
        y, sr = librosa.load(frompath)
        to_y = librosa.resample(y, orig_sr=sr, target_sr=resamplerate)
        # librosa.output.write_wav(tofile, to_y, resamplerate)过时代码, 需要换成下面的代码
        sf.write(topath, to_y, resamplerate)

    @staticmethod
    def randomPick(length):
        rand = random.Random()
        value = rand.random()
        return int(value * length)

    @staticmethod
    def test():
        imgPath = r"D:\ComfyUI_windows_portable_nightly_pytorch\ComfyUI\output\AnimateDiff_00214.png"
        duration = 12
        to = imgPath + ".mp4"
        MovieMakerUtils.imageToVideo(imgPath, duration, to)
        # vpath = 'D:/BaiduNetdiskDownload/clip.mp4'
        # vpath2 = 'D:/BaiduNetdiskDownload/clip2.mp4'
        # toPath = 'D:/BaiduNetdiskDownload/clip3.mp4'
        # video1 = VideoFileClip(vpath).subclipped(0, 13)
        # video2 = VideoFileClip(vpath2).subclipped(0, 10)
        # resized = video2.resized(0.5).with_position((50, 50)).with_start(2)
        # fullscreensize = video1.size
        # animation = MovieMakerUtils.animationsTo(resized, [(100, 50), (400, 100)], [(100, 100), (200, 200)], [1, 2])
        # # enlarged = enlargeFullScreen(resized, fullscreensize, 1)
        # composited = CompositeVideoClip([video1, animation])
        #
        # if Path(toPath).exists():
        #     os.remove(toPath)
        # composited.write_videofile(toPath)
        # print(resized.size)
        pass

if __name__ == '__main__':
    # concatevideo()
    # text = TextClip("克拉戴假发恋爱记", font="C:\\Users\\Administrator\\AppData\\Local\\Microsoft\\Windows\\Fonts\\hanyialitifan.ttf",bg_color='black', color='white', align='center', stroke_color='black', fontsize=80, size=(1920, 1080))
    # text = text.with_fps(5).with_duration(5)
    # text.write_videofile('r:/fonttest.mp4')
    # print(TextClip.list('font'))
    MovieMakerUtils.test()

