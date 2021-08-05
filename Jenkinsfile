pipeline {
  agent any
  stages {
    stage('Test') {
      steps {
        sh 'echo "This is a test\\n"'
      }
    }

    stage('Post Build') {
      steps {
        mail(body: '"${currentBuild.currentResult}: Job ${env.JOB_NAME} build ${env.BUILD_NUMBER}\\n More info at: ${env.BUILD_URL}"', subject: '"Jenkins Build ${currentBuild.currentResult}: Job ${env.JOB_NAME}"')
      }
    }

  }
}