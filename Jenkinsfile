pipeline {
  environment {
    //This variable need be tested as string
    doError = '0'
    VOMS_CREDENTIALS = credentials('gridpass')
    JIRA_CREDENTIALS = credentials('jirapass')
  }
  agent any
  stages {
    stage('Input Processing') {
      steps{
        sh("echo ${VOMS_CREDENTIALS_USR} ${VOMS_CREDENTIALS_PSW}")
        sh('./process_input.py ${JIRA_CREDENTIALS_USR} ${JIRA_CREDENTIALS_PSW}')
      }
    }

    stage('Test') {
      parallel {
        stage('HLT Test') {
          agent {
            label "lxplus1"
          }
          steps {
            sh 'echo "This is a test. To see if collaborator who pushed changes can also receive an email of a build! 2nd Test!!!!\\n"'
          }
          post {
            always {
              archiveArtifacts(artifacts: 'wmcontrol.py', fingerprint: true)
            }
          }
        }

        stage('Express Test') {
          agent {
            label "lxplus2"
          }
          steps {
            echo 'Testing Express workflow'
          }
          post {
            always {
              archiveArtifacts(artifacts: 'wmcontrol.py', fingerprint: true)
            }
          }
        }

        stage('PR Test') {
          agent {
            label "lxplus3"
          }
          steps {
            echo 'Testing PR workflow'
          }
          post {
            always {
              archiveArtifacts(artifacts: 'wmcontrol.py', fingerprint: true)
            }
          }
        }

      }
    }

  }
  post {
    always {
      emailext(body: "${currentBuild.currentResult}: Job ${env.JOB_NAME} build ${env.BUILD_NUMBER}\n More info at: ${env.BUILD_URL}\n Access cosole output at: ${env.BUILD_URL}console. \n ${env.RUN_DISPLAY_URL}", recipientProviders: [[$class: 'DevelopersRecipientProvider'], [$class: 'RequesterRecipientProvider']], subject: "Jenkins Build ${currentBuild.currentResult}: Job ${env.JOB_NAME}", to: 'physics.pritam@gmail.com', attachLog: true)
    }

  }
}
