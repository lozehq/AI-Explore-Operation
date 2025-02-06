from setuptools import setup, find_packages

setup(
    name="ai-explore-operation",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.109.2",
        "uvicorn==0.27.1",
        "python-dotenv==1.0.1",
        "httpx==0.26.0",
        "pydantic==2.6.1",
        "python-multipart==0.0.7",
        "jinja2==3.1.3",
        "aiofiles==23.2.1",
        "starlette==0.36.3",
        "typing-extensions==4.9.0",
        "Flask==2.2.5"
    ],
    python_requires=">=3.12",
) 