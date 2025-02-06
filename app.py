from flask import Flask, render_template

app = Flask(__name__, 
           static_folder='static', 
           template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')  # 渲染模板文件

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html'), 500

# Vercel需要明确的application变量
application = app

# 如果使用main.py作为入口，需要保持文件名一致 