from moviepy.editor import *
import os
import pandas as pd
from gtts import gTTS
from pydub import AudioSegment
from moviepy.video.tools.subtitles import SubtitlesClip


def PrepInstructionAudio(x,y):
    tts = gTTS(y)
    tts.save(x.replace('.png','.mp3'))

def AlterInstructionAudio(x):
    silence_clip0 = AudioSegment.silent(duration=1000)
    silence_clip = AudioSegment.silent(duration=3000)
    
    final = AudioSegment.from_mp3(x)

    final = silence_clip0 + final + silence_clip
    final = final[:int(len(final)/1000)*1000]
    final.export('Vid' + x, format="mp3")

    return int(len(final)/1000)

def ProcessInstructions(df):
    df.apply(lambda x: PrepInstructionAudio(x['Image'],x['Instruction']), axis=1)

def PrepInstructions(df):
    df['mp3s'] = df['Image'].replace('.png','.mp3',regex=True)
    df['time'] = df.apply(lambda x: AlterInstructionAudio(x['mp3s']), axis=1)
    return df

if __name__ == '__main__':

    df = pd.read_excel('AAAA.xlsx')
    print(df.columns)
    # df = df[:6].copy()

    ProcessInstructions(df)

    df = PrepInstructions(df)

    clip_list = []
    for i in range(len(df)):
        dummy = ImageClip(df['Image'][i]).set_duration(df['time'][i])
        audioclip = AudioFileClip('Vid' + df['mp3s'][i])
        dummy = dummy.set_audio(audioclip)
        clip_list.append(dummy)

    video = clip_list[0]

    for z in range(1,len(clip_list)):
        video = concatenate([video, clip_list[z]], method="compose")


    video.write_videofile('test.mp4', fps=1)


    # substitiles
    generator = lambda txt: TextClip(txt, font='Arial', fontsize=60, color='black',bg_color = 'white')
    subtitles = SubtitlesClip("sub.srt", generator)

    video = VideoFileClip("test.mp4")
    result = CompositeVideoClip([video, subtitles.set_pos(('center', 'bottom'))])

    result.write_videofile("file.mp4", fps=video.fps, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264",
                           audio_codec="aac")
