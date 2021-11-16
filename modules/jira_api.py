#
# Author : Pritam Kalbhor (physics.pritam@gmail.com)
#

from jira import JIRA
import base64, os, sys, subprocess, time

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
         # Requires jira version >= 3.1.1
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

def get_workflow_id_names():
   file = 'workflow_config.json'
   if os.path.exists(file):
      config = json.load(open(file))
   else:
      raise FileNotFoundError('Create %s by submitting relval for production' %file)
   campIDs = {'HLT': set(), 'PR': set(), 'EXPR': set()}
   workflow_names = {'HLT': set(), 'PR': set(), 'EXPR': set()}
   for section in config.keys():
      wtype = section.split('_')[0].strip()
      campIDs[wtype].add(config[section]['Config']['Campaign'])
      workflow_names[wtype].add(config[section]['workflow_name'])
   return (campIDs, workflow_names)

def submission_status(campIDs):
   dmytro = 'https://dmytro.web.cern.ch/dmytro/cmsprodmon/requests.php?campaign='
   comment = """Hi All,
   You can monitor status of the submission using following campaign ids:
   HLT: [{hlt}|{dmytro}{hlt}]
   Prompt: [{prompt}|{dmytro}{prompt}]
   Express: [{express}|{dmytro}{express}]

   Best,
   AlCaDB Team""".format(hlt=str(*campIDs['HLT']), 
                              prompt=str(*campIDs['PR']), 
                              express=str(*campIDs['EXPR']), dmytro=dmytro)
   return comment

def countdown(time_sec):
   """Taken from https://www.programiz.com/python-programming/examples/countdown-timer"""
   while time_sec:
      mins, secs = divmod(time_sec, 60)
      timeformat = '{:02d}:{:02d}'.format(mins, secs)
      print(timeformat, end='\r')
      time.sleep(1)
      time_sec -= 1

if __name__ == '__main__':
   from pathlib import Path
   directory = os.path.abspath(__file__)
   sys.path.append(str(Path(directory).parent.parent))
   from process_input import *
   parser.add_argument('--comment', action='store_true', help='Comment status of sumission to the JIRA')
   parsedArgs = parser.parse_known_args()[0]

   get_user()
   args = json.load(open('envs.json'))
   api = JiraAPI(args, parsedArgs.user, parsedArgs.password)
   jira = api.connection
   if parsedArgs.comment:
      campIDs, workflow_names = get_workflow_id_names()
      comment = submission_status(campIDs)
      print('>> Alert!!! You going to comment on CMSALCA-%s. \
           \n>> Make sure you are doing it deliberately' %args['Jira'])
      print('>> You have 15 seconds to quit')
      countdown(15)
      status = api.add_comment(comment)
      print('>> Comment added:\n', comment)