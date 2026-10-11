import unittest
import math
import ROOT


class TestCaloCluster(unittest.TestCase):
    """Unit tests for xAOD::CaloCluster and related EDM classes."""

    @classmethod
    def setUpClass(cls):
        # Ensure ROOT dictionary for Lorenzetti is loaded
        ROOT.gROOT.SetBatch(True)
        ROOT.gSystem.Load("liblorenzetti")
        import CaloCluster

    def test_default_instantiation(self):
        cluster = ROOT.xAOD.CaloCluster()
        self.assertIsNotNone(cluster)
        cluster.setEta(0.35)
        cluster.setPhi(1.20)
        cluster.setE(25000.0)
        cluster.setEt(25000.0 / math.cosh(0.35))

        self.assertAlmostEqual(cluster.eta(), 0.35, places=4)
        self.assertAlmostEqual(cluster.phi(), 1.20, places=4)
        self.assertAlmostEqual(cluster.e(), 25000.0, places=1)
        self.assertGreater(cluster.et(), 0.0)

    def test_parameterized_instantiation(self):
        # CaloCluster(emaxs2, eta, phi, deta, dphi)
        cluster = ROOT.xAOD.CaloCluster(18000.0, 0.45, -0.80, 0.2, 0.2)
        self.assertAlmostEqual(cluster.eta(), 0.45, places=4)
        self.assertAlmostEqual(cluster.phi(), -0.80, places=4)
        self.assertAlmostEqual(cluster.deltaEta(), 0.2, places=4)
        self.assertAlmostEqual(cluster.deltaPhi(), 0.2, places=4)

    def test_shower_shapes_and_moments(self):
        cluster = ROOT.xAOD.CaloCluster()
        cluster.setReta(0.94)
        cluster.setRphi(0.88)
        cluster.setRhad(0.015)
        cluster.setWeta2(0.012)
        cluster.setEratio(0.82)
        cluster.setSecondR(15.4)
        cluster.setSecondLambda(28.2)
        cluster.setLateralMom(0.35)
        cluster.setLongitudinalMom(0.72)

        self.assertAlmostEqual(cluster.reta(), 0.94, places=4)
        self.assertAlmostEqual(cluster.rphi(), 0.88, places=4)
        self.assertAlmostEqual(cluster.rhad(), 0.015, places=4)
        self.assertAlmostEqual(cluster.weta2(), 0.012, places=4)
        self.assertAlmostEqual(cluster.eratio(), 0.82, places=4)
        self.assertAlmostEqual(cluster.secondR(), 15.4, places=4)
        self.assertAlmostEqual(cluster.secondLambda(), 28.2, places=4)
        self.assertAlmostEqual(cluster.lateralMom(), 0.35, places=4)
        self.assertAlmostEqual(cluster.longitudinalMom(), 0.72, places=4)

    def test_calocluster_t_struct(self):
        # Test flat serialization struct
        t_obj = ROOT.xAOD.CaloCluster_t()
        t_obj.e = 32000.0
        t_obj.eta = -0.15
        t_obj.phi = 2.45
        t_obj.reta = 0.96
        self.assertAlmostEqual(t_obj.e, 32000.0, places=1)
        self.assertAlmostEqual(t_obj.eta, -0.15, places=4)
        self.assertAlmostEqual(t_obj.phi, 2.45, places=4)
        self.assertAlmostEqual(t_obj.reta, 0.96, places=4)


if __name__ == "__main__":
    unittest.main()
