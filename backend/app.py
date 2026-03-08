from flask import Flask, request, jsonify
from flask_cors import CORS  # 解决跨域（关键！否则前端调不通）
import json
import os

app = Flask(__name__)
CORS(app)  # 允许所有域名访问（GitHub Pages 调用不会跨域报错）

# 评论数据存储文件（简单起见，用JSON文件存，新手不用学数据库）
COMMENT_FILE = "comments.json"

# 初始化评论文件（如果文件不存在，创建空列表）
def init_comments():
    if not os.path.exists(COMMENT_FILE):
        with open(COMMENT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

# 1. 获取所有评论的接口
@app.route('/api/comments', methods=['GET'])
def get_comments():
    init_comments()
    with open(COMMENT_FILE, "r", encoding="utf-8") as f:
        comments = json.load(f)
    # 按时间倒序返回（最新的评论在最前面）
    comments.sort(key=lambda x: x["time"], reverse=True)
    return jsonify({"status": "success", "comments": comments})

# 2. 提交评论的接口
@app.route('/api/comment', methods=['POST'])
def add_comment():
    init_comments()
    # 获取前端提交的评论数据（用户名、内容）
    data = request.get_json()
    if not data or not data.get("name") or not data.get("content"):
        return jsonify({"status": "error", "message": "用户名和评论内容不能为空"}), 400
    
    # 构造评论数据（加时间戳）
    import time
    new_comment = {
        "id": str(int(time.time())),  # 用时间戳做唯一ID
        "name": data["name"],
        "content": data["content"],
        "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }
    
    # 读取原有评论，添加新评论，再写回文件
    with open(COMMENT_FILE, "r", encoding="utf-8") as f:
        comments = json.load(f)
    comments.append(new_comment)
    with open(COMMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    
    return jsonify({"status": "success", "message": "评论提交成功！", "comment": new_comment})

# 启动服务（适配Render端口）
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
