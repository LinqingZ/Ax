# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import numpy as np
from ax.benchmark.benchmark import (
    benchmark_full_run,
    benchmark_replication,
    benchmark_test,
)
from ax.utils.common.testutils import TestCase
from ax.utils.testing.benchmark_stubs import (
    get_multi_objective_benchmark_problem,
    get_single_objective_benchmark_problem,
    get_sobol_benchmark_method,
    get_sobol_gpei_benchmark_method,
)
from ax.utils.testing.mock import fast_botorch_optimize


class TestBenchmark(TestCase):
    def test_replication_synthetic(self):
        problem = get_single_objective_benchmark_problem()

        res = benchmark_replication(
            problem=problem, method=get_sobol_benchmark_method(), seed=0
        )

        self.assertEqual(
            problem.num_trials,
            len(res.experiment.trials),
        )

        self.assertTrue(np.all(res.score_trace <= 100))

    def test_replication_moo(self):
        problem = get_multi_objective_benchmark_problem()

        res = benchmark_replication(
            problem=problem, method=get_sobol_benchmark_method(), seed=0
        )

        self.assertEqual(
            problem.num_trials,
            len(res.experiment.trials),
        )
        self.assertEqual(
            problem.num_trials * 2,
            len(res.experiment.fetch_data().df),
        )

        self.assertTrue(np.all(res.score_trace <= 100))

    def test_test(self):
        problem = get_single_objective_benchmark_problem()
        agg = benchmark_test(
            problem=problem,
            method=get_sobol_benchmark_method(),
            seeds=(0, 1),
        )

        self.assertEqual(len(agg.results), 2)
        self.assertTrue(
            all(
                len(result.experiment.trials) == problem.num_trials
                for result in agg.results
            ),
            "All experiments must have 4 trials",
        )

        for col in ["mean", "P10", "P25", "P50", "P75", "P90"]:
            self.assertTrue((agg.score_trace[col] <= 100).all())

    @fast_botorch_optimize
    def test_full_run(self):
        aggs = benchmark_full_run(
            problems=[get_single_objective_benchmark_problem()],
            methods=[get_sobol_benchmark_method(), get_sobol_gpei_benchmark_method()],
            seeds=(0, 1),
        )

        self.assertEqual(len(aggs), 2)

        for agg in aggs:
            for col in ["mean", "P10", "P25", "P50", "P75", "P90"]:
                self.assertTrue((agg.score_trace[col] <= 100).all())
