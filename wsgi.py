import os
import sys
import logging
from traceback import format_exc

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # 添加当前目录到 Python 路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(current_dir, 'app')
    site_packages = os.path.join(current_dir, 'site-packages')
    
    # 添加目录到 Python 路径
    for path in [app_dir, site_packages, current_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)
            logger.info(f"Added to Python path: {path}")
    
    # 记录目录内容
    logger.info(f"Current directory contents: {os.listdir(current_dir)}")
    if os.path.exists(app_dir):
        logger.info(f"App directory contents: {os.listdir(app_dir)}")
    
    # 尝试导入
    logger.info("Attempting to import app.routers...")
    from app.routers import analysis, bilibili
    logger.info("Successfully imported routers")
    
    logger.info("Attempting to import main app...")
    from app.main import app
    logger.info("Successfully imported main app")
    
except Exception as e:
    logger.error(f"Error during initialization: {str(e)}\n{format_exc()}")
    raise

# 导出应用
app = app 