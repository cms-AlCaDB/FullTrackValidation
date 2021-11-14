#
# Author : Pritam Kalbhor (physics.pritam@gmail.com)
#

from jira import JIRA
import base64, sys, subprocess

class JiraAPI:
   CERN_CA_BUNDLE = '/etc/pki/tls/certs/ca-bundle.crt'
   def __init__(self, args, username, password):
      self.args = args
      self.username = username
      self.connection = self.get_jira_client(password)

   def get_jira_client(self, password):
      host = 'http://its.cern.ch/jira'
      options={'check_update': False, 'verify': self.CERN_CA_BUNDLE}
      if password is not None: 
         return JIRA(host, basic_auth=(self.username, password), options=options)
      else:
         PAT = subprocess.getoutput("$HOME/private/.auth/.dec")
         return JIRA(host, token_auth=PAT, options=options)

   def create_issue(self):
      """Create new JIRA ticket"""
      jira = self.connection
      new_issue = jira.create_issue(project='CMSALCA', issuetype={'name': 'Task'}, 
         summary = self.args['emailSubject'], description = self.args['emailBody'])
      new_issue.update(assignee={'name': 'tvami'})
      new_issue.update(fields={"labels": self.args['Labels']})
      new_issue.update(fields={"priority": {'name': 'Major'}})

   def add_comment(self, text):
      issue = self.connection.issue('CMSALCA-{}'.format(self.args['Jira']))
      comment = self.connection.add_comment(issue.key, text)

   def check_duplicate(self):
      # Summaries of my last 3 reported issues
      for issue in self.connection.search_issues('project=CMSALCA order by created desc', maxResults=5):
         labels = set(issue.fields.labels)
         if labels == set(self.args['Labels']):
            print(">> Labels ", labels, " matching with ticket: ", issue.key, "!")
            return issue.key
      return False

   def get_key(self):
      """Get Jira issue key of the most recent ticket from CMSALCA project"""
      issue = self.connection.search_issues('project=CMSALCA order by created desc', maxResults=1)[0]
      return issue.key

if __name__ == '__main__':
   args = dict()
   sysArgs = sys.argv
   api = JiraAPI(args, sysArgs[1], sysArgs[2])
   jira = api.connection
   issue = jira.issue("CMSALCA-135")
