"""Run from 02-composition: python -m unittest discover -s tests -v."""
import unittest
import numpy as np
import pandas as pd
from analysis import log_yoy
import analysis


class StatisticsTests(unittest.TestCase):
    def test_contrast_preserves_county_equal_weights(self):
        self.assertTrue(hasattr(analysis, 'contrast'), 'contrast is not implemented')
        d = pd.Series([1., 3., 5., 7.], index=['a', 'b', 'c', 'd'])
        group = pd.Series(['early', 'early', 'late', 'late'], index=d.index)
        got = analysis.contrast(d, group)
        self.assertEqual(got['estimate'], -4.)
        self.assertEqual(got['n_early'], 2)
        self.assertAlmostEqual(got['se'], np.sqrt(2))

    def test_log_yoy_uses_twelve_months(self):
        index = pd.period_range('2024-01', '2025-02', freq='M')
        x = pd.DataFrame({'A': np.arange(1, 15, dtype=float)}, index=index)
        got = log_yoy(x)
        self.assertTrue(got.iloc[:12].isna().all().all())
        self.assertAlmostEqual(got.iloc[12, 0], 100*np.log(13))
        self.assertAlmostEqual(got.iloc[13, 0], 100*np.log(7))


class ModelTests(unittest.TestCase):
    def test_model_ratio_and_common_cost_scale(self):
        self.assertTrue(hasattr(analysis, 'ces_choice'), 'CES choice is not implemented')
        for sigma in [.05, .5, 1., 2., 8.]:
            base = analysis.ces_choice(1., 1., sigma=sigma, beta=.5)
            shock = analysis.ces_choice(1.1, 1., sigma=sigma, beta=.5)
            self.assertAlmostEqual(shock['P']/shock['N'], (1/1.1)**sigma, places=9)
            common = analysis.ces_choice(1.1, 1.1, sigma=sigma, beta=.5)
            self.assertAlmostEqual(common['P']/base['P'], 1.1**-2, places=9)
            self.assertAlmostEqual(common['N']/base['N'], 1.1**-2, places=9)
            self.assertAlmostEqual(base['cost'], base['C']*base['Z'], places=9)

    def test_nonpart_can_rise_or_fall(self):
        self.assertTrue(hasattr(analysis, 'ces_choice'), 'CES choice is not implemented')
        for beta, expected_sign in [(.2, 1), (.7, -1)]:
            b = analysis.ces_choice(1, 1, sigma=2, beta=beta)
            s = analysis.ces_choice(1.1, 1, sigma=2, beta=beta)
            self.assertEqual(np.sign(s['N']-b['N']), expected_sign)

    def test_model_domain_and_yoy_validation(self):
        self.assertTrue(hasattr(analysis, 'ces_choice'), 'CES choice is not implemented')
        with self.assertRaises(ValueError):
            analysis.ces_choice(0, 1)
        with self.assertRaises(ValueError):
            analysis.ces_choice(1, 1, beta=1)
        bad = pd.DataFrame({'a': [1., 2.]}, index=pd.PeriodIndex(['2024-01','2024-03'],freq='M'))
        with self.assertRaises(ValueError):
            log_yoy(bad)


if __name__ == '__main__':
    unittest.main()
