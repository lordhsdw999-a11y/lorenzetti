import unittest
import math
import ROOT


class TestSpacePointEDM(unittest.TestCase):
    """Unit tests for xAOD::SpacePoint EDM object."""

    @classmethod
    def setUpClass(cls):
        ROOT.gROOT.SetBatch(True)
        ROOT.gSystem.Load("liblorenzetti")

    def test_spacepoint_instantiation_and_coordinates(self):
        sp = ROOT.xAOD.SpacePoint()
        sp.setX(120.0)
        sp.setY(160.0)
        sp.setZ(450.0)
        sp.setPhi(math.atan2(160.0, 120.0))
        sp.setDeltaZ(0.05)
        sp.setDeltaPhi(0.01)
        sp.setHash(888222)

        self.assertAlmostEqual(sp.x(), 120.0, places=1)
        self.assertAlmostEqual(sp.y(), 160.0, places=1)
        self.assertAlmostEqual(sp.z(), 450.0, places=1)
        self.assertAlmostEqual(math.sqrt(sp.x()**2 + sp.y()**2), 200.0, places=1)
        self.assertAlmostEqual(sp.deltaZ(), 0.05, places=4)
        self.assertAlmostEqual(sp.deltaPhi(), 0.01, places=4)
        self.assertEqual(sp.hash(), 888222)

        # Deposit energy
        sp.edep(0, 0.42)
        self.assertAlmostEqual(sp.edep(0), 0.42, places=2)

    def test_spacepoint_t_struct(self):
        t_obj = ROOT.xAOD.SpacePoint_t()
        t_obj.x = 50.0
        t_obj.y = 75.0
        t_obj.z = 200.0
        t_obj.r = 90.14
        t_obj.eta = 1.52
        t_obj.phi = 0.98
        t_obj.hash = 777111

        self.assertAlmostEqual(t_obj.x, 50.0, places=1)
        self.assertAlmostEqual(t_obj.y, 75.0, places=1)
        self.assertAlmostEqual(t_obj.z, 200.0, places=1)
        self.assertAlmostEqual(t_obj.eta, 1.52, places=2)
        self.assertEqual(t_obj.hash, 777111)


if __name__ == "__main__":
    unittest.main()
