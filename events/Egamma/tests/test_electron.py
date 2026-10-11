import unittest
import ROOT


class TestElectronEDM(unittest.TestCase):
    """Unit tests for xAOD::Electron EDM object."""

    @classmethod
    def setUpClass(cls):
        ROOT.gROOT.SetBatch(True)
        ROOT.gSystem.Load("liblorenzetti")

    def test_electron_instantiation_and_pid(self):
        el = ROOT.xAOD.Electron()
        el.setEta(1.25)
        el.setPhi(-0.45)
        el.setE(45000.0)
        el.setEt(45000.0 / ROOT.std.cosh(1.25))

        self.assertAlmostEqual(el.eta(), 1.25, places=4)
        self.assertAlmostEqual(el.phi(), -0.45, places=4)
        self.assertAlmostEqual(el.e(), 45000.0, places=1)
        self.assertGreater(el.et(), 0.0)
        self.assertFalse(el.isForward())

        # PID flags
        el.setIsTight(True)
        el.setIsMedium(True)
        el.setIsLoose(True)
        el.setIsVeryLoose(True)
        self.assertTrue(el.isTight())
        self.assertTrue(el.isMedium())
        self.assertTrue(el.isLoose())
        self.assertTrue(el.isVeryLoose())

    def test_forward_electron(self):
        fwd_el = ROOT.xAOD.Electron()
        fwd_el.setEta(2.85)
        self.assertTrue(fwd_el.isForward())

    def test_electron_t_struct(self):
        t_obj = ROOT.xAOD.Electron_t()
        t_obj.e = 35000.0
        t_obj.et = 28000.0
        t_obj.eta = 0.85
        t_obj.phi = 1.10
        t_obj.isTight = True
        t_obj.isMedium = True
        t_obj.isLoose = True
        t_obj.cluster_key_hash = 998877
        t_obj.cluster_index = 0

        self.assertAlmostEqual(t_obj.e, 35000.0, places=1)
        self.assertAlmostEqual(t_obj.et, 28000.0, places=1)
        self.assertAlmostEqual(t_obj.eta, 0.85, places=4)
        self.assertTrue(t_obj.isTight)
        self.assertEqual(t_obj.cluster_key_hash, 998877)


if __name__ == "__main__":
    unittest.main()
