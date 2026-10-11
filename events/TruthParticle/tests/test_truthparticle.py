import unittest
import ROOT


class TestTruthParticleEDM(unittest.TestCase):
    """Unit tests for xAOD::TruthParticle EDM object."""

    @classmethod
    def setUpClass(cls):
        ROOT.gROOT.SetBatch(True)
        ROOT.gSystem.Load("liblorenzetti")

    def test_truthparticle_instantiation_and_kinematics(self):
        # Electron pdgid = 11, seedid = 1
        part = ROOT.xAOD.TruthParticle(
            11, 1,
            45000.0, 35000.0, 0.75, 1.40,
            25000.0, 24000.0, 28000.0,
            0.0, 0.0, 0.0
        )
        self.assertEqual(part.pdgid(), 11)
        self.assertEqual(part.seedid(), 1)
        self.assertAlmostEqual(part.e(), 45000.0, places=1)
        self.assertAlmostEqual(part.et(), 35000.0, places=1)
        self.assertAlmostEqual(part.eta(), 0.75, places=4)
        self.assertAlmostEqual(part.phi(), 1.40, places=4)
        self.assertAlmostEqual(part.px(), 25000.0, places=1)
        self.assertAlmostEqual(part.py(), 24000.0, places=1)
        self.assertAlmostEqual(part.pz(), 28000.0, places=1)

    def test_truthparticle_t_struct(self):
        t_obj = ROOT.xAOD.TruthParticle_t()
        t_obj.pdgid = -11  # Positron
        t_obj.seedid = 2
        t_obj.e = 50000.0
        t_obj.et = 40000.0
        t_obj.eta = -0.65
        t_obj.phi = -2.10
        t_obj.seed_key_hash = 123456
        t_obj.seed_index = 0

        self.assertEqual(t_obj.pdgid, -11)
        self.assertEqual(t_obj.seedid, 2)
        self.assertAlmostEqual(t_obj.e, 50000.0, places=1)
        self.assertAlmostEqual(t_obj.eta, -0.65, places=4)
        self.assertEqual(t_obj.seed_key_hash, 123456)


if __name__ == "__main__":
    unittest.main()
