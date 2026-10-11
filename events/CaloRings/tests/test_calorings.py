import unittest
import ROOT


class TestCaloRingsEDM(unittest.TestCase):
    """Unit tests for xAOD::CaloRings EDM object."""

    @classmethod
    def setUpClass(cls):
        ROOT.gROOT.SetBatch(True)
        ROOT.gSystem.Load("liblorenzetti")

    def test_calorings_instantiation_and_values(self):
        rings = ROOT.xAOD.CaloRings()
        rings.setEta(0.30)
        rings.setPhi(-1.10)

        ring_vec = ROOT.std.vector('float')()
        for val in [12000.0, 8500.0, 3200.0, 1100.0]:
            ring_vec.push_back(val)
        rings.setRings(ring_vec)

        self.assertAlmostEqual(rings.eta(), 0.30, places=4)
        self.assertAlmostEqual(rings.phi(), -1.10, places=4)
        self.assertEqual(len(rings.rings()), 4)
        self.assertAlmostEqual(rings.rings()[0], 12000.0, places=1)
        self.assertAlmostEqual(rings.rings()[1], 8500.0, places=1)

    def test_calorings_t_struct(self):
        t_obj = ROOT.xAOD.CaloRings_t()
        t_obj.eta = 0.55
        t_obj.phi = 1.45
        t_obj.cluster_key_hash = 123456789
        t_obj.cluster_index = 2

        self.assertAlmostEqual(t_obj.eta, 0.55, places=4)
        self.assertAlmostEqual(t_obj.phi, 1.45, places=4)
        self.assertEqual(t_obj.cluster_key_hash, 123456789)
        self.assertEqual(t_obj.cluster_index, 2)


if __name__ == "__main__":
    unittest.main()
