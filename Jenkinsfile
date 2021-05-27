#!/usr/bin/env groovy

properties(
    [
    buildDiscarder
        (logRotator (
            artifactDaysToKeepStr: '',
            artifactNumToKeepStr: '',
            daysToKeepStr: '14',
            numToKeepStr: ''
        ) ),
    disableConcurrentBuilds()
    ]
)

pipeline {
    agent {
        docker { 
            image 'centos/python-38-centos7'
            args '-u root'
        }
    }

    stages {
        stage("Cloning source") {
            steps {
                checkout scm
            }
        }

        stage("Installing modules") {
            steps {
                sh """
                    pip install pytest-flake8 numpy astropy
                """
            }
        }


        stage("Running tests") {
            steps {
                sh """
                    PYTHONPATH=\$(pwd)/python pytest --junitxml=tests/.tests/junit.xml tests || true
                """

                junit 'tests/.tests/junit.xml'
            }
        }
    }
}
