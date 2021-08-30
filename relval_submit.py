#!/usr/bin/env python
'''Script that submits relval workflows for AlCa@HLT,Prompt condition validation
'''
from __future__ import print_function

__author__ = 'Javier Duarte'
__copyright__ = 'Copyright 2012, CERN CMS'
__credits__ = ['Giacomo Govi', 'Salvatore Di Guida', 'Miguel Ojeda', 'Andreas Pfeiffer']
__license__ = 'Unknown'
__maintainer__ = 'Javier Duarte'
__email__ = 'jduarte@caltech.edu'
__version__ = 1


import os
import sys
import logging
import argparse
import json
import errno
import ast
from modules import wma

def execme(command, dryrun=False):
    '''Wrapper for executing commands.
    '''
    if dryrun:
        print(command)
    else:
        print(" * Executing: %s..." % (command))
        os.system(command)
        print(" * Executed!")

def getInput(default, prompt=''):
    '''Like raw_input() but with a default and automatic strip().
    '''
    try:
        input = raw_input
    except NameError:
        pass

    answer = input(prompt)
    if answer:
        return answer.strip()

    return default.strip()

def getInputChoose(optionsList, default, prompt=''):
    '''Makes the user choose from a list of options.
    '''

    while True:
        index = getInput(default, prompt)

        try:
            return optionsList[int(index)]
        except ValueError:
            logging.error('Please specify an index of the list (i.e. integer).')
        except IndexError:
            logging.error('The index you provided is not in the given list.')

def getInputRepeat(prompt=''):
    '''Like raw_input() but repeats if nothing is provided and automatic strip().
    '''

    try:
        input = raw_input
    except NameError:
        pass

    while True:
        answer = input(prompt)
        if answer:
            return answer.strip()

        logging.error('You need to provide a value.')

def checkenoughEvents(DataSet, RunNumber, LumiSec):

  if LumiSec == '':
      query=DataSet+'&run_num='+RunNumber
  else:
      query=DataSet+'&run_num='+RunNumber+'&lumi_list='+LumiSec
  testWMA = wma.ConnectionWrapper()
  listFileArray_output = testWMA.api('files', 'dataset', query, True)
  nEventTot=0
  for nFile in listFileArray_output:
      nEvent = nFile['event_count']
      nEventTot += nEvent
  return int(nEventTot)

def checkStat(DataSet, nEvents):
  checkStat_out = ''
  if nEvents < 30000:
      checkStat_out = 'TOO_LOW_STAT'
  elif nEvents < 50000:
      checkStat_out = 'LOW_STAT'
  return checkStat_out

def main():
    '''Entry point.
    '''

    parser = argparse.ArgumentParser(description='Generate list of commands.')
    parser.add_argument("-f", dest="filename", type=str, help="json file name as input")
    parser.add_argument("--dry",
                  action="store_true", dest="dry", default=False,
                  help="Print list of commands for doing dry run")
    arguments = parser.parse_args()

    try:
        if arguments.filename==None: raise TypeError("Please provide input json file using -f option")
        metadataFilename = arguments.filename
        
    except IndexError:
        logging.error('Need to suply a metadata text file name')
        return -3

    ## check that user has properly set up the WMA libraries in PYTHONPATH
    #try:
    #    pypath = os.environ['PYTHONPATH']
    #except:
    #    print "no PYTHONPATH defined in your environment; exiting"
    #    sys.exit()
    #else:
    #    if len ( filter( lambda r : "WMCore" in r, pypath.split(":") ) ) > 0 :
    #        print "hapy"
    #        pass
    #    else :
    #        print "no WMCore present in your PYTHONPATH; exiting"
    #        sys.exit()

    if True:
        try:
            with open(metadataFilename, 'rb') as metadataFile:
                pass
        except IOError as e:
            if e.errno != errno.ENOENT:
                logging.error('Impossible to open file %s (for other reason than not existing)', metadataFilename)
                return -4

            if getInput('y', '\nIt looks like the metadata file %s does not exist. Do you want me to create it and help you fill it?\nAnswer [y]: ' % metadataFilename).lower() != 'y':
                logging.error('Metadata file %s does not exist', metadataFilename)
                return -5
            # Wizard
            while True:
                print("Enter your GRID certificate password before proceeding...")
                execme("source /afs/cern.ch/cms/PPD/PdmV/tools/subSetupAuto.sh") #subSetup_slc6.sh")
                print('''\nWizard for metadata
I will ask you some questions to fill the metadata file. For some of the questions there are defaults between square brackets (i.e. []), leave empty (i.e. hit Enter) to use them.''')

                typeList = ['HLT+RECO', 'EXPR+RECO', 'PR', 'HLT+RECO+ALCA', 'PR+ALCA']

                print('\nTypes of workflow submissions')
                for (index, type) in enumerate(typeList):
                        print('   %s) %s' % (index, type))

                type = getInputChoose(typeList, '0', '\nWhich type of workflow submission\ntype [0]: ')

                if 'HLT+RECO' in type or 'EXPR+RECO' in type:
                    hlt_release = getInput('CMSSW_11_3_2', '\nWhich CMSSW release for HLT?\ne.g. CMSSW_7_4_9_patch1\nhlt_release [CMSSW_11_3_2]: ')

                if 'PR' == type:
                    is_PR_after_HLTRECO = getInput('True','\nHave you already submitted workflows for type : HLT+RECO?\ntype [y/n] : ')

                pr_release = getInput('CMSSW_11_3_2', '\nWhich CMSSW release for Prompt Reco?\ne.g. CMSSW_7_4_11_patch1\npr_release [CMSSW_11_3_2]: ')

                if 'HLT+RECO' in type or 'EXPR+RECO' in type:
                    hlt_menu = getInput('orcoff:/cdaq/cosmic/commissioning2021/CRUZET/Cosmics/V3', '\nWhich HLT menu?\ne.g. orcoff:/cdaq/physics/Run2015/25ns14e33/v3.5/HLT/V7\nhlt_menu [orcoff:/cdaq/cosmic/commissioning2021/CRUZET/Cosmics/V3]: ')

                newgt = getInput('113X_dataRun3_HLT_Candidate_2021_08_02_15_14_25', '\nWhat is the new GT to be validated?\ne.g. 74X_dataRun2_HLTValidation_2015-09-07-08-26-15\nnewgt [113X_dataRun3_HLT_Candidate_2021_08_02_15_14_25]: ')
                jira = getInput('10', '\nWhat is the JIRA ticket number?\ne.g. 10\njira [10]:')

                gt = getInput('113X_dataRun3_HLT_v3', '\nWhat is the reference GT?\ne.g. 74X_dataRun2_HLT_v1\ngt [113X_dataRun3_HLT_v3]: ')

                if 'HLT+RECO' in type or 'EXPR+RECO' in type:
                    basegt = getInput('113X_dataRun3_Prompt_Candidate_2021_08_02_15_14_18', '\nWhat is the common GT for Reco?\ne.g. 74X_dataRun2_Prompt_v1\nbasegt [113X_dataRun3_Prompt_Candidate_2021_08_02_15_14_18]: ')

                ds = getInput('/ExpressCosmics/Commissioning2021-Express-v1/FEVT', '\nWhat is the dataset to be used (comma-separated if more than one)?\ne.g. /HLTPhysics/Run2015C-v1/RAW\nds [/ExpressCosmics/Commissioning2021-Express-v1/FEVT]: ')

                run_err_mess = 'The run value has to be an integer, a dictionary or empty (null).'
                runORrunLs  = getInput('344068', '\nWhich run number or run number+luminosity sections?\ne.g. 254906 or\n     [254906,254905] or\n     {\'256677\': [[1, 291], [293, 390]]}\nrunORrunLs [344068]: ')
                run = ''
                runLs = ''
                Runs_forcheck = ''
                Lumisec_forcheck = ''

                #subSetup_slc6.sh is required for the query
                os.system("export SCRAM_ARCH=slc7_amd64_gcc900") 
                #os.system("scramv1 project {0}".format(hlt_release))
                #os.chdir("{0}/src".format(hlt_release))
                #os.system("eval `scramv1 runtime -sh`")
                os.environ["X509_USER_PROXY"] = os.popen('voms-proxy-info -path').read().strip()
                execme("source /cvmfs/cms.cern.ch/common/crab-setup.sh")
                # do some type recognition and set run or runLs accordingly
                try:
                    if isinstance(runORrunLs, str) and "{" in runORrunLs :
                        runLs = ast.literal_eval(runORrunLs)                  # turn a string into a dict and check it's valid
                        Runs_forcheck    = str(next(iter(runLs)))
                        lumi_tmp = runLs[Runs_forcheck]
                        Lumisec_forcheck = '[['
                        for i_tmp in range(len(lumi_tmp)):
                          for j_tmp in range(len(lumi_tmp[i_tmp])):
                            print(str(lumi_tmp[i_tmp][j_tmp]))
                            if j_tmp < (len(lumi_tmp[i_tmp])-1):
                              Lumisec_forcheck = Lumisec_forcheck + str(lumi_tmp[i_tmp][j_tmp]) + ','
                            elif j_tmp == (len(lumi_tmp[i_tmp])-1) and i_tmp == (len(lumi_tmp)-1):
                              Lumisec_forcheck = Lumisec_forcheck + str(lumi_tmp[i_tmp][j_tmp]) + ']]'
                            elif j_tmp == (len(lumi_tmp[i_tmp])-1):
                              Lumisec_forcheck = Lumisec_forcheck + str(lumi_tmp[i_tmp][j_tmp]) + '],['
                    elif isinstance(runORrunLs, dict):
                        runLs = runORrunLs                                    # keep dict
                        Runs_forcheck    = str(next(iter(runLs)))
                        lumi_tmp = runLs[Runs_forcheck]
                        Lumisec_forcheck = '[['
                        for i_tmp in range(len(lumi_tmp)):
                          for j_tmp in range(len(lumi_tmp[i_tmp])):
                            print(str(lumi_tmp[i_tmp][j_tmp]))
                            if j_tmp < (len(lumi_tmp[i_tmp])-1):
                              Lumisec_forcheck = Lumisec_forcheck + str(lumi_tmp[i_tmp][j_tmp]) + ','
                            elif j_tmp == (len(lumi_tmp[i_tmp])-1) and i_tmp == (len(lumi_tmp)-1):
                              Lumisec_forcheck = Lumisec_forcheck + str(lumi_tmp[i_tmp][j_tmp]) + ']]'
                            elif j_tmp == (len(lumi_tmp[i_tmp])-1):
                              Lumisec_forcheck = Lumisec_forcheck + str(lumi_tmp[i_tmp][j_tmp]) + '],['
                    elif isinstance(runORrunLs, str) and "[" in runORrunLs :
                        run = ast.literal_eval(runORrunLs)                    # turn a string into a list and check it's valid
                        Runs_forcheck = runORrunLs
                    elif isinstance(runORrunLs, str) :
                        run = int(runORrunLs)                                 # turn string into int
                        Runs_forcheck = str(run)
                    elif isinstance(runORrunLs, list):
                        run = runORrunLs                                      # keep list
                        Runs_forcheck = '['
                        for i_tmp in range(len(run)):
                          if i_tmp < len(run):
                            Runs_forcheck = Runs_forcheck + str(run[i_tmp]) + ','
                          else:
                            Runs_forcheck = Runs_forcheck + str(run[i_tmp]) + ']'
                    else:
                        raise ValueError(run_err_mess)
                except ValueError:
                    logging.error(run_err_mess)

                for DataSet in ds.split(","):                                  # check if you have enough events in each dataset
                  print(Runs_forcheck)
                  print(Lumisec_forcheck)
                  nEvents = checkenoughEvents(DataSet, Runs_forcheck, Lumisec_forcheck)
                  checkStat_out = checkStat(DataSet, nEvents)
                  print(DataSet, 'with RUN', Runs_forcheck, Lumisec_forcheck, 'contains:', nEvents, 'events')
                  if checkStat_out == 'TOO_LOW_STAT':
                    print('ERROR! The statistic is too low. I will exit the script.')
                    sys.exit('POOR_STATISTIC')
                  elif checkStat_out == 'LOW_STAT':
                    print('WARNING! The statistic is low. Please check carefully if you do not want to consider a better RUN/lumisection.')
                b0T = getInput('n', '\nIs this for B=0T?\nAnswer [n]: ')
                hion = getInput('n', '\nIs this for Heavy Ions? Note B=0T is not compatible with Heavy Ions at the moment, also pA runs and Heavy Ions runs are mutually exclusive\nAnswer [n]: ')
                pa_run   = getInput('n', '\nIs this for pA run?\nAnswer [n]:')
                cosmics_run   = getInput('n', '\nIs this for cosmics run?\nAnswer [n]:')
                metadata = {
                    'PR_release': pr_release,
                    'options': {
                        'Type': type,
                        'jira': jira,
                        'newgt': newgt,
                        'gt': gt,
                        'ds': ds,
                        'run': run}}

                if 'PR' == type:
                    if(is_PR_after_HLTRECO.lower() == 'n'):
                        metadata['options'].update({'two_WFs': ''})

                if runLs:
                    metadata['options']['runLs'] = runLs
                    metadata['options'].pop('run')


                if b0T.lower() == 'y':
                    metadata['options'].update({'B0T':''})
                if hion.lower() == 'y':
                    metadata['options'].update({'HIon':''})
                if pa_run.lower() == 'y':
                    metadata['options'].update({'pA':''})
                if cosmics_run.lower() == 'y':
                    metadata['options'].update({'cosmics':''})
                if 'HLT+RECO' in type or 'EXPR+RECO' in type:
                    metadata['HLT_release'] = hlt_release
                    metadata['options'].update({
                        'HLT': 'Custom',
                        'HLTCustomMenu': hlt_menu,
                        'basegt': basegt})
                    if metadata['PR_release'] != metadata['HLT_release']:
                        pr_release = metadata['PR_release']
                        metadata['options']['recoCmsswDir'] = '../%s/' % (pr_release)

                metadata = json.dumps(metadata, sort_keys=True, indent=4)
                print('\nThis is the generated metadata:\n%s' % (metadata))

                if getInput('n', '\nIs it fine (i.e. save in %s)?\nAnswer [n]: ' % (metadataFilename)).lower() == 'y':
                    break

            logging.info('Saving generated metadata in %s...', metadataFilename)
            with open(metadataFilename, 'wb') as metadataFile:
                metadataFile.write(metadata)
                logging.info('...%s file created.', metadataFilename)

    with open(metadataFilename, 'rb') as metadataFile:
        metadata = json.loads(metadataFile.read())
        print('\nexecute the following commands:\n')
        commands = []
        try:
            if metadata['HLT_release']:
                #commands.append('eval \'scramv1 project %s\'' % metadata['HLT_release'] )
                commands.append('source bash/wmsetup.sh')
                #commands.append('cd ..')
                #commands.append('cd %s/..' % os.getcwd())
                commands.append('scramv1 project %s' % (metadata['HLT_release']))
                commands.append('cd %s/src' % (metadata['HLT_release']))
                #commands.append('eval \'scramv1 runtime -sh\'')
                commands.append('eval `scramv1 runtime -sh`')
                commands.append('git cms-addpkg HLTrigger/Configuration')
                #commands.append('eval \'scramv1 b\'')
                commands.append('scramv1 b')
                #commands.append('voms-proxy-init --voms cms') # it is already in subSetup_slc6.sh
                commands.append('cd -')
                if metadata['PR_release'] != metadata['HLT_release']:
                    #commands.append('eval \'scramv1 project %s\'' % metadata['PR_release'])
                    commands.append('scramv1 project %s' % (metadata['PR_release']))
        except KeyError:
            #commands.append('eval \'scramv1 project %s\'' % metadata['PR_release'] )
            commands.append('source bash/wmsetup.sh') #subSetupAuto.sh') #subSetup_slc6.sh')
            #commands.append('cd ..')
            commands.append('scramv1 project %s' % (metadata['PR_release']))
            commands.append('cd %s/src' % (metadata['PR_release']))
            #commands.append('eval \'scramv1 runtime -sh\'')
            commands.append('eval `scramv1 runtime -sh`')
            #commands.append('voms-proxy-init --voms cms') # it is already in subSetup_slc6.sh
            commands.append('cd -')

        cond_submit_command = './condDatasetSubmitter.py '
        for key, val in metadata['options'].items():
            # cond_submit_command += '--%s %s ' % ( key, val )
            if isinstance(val, list):
                cond_submit_command += '--%s "' % (key)
                for u in val:
                    cond_submit_command += '%s,' % (u)
                cond_submit_command = cond_submit_command[:-1]
                cond_submit_command += '" '
            elif isinstance(val, dict):
                cond_submit_command += '--%s "%s" ' % (key, val)
            else:
                cond_submit_command += '--%s %s ' % (key, val)
        if arguments.dry: cond_submit_command += '--dry '

        try:
            if metadata['HLT_release']:
                wtype = 'EXPRESS' if metadata['options']['Type']=='EXPR+RECO' else 'HLT'
                cond_submit_command += '|& tee cond_%s.log'%(wtype)
        except KeyError:
            cond_submit_command += '|& tee cond_PR.log'

        #commands.append(' git clone -b master git@github.com:cms-PdmV/wmcontrol.git  master-my-local-name    (**make sure that that PdmV master is the one you want to use**)')
        # commands.append('cd AlCaDB-WMControl')
        commands.append(cond_submit_command)

        # compose string representing runs, Which will be part of the filename
        # if run is int => single label; if run||runLs are list or dict, '_'-separated composite label
        run_label_for_fn = ''

        if 'run' in metadata['options'] and isinstance( metadata['options']['run'], int):
            run_label_for_fn = metadata['options']['run']
        else:
            # handle the list and dictionary case with the same code snippet
            thisRunKey = 'run'
            if 'runLs' in metadata['options']:
                thisRunKey = 'runLs'
            # loop over elements of a list or keys of a dictionary
            for oneRun in metadata['options'][thisRunKey]:
                if run_label_for_fn != '':
                    run_label_for_fn += '_'
                run_label_for_fn += str(oneRun)

        if not arguments.dry:
            try:
                if metadata['HLT_release']:
                    wtype = 'EXPRESS' if metadata['options']['Type']=='EXPR+RECO' else 'HLT'
                    commands.append('./wmcontrol.py --req_file %sConditionValidation_%s_%s_%s.conf |& tee wmc_%s.log' % (
                            wtype, metadata['HLT_release'], metadata['options']['basegt'], run_label_for_fn, wtype))
            except KeyError:
                commands.append('./wmcontrol.py --req_file PRConditionValidation_%s_%s_%s.conf |& tee wmc_PR.log' % (
                            metadata['PR_release'], metadata['options']['newgt'], run_label_for_fn))
            commands.append('rm *.couchID')
        else:
            commands.append('chmod +x cmsDrivers.sh')
            commands.append('./cmsDrivers.sh')
            if metadata['options']['Type']=='EXPR+RECO' or metadata['options']['Type']=='HLT+RECO':
                commands.append('cp cmsDrivers.sh cmsDrivers_{}.sh'.format(metadata['options']['Type'].split('+')[0]))
                commands.append('cmsRun NEWCONDITIONS0.py')
                commands.append('cmsRun recodqm.py')
                commands.append('cmsRun step4_newco_HARVESTING.py')
                commands.append('mv DQM*.root {}_newco_DQMoutput.root'.format(metadata['options']['Type'].split('+')[0]))
                commands.append('rm step*.root')
                commands.append('cmsRun REFERENCE.py')
                commands.append('cmsRun recodqm.py')
                commands.append('cmsRun step4_refer_HARVESTING.py')
                commands.append('mv DQM*.root {}_refer_DQMoutput.root'.format(metadata['options']['Type'].split('+')[0]))
            elif metadata['options']['Type']=='PR':
                commands.append('cp cmsDrivers.sh cmsDrivers_PR.sh')
                commands.append('cmsRun NEWCONDITIONS0.py')
                commands.append('cmsRun step4_newco_HARVESTING.py')
                commands.append('mv DQM*.root PR_newco_DQMoutput.root')
                commands.append('rm step*.root')
                commands.append('cmsRun REFERENCE.py')
                commands.append('cmsRun step4_refer_HARVESTING.py')
                commands.append('mv DQM*.root PR_refer_DQMoutput.root')

        dryrun = True
        # now execute commands
        for command in commands:
            execme(command, dryrun)

        print("\n------: EXECUTE ALL THE ABOVE COMMANDS IN ONE GO :-------\n")
        command_comb = ''
        for command in commands:
            if command!=commands[-1]:
                command_comb += command +" && "
            else:
                command_comb += command
        print(command_comb)
        with open("commands_in_one_go.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write(command_comb)
        os.system("chmod +x commands_in_one_go.sh")

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
            level=logging.INFO)

    sys.exit(main())
