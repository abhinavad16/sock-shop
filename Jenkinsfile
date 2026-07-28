pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = "192.168.189.131:5000"
        GEMINI_API_KEY = credentials("gemini-api-key")
        SLACK_WEBHOOK = credentials("slack-webhook")
        KUBECONFIG = "/var/lib/jenkins/.kube/config"
        SONAR_TOKEN = credentials("sonar-token")
    }

    stage("SonarQube Scan") {
    steps {
        script {

            dir("front-end") {

                def scannerHome = tool 'SonarQube'

                withSonarQubeEnv("SonarQubeServer") {

                    sh """
                    ${scannerHome}/bin/sonar-scanner \
                    -Dsonar.projectKey=sockshop-front-end \
                    -Dsonar.sources=.
                    """

                    sleep 15

                    curl -u ${SONAR_TOKEN}: \
                    "${SONAR_HOST_URL}/api/issues/search?componentKeys=sockshop-front-end&ps=100" \
                    -o ../sonar-report.json
                }
            }
        }
    }
}
        stage("Build & Scan Front-End") {
            steps {
                dir("front-end") {
                    sh """
                    docker build -t ${DOCKER_REGISTRY}/front-end:latest .
                    trivy image --severity CRITICAL ${DOCKER_REGISTRY}/front-end:latest > ../trivy-front-end.txt
                    docker push ${DOCKER_REGISTRY}/front-end:latest
                    """
                }
            }
        }

        stage("Build & Scan Catalogue") {
            steps {
                dir("catalogue") {
                    sh """
                    docker build -t ${DOCKER_REGISTRY}/catalogue:latest -f docker/catalogue/Dockerfile .
                    trivy image --severity CRITICAL ${DOCKER_REGISTRY}/catalogue:latest > ../trivy-catalogue.txt
                    docker push ${DOCKER_REGISTRY}/catalogue:latest
                    """
                }
            }
        }

        stage("Build & Scan User") {
            steps {
                dir("user") {
                    sh """
                    docker build -t ${DOCKER_REGISTRY}/user:latest .
                    trivy image --severity CRITICAL ${DOCKER_REGISTRY}/user:latest > ../trivy-user.txt
                    docker push ${DOCKER_REGISTRY}/user:latest
                    """
                }
            }
        }

        stage("Build & Scan Payment") {
            steps {
                dir("payment") {
                    sh """
                    docker build -t ${DOCKER_REGISTRY}/payment:latest -f docker/payment/Dockerfile .
                    trivy image --severity CRITICAL ${DOCKER_REGISTRY}/payment:latest > ../trivy-payment.txt
                    docker push ${DOCKER_REGISTRY}/payment:latest
                    """
                }
            }
        }

        stage("Kubernetes Connection Test") {
            steps {
                sh """
                kubectl cluster-info
                kubectl get nodes
                """
            }
        }

        stage("Deploy to Kubernetes") {
            steps {
                sh """
                echo "Deleting old deployments..."

                kubectl delete deployment front-end --ignore-not-found=true
                kubectl delete deployment catalogue --ignore-not-found=true
                kubectl delete deployment catalogue-db --ignore-not-found=true
                kubectl delete deployment user --ignore-not-found=true
                kubectl delete deployment user-db --ignore-not-found=true
                kubectl delete deployment payment --ignore-not-found=true

                sleep 10

                echo "Deploying applications..."

                kubectl apply -f front-end-deployment.yaml
                kubectl apply -f catalogue-deployment.yaml
                kubectl apply -f catalogue-db-deployment.yaml
                kubectl apply -f user-deployment.yaml
                kubectl apply -f user-db-deployment.yaml
                kubectl apply -f payment-deployment.yaml

                echo "Waiting for deployments..."

                kubectl rollout status deployment/front-end --timeout=300s
                kubectl rollout status deployment/catalogue --timeout=300s
                kubectl rollout status deployment/catalogue-db --timeout=300s
                kubectl rollout status deployment/user --timeout=300s
                kubectl rollout status deployment/user-db --timeout=300s
                kubectl rollout status deployment/payment --timeout=300s

                echo "Current Pods"
                kubectl get pods -o wide
                """
            }
        }
    }

    post {

        failure {

            script {

                sh """
                cat trivy-front-end.txt > combined-trivy-report.txt 2>/dev/null || echo "No Trivy reports" > combined-trivy-report.txt
                cat trivy-catalogue.txt >> combined-trivy-report.txt 2>/dev/null || true
                cat trivy-user.txt >> combined-trivy-report.txt 2>/dev/null || true
                cat trivy-payment.txt >> combined-trivy-report.txt 2>/dev/null || true

                tail -n 200 combined-trivy-report.txt | python3 ai/analyzer.py || echo "AI analysis skipped"
                """
            }
        }
    }
}
