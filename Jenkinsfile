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
        sh script: 'set +x; ${AUTH} | ./process_input.py alcauser `xargs`', label: "Processing input template"
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
            sh script: 'python3 -m pytest tests/jira_tests.py -s  --junit-xml=results.xml -o junit_family="xunit1"', label: "Unit test rusult"
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
            unstash 'json'
            script {
              env.emailBody = String.format("${env.emailBody}", "${env.RUN_ARTIFACTS_DISPLAY_URL}")
            }
            sh script: 'python3 -c """import json; f = open("envs.json", "r+"); d = json.load(f); mail=d["emailBody"]; d.update({"emailBody": mail%("${env.emailBody}")}); json.dump(d, f, indent=2); f.close()"""' 
            sh script: 'cat envs.json'
            sh script: 'mail -s "${emailSubject}" -r "AlcaDB Team <alcadb.user@cern.ch>" physics.pritam@gmail.com <<< "${emailBody}"', label: "Sending test email"
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

    stage('Create Jira Ticket') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        unstash 'json'
        sh script: 'python3 -c """import json; f = open("envs.json", "r+"); d = json.load(f); mail=d["emailBody"]; d.update({"emailBody": mail%("${env.emailBody}")}); json.dump(d, f, indent=2); f.close()"""'
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
      sh script: "mail -s 'Jenkins Build ${currentBuild.currentResult}: Job ${JOB_NAME}' -r 'AlcaDB Team <alcadb.user@cern.ch>' -c '101pritam@gmail.com' physics.pritam@gmail.com <<< 'More info at: ${env.RUN_DISPLAY_URL}'", label: "Sending post-build email"
    }

  }
}
