from pathlib import Path
import csv, io, json
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from backend.store import Store
app=FastAPI(title='Doctoral Advising Workspace',version='1.0.0-demo')
store=Store();store.seed()
class Login(BaseModel):
 username:str=Field(max_length=100)
 password:str=Field(max_length=200)
class Mutation(BaseModel):
 action:str=Field(max_length=50)
 data:dict
 revision:int=Field(ge=0)
class NewProject(BaseModel):
 name:str=Field(min_length=3,max_length=150)
 title:str=Field(min_length=5,max_length=300)
 program:str=Field(default='D.Eng. Praxis',min_length=3,max_length=100)
 department:str=Field(default='Engineering',min_length=3,max_length=100)
 personal:bool=False
 start:str
 months:int=Field(default=12,ge=1,le=120)
 hours:int=Field(default=10,ge=1,le=80)
 deadline:str
@app.exception_handler(PermissionError)
async def permission(request,exc):
 from fastapi.responses import JSONResponse
 return JSONResponse({'detail':str(exc)},status_code=403)
@app.exception_handler(ValueError)
async def invalid(request,exc):
 from fastapi.responses import JSONResponse
 return JSONResponse({'detail':str(exc)},status_code=409)
def user(request:Request):
 token=request.cookies.get('session','');return store.user(token)
@app.post('/api/login')
def login(body:Login,response:Response):
 token=store.login(body.username,body.password);response.set_cookie('session',token,httponly=True,samesite='strict',max_age=28800);return store.user(token)
@app.post('/api/logout')
def logout(request:Request,response:Response):
 with store.db() as db:db.execute('DELETE FROM sessions WHERE token=?',(request.cookies.get('session',''),))
 response.delete_cookie('session');return {'ok':True}
@app.get('/api/me')
def me(actor=Depends(user)):return actor
@app.get('/api/projects')
def projects(actor=Depends(user)):return store.list(actor)
@app.post('/api/projects',status_code=201)
def create(body:NewProject,actor=Depends(user)):
 from datetime import date
 if date.fromisoformat(body.deadline)<date.fromisoformat(body.start):raise ValueError('Institutional deadline precedes start')
 if body.personal and actor['role']!='Advisor':raise PermissionError('Personal Advisor mode requires Advisor')
 return store.create(actor,body.model_dump())
@app.post('/api/projects/{ident}/actions')
def action(ident:str,body:Mutation,actor=Depends(user)):return store.update(ident,actor,body.action,body.data,body.revision)
@app.get('/api/projects/{ident}/export/{kind}')
def export(ident:str,kind:str,actor=Depends(user)):
 p=store.get(ident,actor)
 if kind=='json':return Response(json.dumps(p,indent=2),media_type='application/json',headers={'Content-Disposition':'attachment; filename="research-plan.json"'})
 if kind=='csv':
  out=io.StringIO();writer=csv.writer(out);writer.writerow(['Chapter','Title','Status','Due','Revision'])
  for c in p['chapters']:
   def safe(v):
    s=str(v);return "'"+s if s.startswith(('=','+','-','@')) else s
   writer.writerow([safe(c[k]) for k in ['number','title','status','due']]+[p['revision']])
  return Response(out.getvalue(),media_type='text/csv',headers={'Content-Disposition':'attachment; filename="chapter-timeline.csv"'})
 if kind=='ics':
  from datetime import date,timedelta
  lines=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Doctoral Workspace//EN']
  for c in p['chapters']:
   day=date.fromisoformat(c['due']);lines+=['BEGIN:VEVENT',f"UID:{ident}-chapter-{c['number']}@doctoral-workspace",'DTSTAMP:20261005T000000Z','DTSTART;VALUE=DATE:'+day.strftime('%Y%m%d'),'DTEND;VALUE=DATE:'+(day+timedelta(days=1)).strftime('%Y%m%d'),f"SUMMARY:Chapter {c['number']} due",'END:VEVENT']
  return Response('\r\n'.join(lines+['END:VCALENDAR'])+'\r\n',media_type='text/calendar',headers={'Content-Disposition':'attachment; filename="milestones.ics"'})
 raise HTTPException(404,'Unknown export')
app.mount('/',StaticFiles(directory=Path(__file__).resolve().parents[1]/'frontend',html=True),name='ui')
