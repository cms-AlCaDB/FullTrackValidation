from jira import JIRA

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
      jira = get_jira_client()
      new_issue = jira.create_issue(project='CMSALCA', issuetype={'name': 'Task'})

      Summary = "[HLT/EXPRESS/PROMPT] Full track validation of "
      Summary += Title
      Summary += " (Week 32, 2021)"
      new_issue.update(summary=Summary)
      new_issue.update(description='Desciption comming soon!')
      new_issue.update(assignee={'name': 'pkalbhor'})

   def check_duplicate(self):
      # Summaries of my last 3 reported issues
      for issue in self.connection.search_issues('project=CMSALCA order by created desc', maxResults=5):
         print('{}: {}'.format(issue.key, issue.fields.summary))
         labels = set(issue.fields.labels)
         if labels == set(self.args['Labels']):
            print("Labels matching with ticket: ", issue.key)
            print("Not creating new ticket !")
            return issue.key
      return False

   def get_key(self):
      issue = self.connection.search_issues('project=CMSALCA order by created desc', maxResults=1)[0]
      return issue.key

if __name__ == '__main__':
   args = dict()
   api = JiraAPI(args)
   # jira = api.get_jira_client()
   # issue = jira.issue("CMSALCA-135")