#!/bin/env python3
import unittest, os, sys, json, subprocess
from pathlib import Path
directory = os.path.abspath(__file__)
sys.path.append(str(Path(directory).parent.parent))

from createTicket import modify_json

class TestJira(unittest.TestCase):
	def test_input(self):
		ifile = 'envs.json'
		if len(sys.argv)==4: modify_json(ifile)

if __name__ == '__main__':
	unittest.main(argv=['first-arg-is-ignored'], exit=False)


