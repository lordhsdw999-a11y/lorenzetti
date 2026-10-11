import unittest
import ROOT


class TestEventInfoEDM(unittest.TestCase):
    """Unit tests for xAOD::EventInfo and xAOD::Seed EDM objects."""

    @classmethod
    def setUpClass(cls):
        ROOT.gROOT.SetBatch(True)
        ROOT.gSystem.Load("liblorenzetti")

    def test_eventinfo_instantiation_and_properties(self):
        evt = ROOT.xAOD.EventInfo()
        evt.setRunNumber(310000)
        evt.setEventNumber(42)
        evt.setTotalEnergy(13000.0)
        evt.setAvgmu(35.5)
        evt.setTotmu(40.2)

        self.assertEqual(evt.runNumber(), 310000)
        self.assertEqual(evt.eventNumber(), 42)
        self.assertAlmostEqual(evt.totalEnergy(), 13000.0, places=1)
        self.assertAlmostEqual(evt.avgmu(), 35.5, places=2)
        self.assertAlmostEqual(evt.totmu(), 40.2, places=2)
        self.assertAlmostEqual(evt.averageInteractionsPerCrossing(), 35.5, places=2)
        self.assertAlmostEqual(evt.totalInteractionsPerCrossing(), 40.2, places=2)

    def test_seed_instantiation_and_properties(self):
        seed = ROOT.xAOD.Seed(1, 45000.0, 32000.0, 0.45, -1.25)
        self.assertEqual(seed.id(), 1)
        self.assertAlmostEqual(seed.e(), 45000.0, places=1)
        self.assertAlmostEqual(seed.et(), 32000.0, places=1)
        self.assertAlmostEqual(seed.eta(), 0.45, places=4)
        self.assertAlmostEqual(seed.phi(), -1.25, places=4)

    def test_eventinfo_t_struct(self):
        t_obj = ROOT.xAOD.EventInfo_t()
        t_obj.runNumber = 300000
        t_obj.eventNumber = 101
        t_obj.totalEnergy = 13600.0
        t_obj.avgmu = 50.0

        self.assertEqual(t_obj.runNumber, 300000)
        self.assertEqual(t_obj.eventNumber, 101)
        self.assertAlmostEqual(t_obj.totalEnergy, 13600.0, places=1)
        self.assertAlmostEqual(t_obj.avgmu, 50.0, places=1)

    def test_seed_t_struct(self):
        t_seed = ROOT.xAOD.Seed_t()
        t_seed.id = 5
        t_seed.e = 25000.0
        t_seed.et = 20000.0
        t_seed.eta = -0.30
        t_seed.phi = 0.80

        self.assertEqual(t_seed.id, 5)
        self.assertAlmostEqual(t_seed.e, 25000.0, places=1)
        self.assertAlmostEqual(t_seed.et, 20000.0, places=1)
        self.assertAlmostEqual(t_seed.eta, -0.30, places=4)
        self.assertAlmostEqual(t_seed.phi, 0.80, places=4)


if __name__ == "__main__":
    unittest.main()
