pipeline {
  agent any
  stages {
    stage('Test') {
      steps {
        sh 'echo "This is a test\\n"'
      }
    }

  }
  post {
      always {
          echo 'I will always say Hello again!'

          emailext body: "${currentBuild.currentResult}: Job ${env.JOB_NAME} build ${env.BUILD_NUMBER}\n More info at: ${env.BUILD_URL}",
              recipientProviders: [[$class: 'DevelopersRecipientProvider'], [$class: 'RequesterRecipientProvider']],
              subject: "Jenkins Build ${currentBuild.currentResult}: Job ${env.JOB_NAME}"
      }
  }
}
