#!/bin/env python3
import glob, os

files = glob.glob("Validations/*.txt")
files.sort(key=os.path.getmtime)
print(files)
# iFile = open()
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import runregistry
run = runregistry.get_run(run_number=328762)
run['oms_attributes'].keys()