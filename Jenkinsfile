pipeline {
  agent any
  stages {
    stage('Test') {
      steps {
        sh('echo "This is a test. To see if collaborator who pushed changes can also receive an email of a build! 2nd Test!!!!\\n"')
      }
    }

  }
  post {
      always {
          emailext body: "${currentBuild.currentResult}: Job ${env.JOB_NAME} build ${env.BUILD_NUMBER}\n More info at: ${env.BUILD_URL}\n Access cosole output at: ${env.BUILD_URL}console",
              recipientProviders: [[$class: 'DevelopersRecipientProvider'], [$class: 'RequesterRecipientProvider']],
              subject: "Jenkins Build ${currentBuild.currentResult}: Job ${env.JOB_NAME}",
              to: 'physics.pritam@gmail.com',
              attachLog: true
      }
  }
}
