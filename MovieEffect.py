from typing import Literal

from moviepy import VideoFileClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx import *
from moviepy import vfx
from moviepy import *
import numpy as np
import random
from PIL import Image


def concateClipList(cliplist, effect:Literal[None,'none','fade','zoom','rotate','slide']='fade'):
    """
    连接多个视频片段，并可选择转场特效

    参数:
    cliplist: List[VideoFileClip] - 视频片段列表
    effect: str - 转场特效类型，可选值: None(随机), 'fade', 'slide', 'zoom', 'rotate'

    返回:
    VideoClip - 连接后的视频片段
    """
    if not cliplist:
        raise ValueError("视频片段列表不能为空")

    # 如果effect为None，随机选择一种转场效果
    if effect is None:
        effects = ['fade', 'slide', 'zoom', 'rotate']
        effect = random.choice(effects)
        print(f"随机选择了转场效果: {effect}")

    # 无转场效果
    if effect == 'none':
        return concatenate_videoclips(cliplist)

    # 淡入淡出效果
    elif effect == 'fade':
        # 为每个片段添加淡入淡出效果（首尾片段特殊处理）
        clips_with_fx = []
        # offset = 0
        for i, clip in enumerate(cliplist):
            # 第一个片段只添加淡出
            if i == 0:
                if len(cliplist) > 1:
                    clip = clip.with_effects([FadeOut(duration=0.6, final_color=[255,255,255])])
                # offset += clip.duration + 1
            # 最后一个片段只添加淡入
            elif i == len(cliplist) - 1:
                clip = clip.with_effects([FadeIn(duration=0.6,initial_color=[255,255,255])])
            # 中间片段同时添加淡入淡出
            else:
                clip = clip.with_effects([FadeIn(duration=0.6,initial_color=[255,255,255])]).with_effects([FadeOut(duration=0.6,final_color=[255,255,255])])
                # offset += clip.duration + 1
            clips_with_fx.append(clip)

        return concatenate_videoclips(clips_with_fx,padding=0)  # 重叠1秒

    # 左右滑动效果
    elif effect == 'slide':
        final_clips = []
        transition_duration = 1.0

        for i in range(len(cliplist) - 1):
            # 当前片段和下一个片段
            clip1 = cliplist[i]
            clip2 = cliplist[i + 1]

            # 创建滑动转场函数
            def slide_effect(frame, t):
                # 计算进度(0到1之间)
                progress = min(1.0, t / transition_duration)

                if t < transition_duration:
                    # 在转场期间显示两个画面
                    frame1 = clip1.get_frame(clip1.duration - transition_duration + t)
                    frame2 = clip2.get_frame(t)

                    # 计算滑动位置
                    x_offset = int(progress * clip1.w)

                    # 创建新帧，右边是上一个画面，左边是下一个画面
                    new_frame = np.zeros((clip1.h, clip1.w, 3), dtype=np.uint8)
                    new_frame[:, :clip1.w - x_offset] = frame1[:, x_offset:]
                    new_frame[:, clip1.w - x_offset:] = frame2[:, :x_offset]

                    return new_frame
                else:
                    # 转场结束后只显示下一个画面
                    return clip2.get_frame(t - transition_duration)

            # 创建转场片段
            transition = clip2.transform(slide_effect).with_duration(transition_duration)

            # 添加片段到列表
            if i == 0:
                final_clips.append(clip1.subclipped(0, clip1.duration - transition_duration))
            final_clips.append(transition)
            final_clips.append(clip2.subclipped(transition_duration, clip2.duration))

        return concatenate_videoclips(final_clips)

    # 缩放转场效果
    elif effect == 'zoom':
        final_clips = []
        transition_duration = 1.0

        for i, clip in enumerate(cliplist):
            # 第一个片段不需要特殊处理
            if i == 0:
                final_clips.append(clip)
                continue

            # 获取前一个片段和当前片段
            prev_clip = cliplist[i - 1]
            current_clip = clip

            # 创建缩放转场函数
            def zoom_transition(frame, t):
                if t < transition_duration:
                    # 计算缩放比例
                    progress = t / transition_duration
                    zoom_factor = 1.0 + progress * 0.5  # 放大到1.5倍

                    # 获取当前帧
                    frame = current_clip.get_frame(t)

                    # 计算缩放后的尺寸
                    h, w = frame.shape[:2]
                    new_h, new_w = int(h / zoom_factor), int(w / zoom_factor)

                    # 计算裁剪区域
                    y_start = (h - new_h) // 2
                    x_start = (w - new_w) // 2

                    # 缩放并裁剪
                    img = Image.fromarray(frame)
                    img = img.resize((new_w, new_h), Image.LANCZOS)

                    # 创建新图像并居中放置缩放后的图像
                    new_img = Image.new('RGB', (w, h), (0, 0, 0))
                    new_img.paste(img, (x_start, y_start))

                    return np.array(new_img)
                else:
                    return current_clip.get_frame(t - transition_duration)

            # 创建转场片段
            transition = current_clip.transform(zoom_transition).with_duration(transition_duration)

            # 调整前一个片段的结束时间
            final_clips[-1] = final_clips[-1].subclipped(0, final_clips[-1].duration - transition_duration)

            # 添加转场和当前片段
            final_clips.append(transition)
            final_clips.append(current_clip.subclipped(transition_duration, current_clip.duration))

        return concatenate_videoclips(final_clips)

    # 旋转转场效果
    elif effect == 'rotate':
        final_clips = []
        transition_duration = 1.0

        for i, clip in enumerate(cliplist):
            # 第一个片段不需要特殊处理
            if i == 0:
                final_clips.append(clip)
                continue

            # 获取前一个片段和当前片段
            prev_clip = cliplist[i - 1]
            current_clip = clip

            # 创建旋转转场函数
            def rotate_transition(frame, t):
                if t < transition_duration:
                    # 计算旋转角度
                    progress = t / transition_duration
                    angle = progress * 360  # 旋转360度

                    # 获取当前帧
                    frame = current_clip.get_frame(t)

                    # 旋转图像
                    img = Image.fromarray(frame)
                    img = img.rotate(angle, expand=True)

                    # 计算居中位置
                    w, h = img.size
                    orig_w, orig_h = frame.shape[1], frame.shape[0]

                    # 创建新图像并居中放置旋转后的图像
                    new_img = Image.new('RGB', (orig_w, orig_h), (0, 0, 0))
                    x_offset = (orig_w - w) // 2
                    y_offset = (orig_h - h) // 2
                    new_img.paste(img, (x_offset, y_offset))

                    return np.array(new_img)
                else:
                    return current_clip.get_frame(t - transition_duration)

            # 创建转场片段
            transition = current_clip.transform(rotate_transition).with_duration(transition_duration)

            # 调整前一个片段的结束时间
            final_clips[-1] = final_clips[-1].subclipped(0, final_clips[-1].duration - transition_duration)

            # 添加转场和当前片段
            final_clips.append(transition)
            final_clips.append(current_clip.subclipped(transition_duration, current_clip.duration))

        return concatenate_videoclips(final_clips)

    else:
        raise ValueError("不支持的转场效果类型。请选择: None(随机), 'fade', 'slide', 'zoom', 'rotate'")


# 使用示例
if __name__ == "__main__":
    # 加载视频片段
    clip1 = VideoFileClip(r"D:\ComfyUI_windows_portable_nightly_pytorch\ComfyUI\output\video\ComfyUI_00011_.mp4")
    clip2 = VideoFileClip(r"D:\ComfyUI_windows_portable_nightly_pytorch\ComfyUI\output\video\ComfyUI_00012_.mp4")
    clip3 = VideoFileClip(r"D:\ComfyUI_windows_portable_nightly_pytorch\ComfyUI\output\video\ComfyUI_00013_.mp4")

    # 连接片段并使用随机转场效果
    final_clip = concateClipList([clip1, clip2, clip3], effect='fade')

    # 输出结果
    final_clip.write_videofile(r"D:\ComfyUI_windows_portable_nightly_pytorch\ComfyUI\output\video\ComfyUI_00014_.mp4")