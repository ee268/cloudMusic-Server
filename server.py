import os
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # 引入 CORS 库

# 启用 CORS 支持

app = Flask(__name__)

CORS(app, resources={r"/upload": {"origins": "http://localhost:5173"}})

app.config['UPLOAD_FOLDER'] = 'uploads'  # 保存目录（相对路径）

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'mp3', 'wma', 'wav', 'ape', 'flac', 'ogg', 'aac'}

def allowed_file(filename):
    # 检查文件扩展名是否在允许的列表中
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        # 确保上传目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # 处理文件名（避免重名和安全问题）
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 构造文件的访问 URL
        file_url = f"http://localhost:5000/files/{filename}"

        # 返回符合要求的 JSON 数据格式
        return jsonify({
            "files": [
                {"name": filename, "url": file_url}
            ]
        }), 200

    return jsonify({'error': 'File type not allowed'}), 400


# 新增路由：列出 uploads 目录下的文件并返回 JSON 格式数据
@app.route('/files', methods=['GET'])
def list_files():
    files = []
    upload_folder = app.config['UPLOAD_FOLDER']

    # 遍历 uploads 目录下的文件
    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        if os.path.isfile(file_path):
            # 构造文件的访问 URL
            file_url = f"http://localhost:5000/files/{filename}"
            files.append({"name": filename, "url": file_url})

    # 修改返回格式以符合需求
    return jsonify({"files": files}), 200


# 新增路由：处理 /files/{filename} 的 GET 请求，返回文件内容
@app.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.isfile(file_path):
        # 启用 CORS 支持，允许来自 http://localhost:5173 的跨域请求
        response = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        return response
    else:
        return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)