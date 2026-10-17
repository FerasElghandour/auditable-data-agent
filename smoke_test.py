import math
import json
import re
import datetime
import pandas as pd
from notebook_units import definitions
df=pd.DataFrame({'Sex':['F','F','M'], 'Rings':[10,12,8], 'Shell_weight':[.2,.4,.8]})
scope={'math':math,'json':json,'re':re,'datetime':datetime,'DF':df,'DF_COLS_LOWER':{c.lower():c for c in df},'TOOL_REGISTRY':{}}
definitions(['register_tool','calculate','query_dataset'],scope)
assert scope['calculate']('sqrt(16) + 2^3')=='Result: 12.0'
for expression in ["().__class__", "__import__('os')", '2**999', '1/0', '9'*201]:
    assert scope['calculate'](expression).startswith('Error'),expression
out=scope['query_dataset']('What is the mean shell weight of female abalone?')
assert 'Shell_weight' in out and '0.3' in out,out
assert '0.3' in scope['query_dataset']('mean shell_weight for female')
print('Data agent: bounded arithmetic, code-execution rejection, and column-resolution regressions passed.')
