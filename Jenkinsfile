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
        script {
            def props = readProperties file: 'envs.properties' 
            env.Validate = props.Validate
        }
        echo "The username  is ${Validate}"
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
            sh('echo ${VOMS_CREDENTIALS_PSW} | voms-proxy-init --rfc --voms cms --pwstdin')
            sh('./relval_submit.py -f metadata_HLT.json --dry')
            sh('./commands_in_one_go.sh')
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
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
            sh('echo ${VOMS_CREDENTIALS_PSW} | voms-proxy-init --rfc --voms cms --pwstdin')
            sh('./relval_submit.py -f metadata_Express.json --dry')
            sh('./commands_in_one_go.sh')
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
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
            sh('echo ${VOMS_CREDENTIALS_PSW} | voms-proxy-init --rfc --voms cms --pwstdin')
            sh('./relval_submit.py -f metadata_Prompt.json --dry')
            sh('./commands_in_one_go.sh')
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

      }
    }
    stage('Create Jira Ticket') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        echo "Creating a Jira ticket for further discussion"
      }
    }
    stage('Email') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        echo "Sending email request to AlCa Hypernews"
      }
    }
    stage('Submission') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        echo "Submitting request to Request Manager/WMAgent production tool."
      }
    }
    stage('Twiki update') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        echo "Creating validation report on dedicated Twiki"
      }
    }
  }
  post {
    always {
      emailext(body: "${currentBuild.currentResult}: Job ${env.JOB_NAME} build ${env.BUILD_NUMBER}\n More info at: ${env.BUILD_URL}\n Access cosole output at: ${env.BUILD_URL}console. \n ${env.RUN_DISPLAY_URL}", recipientProviders: [[$class: 'DevelopersRecipientProvider'], [$class: 'RequesterRecipientProvider']], subject: "Jenkins Build ${currentBuild.currentResult}: Job ${env.JOB_NAME}", to: 'physics.pritam@gmail.com', attachLog: true)
    }

  }
}
