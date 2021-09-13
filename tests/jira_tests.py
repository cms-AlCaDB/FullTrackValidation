import unittest, os, sys, json
from pathlib import Path
directory = os.path.abspath(__file__)
sys.path.append(str(Path(directory).parent.parent))

from modules.jira_api import JiraAPI

class TestJira(unittest.TestCase):
    def test_input(self):
        self.assertTrue(os.path.exists('envs.json'))
        ifile = open('envs.json')
        args = json.load(ifile)
        self.assertTrue(type(args)==dict)

    def test_createIssue(self):
        pass

if __name__ == '__main__':
    unittest.main()
