#!/bin/env python3
import unittest, os, sys, json, subprocess
from pathlib import Path
directory = os.path.abspath(__file__)
sys.path.append(str(Path(directory).parent.parent))

import process_input as process_input

class TestJira(unittest.TestCase):
    def test_input(self):
        ifile = open('metadata_HLT.json')
        args = json.load(ifile)
        ifile.close()
        self.assertTrue(type(args)==dict)

    def test_roles(self):
        args = process_input.get_arguments()
        args = process_input.extract_keys(args)
        cred = (subprocess.getoutput("whoami"), subprocess.getoutput("$HOME/private/.auth/.dec"))
        api = process_input.JiraAPI(args, *cred)

if __name__ == '__main__':
#     sysArgs = sys.argv
#     # pytest.main()
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
