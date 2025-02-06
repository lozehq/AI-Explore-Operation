#!/bin/bash

# 检查 Python 版本
echo "Checking Python version..."
python3 --version
python3.12 --version

# 强制使用 Python 3.12
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD=python3.12
    echo "Using Python 3.12"
else
    echo "Python 3.12 not found, attempting to install..."
    # 尝试安装 Python 3.12
    apt-get update && apt-get install -y python3.12 || true
    if command -v python3.12 &> /dev/null; then
        PYTHON_CMD=python3.12
        echo "Successfully installed Python 3.12"
    else
        echo "WARNING: Could not find or install Python 3.12, using system Python"
        PYTHON_CMD=python3
    fi
fi

# 显示实际使用的 Python 版本
$PYTHON_CMD --version

# 设置工作目录
WORK_DIR="$(pwd)"
echo "Working directory: $WORK_DIR"

# 创建必要的目录
echo "Creating directory structure..."
mkdir -p .vercel/output/functions
mkdir -p .vercel/output/static

# 进入函数目录
cd .vercel/output/functions

# 创建应用目录结构
echo "Creating application structure..."
mkdir -p app/routers app/services app/models
touch app/__init__.py
touch app/routers/__init__.py
touch app/services/__init__.py
touch app/models/__init__.py

# 复制核心文件
echo "Copying core files..."
cp "$WORK_DIR/main.py" app/
cp "$WORK_DIR/config.py" app/
cp "$WORK_DIR/requirements.txt" .

# 复制模块文件
echo "Copying module files..."
cp -r "$WORK_DIR/routers/"* app/routers/
cp -r "$WORK_DIR/services/"* app/services/
cp -r "$WORK_DIR/models/"* app/models/

# 复制静态文件和模板
echo "Copying static files and templates..."
cp -r "$WORK_DIR/static" app/
cp -r "$WORK_DIR/templates" app/

# 创建 site-packages 目录
mkdir -p site-packages

# 安装依赖
echo "Installing dependencies..."
$PYTHON_CMD -m pip install --upgrade pip wheel setuptools
$PYTHON_CMD -m pip install -r requirements.txt --target=site-packages --no-cache-dir

# 创建 wsgi.py
echo "Creating WSGI wrapper..."
cat > wsgi.py << EOL
import os
import sys
import logging
from traceback import format_exc

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # 添加应用目录到 Python 路径
    app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
    site_packages = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site-packages')
    
    # 确保目录存在
    logger.info(f"Checking directories...")
    logger.info(f"app_dir exists: {os.path.exists(app_dir)}")
    logger.info(f"site_packages exists: {os.path.exists(site_packages)}")
    
    # 添加到 Python 路径
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    if site_packages not in sys.path:
        sys.path.insert(0, site_packages)
    
    # 记录环境信息
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"App directory contents: {os.listdir(app_dir)}")
    
    # 检查 routers 目录
    routers_dir = os.path.join(app_dir, 'routers')
    if os.path.exists(routers_dir):
        logger.info(f"routers directory exists: {os.listdir(routers_dir)}")
    else:
        logger.error("routers directory not found")
    
    # 修改 main.py 中的导入
    main_file = os.path.join(app_dir, 'main.py')
    if os.path.exists(main_file):
        with open(main_file, 'r') as f:
            content = f.read()
        
        # 更新导入语句
        content = content.replace('from routers', 'from app.routers')
        content = content.replace('from services', 'from app.services')
        content = content.replace('from models', 'from app.models')
        
        with open(main_file, 'w') as f:
            f.write(content)
        logger.info("Updated imports in main.py")
    
    # 导入应用
    logger.info("Importing application...")
    from app.main import app
    logger.info("Application imported successfully")
    
except Exception as e:
    logger.error(f"Error during initialization: {str(e)}\n{format_exc()}")
    raise

# 导出应用
app = app
EOL

# 创建 vercel-python-wsgi 包装器
echo "Creating Vercel Python handler..."
cat > vc__handler__python.py << EOL
import os
import sys

# 添加应用目录到 Python 路径
app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
site_packages = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site-packages')

if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
if site_packages not in sys.path:
    sys.path.insert(0, site_packages)

from wsgi import app

def handler(event, context):
    return app(event, context)
EOL

# 设置权限
chmod -R 755 .

# 显示最终的目录结构
echo "Final directory structure:"
find . -type f -o -type d

# 验证目录结构
echo "Validating directory structure..."
for dir in app app/routers app/services app/models; do
    if [ ! -d "$dir" ]; then
        echo "Creating missing directory: $dir"
        mkdir -p "$dir"
    fi
    touch "$dir/__init__.py"
done

# 验证文件复制
echo "Validating file copying..."
for file in main.py config.py; do
    if [ ! -f "app/$file" ]; then
        echo "Copying $file to app directory"
        cp "$WORK_DIR/$file" "app/$file"
    fi
done

# 验证 routers 目录
if [ -d "$WORK_DIR/routers" ]; then
    echo "Copying routers files..."
    cp -r "$WORK_DIR/routers/"* "app/routers/"
    find "app/routers" -type d -exec touch {}/__init__.py \;
fi

# 验证 Python 路径
echo "Python path validation:"
$PYTHON_CMD -c "
import sys
import os
print('Python path:', sys.path)
print('Current directory:', os.getcwd())
print('Directory structure:')
for root, dirs, files in os.walk('.'):
    level = root.replace('.', '').count(os.sep)
    indent = ' ' * 4 * level
    print(f'{indent}{os.path.basename(root)}/')
    for f in files:
        print(f'{indent}    {f}')
"

# 创建运行时验证文件
echo "Creating runtime verification..."
cat > app/verify.py << EOL
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Python version: {sys.version}")
logger.info(f"Python path: {sys.path}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir('.')}")

try:
    logger.info("Importing app.routers...")
    from app.routers import analysis, bilibili
    logger.info("Routers imported successfully")
except Exception as e:
    logger.error(f"Import error: {str(e)}")
    raise
EOL 