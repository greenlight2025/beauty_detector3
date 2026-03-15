from flask import Flask, render_template, request, jsonify
import base64
import requests
import json
import os  # 新增：读取 Render 环境变量

app = Flask(__name__)

# 保留你的密钥（也可以后续移到 Render 环境变量）
API_KEY = "PqqR2qsx5s6PaswuE9074BfI"
SECRET_KEY = "falnqvP6X59F3iDhYZXlMPN0LzvFJ9LS"

def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    try:
        res = requests.post(url, params=params, timeout=10).json()
        # 新增：打印 Token 信息，方便 Render 日志排查
        print("Token 获取结果：", res)
        return res.get("access_token")
    except Exception as e:
        print("Token 获取失败：", str(e))
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect():
    # 修复：用 get 避免无文件时 KeyError
    file = request.files.get('file')
    if not file:
        return jsonify({"error_code": -1, "error_msg": "没有上传文件"})

    try:
        # 图片转 Base64
        img_base64 = base64.b64encode(file.read()).decode('utf-8')
    except Exception as e:
        return jsonify({"error_code": -1, "error_msg": f"图片编码失败：{str(e)}"})

    # 获取 Access Token
    access_token = get_access_token()
    if not access_token:
        return jsonify({"error_code": -1, "error_msg": "获取百度 Access Token 失败"})

    # 调用百度人脸检测接口
    url = f"https://aip.baidubce.com/rest/2.0/face/v3/detect?access_token={access_token}"
    payload = json.dumps({
        "image": img_base64,
        "image_type": "BASE64",
        "face_field": "beauty,age,gender"
    })
    headers = {'Content-Type': 'application/json'}

    try:
        # 新增：超时限制 + 异常捕获
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error_code": -1, "error_msg": f"百度 API 调用失败：{str(e)}"})

# 修复：适配 Render 环境（必须！）
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',  # 允许外部访问（Render 必需）
        port=int(os.getenv("PORT", 5000)),  # 读取 Render 分配的端口
        debug=False  # 生产环境关闭 debug（Render 必需）
    )
