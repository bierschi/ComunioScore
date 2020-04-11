pipeline {
         agent any
         stages {

                 stage('Build Package ComunioScore') {
                     steps {
                         echo 'Build package ComunioScore'
                         sh 'pip3 install -r requirements.txt'
                     }
                 }

                 stage('Static Code Metrics') {

                    steps {
                        echo 'Test Coverage'

                        echo 'Style checks with pylint'
                        sh 'pylint3 --reports=y ComunioScore/ || exit 0'
                    }

                 }

                 stage('Unit Tests') {
                    steps {
                        echo 'Test package ComunioScore'
                        sh 'python3 -m unittest discover ComunioScore/test/ -v'
                    }
                 }

                 stage('Build Distribution Packages') {
                    when {
                         expression {
                             currentBuild.result == null || currentBuild.result == 'SUCCESS'
                         }
                    }
                    steps {
                        echo 'Build Source Distribution'
                        sh 'python3 setup.py sdist'

                        echo 'Build Wheel Distribution'
                        sh 'python3 setup.py bdist_wheel'
                    }
                    post {
                        always {
                              archiveArtifacts (allowEmptyArchive: true,
                              artifacts: 'dist/*whl', fingerprint: true)
                        }
                        success {
                            echo 'Install package ComunioScore'
                            sh 'sudo python3 setup.py install'
                        }
                    }
                 }

                 stage('Deploy') {
                    steps {
                        echo "Deploy ComunioScore to target server"
                        sshPublisher(publishers: [sshPublisherDesc(configName: 'christian@server', transfers: [sshTransfer(cleanRemote: false, excludes: '', execCommand: 'sudo pip3 install projects/ComunioScore/$BUILD_NUMBER/ComunioScore-*.whl', execTimeout: 120000, flatten: false, makeEmptyDirs: false, noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: 'ComunioScore/$BUILD_NUMBER', remoteDirectorySDF: false, removePrefix: 'dist', sourceFiles: 'dist/*.whl')], usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: false)])
                    }
                }

                stage('Deploy to PyPI') {
                    when {
                        expression { "${env.GIT_BRANCH}" =~ "origin/release/" }
                        }
                    steps {
                        echo 'Deploy to PyPI'
                        sh "python3 -m twine upload dist/*"
                    }
                }

         }
}

