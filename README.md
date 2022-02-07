
**_Jenkins_**: [Jenkins instance![](https://twiki.cern.ch/twiki/pub/TWiki/TWikiDocGraphics/external-link.gif)](https://cmssdt.cern.ch/cms-jenkins/blue/organizations/jenkins/AlCaDBValidation/activity) **_Tutorial_**: [AlCaDB Presentation![](https://twiki.cern.ch/twiki/pub/TWiki/TWikiDocGraphics/external-link.gif)](https://indico.cern.ch/event/1092525/contributions/4594424/attachments/2341402/3991775/Automated%20Full%20Track%20Validation%20Report.pdf)

## Introduction
The Full Track Validation is performed using an automated [Jenkins instance![](https://twiki.cern.ch/twiki/pub/TWiki/TWikiDocGraphics/external-link.gif)](https://cmssdt.cern.ch/cms-jenkins/blue/organizations/jenkins/AlCaDBValidation/activity) and [GitHub![](https://twiki.cern.ch/twiki/pub/TWiki/TWikiDocGraphics/external-link.gif)](https://github.com/cms-AlCaDB/FullTrackValidation) repository. Github repository contains the configuration for submitting the validation while Jenkins hosts the automated procedure for submitting the relvals. Following are the steps for automated Full track validation:

-   After receiving the validation request from the various groups (Tracker/Pixel/HCAL/ECAL etc ..) according to the details present in the request-email, one needs to edit/create the template inside the folder named `Validations` at AlCaDB GitHub repo and then save the file by committing changes to GitHub repository or using PR. The validation file contains the information of the validation such as the title, labels (should be unique for each validation), target and reference GTs, dataset, run number, and validation status. For every new validation, the lastly edited template will be processed. More details are here [Automated Procedure![](https://twiki.cern.ch/twiki/pub/TWiki/TWikiDocGraphics/external-link.gif)](https://indico.cern.ch/event/1092525/contributions/4594424/attachments/2341402/3991775/Automated%20Full%20Track%20Validation%20Report.pdf)

-   After the successful commit/merged PR, an email will be sent informing build is started, containing a link to Jenkins build and cmsDriver steps, if the build is failed the committer will be notified, after that the validation will be automatically triggered at Jenkins and the pipeline will be created, where at various nodes commands are executed one after the other automatically which are as follow

### Input Process

 ```bash
 ./process_input.py 
 ```

Information from the input template is converted to JSON format and saved to files. The user is required to provide a password used for Jira as we extract the Jira ticket number from the site. To authenticate using PAT use the option `--pat`

### Local Tests/ Central Submission of RelVals

The following set of commands will be executed automatically for performing the local test (option `--dry`) and submitting the workflows for central production (without option `--dry`).
 ```bash
voms-proxy-init --rfc --voms cms
 ```
this will generate VOMS proxy certificate.
 ```bash
./relval_submit.py -f metadata_Express.json --dry --new
 ```
this will collect commands to create cmsDriver steps.
 ```bash
./commands_in_one_go.sh
 ```
this will finally create and run cmsDriver steps and submit (if this is not dry run) the conditions workflow to Request Manager.

### Other Steps

After the successful submission, other steps executed in the pipeline are sending the email to HN, creating the JIRA request, and updating the TWiki for the new validation

#### Create Jira ticket

The command for JIRA ticket creation is
 ```bash
./createTicket.py --pat --url "Provide path where cmsDrivers are published"
 ```
It takes the output of `process_input.py` script as an input, so remember to run that script first.

#### TWiki documentation
For TWiki page modification, run:
 ```bash
python3.8 TWikiUpdate.py --headless
 ```
**_Note_**: This script uses the Firefox browser along with the GeckoDriver client for connecting the Selenium web testing tool with the Firefox. However, these tools are not operable in lxplus at the moment. The workaround for executing the above script is as follows.

For testing this script on lxplus, run the following commands in **lxplus8** machine. Build the Singularity container from the Docker image containing all dependencies:
 ```bash
singularity build -F --sandbox ${TMPDIR}/selenium docker-archive:///eos/home-a/alcauser/selenium-docker.tar
 ```
This `singularity build` command needs to run only once. Run `TWikiUpdate.py` script in this container using:
 ```bash
singularity exec --home /home/jovyan --writable --cleanenv --bind ${TMPDIR}/selenium/home/jovyan:/home/jovyan ${TMPDIR}/selenium python3.8 TWikiUpdate.py --headless
 ```