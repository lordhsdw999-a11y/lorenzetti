import os
import subprocess
import tempfile
import unittest
import ROOT


class TestFullChainIntegration(unittest.TestCase):
    """Integration test executing event generation pipeline and validating ROOT outputs."""

    def setUp(self):
        ROOT.gROOT.SetBatch(True)
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_gen_zee_single_process(self):
        out_file = os.path.join(self.temp_dir.name, "Zee.EVT.root")
        cmd = f"gen_zee.py --nov 2 -nt 1 -o {out_file}"

        res = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            res.returncode,
            0,
            f"gen_zee.py failed with stderr:\n{res.stderr}\nstdout:\n{res.stdout}",
        )
        self.assertTrue(os.path.exists(out_file), f"Output ROOT file {out_file} was not generated.")

        # Validate with ROOT
        f = ROOT.TFile.Open(out_file)
        self.assertIsNotNone(f)
        self.assertFalse(f.IsZombie(), "Generated ROOT file is corrupted (Zombie).")

        tree = f.Get("particles")
        self.assertIsNotNone(tree, "Tree 'particles' not found in generated file.")
        self.assertEqual(tree.GetEntries(), 2, f"Expected 2 events, found {tree.GetEntries()}")
        f.Close()


if __name__ == "__main__":
    unittest.main()
