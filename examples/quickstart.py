"""Offline example using the public implementation; see README for evidence scope."""
import sys,json,pathlib,os
repo=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(repo));sys.path.insert(0,str(repo/'src'));os.chdir(repo)
import math,re,datetime,pandas as pd
from notebook_units import definitions
df=pd.DataFrame({'Sex':['F','F','M'],'Rings':[10,12,8],'Shell_weight':[.2,.4,.8]})
scope={'math':math,'json':json,'re':re,'datetime':datetime,'DF':df,'DF_COLS_LOWER':{c.lower():c for c in df},'TOOL_REGISTRY':{}}
definitions(['register_tool','calculate','query_dataset'],scope)
print(json.dumps({"fixture":"three generated abalone rows","calculation":scope['calculate']('sqrt(16) + 2^3'),"female_shell":scope['query_dataset']('What is the mean shell weight of female abalone?'),"blocked_expression":scope['calculate']("().__class__")}))
