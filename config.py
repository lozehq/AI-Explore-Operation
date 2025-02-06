import os
from dotenv import load_dotenv

load_dotenv()

# API配置
API_CONFIG = {
    "MISTRAL_API_KEY": os.getenv("MISTRAL_API_KEY"),
    "MISTRAL_API_URL": "https://api.mistral.ai/v1/chat/completions",
    "MODEL_VERSION": "mistral-medium"
}

# 数据库配置
DB_CONFIG = {
    "POSTGRES_URL": os.getenv("POSTGRES_URL", "postgresql://user:password@localhost:5432/content_analysis"),
    "REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    "ELASTICSEARCH_URL": os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
}

# Celery配置
CELERY_CONFIG = {
    "BROKER_URL": os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    "RESULT_BACKEND": os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
}

# 分析配置
ANALYSIS_CONFIG = {
    "SUPPORTED_PLATFORMS": [
        "douyin", "kuaishou", "bilibili", 
        "weibo", "xiaohongshu", "zhihu"
    ],
    "MAX_CONTENT_LENGTH": 50000,
    "CACHE_TIMEOUT": 3600,
    "ANALYSIS_TIMEOUT": 300
}

# 报告配置
REPORT_CONFIG = {
    "TEMPLATES_DIR": "templates/reports",
    "OUTPUT_DIR": "output/reports",
    "SUPPORTED_FORMATS": ["pdf", "docx", "pptx", "xlsx"],
    "DEFAULT_TEMPLATE": "standard_report"
}

# 模型配置
MODEL_CONFIG = {
    "SENTIMENT_MODEL": "bert-base-chinese",
    "TOPIC_MODEL": "bert-base-chinese",
    "TREND_MODEL": "bert-base-chinese",
    "BATCH_SIZE": 16,
    "MAX_SEQUENCE_LENGTH": 512,
    "CACHE_DIR": "models",
    "OFFLINE_MODE": False
}

# 缓存配置
CACHE_CONFIG = {
    "ENABLED": True,
    "EXPIRE_TIME": 300,  # 5分钟
    "MAX_SIZE": 1000,
}

# 监控配置
MONITORING_CONFIG = {
    "ENABLE_MONITORING": True,
    "LOG_LEVEL": "INFO",
    "METRICS_PORT": 9090
}

# 协作配置
COLLABORATION_CONFIG = {
    "ENABLE_TEAM_FEATURES": True,
    "MAX_TEAM_SIZE": 10,
    "COMMENT_MAX_LENGTH": 1000
}

# 安全配置
SECURITY_CONFIG = {
    "RATE_LIMIT": {
        "REQUESTS_PER_MINUTE": 60,
        "BURST_SIZE": 100
    },
    "API_KEY_HEADER": "X-API-Key",
    "CORS_ORIGINS": ["*"],
    "CORS_HEADERS": ["*"],
    "CORS_METHODS": ["*"],
}

# B站API配置
BILIBILI_CONFIG = {
    "API_BASE": "https://api.bilibili.com",
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "REFERER": "https://www.bilibili.com",
    "TIMEOUT": 10.0,
    "RETRY_TIMES": 3,
    "RETRY_DELAY": 1.0,
}

# 日志配置
LOG_CONFIG = {
    "LEVEL": "INFO",
    "FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "DATE_FORMAT": "%Y-%m-%d %H:%M:%S",
}