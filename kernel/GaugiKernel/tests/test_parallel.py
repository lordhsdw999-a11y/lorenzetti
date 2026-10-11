import unittest
from GaugiKernel.Parallel import ParallelJob, append_index_to_file


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


if __name__ == "__main__":
    unittest.main()
