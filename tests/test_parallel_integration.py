import os
import subprocess
import tempfile
import unittest
import ROOT


class TestParallelIntegration(unittest.TestCase):
    """Integration test validating multi-process parallel execution and hadd merging."""

    def setUp(self):
        ROOT.gROOT.SetBatch(True)
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_gen_zee_multiprocess_parallel(self):
        out_file = os.path.join(self.temp_dir.name, "Zee.parallel.root")
        chunk0 = os.path.join(self.temp_dir.name, "Zee.parallel.0.root")
        chunk1 = os.path.join(self.temp_dir.name, "Zee.parallel.1.root")

        # 4 events split across 2 worker processes
        cmd = f"gen_zee.py --nov 4 -nt 2 -o {out_file}"

        res = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            res.returncode,
            0,
            f"Parallel gen_zee.py failed with stderr:\n{res.stderr}\nstdout:\n{res.stdout}",
        )
        self.assertTrue(os.path.exists(out_file), "Merged output file was not created.")

        # Ensure temporary chunks were cleaned up
        self.assertFalse(os.path.exists(chunk0), "Intermediate chunk 0 was not cleaned up.")
        self.assertFalse(os.path.exists(chunk1), "Intermediate chunk 1 was not cleaned up.")

        # Validate entries in merged file
        f = ROOT.TFile.Open(out_file)
        self.assertIsNotNone(f)
        self.assertFalse(f.IsZombie(), "Merged ROOT file is corrupted.")
        tree = f.Get("particles")
        self.assertIsNotNone(tree, "Tree 'particles' not found in merged file.")
        self.assertEqual(tree.GetEntries(), 4, f"Expected 4 events merged, got {tree.GetEntries()}")
        f.Close()


if __name__ == "__main__":
    unittest.main()
