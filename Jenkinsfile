pipeline {
  agent any
  stages {
    stage('Test') {
      parallel {
        stage('HLT Test') {
          steps {
            sh 'echo "This is a test. To see if collaborator who pushed changes can also receive an email of a build! 2nd Test!!!!\\n"'
          }
        }

        stage('Express Test') {
          steps {
            echo 'Testing Express workflow'
          }
        }

        stage('PR Test') {
          steps {
            echo 'Testing PR workflow'
          }
        }

      }
    }

  }
  post {
    always {
      emailext(body: "${currentBuild.currentResult}: Job ${env.JOB_NAME} build ${env.BUILD_NUMBER}\n More info at: ${env.BUILD_URL}\n Access cosole output at: ${env.BUILD_URL}console. \n ${env.RUN_DISPLAY_URL}", recipientProviders: [[$class: 'DevelopersRecipientProvider'], [$class: 'RequesterRecipientProvider']], subject: "Jenkins Build ${currentBuild.currentResult}: Job ${env.JOB_NAME}", to: 'physics.pritam@gmail.com', attachLog: true)
      archiveArtifacts(artifacts: 'wmcontrol.py', fingerprint: true)
    }

  }
}