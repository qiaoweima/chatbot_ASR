import requests

# 上传 WAV 文件到服务器
response = requests.post('222.201.144.189/upload', files={'file': ('test.wav', open('<WAV文件路径>', 'rb'), 'audio/wav')})

# 输出服务器响应
print(response.text)
