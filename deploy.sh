#!/bin/bash

# 设置变量
IMAGE_NAME="explore-operation"
IMAGE_TAG="latest"
NAMESPACE="default"

# 构建 Docker 镜像
echo "Building Docker image..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

# 检查镜像是否构建成功
if [ $? -ne 0 ]; then
    echo "Error: Docker build failed"
    exit 1
fi

# 应用 Kubernetes 配置
echo "Applying Kubernetes configurations..."
kubectl apply -f deployment.yaml -n ${NAMESPACE}

# 等待部署完成
echo "Waiting for deployment to complete..."
kubectl rollout status deployment/explore-operation -n ${NAMESPACE}

# 获取服务信息
echo "Service information:"
kubectl get svc explore-operation-service -n ${NAMESPACE}

# 获取 Ingress 信息
echo "Ingress information:"
kubectl get ingress explore-operation-ingress -n ${NAMESPACE}

echo "Deployment completed successfully!" 