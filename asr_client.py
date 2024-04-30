import requests

url = "http://localhost:5000/recognition"
files = {'audio': open('/home/cl/AIproject/PPASR-V0/dataset/test.wav', 'rb')}
print("please enter wav file name:")

response = requests.post(url, files=files)
result = response.text
print(result)

