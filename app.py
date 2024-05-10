from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, send_file
import os
import cv2
from ultralytics import YOLO

app = Flask(__name__,static_folder='static')
app.secret_key = 'your_secret_key'
# 静态文件夹路径
STATIC_FOLDER = 'static'
# 加载分类模型
classify_model = YOLO('classifyBest.pt')  # 加载你的分类模型
# 加载检测模型
detect_model = YOLO('detectBest.pt')  # 加载你的检测模型

# 用户名和密码
USERNAME = 'lifelogger'
PASSWORD = 'password'


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # 检查是否有上传文件
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        file = request.files['file']
        privacy_preference = request.form['privacy']  # 获取隐私偏好选项的值
        # 如果用户没有选择文件，则返回上传页面
        if file.filename == '':
            return render_template('index.html', error='No selected file')

        # 如果用户上传了文件，保存文件到指定目录
        if file:
            if privacy_preference == "all":
                file_path = os.path.join('./uploads', file.filename)
                file.save(file_path)

                # 读取上传的图片
                source = cv2.imread(file_path)

                # 保存原始图片路径
                original_file_path = os.path.join('static', file.filename)
                cv2.imwrite(original_file_path, source)

                # 进行图片分类
                classify_results = classify_model(source)

                # 遍历分类结果
                for classify_result in classify_results:
                    if classify_result.probs.top1 in [0, 1, 3]:  # 如果分类为 0、1 或 3
                        # 如果是指定的类别，将整张图片变黑
                        source[:] = 0  # 将整张图片变黑
                        break  # 结束循环，不进行目标检测

                # 如果不是指定的类别，则进行目标检测
                else:
                    # 进行目标检测
                    detect_results = detect_model(source)

                    # 遍历目标检测结果，并将检测到的物体区域变黑
                    for detect_result in detect_results:
                        for box in detect_result.boxes.xyxy:
                            x1, y1, x2, y2 = map(int, box)
                            cv2.rectangle(source, (x1, y1), (x2, y2), (0, 0, 0), -1)  # 将检测到的物体区域变黑

                # 保存处理后的图片
                processed_file_path = os.path.join('static', 'processed_' + file.filename)
                cv2.imwrite(processed_file_path, source)

                # 返回处理后的图片路径
                return render_template('index.html', original=original_file_path, processed=processed_file_path)
            else:
                file_path = os.path.join('./uploads', file.filename)
                file.save(file_path)

                # 读取上传的图片
                source = cv2.imread(file_path)

                # 保存原始图片路径
                original_file_path = os.path.join('static', file.filename)
                cv2.imwrite(original_file_path, source)
                # 进行目标检测
                detect_results = detect_model(source)

                # 遍历目标检测结果，并将检测到的物体区域变黑
                for detect_result in detect_results:
                    for box in detect_result.boxes.xyxy:
                        x1, y1, x2, y2 = map(int, box)
                        cv2.rectangle(source, (x1, y1), (x2, y2), (0, 0, 0), -1)  # 将检测到的物体区域变黑

                # 保存处理后的图片
                processed_file_path = os.path.join('static', 'processed_' + file.filename)
                cv2.imwrite(processed_file_path, source)

                # 返回处理后的图片路径
                return render_template('index.html', original=original_file_path, processed=processed_file_path)

    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))
@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        # 获取表单数据
        username = request.form['username']
        email = request.form['email']
        reason = request.form['reason']
        # 在这里处理申请逻辑，比如将申请信息保存到数据库
        # 这里简单起见，直接打印申请信息
        print(f"Username: {username}, Email: {email}, Reason: {reason}")
        return render_template('apply_return.html')
    return render_template('apply.html')
@app.route('/download')
def download_file():
    # 这里的路径是你要提供下载的文件路径
    file_path = 'static/data.zip'
    return send_file(file_path, as_attachment=True)
if __name__ == '__main__':
    app.run(debug=True)
