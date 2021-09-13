import unittest, os, sys, json
from pathlib import Path
directory = os.path.abspath(__file__)
sys.path.append(str(Path(directory).parent.parent))

class TestEmails(unittest.TestCase):
    def test_input(self):
        pass
    def test_createIssue(self):
        pass

if __name__ == '__main__':
    unittest.main()
