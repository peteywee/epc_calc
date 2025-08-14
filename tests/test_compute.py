import unittest, json
import epc_model as epc

class TestEPC(unittest.TestCase):
    def test_example_numbers(self):
        model = {
            "modules": [
                {"name":"A","weight":0.60,"conv":0.030,"aov":45.0,"rate":0.030},
                {"name":"B","weight":0.25,"conv":0.030,"aov":90.0,"rate":0.045},
                {"name":"C","weight":0.15,"conv":0.025,"aov":150.0,"rate":0.040}
            ],
            "bounties":[{"name":"B1","attach":0.008,"payout":3.0},
                        {"name":"B2","attach":0.002,"payout":10.0}],
            "bonuses":[{"name":"Q1","order_share":0.10,"payout":3.0}]
        }
        res = epc.compute(model, margin=0.30, strict=True)
        self.assertAlmostEqual(res["totals"]["epc"], 0.12995, places=5)
        self.assertAlmostEqual(res["components"]["epc_products"], 0.077175, places=6)
        self.assertAlmostEqual(res["components"]["epc_bounties"], 0.044000, places=6)
        self.assertAlmostEqual(res["components"]["epc_bonuses"], 0.008775, places=6)

if __name__ == "__main__":
    unittest.main()
