#!/bin/bash                                                                             

# eval `scramv1 runtime -sh`
source /cvmfs/cms.cern.ch/crab3/crab.sh
source /afs/cern.ch/cms/PPD/PdmV/tools/wmclient/current/etc/wmclient_testful.sh
export PATH=/afs/cern.ch/cms/PPD/PdmV/tools/wmcontrol:${PATH}
export PYTHONPATH=/afs/cern.ch/cms/PPD/PdmV/tools/wmcontrol:${PYTHONPATH}
export X509_USER_PROXY=` voms-proxy-info -path`
