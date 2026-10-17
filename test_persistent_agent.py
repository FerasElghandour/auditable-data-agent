import unittest,tempfile,sqlite3
from pathlib import Path
import pandas as pd
from agent import DataAgent
class PersistentAgent(unittest.TestCase):
 def test_exact_cache_keys_and_restart(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'data.csv';db=Path(tmp)/'audit.sqlite';pd.DataFrame({'Sex':['F','M'],'Rings':[10,12],'Shell_weight':[.2,.4]}).to_csv(path,index=False)
   a=DataAgent(path,str(db));prefix='Calculate 1'+' '*80
   self.assertIn('2',a.run(prefix+'+1')['observation']);self.assertIn('3',a.run(prefix+'+2')['observation']);self.assertFalse(a.run('mean rings')['cached']);self.assertTrue(a.verify_audit());a.close()
   b=DataAgent(path,str(db));self.assertTrue(b.run('mean rings')['cached']);self.assertIn('OUT_OF_SCOPE',b.run('financial advice mean rings')['observation']);self.assertTrue(b.verify_audit())
   with self.assertRaises(sqlite3.IntegrityError):b.db.execute('DELETE FROM audit')
   b.close()
if __name__=='__main__':unittest.main()
