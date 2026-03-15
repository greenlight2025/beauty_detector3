from flask import Flask, render_template, request, jsonify
import base64
import requests
import json
import os  # 新增：读取环境变量

app = Flask(__name__)

# 【可选优化】建议将密钥放到 Render 环境变量，而非硬编码
API_KEY = os.getenv("BAIDU_API_KEY", "PqqR2qsx5s6PaswuE9074BfI")
SECRET_KEY = os.getenv("BAIDU_SECRET_KEY", "falnqvP6X59F3iDhYZXlMPN0LzvFJ9LS")

def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    res = requests.post(url, params=params).json()
    return res.get("access_token")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect():
    file = request.files['file']
    if not file:
        return jsonify({"error_msg": "没有上传文件"})

    img_base64 = base64.b64encode(file.read()).decode('utf-8')
    url = "https://aip.baidubce.com/rest/2.0/face/v3/detect?access_token=" + get_access_token()
    payload = json.dumps({
        "image": img_base64,
        "image_type": "BASE64",
        "face_field": "beauty,age,gender"
    })
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=payload)
    return response.json()

# 关键修改：适配 Render 的端口和生产环境
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv("PORT", 5000)),  # Render 会设置 PORT 环境变量
        debug=False  # 生产环境必须关闭 debug
    )
