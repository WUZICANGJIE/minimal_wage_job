"""再計算とモデルの回帰テスト。python -m unittest discover -s .../tests -v"""
import importlib.util
from pathlib import Path
import unittest
import numpy as np
from scipy import stats

HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('basic_analysis',HERE/'analysis.py')
a=importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class AnalysisTest(unittest.TestCase):
    def test_welch_matches_independent_scipy_interval(self):
        x=np.array([1.,4.,-2.,5.,8.])
        y=np.array([3.,-1.,7.])
        r=a.welch_difference(x,y)
        t=stats.ttest_ind(x,y,equal_var=False)
        ci=t.confidence_interval(.95)
        self.assertAlmostEqual(r['ci_low'],ci.low)
        self.assertAlmostEqual(r['ci_high'],ci.high)
        self.assertAlmostEqual(r['p_one_sided_negative'],stats.ttest_ind(x,y,equal_var=False,alternative='less').pvalue)

    def test_group_order_reverses_sign_not_standard_error(self):
        x,y=[1,3,6,8],[2,4,9]
        r,s=a.welch_difference(x,y),a.welch_difference(y,x)
        self.assertAlmostEqual(r['delta'],-s['delta'])
        self.assertAlmostEqual(r['se'],s['se'])
        self.assertAlmostEqual(r['ci_low'],-s['ci_high'])

    def test_data_parser_months_national_and_year_headers(self):
        import pandas as pd
        sheets=pd.ExcelFile(a.RAW/a.FILES[0]).sheet_names
        part=a.load_t12(a.RAW/a.FILES[0],sheets[2])
        self.assertEqual(len(part),164)
        self.assertEqual(str(part.index[0]),'2013-01')
        self.assertEqual(str(part.index[-1]),'2026-08')
        p,cols=a.load_policy(a.RAW/a.FILES[1],part.columns.drop('全国').tolist())
        self.assertEqual(p.group.value_counts().to_dict(),{a.EARLY:20,a.LATE:14,a.MIDDLE:13})
        self.assertEqual(cols['2025']['label'],'令和７年度')
        self.assertEqual(p.loc['東京都','mw_2025'],1226)
        self.assertEqual(str(p.loc['秋田県','effective_2025'].date()),'2026-03-31')

    def test_model_foc_and_elasticity_grid(self):
        self.assertEqual(a.verify_model()['grid_cases'],9)

    def test_replacement_not_employment(self):
        self.assertEqual(a.new_vacancies(100,100,separation=.1,fill=1.,channel=1.),10.)
        self.assertEqual(a.new_vacancies(100,100,separation=0,fill=1.,channel=1.),0.)
        self.assertEqual(a.new_vacancies(80,100,separation=.1),0.)

    def test_invalid_parameters_rejected(self):
        for kwargs in [dict(w=0),dict(w=-1),dict(w=1,beta=1),dict(w=1,beta=0)]:
            with self.assertRaises(ValueError): a.desired_employment(**kwargs)
        for kwargs in [dict(fill=0),dict(channel=1.1),dict(separation=-.1)]:
            with self.assertRaises(ValueError): a.new_vacancies(100,100,**kwargs)


if __name__=='__main__': unittest.main()
