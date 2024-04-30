import pyaudio
import requests
import wave
from pyaudio import PyAudio, paInt16
import numpy as np
import webrtcvad
import time
import audioop

# asr服务端
url = "http://localhost:5000/recognition"
# 录音文件本地存放地址
AudioPath = 'E:\SCUT_Local\日常事\\recognition\\audio.wav'#前面的路径根据录音文件存放地址来修改
WAVE_OUTPUT_FILENAME = 'audio.wav'




# 录音参数
CHUNK = 1024  # wav文件是由若干个CHUNK组成的，CHUNK我们就理解成数据包或者数据片段。
FORMAT = pyaudio.paInt16  # 表示我们使用量化位数 16位来进行录音
CHANNELS = 1  # 代表的是声道，1是单声道，2是双声道。
RATE = 44100  # 采样率 一秒内对声音信号的采集次数，常用的有8kHz, 16kHz, 32kHz, 48kHz,
# 11.025kHz, 22.05kHz, 44.1kHz。
MAX_RECORD_SECONDS = 8  #最大录音时长（s）
TIMEOUT_LENGTH = 2  # 音量小于一定时间后停止录音（s）
MIN_VOCIE = 1500  #音量最低阈值  当计算得到的rms小于1500时，则认为没有说话



def save_wave_file(pa, filename, data):
    '''save the date to the wavfile'''
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    # wf.setsampwidth(sampwidth)
    wf.setsampwidth(pa.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(data))
    wf.close()
    print("保存录音文件成功")



def get_audio(filepath):
    RECORD_SECONDS = 2
    isstart = str(input("是否开始录音？ （Y/N）"))  # 输出提示文本，input接收一个值,转为str，赋值给aa
    if isstart == str("Y"):
        pa = PyAudio()
        stream = pa.open(format=FORMAT,
                         channels=CHANNELS,
                         rate=RATE,
                         input=True,
                         frames_per_buffer=CHUNK)
        print("*" * 10, "开始录音：请在3秒内输入语音")
        frames = []  # 定义一个列表
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):  # 循环，采样率 44100 / 1024 * 5
            data = stream.read(CHUNK)  # 读取chunk个字节 保存到data中
            frames.append(data)  # 向列表frames中添加数据data
        # print(frames)
        print("*" * 10, "录音结束\n")

        stream.stop_stream()
        stream.close()  # 关闭
        pa.terminate()  # 终结

        save_wave_file(pa, filepath, frames)
    elif isstart == str("N"):
        exit()
    else:
        print("无效输入，请重新选择")
        get_audio(filepath)


#根据麦克检测到声音的大小来判断是否说话完毕
#------->
#       检测到声音小于某个值后，再停顿一点时间，再次检测，若声音依旧小于某个值，再次检测，
#       若依然小于某个值，则判断为说话结束；如果其中声音再次大于某个值，则重新检测
def record_auto():
    temp = 20
    RECORD_SECONDS = 2


    mindb=2000    #最小声音，大于则开始录音，否则结束
    delayTime=1.3  #小声1.3秒后自动终止
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    #snowboydecoder.play_audio_file()
    print("开始!计时")

    frames = []
    flag = False            # 开始录音节点
    stat = True				#判断是否继续录音
    stat2 = False			#判断声音小了

    tempnum = 0				#tempnum、tempnum2、tempnum3为时间
    tempnum2 = 0

    while stat:
        data = stream.read(CHUNK,exception_on_overflow = False)
        frames.append(data)
        audio_data = np.frombuffer(data, dtype=np.short)
        temp = np.max(audio_data)
        if temp > mindb and flag==False:
            flag =True
            print("开始录音")
            tempnum2=tempnum

        if flag:
            if(temp < mindb and stat2==False):
                stat2 = True
                tempnum2 = tempnum
                print("声音小，且之前是是大的或刚开始，记录当前点")
            if(temp > mindb):
                stat2 =False
                tempnum2 = tempnum
                #刷新

            if(tempnum > tempnum2 + delayTime*15 and stat2==True):
                print("间隔%.2lfs后开始检测是否还是小声"%delayTime)
                if(stat2 and temp < mindb):
                    stat = False
                    #还是小声，则stat=True
                    print("小声！")
                else:
                    stat2 = False
                    print("大声！")


        print(str(temp)  +  "      " +  str(tempnum))
        tempnum = tempnum + 1
        if tempnum > 500:				#超时直接退出
            stat = False
    print("录音结束")

    stream.stop_stream()
    stream.close()
    p.terminate()

    save_wave_file(p,WAVE_OUTPUT_FILENAME,frames)
    # wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    # wf.setnchannels(CHANNELS)
    # wf.setsampwidth(p.get_sample_size(FORMAT))
    # wf.setframerate(RATE)
    # wf.writeframes(b''.join(frames))
    # wf.close()


##这里是自己设置的静音阈值，后面如果可以，看看使用webrtcvad的静音检测怎么样，估计效果差不多，关键在与对静音阈值的设置，这个不知道和录音的设备有无关系
#放到开发板上后应该要测试一下，并可能要修改一下静音阈值MIN_VOCIE的值
def rec():
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("开始录音...")

    frames = []

    endTime = time.time() + MAX_RECORD_SECONDS  # 超过此时间自动停止
    lastTime = time.time()

    while True:
        if lastTime < endTime:

            input = stream.read(CHUNK)
            frames.append(input)

            # 声音大小，小于音量后超过多少秒停止 / 超过多长时间停止
            rms_val = audioop.rms(input,2)  # 当前音量
           # print(rms_val)

            if rms_val > MIN_VOCIE:  # 如果说话了（音量大于 1）就更新时间
                lastTime = time.time()
                print("Mic_Status========> Speaking")
            else:
                print("Mic_Status========> Silence")

            if time.time() - lastTime > TIMEOUT_LENGTH:     # 超过一定时间不说话，停止录音
                break

        else:   # 超时停止
            break

    print("录音结束")

    stream.stop_stream()
    stream.close()
    p.terminate()

    save_wave_file(p,WAVE_OUTPUT_FILENAME,frames)
    # wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    # wf.setnchannels(CHANNELS)
    # wf.setsampwidth(p.get_sample_size(FORMAT))
    # wf.setframerate(RATE)
    # wf.writeframes(b''.join(frames))
    # wf.close()



def wav2str():
    rec()
    #record_auto()
    files = {'audio': open(AudioPath, 'rb')}
    response = requests.post(url, files=files)
    result = response.text
    return result




if __name__ == "__main__":
    # if args.real_time_demo:
    #     real_time_predict_demo()
    # else:
    #     if args.is_long_audio:
    #         predict_long_audio()
    #     else:
    #         predict_audio()get
    # while(True):
    #     predict_audio()
    #     args.wav_path=input("请输入预测音频地址：")

    # result = wav2str('audio.wav')
    # print(result)

    #record_audio()
    # record_auto()
    # files = {'audio': open(AudioPath, 'rb')}
    # response = requests.post(url,files=files)
    # result = response.text
    # print(result)

    #print("asd")
     result = wav2str()
     print(result)
    # while(True):
    #     filepath = 'audio.wav'
    #     #args.wav_path = filepath
    #     get_audio(filepath)
    #     files = {'audio': open('E:\SCUT_Local\日常事\\recognition\\audio.wav', 'rb')}
    #     #play()
    #     #start = time.time()
    #     response = requests.post(url, files=files)
    #     result = response.text
    #
    #    # use_time = int(round((time.time() - start) * 1000))
    #     #time = int(round((time.time() - start) * 1000))
    #    # print(f"消耗时间：{time}")
    #     print(result)
