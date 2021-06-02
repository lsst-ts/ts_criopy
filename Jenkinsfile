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
            image 'lsstts/develop-env:develop'
            args '--entrypoint ""'
        }
    }

    stages {
        stage("Cloning source") {
            steps {
                checkout scm
            }
        }

        stage("Running tests") {
            steps {
                sh """
                    export HOME=/tmp
                    source \$WORKDIR/loadLSST.bash
                    PYTHONPATH=\$(pwd)/python pytest -p no:cacheprovide --junitxml=/tmp/junit.xml tests || true
                """

                junit '/tmp/junit.xml'
            }
        }
    }
}
