pipeline {
         agent any
         stages {
                 stage('Build') {
                     steps {
                         echo 'Build ComunioScore'
                         sh 'pip3 install -r requirements.txt'
                         sh 'python3 setup.py bdist_wheel'
                         sh 'sudo python3 setup.py install'
                     }
                 }
                 stage('Test') {
                    steps {
                        echo 'Test ComunioScore'
                        sh 'python3 -m unittest discover ComunioScore/test/ -v'
                    }
                 }
                 stage('Deploy') {
                    steps {
                        echo "Deploy ComunioScore to target server"
                        sshPublisher(publishers: [sshPublisherDesc(configName: 'christian@server', transfers: [sshTransfer(cleanRemote: false, excludes: '', execCommand: 'sudo pip3 install projects/ComunioScore/$BUILD_NUMBER/ComunioScore-*.whl', execTimeout: 120000, flatten: false, makeEmptyDirs: false, noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: 'ComunioScore/$BUILD_NUMBER', remoteDirectorySDF: false, removePrefix: 'dist', sourceFiles: 'dist/*.whl')], usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: false)])
                    }
                }
    }
}
