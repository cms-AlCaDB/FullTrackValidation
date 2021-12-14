#!/bin/env python3
import unittest, os, sys, json, subprocess, xmlrunner
from argparse import Namespace
from pathlib import Path
directory = os.path.abspath(__file__)
sys.path.append(str(Path(directory).parent.parent))

from process_input import *

def get_project_permissions():
    """Logs into Jira and returns permissions of the user for CMSALCA project"""
    from modules.jira_api import JiraAPI
    get_user()
    args = json.load(open('envs.json'))
    api = JiraAPI(args, parsedArgs.user, parsedArgs.password)
    ticket = api.check_duplicate()
    jira = api.connection
    mp = jira.my_permissions(projectKey='CMSALCA')['permissions']
    permissions = Namespace(**mp)
    return permissions

class TestJira(unittest.TestCase):
    access = get_project_permissions()
    def test_input(self):
        Dict = json.load(open('envs.json'))
        input_files = ['metadata_%s.json'%wf for wf in Dict['WorkflowsToSubmit'].split('/')]
        for f in input_files:
            self.assertTrue(os.path.exists(f))

        for f in input_files:
            ifile = open(f)
            args = json.load(ifile)
            ifile.close()
            self.assertTrue(type(args) == dict)
            self.assertTrue(len(list(args.keys())) >= 2)

    def test_roles_BROWSE_PROJECTS(self):
        self.assertTrue(self.access.BROWSE_PROJECTS['havePermission'])

    def test_roles_CREATE_ISSUES(self):
        self.assertTrue(self.access.CREATE_ISSUES['havePermission'])

    def test_roles_ASSIGN_ISSUE(self):
        self.assertTrue(self.access.ASSIGN_ISSUE['havePermission'])

    def test_roles_EDIT_ISSUE(self):
        self.assertTrue(self.access.EDIT_ISSUE['havePermission'])

    def test_roles_RESOLVE_ISSUES(self):
        self.assertTrue(self.access.RESOLVE_ISSUES['havePermission'])

    def test_roles_CLOSE_ISSUES(self):
        self.assertTrue(self.access.CLOSE_ISSUES['havePermission'])

if __name__ == '__main__':
    with open('results.xml', 'wb') as output:
        unittest.main(argv=['first-arg-is-ignored'], exit=False,
            testRunner=xmlrunner.XMLTestRunner(output=output),
            failfast=False, buffer=False, catchbreak=False)
