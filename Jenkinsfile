pipeline {
    agent any

    environment {
        PROJECT_DIR = "/home/ubuntu/aukey-finance-ocr-identify"
        VENV_DIR = "${PROJECT_DIR}/venv"
        PYTHON = "${VENV_DIR}/bin/python"
        PIP = "${VENV_DIR}/bin/pip"
    }

    stages {
        stage('拉取代码') {
            steps {
                git branch: 'master', url: 'http://gitlab.aukeyit.com/aukey-finance/aukey-finance-ocr-identify.git'
            }
        }
        stage('创建虚拟环境') {
            steps {
                sh 'python3 -m venv venv'
            }
        }
        stage('安装依赖') {
            steps {
                sh './venv/bin/pip install -r requirements.txt'
            }
        }
        // stage('初始化数据库') {
        //     steps {
        //         sh './venv/bin/python init_db.py'
        //     }
        // }
        stage('重启服务') {
            steps {
                // 这里假设用 supervisor 管理服务
                sh 'supervisorctl restart aukey-ocr'
                // 或者用 nohup/pm2/自定义脚本重启
            }
        }
    }
}