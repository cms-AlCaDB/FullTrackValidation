pipeline {
  environment {
    //This variable need be tested as string
    doTest = '0'
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
        sh script: './process_input.py --pat', label: "Processing input template"
        stash includes: '*.json', name: 'json'
        script {
            def dict = readJSON file: 'envs.json'
            dict.each { key, value -> env."${key}"= value }
            buildName "${env.Label}"
            buildDescription "${env.emailSubject} Executed @ ${NODE_NAME}"
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
            sh script: 'python3 tests/jira_tests.py --pat', label: "Unit test rusult"
          }
          post {
            always {
              junit 'results.xml'
            }
          }
        }

        stage('Email Test') {
          agent {
            label "user-alcauser"
          }
          steps {
            checkout scm
            unstash 'json'
            script {
              env.emailBody = String.format("${env.emailBody}", "${env.RUN_ARTIFACTS_DISPLAY_URL}")
              env.COMMITTER_EMAIL = sh(script: 'echo $(git show -s --format="%ae")', returnStdout: true).toString().trim()
            }
            sh script: "mail -s '${emailSubject}' -r 'AlcaDB Team <alcadb.user@cern.ch>' -c '${env.COMMITTER_EMAIL}' physics.pritam@gmail.com <<< '${emailBody}'", label: "Sending test email"
          }
        }
      }
    }

    stage('Local Tests') {
      when {
        expression { doTest == '1' }
      }
      parallel {
        stage('HLT New') {
          when {
            expression { WorkflowsToSubmit.contains('HLT') }
          }
          agent {
            label "user-alcauser"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms', label: "Generate VOMS proxy certificate"
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
          when {
            expression { WorkflowsToSubmit.contains('HLT') }
          }
          agent {
            label "user-alcauser"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_HLT.json --dry --refer', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${TEST_RESULT}/${Label} && cp HLT_refer*.root ${TEST_RESULT}/${Label}/', label: "Moving output files to eos area"
          }
        }

        stage('Express New') {
          when {
            expression { WorkflowsToSubmit.contains('Express') }
          }
          agent {
            label "user-alcauser"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms', label: "Generate VOMS proxy certificate"
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
          when {
            expression { WorkflowsToSubmit.contains('Express') }
          }
          agent {
            label "user-alcauser"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_Express.json --dry --refer', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${TEST_RESULT}/${Label} && cp EXPR_refer*.root ${TEST_RESULT}/${Label}/', label: "Moving output files to eos area"
          }
        }

        stage('Prompt New') {
          when {
            expression { WorkflowsToSubmit.contains('Prompt') }
          }
          agent {
            label "user-alcauser"
          }
          steps {
            cleanWs()
            checkout scm  
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms', label: "Generate VOMS proxy certificate"
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
          when {
            expression { WorkflowsToSubmit.contains('Prompt') }
          }
          agent {
            label "user-alcauser"
          }
          steps {
            cleanWs()
            checkout scm  
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_Prompt.json --dry --refer', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${TEST_RESULT}/${Label} && cp PR_refer*.root ${TEST_RESULT}/${Label}/', label: "Moving output files to eos area"
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
        sh script: './createTicket.py --pat --url "${RUN_ARTIFACTS_DISPLAY_URL}"', label: "Creating a JIRA ticket for validation discussions"
      }
    }
    stage('Email') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        echo "Sending email request to AlCa Hypernews"
        echo "${env.emailSubject}"
        echo "${env.emailBody}"
        sh script: 'mail -s "${emailSubject}" -r "AlcaDB Team <alcadb.user@cern.ch>" -c "alcadb.user@cern.ch" hn-cms-alca@cern.ch <<< "${emailBody}"', label: "Sending announcement email"
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
        sh script: 'voms-proxy-init --rfc --voms cms', label: "Generate VOMS proxy certificate"
        script {
          if (WorkflowsToSubmit.contains('HLT')) {
            sh script: './relval_submit.py -f metadata_HLT.json', label: "HLT Workflow: Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Submit HLT conditions workflow to Request Manager"
          }
          if (WorkflowsToSubmit.contains('Prompt')) {
            sh script: './relval_submit.py -f metadata_Prompt.json', label: "Prompt Workflow: Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Submit Prompt conditions workflow to Request Manager"
          }
          if (WorkflowsToSubmit.contains('Express')) {
            sh script: './relval_submit.py -f metadata_Express.json', label: "Express Workflow: Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Submit Express conditions workflow to Request Manager"
          }
        }
        sh script: 'python3 modules/jira_api.py --comment --pat', label: "Comment status of the submission inside jira ticket"
      }
      post {
        success {
          archiveArtifacts(artifacts: 'workflow_config.json', fingerprint: true)
          sh script: 'mkdir -p ${TEST_RESULT}/${Label} && cp *.json ${TEST_RESULT}/${Label}/', label: "Moving json files to eos area"
          stash includes: 'workflow_config.json', name: 'json'
        }
      }
    }
    stage('Twiki update') {
      when {
        expression { env.Validate == 'No' }
      }
      agent {
        label "cs8-alcauser"
      }
      steps {
        checkout scm
        unstash 'json'
        sh script: 'cp ${TEST_RESULT}/${Label}/workflow_config.json .'
        sh script: 'singularity build -F --sandbox ${TMPDIR}/selenium docker-archive:///eos/home-a/alcauser/selenium-docker.tar', label: "Creating environment for running TWiki script"
        sh script: 'singularity exec --home "/home/jovyan" --writable --cleanenv --bind "${TMPDIR}/selenium/home/jovyan:/home/jovyan" ${TMPDIR}/selenium python3.8 TWikiUpdate.py --headless', label: "Creating validation report on dedicated Twiki"
      }
    }
  }
  post {
    always {
      sh script: "mail -s 'Jenkins Build ${currentBuild.currentResult}: Job ${JOB_NAME}' -r 'AlcaDB Team <alcadb.user@cern.ch>' -c '${env.COMMITTER_EMAIL}' physics.pritam@gmail.com <<< 'More info at: ${env.RUN_DISPLAY_URL}'", label: "Sending post-build email"
    }
  }
}
