import sqlite3, json, os, hashlib, secrets
from contextlib import contextmanager
from backend.domain import project, apply
class Store:
 def __init__(self,path=None):
  self.path=path or os.getenv('DATABASE_PATH','advising.db')
  with self.db() as db:
   db.executescript('CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,name TEXT,role TEXT,salt TEXT,hash TEXT);CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,body TEXT);CREATE TABLE IF NOT EXISTS assignments(project_id TEXT,user_id TEXT,PRIMARY KEY(project_id,user_id));CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user_id TEXT,expires REAL);')
 @contextmanager
 def db(self):
  db=sqlite3.connect(self.path);db.row_factory=sqlite3.Row
  try:
   with db:yield db
  finally:db.close()
 def seed(self):
  with self.db() as db:
   if db.execute('SELECT 1 FROM users').fetchone():return
   accounts=[('candidate','Alex Morgan','Candidate'),('advisor','Dr. Taylor Reed','Advisor'),('university','Program Office','University'),('chair','Dr. Jordan Lee','Chair'),('member','Dr. Casey Chen','Member')]
   for ident,name,role in accounts:
    salt=secrets.token_hex(16);h=hashlib.pbkdf2_hmac('sha256',b'demo-research',salt.encode(),200000).hex()
    db.execute('INSERT INTO users VALUES(?,?,?,?,?)',(ident,name,role,salt,h))
   for p in [project('Alex Morgan','Behavioral Risk Modeling for Healthcare Security'),project('Dr. Taylor Reed','Research Supervision Effectiveness',personal=True)]:
    db.execute('INSERT INTO projects VALUES(?,?)',(p['id'],json.dumps(p)))
    for ident,_,role in accounts:
     if not p['personal'] or role=='Advisor':db.execute('INSERT INTO assignments VALUES(?,?)',(p['id'],ident))
 def login(self,ident,password):
  import time
  with self.db() as db:
   row=db.execute('SELECT * FROM users WHERE id=?',(ident,)).fetchone()
   if not row or not secrets.compare_digest(row['hash'],hashlib.pbkdf2_hmac('sha256',password.encode(),row['salt'].encode(),200000).hex()):raise PermissionError('Invalid login')
   token=secrets.token_urlsafe(32);db.execute('INSERT INTO sessions VALUES(?,?,?)',(token,ident,time.time()+28800))
   return token
 def user(self,token):
  import time
  with self.db() as db:
   row=db.execute('SELECT u.id,u.name,u.role FROM users u JOIN sessions s ON u.id=s.user_id WHERE s.token=? AND s.expires>?',(token,time.time())).fetchone()
   if not row:raise PermissionError('Sign in required')
   return dict(row)
 def allowed(self,db,ident,user):
  if not db.execute('SELECT 1 FROM assignments WHERE project_id=? AND user_id=?',(ident,user['id'])).fetchone():raise PermissionError('Workspace access denied')
 def list(self,user):
  with self.db() as db:return [json.loads(r[0]) for r in db.execute('SELECT p.body FROM projects p JOIN assignments a ON p.id=a.project_id WHERE a.user_id=?',(user['id'],))]
 def get(self,ident,user):
  with self.db() as db:
   self.allowed(db,ident,user);row=db.execute('SELECT body FROM projects WHERE id=?',(ident,)).fetchone()
   if not row:raise ValueError('Workspace not found')
   return json.loads(row[0])
 def update(self,ident,user,action,data,revision):
  with self.db() as db:
   db.execute('BEGIN IMMEDIATE');self.allowed(db,ident,user)
   p=json.loads(db.execute('SELECT body FROM projects WHERE id=?',(ident,)).fetchone()[0])
   if p['revision']!=revision:raise ValueError('Record changed. Reload before saving.')
   apply(p,user,action,data);db.execute('UPDATE projects SET body=? WHERE id=?',(json.dumps(p),ident));return p
 def create(self,user,data):
  if user['role'] not in ['Advisor','Candidate']:raise PermissionError('Researcher or Advisor required')
  p=project(**data)
  with self.db() as db:
   db.execute('INSERT INTO projects VALUES(?,?)',(p['id'],json.dumps(p)))
   ids=[user['id']] if p['personal'] else [r[0] for r in db.execute('SELECT id FROM users')]
   for ident in ids:db.execute('INSERT INTO assignments VALUES(?,?)',(p['id'],ident))
  return p
