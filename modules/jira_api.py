#
# Author : Pritam Kalbhor (physics.pritam@gmail.com)
#

from jira import JIRA
import base64, sys

class JiraAPI:
   CERN_CA_BUNDLE = '/etc/pki/tls/certs/ca-bundle.crt'
   cert = '/afs/cern.ch/user/p/pkalbhor/private/usercert.pem'
   key = '/afs/cern.ch/user/p/pkalbhor/private/userkey.pem'
   def __init__(self, args, username, password):
      self.args = args
      self.connection = self.get_jira_client(username, password)

   def get_jira_client(self, username, password):
      return JIRA('http://its.cern.ch/jira',
                  basic_auth=(username, password),
                  options={'check_update': False, 'verify': self.CERN_CA_BUNDLE, 'client_cert': (self.cert, self.key)})

   def create_issue(self):
      """Create new JIRA ticket"""
      jira = self.connection
      new_issue = jira.create_issue(project='CMSALCA', issuetype={'name': 'Task'}, summary = args['emailSubject'], description = args['emailBody'])
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
      issue = self.connection.search_issues('project=CMSALCA order by created desc', maxResults=1)[0]
      return issue.key

if __name__ == '__main__':
   args = dict()
   sysArgs = sys.argv
   api = JiraAPI(args, sysArgs[1], sysArgs[2])
   jira = api.connection
   issue = jira.issue("CMSALCA-135")
