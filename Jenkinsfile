pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS_ID = 'dockerhub-credentials' 
        DOCKERHUB_USERNAME = 'yuvrajdevs' 
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/YuvrajDevs/Chatops.git'
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    docker.image('python:3.11-slim').inside('-u root') {
                        sh 'pip install --no-cache-dir -r requirements.txt'
                        sh 'python3 -m pytest'
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def imageName = "${DOCKERHUB_USERNAME}/chatops-bot:${env.GIT_COMMIT.take(7)}"
                    docker.build(imageName, '.')
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    def imageName = "${DOCKERHUB_USERNAME}/chatops-bot:${env.GIT_COMMIT.take(7)}"
                    docker.withRegistry('https://registry.hub.docker.com', DOCKERHUB_CREDENTIALS_ID) {
                        docker.image(imageName).push()
                    }
                    echo "Successfully pushed ${imageName} to Docker Hub."
                }
            }
        }
    }
}
