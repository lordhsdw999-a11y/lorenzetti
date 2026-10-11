import unittest
import tempfile
from pathlib import Path
from GaugiKernel.Parallel import ParallelJob, FileParallelJob, append_index_to_file


class TestParallelJobPlanning(unittest.TestCase):
    """Unit tests for ParallelJob event partitioning and plan generation."""

    def test_append_index_to_file(self):
        self.assertEqual(append_index_to_file("output.root", 0), "output.0.root")
        self.assertEqual(append_index_to_file("dir/data.root", 3), "dir/data.3.root")
        self.assertEqual(append_index_to_file("no_ext", 1), "no_ext.1")

    def test_build_plan_even_split(self):
        job = ParallelJob(
            output_file="zee.root",
            seed=42,
            number_of_threads=4,
            number_of_events=100,
        )
        plan = job.build_plan()
        self.assertEqual(len(plan), 4)

        expected_files = ["zee.0.root", "zee.1.root", "zee.2.root", "zee.3.root"]
        self.assertEqual(list(plan.keys()), expected_files)

        total_events = 0
        seeds = set()
        for idx, (f, cfg) in enumerate(plan.items()):
            self.assertEqual(len(cfg["events"]), 25)
            self.assertIn("seed", cfg)
            self.assertIn("event_start", cfg)
            seeds.add(cfg["seed"])
            total_events += len(cfg["events"])

        self.assertEqual(total_events, 100)
        # Seeds must be unique
        self.assertEqual(len(seeds), 4)

    def test_build_plan_uneven_split(self):
        job = ParallelJob(
            output_file="zee.root",
            seed=100,
            number_of_threads=3,
            number_of_events=10,
        )
        plan = job.build_plan()
        # ceil(10 / 3) = 4 per job -> chunks: [4, 4, 2] -> 3 jobs
        self.assertEqual(len(plan), 3)

        chunk_sizes = [len(cfg["events"]) for cfg in plan.values()]
        self.assertEqual(chunk_sizes, [4, 4, 2])
        self.assertEqual(sum(chunk_sizes), 10)

    def test_build_plan_explicit_event_numbers(self):
        job = ParallelJob(
            output_file="zee.root",
            seed=512,
            number_of_threads=2,
            event_numbers="10, 20, 30, 40, 50",
        )
        plan = job.build_plan()
        self.assertEqual(len(plan), 2)
        events_collected = []
        for cfg in plan.values():
            events_collected.extend(cfg["events"])
        self.assertEqual(events_collected, [10, 20, 30, 40, 50])

    def test_build_plan_single_thread(self):
        job = ParallelJob(
            output_file="single.root",
            seed=999,
            number_of_threads=1,
            number_of_events=50,
        )
        plan = job.build_plan()
        self.assertEqual(len(plan), 1)
        self.assertIn("single.0.root", plan)
        self.assertEqual(len(plan["single.0.root"]["events"]), 50)


class TestFileParallelJobPlanning(unittest.TestCase):
    """Unit tests for FileParallelJob batch partitioning and plan generation."""

    def test_discover_files_single_file(self):
        job = FileParallelJob(
            input_path="data/test.EVT.root",
            output_path="data/test.HIT.root",
        )
        files = job.discover_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0], Path("data/test.EVT.root"))

    def test_threads_and_concurrency_calculation(self):
        # 40 cores, 4 threads per job -> 10 workers
        job = FileParallelJob(
            input_path="dummy.root",
            output_path="out.root",
            number_of_threads=40,
            threads_per_job=4,
        )
        tpj, workers = job.get_threads_and_concurrency(total_files=10)
        self.assertEqual(tpj, 4)
        self.assertEqual(workers, 10)

        # 40 cores, single file -> uses 40 threads for that single file
        job_single = FileParallelJob(
            input_path="dummy.root",
            output_path="out.root",
            number_of_threads=40,
            threads_per_job=-1,
        )
        tpj_single, workers_single = job_single.get_threads_and_concurrency(total_files=1)
        self.assertEqual(tpj_single, 40)
        self.assertEqual(workers_single, 1)

    def test_build_plan_directory(self):
        with tempfile.TemporaryDirectory() as in_dir, tempfile.TemporaryDirectory() as out_dir:
            in_p = Path(in_dir)
            out_p = Path(out_dir)

            # Create mock input files
            f1 = in_p / "sample.0.EVT.root"
            f2 = in_p / "sample.1.EVT.root"
            f1.touch()
            f2.touch()

            job = FileParallelJob(
                input_path=in_dir,
                output_path=out_dir,
                number_of_threads=8,
                threads_per_job=4,
                file_pattern="*.EVT.root",
            )
            plan = job.build_plan()
            self.assertEqual(len(plan), 2)

            expected_out1 = str(out_p / "sample.0.HIT.root")
            expected_out2 = str(out_p / "sample.1.HIT.root")

            self.assertIn(expected_out1, plan)
            self.assertIn(expected_out2, plan)
            self.assertEqual(plan[expected_out1]["threads_per_job"], 4)
            self.assertEqual(plan[expected_out2]["threads_per_job"], 4)


class TestCliFlagExtraction(unittest.TestCase):
    """Unit tests for automatic Typer CLI option resolution."""

    def test_extract_cli_flags(self):
        import typer
        from typing_extensions import Annotated
        from GaugiKernel.Parallel import _extract_cli_flags, file_parallel_job

        @file_parallel_job
        def dummy_worker(
            input_file: str,
            output_file: str,
            number_of_threads: int = 1,
            logging_level: Annotated[str, typer.Option("-l", "--output-level")] = "INFO",
            enable_feature: Annotated[bool, typer.Option("--enable-feature/--disable-feature")] = False,
            simple_flag: Annotated[bool, typer.Option("--simple-flag")] = False,
        ):
            pass

        flags, neg_flags = _extract_cli_flags(dummy_worker.app)
        self.assertEqual(flags["logging_level"], "--output-level")
        self.assertEqual(flags["enable_feature"], "--enable-feature")
        self.assertEqual(neg_flags["enable_feature"], "--disable-feature")
        self.assertEqual(flags["simple_flag"], "--simple-flag")
        self.assertNotIn("simple_flag", neg_flags)


if __name__ == "__main__":
    unittest.main()
