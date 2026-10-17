"""Persistent deterministic data-tool routing, with dataset-scoped cache and audit.

Uses notebook tools; this is not an LLM or multi-step planner. SQLite triggers
reject normal update/delete of audit records. Hash chaining detects alterations;
a privileged database owner is outside this integrity boundary.
"""
import argparse,datetime,hashlib,json,math,re,sqlite3
from pathlib import Path
import pandas as pd,numpy as np
from notebook_units import definitions
BLOCKLIST=['password','credit card','medical diagnosis','legal advice','stock tip','diagnose','exploit','hack','financial advice']
class DataAgent:
 def __init__(self,csv,database=':memory:'):
  path=Path(csv);frame=pd.read_csv(path);self.dataset_sha=hashlib.sha256(path.read_bytes()).hexdigest()
  self.scope={'math':math,'json':json,'re':re,'datetime':datetime,'np':np,'pd':pd,'DF':frame,'DF_COLS_LOWER':{c.lower():c for c in frame},'TOOL_REGISTRY':{},'SCOPE_BLOCKLIST':BLOCKLIST}
  definitions(['register_tool','calculate','query_dataset','correlation_analysis','get_current_date','check_scope','classify_intent'],self.scope)
  self.db=sqlite3.connect(database)
  self.db.executescript('''CREATE TABLE IF NOT EXISTS cache(key TEXT PRIMARY KEY, result TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, payload TEXT NOT NULL, previous TEXT NOT NULL, digest TEXT NOT NULL);
CREATE TRIGGER IF NOT EXISTS no_audit_update BEFORE UPDATE ON audit BEGIN SELECT RAISE(ABORT,'append-only audit'); END;
CREATE TRIGGER IF NOT EXISTS no_audit_delete BEFORE DELETE ON audit BEGIN SELECT RAISE(ABORT,'append-only audit'); END;''')
 def verify_audit(self):
  previous='0'*64
  for payload,prev,digest in self.db.execute('SELECT payload,previous,digest FROM audit ORDER BY id'):
   if prev!=previous or hashlib.sha256((previous+payload).encode()).hexdigest()!=digest:return False
   previous=digest
  return True
 def run(self,query):
  if not isinstance(query,str) or not query.strip() or len(query)>10000:raise ValueError('Nonempty bounded query required')
  tool,arg=self.scope['classify_intent'](query)
  if any(word in query.lower() for word in BLOCKLIST):tool,arg='check_scope',query
  key=hashlib.sha256(json.dumps([self.dataset_sha,tool,arg],ensure_ascii=False).encode()).hexdigest()
  row=self.db.execute('SELECT result FROM cache WHERE key=?',(key,)).fetchone() if tool!='get_current_date' else None
  if tool=='get_current_date':observation=datetime.datetime.now(datetime.timezone.utc).isoformat()
  else:observation=row[0] if row else str(self.scope['TOOL_REGISTRY'][tool](arg))
  result={'tool':tool,'observation':observation,'cached':row is not None,'dataset_sha256':self.dataset_sha}
  payload=json.dumps({'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'query':query,'result':result},sort_keys=True)
  with self.db:
   if tool!='get_current_date' and not observation.startswith('Error'):self.db.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(key,observation))
   previous=self.db.execute('SELECT digest FROM audit ORDER BY id DESC LIMIT 1').fetchone();previous=previous[0] if previous else '0'*64
   self.db.execute('INSERT INTO audit(payload,previous,digest) VALUES (?,?,?)',(payload,previous,hashlib.sha256((previous+payload).encode()).hexdigest()))
  return result
 def close(self):self.db.close()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('csv',type=Path);p.add_argument('question');p.add_argument('--database',default=':memory:');a=p.parse_args();agent=DataAgent(a.csv,a.database)
 try:print(json.dumps(agent.run(a.question),indent=2));assert agent.verify_audit()
 finally:agent.close()
