pipeline {
  environment {
    //This variable need be tested as string
    doError = '0'
    VOMS_CREDENTIALS = credentials('gridpass')
    JIRA_CREDENTIALS = credentials('jirapass')
  }
  agent any
  options {
    // This is required if you want to clean before build
    skipDefaultCheckout(true)
  }
  stages {
    stage('Input Processing') {
      steps{
        cleanWs()
        checkout scm
        sh('./process_input.py ${JIRA_CREDENTIALS_USR} ${JIRA_CREDENTIALS_PSW}')
        stash includes: '*.json', name: 'json'
      }
    }

    stage('Test') {
      parallel {
        stage('HLT Test') {
          agent {
            label "lxplus1"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            sh 'echo "This is a test. To see if collaborator who pushed changes can also receive an email of a build! 2nd Test!!!!\\n"'
          }
          post {
            success {
              archiveArtifacts(artifacts: 'wmcontrol.py', fingerprint: true)
            }
          }
        }

        stage('Express Test') {
          agent {
            label "lxplus2"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            echo 'Testing Express workflow'
          }
          post {
            success {
              archiveArtifacts(artifacts: 'wmcontrol.py', fingerprint: true)
            }
          }
        }

        stage('PR Test') {
          agent {
            label "lxplus3"
          }
          steps {
            cleanWs()
            checkout scm  
            unstash 'json'
            echo 'Testing PR workflow'
          }
          post {
            success {
              archiveArtifacts(artifacts: 'wmcontrol.py', fingerprint: true)
            }
          }
        }

      }
    }
    stage('Create Jira Ticket') {
      when {
        expression { doError == '1' }
      }
      steps {
        echo "Creating a Jira ticket for further discussion"
      }
    }
    stage('Email') {
      when {
        expression { doError == '1' }
      }
      steps {
        echo "Sending email request to AlCa Hypernews"
      }
    }
  }
  post {
    always {
      emailext(body: "${currentBuild.currentResult}: Job ${env.JOB_NAME} build ${env.BUILD_NUMBER}\n More info at: ${env.BUILD_URL}\n Access cosole output at: ${env.BUILD_URL}console. \n ${env.RUN_DISPLAY_URL}", recipientProviders: [[$class: 'DevelopersRecipientProvider'], [$class: 'RequesterRecipientProvider']], subject: "Jenkins Build ${currentBuild.currentResult}: Job ${env.JOB_NAME}", to: 'physics.pritam@gmail.com', attachLog: true)
    }

  }
}
