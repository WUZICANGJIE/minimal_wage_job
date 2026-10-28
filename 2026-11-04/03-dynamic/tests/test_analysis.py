"""実データと二期モデルの再現テスト（unittest、追加依存なし）。"""
import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

class DataTest(unittest.TestCase):
    def test_primary_statistic_and_data_invariants(self):
        import analysis as a
        panel, policy, audit = a.load_data()
        self.assertTrue(all(audit['checks'].values()))
        self.assertEqual(policy.group.value_counts().to_dict(), {'early':20,'late':14,'excluded':13})
        result, d = a.contrast(panel, policy, '2025-11', 9)
        # Parent's independent openpyxl/stdlib result, not used in computation.
        self.assertAlmostEqual(result['estimate'], -1.55541045199039, places=10)
        self.assertEqual((len(d), panel.pref.nunique()), (34,47))
        self.assertAlmostEqual(result['estimate'], d.loc[d.early==1,'d'].mean()-d.loc[d.early==0,'d'].mean(),places=12)

    def test_outputs_timing_and_numerical_validation(self):
        import analysis as a
        result=a.run_all()
        self.assertTrue(all(result['data']['checks'].values()))
        self.assertTrue(result['model']['all_kkt_pass'])
        self.assertLess(result['model']['max_derivative_error'],1e-7)
        import pandas as pd
        t=pd.read_csv(a.HERE/'results'/'timing_support.csv')
        nov=t[(t.month=='2025-11')&(t.group=='late')].iloc[0]
        dec=t[(t.month=='2025-12')&(t.group=='late')].iloc[0]
        self.assertEqual((nov.full,nov.partial,nov.untreated),(0,0,14))
        self.assertEqual((dec.full,dec.partial,dec.untreated),(7,1,6))
        self.assertTrue((t[t.month=='2026-04']['untreated']==0).all())

class ModelTest(unittest.TestCase):
    def test_two_period_future_choice_and_derivatives(self):
        import analysis as a
        p=dict(a=10.,b=1.,q=.8,r=.8,beta=.95,kappa=2.,c=.2,L0=3.)
        v,L,H,g=a.solve_model(4.,4.,**p)
        self.assertTrue(np.all(v>0))
        self.assertTrue(np.all(np.linalg.eigvalsh(H)>0))
        np.testing.assert_allclose(H@v,g,atol=1e-11)
        J=a.wage_derivatives(**p)
        eps=1e-5
        for j in range(2):
            w=np.array([4.,4.]); w[j]+=eps
            vp=a.solve_model(*w,**p)[0]
            w[j]-=2*eps
            vm=a.solve_model(*w,**p)[0]
            np.testing.assert_allclose((vp-vm)/(2*eps),J[:,j],atol=1e-8)
        self.assertLess(J[0,0],0); self.assertLess(J[0,1],0)
        self.assertGreater(J[1,0],0); self.assertLess(J[1,1],0)
        # Early has high current wage; both face same later wage.
        early=a.solve_model(4.,4.,**p)[0]
        late=a.solve_model(3.5,4.,**p)[0]
        self.assertLess(early[0],late[0]); self.assertGreater(early[1],late[1])
        for k in [0.]:
            p['kappa']=k
            self.assertAlmostEqual(a.wage_derivatives(**p)[0,1],0.,places=12)
        corner=a.solve_model(100.,100.,**p)[0]
        np.testing.assert_array_equal(corner,np.zeros(2))

if __name__ == '__main__':
    unittest.main(verbosity=2)
