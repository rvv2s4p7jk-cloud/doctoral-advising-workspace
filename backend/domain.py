"""Workflow gates and role permissions; no automated academic decisions."""
from datetime import date, datetime, timezone
from uuid import uuid4
import calendar
AI_NOTICE = 'Generative AI may be used only where permitted by your university and program. You remain responsible for authorship, accuracy, citations, analysis and integrity. Verify generated claims and references. Never fabricate research or upload restricted information without authorization. Disclose tools, purpose and extent of assistance as required. Consult your Advisor when permission is unclear. Acknowledgment does not authorize AI use. Proposed notice v1; not an official university policy.'
CHAPTERS=['Introduction','Literature Review','Methodology','Results','Discussion and Conclusions']
def now(): return datetime.now(timezone.utc).isoformat()
def add_months(day,months):
 d=date.fromisoformat(day); y,m=divmod(d.year*12+d.month-1+months,12); m+=1
 return date(y,m,min(d.day,calendar.monthrange(y,m)[1])).isoformat()
def template(program,department):
 return {'university':'Demonstration University','department':department,'program':program,'version':1,'chapters':CHAPTERS[:],'meeting_interval_days':14,'formal_review':'Semester','ratings':{'Green':'On track','Yellow':'Corrective action needed','Red':'Substantial concern requiring intervention'},'ai_policy':AI_NOTICE,'proposal_required':True,'final_topic_approver':'University','leave_rule':'Manual review of each institutional deadline'}
def project(name,title,program='D.Eng. Praxis',department='Engineering',personal=False,start=None,months=12,hours=10,deadline=None):
 start=start or date.today().isoformat(); end=add_months(start,months)
 return {'id':str(uuid4()),'student':name,'personal':personal,'template':template(program,department),'topic':{'approved':None,'request':{'title':title,'reason':'Initial proposal','status':'Draft','version':1}},'chapters':[{'number':i+1,'title':x,'status':'Not started','due':add_months(start,min(months,max(1,round(months*(i+1)/6)))),'note':''} for i,x in enumerate(CHAPTERS)],'plan':{'start':start,'duration_months':months,'hours_per_week':hours,'original_target':end,'current_target':end,'degree_start':start,'institutional_deadline':deadline or add_months(start,36),'revisions':[]},'meetings':[],'tasks':[],'alignment':[],'ai_log':[],'defense':{'ready':False,'notification':'Not prepared','notification_record':'','scheduled_date':None,'outcome':None,'feedback':[],'clearance':False,'final_submitted':False},'approvals':{'proposal':False,'research_execution':False,'manuscript':False},'audit':[],'revision':0}
def apply(p,actor,action,data):
 role=actor['role']; owner=actor['name']; personal=p['personal']
 def require(*roles):
  if role not in roles: raise PermissionError('This action requires '+', '.join(roles))
 def text(key):
  val=str(data.get(key,'')).strip()
  if not val or len(val)>5000: raise ValueError(key+' is required (maximum 5000 characters)')
  return val
 def review(): return text('note')
 if action=='topic_submit':
  require('Candidate','Advisor');req=p['topic']['request']
  if req['status'] not in ['Draft','Revisions needed']: raise ValueError('Topic is not editable at this stage')
  req['title']=text('title');req['reason']=text('reason');req['status']='Advisor review'
 elif action=='topic_change':
  require('Candidate','Advisor')
  if not p['topic']['approved'] or p['topic']['request']['status']!='Approved': raise ValueError('Finish the current approval first')
  p['topic']['request']={'title':text('title'),'reason':text('reason'),'impact':text('impact'),'status':'Draft','version':p['topic']['request']['version']+1}
 elif action=='topic_endorse':
  require('Advisor')
  if p['topic']['request']['status']!='Advisor review': raise ValueError('Awaiting submission')
  p['topic']['request']['status']='University review';p['topic']['request']['advisor_note']=review()
 elif action=='topic_approve':
  require('Advisor' if personal else 'University')
  if p['topic']['request']['status']!='University review': raise ValueError('Advisor endorsement is required')
  p['topic']['request']['status']='Approved';p['topic']['request']['approval_record']=review();p['topic']['approved']=dict(p['topic']['request'])
 elif action=='topic_return':
  require('Advisor','University');expected='Advisor review' if role=='Advisor' else 'University review'
  if p['topic']['request']['status']!=expected: raise ValueError('Not awaiting your review')
  p['topic']['request']['status']='Revisions needed';p['topic']['request']['feedback']=review()
 elif action=='chapter':
  require('Candidate','Advisor')
  if not p['topic']['approved']: raise ValueError('Topic approval is required before Chapter 1')
  i=int(data['number'])-1
  if i<0 or i>=len(p['chapters']): raise ValueError('Unknown chapter')
  c=p['chapters'][i];target=data['status'];edges={'Not started':['Drafting'],'Drafting':['Submitted'],'Submitted':['Advisor review'],'Advisor review':['Revisions needed','Advisor accepted'],'Revisions needed':['Submitted'],'Advisor accepted':[]}
  if target in ['Advisor review','Revisions needed','Advisor accepted']: require('Advisor')
  if target not in edges[c['status']]: raise ValueError('Invalid chapter transition')
  if target=='Advisor accepted' and any(x['status']!='Advisor accepted' for x in p['chapters'][:i]): raise ValueError('Earlier chapters must be accepted first')
  c['status']=target;c['note']=review()
 elif action=='gate':
  require('Advisor');gate=data['gate']
  if gate not in p['approvals']: raise ValueError('Unknown approval')
  needed=3 if gate in ['proposal','research_execution'] else len(p['chapters'])
  if any(c['status']!='Advisor accepted' for c in p['chapters'][:needed]): raise ValueError('Required chapters have not been accepted')
  if gate=='research_execution' and not p['approvals']['proposal']: raise ValueError('Proposal approval required')
  p['approvals'][gate]=True;review()
 elif action=='checkin':
  require('Candidate','Advisor')
  date.fromisoformat(text('date'));date.fromisoformat(text('next_meeting'))
  p['meetings'].append({'id':str(uuid4()),'date':data['date'],'next_meeting':data['next_meeting'],'kind':data.get('kind','Advisor meeting'),'accomplishments':text('accomplishments'),'blockers':text('blockers'),'agenda':text('agenda'),'reports':[],'acknowledged_version':0})
 elif action=='report':
  require('Advisor');m=next((x for x in p['meetings'] if x['id']==data['meeting_id']),None)
  if m is None: raise ValueError('Meeting not found')
  fields=['progress','quality','professionalism','timeline'];r={k:data[k] for k in fields}
  if any(v not in ['Green','Yellow','Red','Not assessed'] for v in r.values()): raise ValueError('Invalid rating')
  for k in ['strengths','improvements','behavior_evidence','advisor_commitments']:r[k]=text(k)
  if r['progress'] in ['Yellow','Red']:r['improvement_plan']=text('improvement_plan')
  r.update(version=len(m['reports'])+1,at=now(),author=owner);m['reports'].append(r)
 elif action=='acknowledge':
  require('Candidate');m=next((x for x in p['meetings'] if x['id']==data['meeting_id']),None)
  if not m or not m['reports']: raise ValueError('No report to acknowledge')
  m['acknowledged_version']=len(m['reports']);m['response']=text('response')
 elif action=='task':
  require('Advisor','Candidate');date.fromisoformat(text('due'))
  p['tasks'].append({'id':str(uuid4()),'title':text('title'),'owner':text('owner'),'due':data['due'],'criteria':text('criteria'),'status':'Open'})
 elif action=='task_complete':
  require('Candidate','Advisor');t=next((x for x in p['tasks'] if x['id']==data['task_id']),None)
  if not t: raise ValueError('Task not found')
  t['status']='Completed';t['evidence']=review()
 elif action=='chapter_due':
  require('Advisor');i=int(data['number'])-1
  if i<0 or i>=len(p['chapters']):raise ValueError('Unknown chapter')
  date.fromisoformat(text('due'));p['chapters'][i]['due']=data['due'];review()
 elif action=='settings':
  require('University' if not personal else 'Advisor')
  import copy
  p.setdefault('template_history',[]).append(copy.deepcopy(p['template']))
  p['template']['meeting_interval_days']=int(data['interval'])
  if not 1<=p['template']['meeting_interval_days']<=365:raise ValueError('Meeting interval must be 1–365 days')
  p['template']['formal_review']=text('formal_review');p['template']['ai_policy']=text('ai_policy')
  p['template']['version']+=1;review()
 elif action=='plan':
  require('Advisor');target=text('target');date.fromisoformat(target)
  if target<p['plan']['start']: raise ValueError('Target cannot precede start')
  p['plan']['revisions'].append({'previous':p['plan']['current_target'],'target':target,'reason':review(),'at':now()});p['plan']['current_target']=target
 elif action=='alignment':
  require('Candidate','Advisor');p['alignment'].append({k:text(k) for k in ['question','objective','evidence','analysis','success'] }|{'hypothesis':str(data.get('hypothesis','Not applicable'))})
 elif action=='ai_log':
  require('Candidate','Advisor');p['ai_log'].append({k:text(k) for k in ['tool','purpose','extent','verification','disclosure']}|{'at':now(),'notice_version':1,'acknowledged':True})
 elif action=='ready':
  require('Advisor')
  if not all(p['approvals'].values()) or any(c['status']!='Advisor accepted' for c in p['chapters']): raise ValueError('All chapters and research gates must be accepted')
  if p['topic']['request']['status']!='Approved': raise ValueError('Pending topic change must be resolved')
  p['defense']['ready']=True;p['defense']['readiness_note']=review()
 elif action=='notification':
  require('Advisor');d=p['defense'];target=data['status'];edges={'Not prepared':'Prepared','Prepared':'Sent'}
  if not d['ready'] or edges.get(d['notification'])!=target: raise ValueError('Invalid notification transition')
  d['notification']=target;d['notification_record']=review();d['notification_at']=now()
 elif action=='notification_ack':
  require('University')
  if p['defense']['notification']!='Sent':raise ValueError('Notification has not been sent')
  p['defense']['notification']='Acknowledged';p['defense']['ack_record']=review()
 elif action=='schedule':
  require('University')
  if p['defense']['notification']!='Acknowledged': raise ValueError('Acknowledge notification first')
  date.fromisoformat(text('date'));p['defense']['scheduled_date']=data['date'];p['defense']['schedule_record']=review()
 elif action=='feedback':
  require('Chair','Member')
  if p['defense']['clearance']:raise ValueError('Feedback is locked after final clearance')
  if not p['defense']['scheduled_date']:raise ValueError('Defense must be scheduled first')
  kind=data['kind']
  if kind not in ['Required correction','Recommendation']: raise ValueError('Invalid feedback type')
  p['defense']['feedback'].append({'id':str(uuid4()),'author':owner,'role':role,'reference':text('reference'),'comment':text('comment'),'kind':kind,'status':'Open','responses':[]})
 elif action=='outcome':
  require('Chair')
  if not p['defense']['scheduled_date']:raise ValueError('Defense not scheduled')
  if data['outcome'] not in ['Pass','Pass with corrections','Further examination required','Fail']: raise ValueError('Unknown outcome')
  p['defense']['outcome']=data['outcome'];p['defense']['outcome_record']=review()
 elif action=='correction_submit':
  require('Candidate');f=next((x for x in p['defense']['feedback'] if x['id']==data['feedback_id']),None)
  if not f or f['status'] not in ['Open','Further revision needed']:raise ValueError('Correction is not open')
  f['responses'].append({'at':now(),'note':review()});f['status']='Revision submitted'
 elif action=='correction_review':
  require('Chair','Member');f=next((x for x in p['defense']['feedback'] if x['id']==data['feedback_id']),None)
  if not f or f['status']!='Revision submitted':raise ValueError('No revision to review')
  if role=='Member' and f['author']!=owner: raise PermissionError('Only the assigned member or chair may verify')
  if data['status'] not in ['Accepted','Further revision needed']:raise ValueError('Invalid decision')
  f['status']=data['status'];f['verification']=review()
 elif action=='clearance':
  require('Chair')
  if p['defense']['outcome'] not in ['Pass','Pass with corrections']: raise ValueError('A passing outcome is required')
  if any(f['kind']=='Required correction' and f['status']!='Accepted' for f in p['defense']['feedback']): raise ValueError('Required corrections remain open')
  p['defense']['clearance']=True;p['defense']['clearance_record']=review()
 elif action=='final_submission':
  require('University')
  if not p['defense']['clearance']:raise ValueError('Final clearance required')
  p['defense']['final_submitted']=True;p['defense']['submission_record']=review()
 else:raise ValueError('Unknown action')
 p['revision']+=1;p['audit'].append({'at':now(),'actor':owner,'role':role,'action':action,'revision':p['revision']})
 return p
