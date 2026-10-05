import pytest
from backend.domain import project,apply,add_months
from backend.store import Store
from fastapi.testclient import TestClient
from backend import app as module
ACTORS={r:{'id':r.lower(),'name':r,'role':r} for r in ['Candidate','Advisor','University','Chair','Member']}
def act(p,role,action,**data):return apply(p,ACTORS[role],action,data)
def approved():
 p=project('Test Researcher','Test topic')
 act(p,'Candidate','topic_submit',title='Approved topic',reason='Feasible contribution')
 act(p,'Advisor','topic_endorse',note='Reviewed feasibility')
 act(p,'University','topic_approve',note='Official program approval')
 return p
def defense_ready():
 p=approved()
 for c in p['chapters']:
  for status in ['Drafting','Submitted','Advisor review','Advisor accepted']:act(p,'Advisor','chapter',number=c['number'],status=status,note='Reviewed manuscript version')
 for gate in ['proposal','research_execution','manuscript']:act(p,'Advisor','gate',gate=gate,note='Approval evidence')
 act(p,'Advisor','ready',note='Administrative requirements checked')
 for status in ['Prepared','Sent']:act(p,'Advisor','notification',status=status,note='Office record')
 act(p,'University','notification_ack',note='Receipt confirmed')
 act(p,'University','schedule',date='2027-09-10',note='Official committee arrangements')
 return p
def test_topic_authority_and_gate():
 p=project('A','Topic')
 with pytest.raises(ValueError):act(p,'Candidate','chapter',number=1,status='Drafting',note='Start')
 with pytest.raises(PermissionError):act(p,'Candidate','topic_approve',note='Unauthorized')
 with pytest.raises(ValueError):act(p,'University','topic_approve',note='Premature')
def test_change_keeps_active_topic():
 p=approved();act(p,'Candidate','topic_change',title='Changed topic',reason='Data unavailable',impact='Methodology revision')
 assert p['topic']['approved']['title']=='Approved topic'
 assert p['topic']['request']['version']==2
 with pytest.raises(ValueError):act(p,'Advisor','ready',note='Premature')
def test_chapter_acceptance_sequence():
 p=approved()
 with pytest.raises(PermissionError):act(p,'Candidate','chapter',number=1,status='Advisor accepted',note='Self acceptance')
 for status in ['Drafting','Submitted','Advisor review']:act(p,'Advisor','chapter',number=2,status=status,note='Version one')
 with pytest.raises(ValueError):act(p,'Advisor','chapter',number=2,status='Advisor accepted',note='Skip chapter one')
def test_report_versions_and_response():
 p=approved();act(p,'Candidate','checkin',date='2026-10-05',next_meeting='2026-10-19',accomplishments='Revised questions',blockers='No blockers',agenda='Review methods')
 m=p['meetings'][0];data=dict(meeting_id=m['id'],progress='Yellow',quality='Green',professionalism='Green',timeline='Yellow',strengths='Clear questions',improvements='Metric definition',behavior_evidence='Prepared and timely',advisor_commitments='Review by Friday',improvement_plan='Submit metric definitions next week')
 act(p,'Advisor','report',**data);act(p,'Candidate','acknowledge',meeting_id=m['id'],response='Received, clarification requested');act(p,'Advisor','report',**data)
 assert len(m['reports'])==2 and m['acknowledged_version']==1
 assert m['reports'][0]['version']==1
def test_defense_corrections_clearance():
 p=defense_ready();act(p,'Member','feedback',kind='Required correction',reference='Chapter 4 page 80',comment='Correct confidence interval')
 act(p,'Chair','outcome',outcome='Pass with corrections',note='Committee official decision')
 with pytest.raises(ValueError):act(p,'Chair','clearance',note='Premature')
 f=p['defense']['feedback'][0];act(p,'Candidate','correction_submit',feedback_id=f['id'],note='Revised table with verified interval')
 act(p,'Member','correction_review',feedback_id=f['id'],status='Accepted',note='Verified corrected table')
 act(p,'Chair','clearance',note='All required changes verified');act(p,'University','final_submission',note='Repository receipt recorded')
 assert p['defense']['final_submitted']
 with pytest.raises(ValueError):act(p,'Member','feedback',kind='Required correction',reference='New issue',comment='Late feedback')
def test_notification_cannot_skip():
 p=approved()
 with pytest.raises(ValueError):act(p,'Advisor','notification',status='Sent',note='No readiness')
 with pytest.raises(PermissionError):act(p,'Candidate','ready',note='Self readiness')
def test_end_of_month_dates():
 assert add_months('2028-01-31',1)=='2028-02-29'
 assert add_months('2027-01-31',1)=='2027-02-28'
@pytest.fixture
def client(tmp_path,monkeypatch):
 store=Store(str(tmp_path/'test.db'));store.seed();monkeypatch.setattr(module,'store',store)
 return TestClient(module.app)
def login(client,user='candidate'):
 assert client.post('/api/login',json={'username':user,'password':'demo-research'}).status_code==200
 return client.get('/api/projects').json()
def test_authentication(client):
 assert client.get('/api/projects').status_code==403
 assert client.post('/api/login',json={'username':'advisor','password':'wrong'}).status_code==403
 login(client);client.post('/api/logout');assert client.get('/api/me').status_code==403
def test_personal_workspace_isolation(client):
 projects=login(client,'advisor');personal=next(p for p in projects if p['personal']);client.post('/api/logout');login(client)
 assert client.get(f"/api/projects/{personal['id']}/export/json").status_code==403
 assert len(client.get('/api/projects').json())==1
def test_stale_writes_rollback(client):
 p=login(client)[0];url=f"/api/projects/{p['id']}/actions";body={'action':'topic_submit','data':{'title':'New title','reason':'Feasible'},'revision':0}
 assert client.post(url,json=body).status_code==200
 assert client.post(url,json=body).status_code==409
 assert client.get('/api/projects').json()[0]['revision']==1
def test_exports_and_validation(client):
 p=login(client)[0]
 for kind in ['json','csv','ics']:assert client.get(f"/api/projects/{p['id']}/export/{kind}").status_code==200
 assert client.post('/api/projects',json={'name':'A','title':'B'}).status_code==422
 assert client.get('/').status_code==200
def test_persistence(tmp_path):
 path=str(tmp_path/'test.db');s=Store(path);s.seed();u=s.user(s.login('advisor','demo-research'));p=s.list(u)[0]
 s.update(p['id'],u,'task',{'title':'Review chapter','owner':'Advisor','due':'2026-10-20','criteria':'Return written feedback'},0)
 assert Store(path).get(p['id'],u)['tasks'][0]['title']=='Review chapter'
