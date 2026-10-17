"""Execute the retained notebook, capture outputs and export fitted artifacts.

Run in a new output directory, preserving the notebook byte-for-byte. A supplied
CSV is copied under the notebook's documented input name. This executes trusted
repository code; source parsing is not substituted for training or evaluation.
"""
import ast,argparse,contextlib,hashlib,io,json,os,sys,time,traceback
from pathlib import Path
import numpy as np


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parent
 if a.output.exists():raise ValueError('Use a new output directory')
 out=a.output.resolve();out.mkdir(parents=True);nb=root/'analysis.ipynb';source=json.loads(nb.read_text());record={'source_sha256':hashlib.sha256(nb.read_bytes()).hexdigest(),'input_sha256':hashlib.sha256(a.input.read_bytes()).hexdigest() if a.input else None,'python':sys.version.split()[0],'started_unix':time.time(),'cells':[]}
 names={'abalone-age-regression':'abalone.csv','marine-ai-decision-pipeline':'abalone.csv','auditable-data-agent':'abalone.csv','retail-sales-data-pipeline':'laptop_sales.csv','wine-quality-statistical-analysis':'wine_quality.csv'}
 if root.name in names:
  if not a.input:raise ValueError('This notebook requires --input CSV')
  import shutil
  shutil.copyfile(a.input,out/names[root.name])
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 def display(value):
  if hasattr(value,'to_csv'):value.to_csv(out/f'display-{len(list(out.glob("display-*"))):03}.csv',index=False)
  else:print(repr(value))
 figure_number=[0]
 def capture_figures(*args,**kwargs):
  for n in plt.get_fignums():
   figure_number[0]+=1;plt.figure(n).savefig(out/f'figure-{figure_number[0]:03}.png',dpi=120,bbox_inches='tight')
  plt.close('all')
 plt.show=capture_figures
 namespace={'__name__':'__main__','display':display};os.chdir(out);sys.path.insert(0,str(root));log=io.StringIO()
 os.environ.setdefault('LOKY_MAX_CPU_COUNT','2')
 try:
  import torch;torch.set_num_threads(2)
 except ImportError:pass
 try:
  with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
   for index,cell in enumerate(source['cells']):
    if cell['cell_type']!='code':continue
    code=''.join(cell['source'])
    if any(line.lstrip().startswith(('!','%')) for line in code.splitlines()):raise ValueError('Notebook magic requires explicit kernel execution; not silently skipped')
    started=time.perf_counter();tree=ast.parse(code)
    if tree.body and isinstance(tree.body[-1],ast.Expr):
     expr=tree.body.pop();exec(compile(tree,str(nb)+f':cell{index}','exec'),namespace);value=eval(compile(ast.Expression(expr.value),str(nb)+f':cell{index}','eval'),namespace)
     if value is not None:display(value)
    else:exec(compile(tree,str(nb)+f':cell{index}','exec'),namespace)
    record['cells'].append({'index':index,'seconds':time.perf_counter()-started})
  # Export small JSON-compatible metrics and trained models, not raw dataframes.
  summary={}
  for name,v in namespace.items():
   if name.startswith('_'):continue
   if isinstance(v,(str,int,float,bool)) or v is None:summary[name]=v
   if isinstance(v,np.generic):summary[name]=v.item()
   if 'torch' in sys.modules:
    import torch
    if isinstance(v,torch.nn.Module):torch.save(v.state_dict(),out/(name+'.pt'))
   if type(v).__module__.startswith('sklearn.') and hasattr(v,'fit'):
    import joblib
    try:joblib.dump(v,out/(name+'.joblib'))
    except Exception:pass
  (out/'metrics.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n');record['status']='success'
 except Exception:
  record['status']='failed';record['error']=traceback.format_exc();raise
 finally:
  (out/'execution.log').write_text(log.getvalue());record['finished_unix']=time.time()
  (out/'execution.json').write_text(json.dumps(record,indent=2)+'\n');plt.close('all')
 print(json.dumps({'status':record['status'],'cells':len(record['cells']),'output':str(out)}))
if __name__=='__main__':main()
