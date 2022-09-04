properties([
    buildDiscarder(
        logRotator(
            artifactDaysToKeepStr: '',
            artifactNumToKeepStr: '',
            daysToKeepStr: '14',
            numToKeepStr: '10',
        )
    ),
    // Make new builds terminate existing builds
    disableConcurrentBuilds(
        abortPrevious: true,
    )
])
pipeline {
    agent {
        docker {
            alwaysPull true
            image 'lsstts/develop-env:develop'
            args "-u root --entrypoint ''"
        }
    }
    environment {
        // Python module name.
        MODULE_NAME = "lsst.ts.cRIOpy"
        // Space-separated list of SAL component names for all IDL files required.
        IDL_NAMES = "MTM1M3 MTM1M3TS MTMount MTAirCompressor"
        // Product name for documentation upload; the associated
        // documentation site is `https://{DOC_PRODUCT_NAME}.lsst.io`.
        DOC_PRODUCT_NAME = "ts-cRIOpy"

        WORK_BRANCHES = "${GIT_BRANCH} ${CHANGE_BRANCH} develop"
        LSST_IO_CREDS = credentials('lsst-io')
        XML_REPORT_PATH = 'jenkinsReport/report.xml'
    }


    stages {
        stage("Cloning source") {
            steps {
                checkout scm
            }
        }

        stage("Updating dependencies") {
            steps {
                sh """
                    cd /home/saluser/repos/ts_idl
                    git checkout develop
                """
            }
        }

        stage("Running unit tests") {
            steps {
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    sh """
                        source /home/saluser/.setup_dev.sh || echo "Loading env failed; continuing..."
                        mamba install -y pyside2 asyncqt h5py
                        setup -r .
                        pytest --cov-report html --cov=${env.MODULE_NAME} --junitxml=${env.XML_REPORT_PATH}
                    """
                }
            }
        }
    }
    post {
        always {
            // Change ownership of the workspace to Jenkins for clean up.
            withEnv(["HOME=${env.WORKSPACE}"]) {
                sh 'chown -R 1003:1003 ${HOME}/'
            }

            // The path of xml needed by JUnit is relative to the workspace.
            junit 'jenkinsReport/*.xml'

            // Publish the HTML report.
            publishHTML (
                target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: false,
                    keepAll: true,
                    reportDir: 'jenkinsReport',
                    reportFiles: 'index.html',
                    reportName: "Coverage Report"
                ]
            )
        }
        cleanup {
            // Clean up the workspace.
            deleteDir()
        }
    }
}
