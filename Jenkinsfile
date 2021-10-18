pipeline {
  environment {
    //This variable need be tested as string
    doTest = '1'
    AUTH = "$HOME/private/.auth/.dec"
    TEST_RESULT = "/eos/home-a/alcauser/AlCaValidations"
  }
  agent {
    label "user-alcauser"
  }
  options {
    // This is required if you want to clean before build
    skipDefaultCheckout(true)
  }
  stages {
    stage('Input Processing') {
      steps{
        cleanWs()
        checkout scm
        sh script: 'pip3 install --upgrade --user pip; pip3 install --user -r requirements.txt', label: "Check for dependencies"
        sh script: 'set +x; ${AUTH} | ./process_input.py alcauser `xargs`', label: "Processing input template"
        stash includes: '*.json', name: 'json'
        script {
            def dict = readJSON file: 'envs.json'
            dict.each { key, value -> env."${key}"= value }
        }
      }
    }

    stage('Local Tests') {
      when {
        expression { doTest == '1' }
      }
      parallel {
        stage('HLT New') {
          agent {
            label "user-alcauser"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms --pwstdin', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_HLT.json --dry --new', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${TEST_RESULT}/${Label} && cp HLT_new*.root ${TEST_RESULT}/${Label}/', label: "Moving output files to eos area"
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

        stage('HLT Reference') {
          agent {
            label "user-alcauser"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms --pwstdin', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_HLT.json --dry --refer', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${TEST_RESULT}/${Label} && cp HLT_refer*.root ${TEST_RESULT}/${Label}/', label: "Moving output files to eos area"
          }
        }

        stage('Express New') {
          agent {
            label "user-alcauser"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms --pwstdin', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_Express.json --dry --new', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${TEST_RESULT}/${Label} && cp EXPR_new*.root ${TEST_RESULT}/${Label}/', label: "Moving output files to eos area"
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

        stage('Express Reference') {
          agent {
            label "user-alcauser"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms --pwstdin', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_Express.json --dry --refer', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${TEST_RESULT}/${Label} && cp EXPR_refer*.root ${TEST_RESULT}/${Label}/', label: "Moving output files to eos area"
          }
        }

        stage('Prompt New') {
          agent {
            label "user-alcauser"
          }
          steps {
            cleanWs()
            checkout scm  
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms --pwstdin', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_Prompt.json --dry --new', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${TEST_RESULT}/${Label} && cp PR_new*.root ${TEST_RESULT}/${Label}/', label: "Moving output files to eos area"
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

        stage('Prompt Reference') {
          agent {
            label "user-alcauser"
          }
          steps {
            cleanWs()
            checkout scm  
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms --pwstdin', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_Prompt.json --dry --refer', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${TEST_RESULT}/${Label} && cp PR_refer*.root ${TEST_RESULT}/${Label}/', label: "Moving output files to eos area"
          }
        }

      }
    }

    stage('Unit Tests') {
      parallel {
        stage('JIRA Test') {
          agent {
            label "user-alcauser"
          }
          steps {
            cleanWs()
            checkout scm  
            unstash 'json'
          }
        }

        stage('Email Test') {
          agent {
            label "user-alcauser"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
          }
        }
      }
    }

    stage('Create Jira Ticket') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        unstash 'json'
        sh script: 'set +x; ${AUTH} | ./process_input.py alcauser `xargs`', label: "Creating a JIRA ticket for validation discussions"
      }
    }
    stage('Email') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        echo "Sending email request to AlCa Hypernews"
        echo "${env.emailBody}"
        echo "${env.emailSubject}"
        emailext(body: "${env.emailBody}", subject: "${env.emailSubject}", to: 'hn-cms-alca@cern.ch, physics.pritam@gmail.com')
      }
    }
    stage('Submission') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        cleanWs()
        checkout scm  
        unstash 'json'
        sh script: 'voms-proxy-init --rfc --voms cms --pwstdin', label: "Generate VOMS proxy certificate"
        sh script: './relval_submit.py -f metadata_HLT.json', label: "HLT Workflow: Collect commands to create cmsDriver steps"
        sh script: './commands_in_one_go.sh', label: "Submit HLT conditions workflow to Request Manager"
        sh script: './relval_submit.py -f metadata_Express.json', label: "Express Workflow: Collect commands to create cmsDriver steps"
        sh script: './commands_in_one_go.sh', label: "Submit Express conditions workflow to Request Manager"
        sh script: './relval_submit.py -f metadata_Prompt.json', label: "Prompt Workflow: Collect commands to create cmsDriver steps"
        sh script: './commands_in_one_go.sh', label: "Submit Prompt conditions workflow to Request Manager"
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
