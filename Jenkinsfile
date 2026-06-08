pipeline {

    agent any

    environment {
        AWS_REGION   = "us-east-1"
        AWS_ACCOUNT  = "066288112657"  // 12-digit account ID
        ECR_REPO     = "${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/python-cicd-app"
        IMAGE_TAG    = "${env.BUILD_NUMBER}"
        EKS_CLUSTER  = "flask-cicd-eks"        // replace with your cluster name
    }

    stages {

        stage("Checkout") {
            steps {
                echo "Checking out source code..."
                checkout scm
            }
        }

        stage("Test") {
            steps {
                echo "Installing dependencies and running tests..."
                sh """
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pytest tests/ -v
                """
            }
        }

        stage("Build Docker Image") {
            steps {
                echo "Building Docker image: ${ECR_REPO}:${IMAGE_TAG}"
                sh "docker build -t ${ECR_REPO}:${IMAGE_TAG} ."
            }
        }

        stage("Trivy Security Scan") {
            steps {
                echo "Scanning image for vulnerabilities..."
                sh """
                    trivy image \
                        --severity HIGH,CRITICAL \
                        --exit-code 1 \
                        --no-progress \
                        ${ECR_REPO}:${IMAGE_TAG}
                """
            }
        }

        stage("Push to ECR") {
            steps {
                echo "Pushing image to AWS ECR..."
                withCredentials([
                    string(credentialsId: "AWS_ACCESS_KEY_ID",     variable: "AWS_ACCESS_KEY_ID"),
                    string(credentialsId: "AWS_SECRET_ACCESS_KEY", variable: "AWS_SECRET_ACCESS_KEY")
                ]) {
                    sh """
                        export AWS_ACCESS_KEY_ID=\$AWS_ACCESS_KEY_ID
                        export AWS_SECRET_ACCESS_KEY=\$AWS_SECRET_ACCESS_KEY

                        aws ecr get-login-password --region ${AWS_REGION} | \
                            docker login --username AWS --password-stdin ${ECR_REPO}

                        docker push ${ECR_REPO}:${IMAGE_TAG}
                    """
                }
            }
        }

        stage("Deploy to Staging") {
            when {
                branch "develop"
            }
            steps {
                echo "Deploying to STAGING namespace..."
                withCredentials([
                    string(credentialsId: "AWS_ACCESS_KEY_ID",     variable: "AWS_ACCESS_KEY_ID"),
                    string(credentialsId: "AWS_SECRET_ACCESS_KEY", variable: "AWS_SECRET_ACCESS_KEY")
                ]) {
                    sh """
                        export AWS_ACCESS_KEY_ID=\$AWS_ACCESS_KEY_ID
                        export AWS_SECRET_ACCESS_KEY=\$AWS_SECRET_ACCESS_KEY

                        aws eks update-kubeconfig --region ${AWS_REGION} --name ${EKS_CLUSTER}

                        sed 's|PLACEHOLDER_IMAGE|${ECR_REPO}:${IMAGE_TAG}|g' k8s/deployment.yaml | \
                            kubectl apply -f - --namespace=staging

                        kubectl apply -f k8s/service.yaml --namespace=staging
                        kubectl apply -f k8s/hpa.yaml     --namespace=staging

                        kubectl rollout status deployment/python-cicd-app \
                            --namespace=staging --timeout=120s
                    """
                }
            }
        }

        stage("Approval Gate") {
            when {
                branch "main"
            }
            steps {
                input message: "Deploy ${ECR_REPO}:${IMAGE_TAG} to production?", ok: "Deploy"
            }
        }

        stage("Deploy to Production") {
            when {
                branch "main"
            }
            steps {
                echo "Deploying to PRODUCTION namespace..."
                withCredentials([
                    string(credentialsId: "AWS_ACCESS_KEY_ID",     variable: "AWS_ACCESS_KEY_ID"),
                    string(credentialsId: "AWS_SECRET_ACCESS_KEY", variable: "AWS_SECRET_ACCESS_KEY")
                ]) {
                    sh """
                        export AWS_ACCESS_KEY_ID=\$AWS_ACCESS_KEY_ID
                        export AWS_SECRET_ACCESS_KEY=\$AWS_SECRET_ACCESS_KEY

                        aws eks update-kubeconfig --region ${AWS_REGION} --name ${EKS_CLUSTER}

                        sed 's|PLACEHOLDER_IMAGE|${ECR_REPO}:${IMAGE_TAG}|g' k8s/deployment.yaml | \
                            kubectl apply -f - --namespace=production

                        kubectl apply -f k8s/service.yaml --namespace=production
                        kubectl apply -f k8s/hpa.yaml     --namespace=production

                        kubectl rollout status deployment/python-cicd-app \
                            --namespace=production --timeout=120s
                    """
                }
            }
        }

    }

    post {
        success {
            echo "Pipeline completed! ${ECR_REPO}:${IMAGE_TAG} is live."
        }
        failure {
            echo "Pipeline failed. Check the logs above."
        }
        always {
            sh "docker rmi ${ECR_REPO}:${IMAGE_TAG} || true"
            cleanWs()
        }
    }

}
