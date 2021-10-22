#!/bin/env python3
import unittest, os, sys, json, subprocess, pytest
from pathlib import Path
directory = os.path.abspath(__file__)
sys.path.append(str(Path(directory).parent.parent))

import process_input as process_input

def test_roles(record_property):
    """Testing JIRA api access"""
    args = process_input.get_arguments()
    args = process_input.extract_keys(args)
    cred = (subprocess.getoutput("whoami"), subprocess.getoutput("$HOME/private/.auth/.dec"))
    api = process_input.JiraAPI(args, *cred)
    record_property('Jira', args['Jira'])

class TestJira(unittest.TestCase):
    def test_input(self):
        input_files = ['metadata_HLT.json', 'metadata_Prompt.json', 'metadata_Express.json']
        for f in input_files:
            self.assertTrue(os.path.exists(f))

        for f in input_files:
            ifile = open(f)
            args = json.load(ifile)
            ifile.close()
            self.assertTrue(type(args) == dict)
            self.assertTrue(len(list(args.keys())) >= 2)

if __name__ == '__main__':
#     sysArgs = sys.argv
#     # pytest.main()
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
