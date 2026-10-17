"""Evaluate actual data-agent routes against independently computed CSV answers."""
import argparse,json,hashlib,tempfile
from pathlib import Path
import pandas as pd
from agent import DataAgent
p=argparse.ArgumentParser();p.add_argument('csv',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists():raise ValueError('New output directory required')
a.output.mkdir(parents=True);frame=pd.read_csv(a.csv);agent=DataAgent(a.csv,str(a.output/'audit.sqlite'))
cases=[('How many rows are in the dataset?',str(len(frame)),'query_dataset'),('Calculate sqrt(16)+2^3','12.0','calculate'),('financial advice mean rings','OUT_OF_SCOPE','check_scope')]
if 'Rings' in frame:cases.append(('mean rings',str(round(float(frame.Rings.mean()),4)),'query_dataset'))
records=[]
for query,expected,tool in cases:
 result=agent.run(query);passed=result['tool']==tool and expected in result['observation'];records.append({'query':query,'expected_tool':tool,'expected_fragment':expected,'result':result,'passed':passed})
# Persistence and exact input identity are verified separately from routing accuracy.
assert agent.verify_audit();agent.close();again=DataAgent(a.csv,str(a.output/'audit.sqlite'));assert again.run(cases[0][0])['cached'];assert again.verify_audit();again.close()
record={'input_sha256':hashlib.sha256(a.csv.read_bytes()).hexdigest(),'cases':records,'passed':sum(r['passed'] for r in records),'total':len(records),'persistent_cache_reload':True,'audit_chain_valid':True,'scope':'Deterministic routing/tool correctness, not language-model reasoning or answer entailment'}
(a.output/'benchmark.json').write_text(json.dumps(record,indent=2)+'\n')
if record['passed']!=record['total']:raise AssertionError('Benchmark case failed')
