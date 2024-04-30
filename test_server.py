from flask import Flask, request

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    # 获取 WAV 文件
    file = request.files['file']
    # 储存 WAV 文件
    file.save("./dataset/upload")
    # 返回结果给客户端
    return 'Upload Success!'

if __name__ == '__main__':
    app.run(host='222.201.144.189', port=5050)
