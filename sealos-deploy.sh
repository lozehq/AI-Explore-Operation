#!/bin/bash

# 设置变量
REGISTRY="cloud.sealos.io"
NAMESPACE="your-namespace"  # 替换为你的 Sealos 命名空间
IMAGE_NAME="explore-operation"
IMAGE_TAG=$(git rev-parse --short HEAD 2>/dev/null || echo "latest")
DOMAIN="your-app.cloud.sealos.io"  # 替换为你的域名

# 检查 sealos 登录状态
echo "Checking Sealos login status..."
if ! sealos login -h >/dev/null 2>&1; then
    echo "Please login to Sealos first using: sealos login cloud.sealos.io"
    exit 1
fi

# 构建 Docker 镜像
echo "Building Docker image..."
docker build -t ${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}:${IMAGE_TAG} .

# 检查镜像是否构建成功
if [ $? -ne 0 ]; then
    echo "Error: Docker build failed"
    exit 1
fi

# 推送镜像到 Sealos 仓库
echo "Pushing image to Sealos registry..."
docker push ${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}:${IMAGE_TAG}

# 替换部署文件中的变量
echo "Preparing deployment files..."
envsubst < deployment.yaml > deployment-sealos.yaml

# 应用 Kubernetes 配置
echo "Applying Kubernetes configurations..."
kubectl apply -f deployment-sealos.yaml

# 等待部署完成
echo "Waiting for deployment to complete..."
kubectl rollout status deployment/explore-operation -n ${NAMESPACE}

# 获取部署信息
echo "Deployment information:"
kubectl get deployment explore-operation -n ${NAMESPACE}

# 获取服务信息
echo "Service information:"
kubectl get svc explore-operation-service -n ${NAMESPACE}

# 获取 Ingress 信息
echo "Ingress information:"
kubectl get ingress explore-operation-ingress -n ${NAMESPACE}

# 清理临时文件
rm deployment-sealos.yaml

echo "Deployment completed successfully!"
echo "Your application should be accessible at: http://${DOMAIN}"

# 检查应用状态
echo "Checking application status..."
kubectl get pods -n ${NAMESPACE} -l app=explore-operation
echo "Use the following command to check logs:"
echo "kubectl logs -n ${NAMESPACE} -l app=explore-operation --tail=100 -f" 