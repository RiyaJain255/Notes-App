// Jenkins pipeline for Notes App (works on Windows and Linux Jenkins agents)

def run(cmd) {
    if (isUnix()) { sh cmd } else { bat cmd }
}

def py() {
    return isUnix() ? 'venv/bin/python' : 'venv\\Scripts\\python'
}

pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    run(isUnix() ? 'python3 -m venv venv' : 'python -m venv venv')
                    run("${py()} -m pip install -r requirements.txt")
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    run("${py()} -m pytest -v")
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    run("docker build -t notes-app:${env.BUILD_NUMBER} .")
                }
            }
        }
    }

    post {
        success { echo 'Pipeline finished successfully.' }
        failure { echo 'Pipeline failed. Check the console output.' }
    }
}
