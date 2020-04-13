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
                        dir('dist_package'){
                            sh 'sudo ./build_package.sh --wheel --debian'
                        }
                    }
                    post {
                        success {
                            echo 'Install package ComunioScore'
                            sh 'sudo python3 setup.py install'
                        }
                    }
                 }

                 stage('Deploy') {
                    steps {
                        echo "Deploy ComunioScore to target server"
                        sshPublisher(publishers: [sshPublisherDesc(configName: 'christian@server', transfers: [sshTransfer(cleanRemote: false, excludes: '', execCommand: 'sudo dpkg -i projects/ComunioScore/$BUILD_NUMBER/ComunioScore_*.deb', execTimeout: 120000, flatten: false, makeEmptyDirs: false, noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: 'ComunioScore/$BUILD_NUMBER', remoteDirectorySDF: false, removePrefix: 'dist_package', sourceFiles: 'dist_package/*.deb')], usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: false)])
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

