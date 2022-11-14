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
                        sh 'pylint --reports=y ComunioScore/ || exit 0'
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
                        echo 'Build Distribution Packages'
                        dir('dist_package'){
                            sh './build_package.sh --wheel --debian'
                        }
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

