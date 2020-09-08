#!/usr/bin/env python
# coding: utf-8

# In[1]:


import PySimpleGUI as sg
import time
import datetime
import pyaudio  #録音機能を使うためのライブラリ
import wave     #wavファイルを扱うためのライブラリ
import pydub
import threading
import sys
import os


# In[2]:


def now_unixtime():
    return datetime.datetime.now().timestamp()


# In[3]:


# RECORD_SECONDS = 10 #録音する時間の長さ（秒）
# WAVE_OUTPUT_FILENAME = "sample.wav" #音声を保存するファイル名
# iDeviceIndex = 0 #録音デバイスのインデックス番号
 
#基本情報の設定
# FORMAT = pyaudio.paInt16 #音声のフォーマット
# CHANNELS = 2             #ステレオ
# RATE = 44100             #サンプルレート
# CHUNK = 2**11            #データ点数
 
def wav_maker(RECORD_SECONDS = 10,WAVE_OUTPUT_FILENAME = "sample.wav",
              iDeviceIndex = 0,FORMAT = pyaudio.paInt16,CHANNELS = 2,RATE = 44100,CHUNK = 2**11): 
    audio = pyaudio.PyAudio() #pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
            rate=RATE, input=True,
            input_device_index = iDeviceIndex, #録音デバイスのインデックス番号
            frames_per_buffer=CHUNK)

    #--------------録音開始---------------
    
    print ("recording...")
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    
    print ("finished recording and converting the format")
    
    #--------------録音終了---------------
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    waveFile = wave.open("sample.wav", 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    
    sound_1 = pydub.AudioSegment.from_wav("sample.wav")
    sound_1.export(WAVE_OUTPUT_FILENAME, format=WAVE_OUTPUT_FILENAME.split('.')[-1])
    if WAVE_OUTPUT_FILENAME != "sample.wav":
        os.remove("sample.wav")
        
    print(f'saved as {WAVE_OUTPUT_FILENAME}')


# In[4]:


sg.theme()
layout = [[sg.Text('フォルダー', size=(10, 1)), sg.Input(key='inputFilePath'),sg.FolderBrowse('保存先を選択')],
          [sg.Text('保存ファイル名'),sg.Input(datetime.datetime.now().strftime('%Y%m%d%H%M%S')+'_sample',key='fname'),sg.Combo(('.mp3','.wav'),default_value='.mp3',key='format')],
          [sg.Spin([i for i in range(0,39)],size=(5, 1),key='h'),sg.Text('時間'),sg.Spin([i for i in range(0,60)],size=(5, 1),key='m'),sg.Text('分'),sg.Spin([i for i in range(0,60)],size=(5, 1),key='s'),sg.Text('秒'),sg.Button('録音開始', key='start'),sg.Button('録音中止', key='cancel')],
          [sg.Text('経過秒 / 総録音秒：'),sg.Text('0', key='keika_second',size=(5, 1)),sg.Text('秒 / '),sg.Text('0', key='all_second',size=(5, 1)),sg.Text('秒')],
          [sg.Output(size=(80, 10))]]
window = sg.Window('watch',layout)

count_down = False

while True:
    event,values = window.read(timeout=100,timeout_key='-timeout-')
    # timeoutを指定することで、timeoutイベントが起こります。timeoutの単位はたぶんms
    
    if event in (None,):
        break
        
    elif event in '-timeout-' and count_down:
        nokori = int(end_unix-now_unixtime())
        if nokori < 0:
            count_down = False
        else:
            window['keika_second'].update(nokori)
        
    elif event in 'start' and count_down == False:
        #print(values)
        start_time = now_unixtime()
        h = int(values['h'])
        m = int(values['m'])
        s = int(values['s'])
        all_second = h*60*60+m*60+s
        end_unix = now_unixtime() + all_second
        window['all_second'].update(all_second)
        count_down = True
        
        if values['inputFilePath'] != '':
            fpath = values['inputFilePath']+'/'+values['fname']+values['format']
        else:
            fpath = values['fname']+values['format']
        kw = {'RECORD_SECONDS':all_second,
              'WAVE_OUTPUT_FILENAME':fpath}
        #print(kw)
        t = threading.Thread(target=wav_maker,kwargs=kw)
        t.start()
        
    elif event in 'cancel' and count_down:
        break
        
window.close()

