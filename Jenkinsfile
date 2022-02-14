pipeline {
  environment {
    //This variable need be tested as string
    doTest = '1'
  }
  agent {
    label "lxplus7 && slc7 && user-alcauser"
  }
  options {
    // This is required if you want to clean before build
    skipDefaultCheckout(true)
    preserveStashes()
  }
  stages {
    stage('Input Processing') {
      steps{
        echo "Stage getting executed @ ${NODE_NAME}. Workspace: ${WORKSPACE}"
        cleanWs()
        checkout scm
        sh script: 'voms-proxy-init --rfc --voms cms', label: "Generate VOMS proxy certificate"
        sh script: './process_input.py --pat', label: "Processing input template"
        stash includes: '*.json', name: 'json'
        script {
            def dict = readJSON file: 'envs.json'
            dict.each { key, value -> env."${key}"= value }
            buildName "${env.Label}"
            buildDescription "${env.emailSubject}"
        }
      }
    }

    stage('Unit Tests') {
      parallel {
        stage('JIRA Test') {
          agent {
            label "lxplus7 && slc7 && user-alcauser"
          }
          steps {
            echo "Stage getting executed @ ${NODE_NAME}. Workspace: ${WORKSPACE}"
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
            label "lxplus7 && slc7 && user-alcauser"
          }
          steps {
            echo "Stage getting executed @ ${NODE_NAME}. Workspace: ${WORKSPACE}"
            cleanWs()
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
            expression { WorkflowsToSubmit.contains('HLT') && (NewOrReference.contains('New') || NewOrReference.contains('Both')) }
          }
          agent {
            label "lxplus7 && slc7 && user-alcauser"
          }
          steps {
            echo "Stage getting executed @ ${NODE_NAME}. Workspace: ${WORKSPACE}"
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_HLT.json --dry --new', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${EOS_PATH}/${Label} && cp HLT_new*.root ${EOS_PATH}/${Label}/', label: "Moving output files to eos area"
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

        stage('HLT Reference') {
          when {
            expression { WorkflowsToSubmit.contains('HLT') && (NewOrReference.contains('Reference') || NewOrReference.contains('Both')) }
          }
          agent {
            label "lxplus7 && slc7 && user-alcauser"
          }
          steps {
            echo "Stage getting executed @ ${NODE_NAME}. Workspace: ${WORKSPACE}"
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_HLT.json --dry --refer', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${EOS_PATH}/${Label} && cp HLT_refer*.root ${EOS_PATH}/${Label}/', label: "Moving output files to eos area"
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

        stage('Express New') {
          when {
            expression { WorkflowsToSubmit.contains('Express') && (NewOrReference.contains('New') || NewOrReference.contains('Both')) }
          }
          agent {
            label "lxplus7 && slc7 && user-alcauser"
          }
          steps {
            echo "Stage getting executed @ ${NODE_NAME}. Workspace: ${WORKSPACE}"
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_Express.json --dry --new', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${EOS_PATH}/${Label} && cp EXPR_new*.root ${EOS_PATH}/${Label}/', label: "Moving output files to eos area"
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

        stage('Express Reference') {
          when {
            expression { WorkflowsToSubmit.contains('Express') && (NewOrReference.contains('Reference') || NewOrReference.contains('Both')) }
          }
          agent {
            label "lxplus7 && slc7 && user-alcauser"
          }
          steps {
            echo "Stage getting executed @ ${NODE_NAME}. Workspace: ${WORKSPACE}"
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_Express.json --dry --refer', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${EOS_PATH}/${Label} && cp EXPR_refer*.root ${EOS_PATH}/${Label}/', label: "Moving output files to eos area"
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

        stage('Prompt New') {
          when {
            expression { WorkflowsToSubmit.contains('Prompt') && (NewOrReference.contains('New') || NewOrReference.contains('Both')) }
          }
          agent {
            label "lxplus7 && slc7 && user-alcauser"
          }
          steps {
            echo "Stage getting executed @ ${NODE_NAME}. Workspace: ${WORKSPACE}"
            cleanWs()
            checkout scm  
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_Prompt.json --dry --new', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${EOS_PATH}/${Label} && cp PR_new*.root ${EOS_PATH}/${Label}/', label: "Moving output files to eos area"
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

        stage('Prompt Reference') {
          when {
            expression { WorkflowsToSubmit.contains('Prompt') && (NewOrReference.contains('Reference') || NewOrReference.contains('Both')) }
          }
          agent {
            label "lxplus7 && slc7 && user-alcauser"
          }
          steps {
            echo "Stage getting executed @ ${NODE_NAME}. Workspace: ${WORKSPACE}"
            cleanWs()
            checkout scm
            unstash 'json'
            sh script: 'voms-proxy-init --rfc --voms cms', label: "Generate VOMS proxy certificate"
            sh script: './relval_submit.py -f metadata_Prompt.json --dry --refer', label: "Collect commands to create cmsDriver steps"
            sh script: './commands_in_one_go.sh', label: "Create and run cmsDriver steps"
            sh script: 'mkdir -p ${EOS_PATH}/${Label} && cp PR_refer*.root ${EOS_PATH}/${Label}/', label: "Moving output files to eos area"
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

      }
    }


    stage('Email') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        echo "Stage getting executed @ ${NODE_NAME}. Workspace: ${WORKSPACE}"
        unstash 'json'
        script {
          env.Ticket_Matched = sh(script: 'echo $(python3 modules/jira_api.py --scan --pat 2>&1 > /dev/null)', returnStdout: true).toString().trim()
          if ( env.Ticket_Matched == '0' ) {
            echo "Sending email request to AlCa Hypernews"
            echo "${env.emailSubject}"
            echo "${env.emailBody}"
            sh script: 'mail -s "${emailSubject}" -r "AlcaDB Team <alcadb.user@cern.ch>" -c "alcadb.user@cern.ch" cmstalk+alca@dovecotmta.cern.ch <<< "${emailBody}"', label: "Sending announcement email"
          } else {
            echo 'Jira ticket exists for given set of labels. So email will not be sent assuming it was sent while creating Jira ticket'
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
    stage('Submission') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        echo "Stage getting executed @ ${NODE_NAME}. Workspace: ${WORKSPACE}"
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
          stash includes: 'workflow_config.json', name: 'WorkflowStash'
          sh script: 'mkdir -p ${EOS_PATH}/${Label} && cp *.json ${EOS_PATH}/${Label}/', label: "Moving json files to eos area"
        }
      }
    }
    stage('Twiki update') {
      when {
        expression { env.Validate == 'Yes' }
      }
      agent {
        label "lxplus7 && slc7 && user-alcauser"
      }
      steps {
        echo "Stage getting executed @ ${NODE_NAME}. Workspace: ${WORKSPACE}"
        cleanWs()
        checkout scm
        unstash 'json'
        sh script: 'cp ${EOS_PATH}/${Label}/workflow_config.json .', label: "Copy json file containing workflow configuration"
        sh script: 'singularity build -F --sandbox ${TMPDIR}/selenium docker-archive:///eos/home-a/alcauser/selenium-docker.tar', label: "Creating environment for running TWiki script"
        sh script: 'singularity exec --home "/home/jovyan"  --no-home --cleanenv --bind "${TMPDIR}/selenium/home/jovyan:/home/jovyan" ${TMPDIR}/selenium python3.8 TWikiUpdate.py --headless', label: "Creating validation report on dedicated Twiki"
      }
    }
  }
  post {
    always {
      sh script: "mail -s 'Jenkins Build ${currentBuild.currentResult}: Job ${JOB_NAME}' -r 'AlcaDB Team <alcadb.user@cern.ch>' -c '${env.COMMITTER_EMAIL}' physics.pritam@gmail.com <<< 'More info at: ${env.RUN_DISPLAY_URL}'", label: "Sending post-build email"
    }
  }
}
