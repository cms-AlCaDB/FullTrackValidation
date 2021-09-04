pipeline {
  environment {
    //This variable need be tested as string
    doTest = '0'
    VOMS_CREDENTIALS = credentials('gridpass')
    JIRA_CREDENTIALS = credentials('jirapass')
    TEST_RESULT = "/eos/user/p/pkalbhor/AlCaValidations"
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
        sh script: './process_input.py ${JIRA_CREDENTIALS_USR} ${JIRA_CREDENTIALS_PSW}', label: "Processing input template"
        stash includes: '*.json', name: 'json'
        script {
            def props = readProperties file: 'envs.properties' 
            env.Validate = props.Validate
            env.Title = props.Title
            env.Week = props.Week
            env.Year = props.Year
            env.Labels = props.Labels
            def dict = readJSON file: 'envs.json'
            env.Hlt_key = dict.Hlt_key
        }
        echo "HLT_Key is $Hlt_key"
      }
    }

    stage('Local Tests') {
      when {
        expression { doTest == '1' }
      }
      parallel {
        stage('HLT New') {
          agent {
            label "lxplus"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'echo ${VOMS_CREDENTIALS_PSW} | voms-proxy-init --rfc --voms cms --pwstdin', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_HLT.json --dry --new', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${TEST_RESULT}/${Labels} && cp HLT_new*.root ${TEST_RESULT}/${Labels}/', label: "Moving output files to eos area"
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

        stage('HLT Reference') {
          agent {
            label "lxplus"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'echo ${VOMS_CREDENTIALS_PSW} | voms-proxy-init --rfc --voms cms --pwstdin', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_HLT.json --dry --refer', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${TEST_RESULT}/${Labels} && cp HLT_refer*.root ${TEST_RESULT}/${Labels}/', label: "Moving output files to eos area"
          }
        }

        stage('Express New') {
          agent {
            label "lxplus"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'echo ${VOMS_CREDENTIALS_PSW} | voms-proxy-init --rfc --voms cms --pwstdin', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_Express.json --dry --new', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${TEST_RESULT}/${Labels} && cp EXPR_new*.root ${TEST_RESULT}/${Labels}/', label: "Moving output files to eos area"
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

        stage('Express Reference') {
          agent {
            label "lxplus"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'echo ${VOMS_CREDENTIALS_PSW} | voms-proxy-init --rfc --voms cms --pwstdin', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_Express.json --dry --refer', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${TEST_RESULT}/${Labels} && cp EXPR_refer*.root ${TEST_RESULT}/${Labels}/', label: "Moving output files to eos area"
          }
        }

        stage('Prompt New') {
          agent {
            label "lxplus"
          }
          steps {
            cleanWs()
            checkout scm  
            unstash 'json'
            sh script: 'echo ${VOMS_CREDENTIALS_PSW} | voms-proxy-init --rfc --voms cms --pwstdin', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_Prompt.json --dry --new', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${TEST_RESULT}/${Labels} && cp PR_new*.root ${TEST_RESULT}/${Labels}/', label: "Moving output files to eos area"
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

        stage('Prompt Reference') {
          agent {
            label "lxplus"
          }
          steps {
            cleanWs()
            checkout scm  
            unstash 'json'
            sh script: 'echo ${VOMS_CREDENTIALS_PSW} | voms-proxy-init --rfc --voms cms --pwstdin', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_Prompt.json --dry --refer', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${TEST_RESULT}/${Labels} && cp PR_refer*.root ${TEST_RESULT}/${Labels}/', label: "Moving output files to eos area"
          }
        }

      }
    }
    stage('Create Jira Ticket') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        sh script: './createTicket.py ${JIRA_CREDENTIALS_USR} ${JIRA_CREDENTIALS_PSW}', label: "Creating a JIRA ticket for validation discussions"
      }
    }
    stage('Email') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        echo "Sending email request to AlCa Hypernews"
        emailext(body: "This is a TEST! Please ignore", subject: "[HLT/EXPRESS/PROMPT] Full track validation of ${env.Title} (${env.Week}, ${env.Year})", to: 'physics.pritam@gmail.com')
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
