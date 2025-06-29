#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ベンチマーク結果検証モジュール(validator.py)のテスト
"""

import unittest
from datetime import datetime

from benchmarks.core.types import BenchmarkResult, BenchmarkStatus
from benchmarks.core.validator import BenchmarkValidator, BenchmarkResultAnalyzer


def create_dummy_result(
    module: str,
    success: bool,
    avg_times: dict[str, float],
    timings: dict[str, list[float]] = None,
    error: str = None,
    status: BenchmarkStatus = "success",
) -> BenchmarkResult:
    """テスト用のダミーBenchmarkResultを作成するヘルパー関数"""
    if success and status == "success":
        status = "success"
    elif not success and status == "success":
        status = "failed"
        
    if timings is None:
        timings = {k: [v] for k, v in avg_times.items()}

    return BenchmarkResult(
        module=module,
        timestamp=datetime.now().isoformat(),
        success=success,
        error=error,
        status=status,
        timings=timings,
        average_times=avg_times,
        metrics={"has_njit": False, "has_cache": True},
    )


class TestBenchmarkValidator(unittest.TestCase):
    """BenchmarkValidatorのテスト"""

    def setUp(self):
        self.validator = BenchmarkValidator()
        self.successful_result = create_dummy_result(
            "test_module_ok", True, {"small": 0.1, "medium": 0.5, "large": 1.0}
        )
        self.failed_result = create_dummy_result(
            "test_module_fail", False, {}, error="Test Error", status="failed"
        )

    def test_validate_result_success(self):
        """正常な結果の検証テスト"""
        validation = self.validator.validate_result(self.successful_result)
        self.assertTrue(validation["is_valid"])
        self.assertEqual(len(validation["errors"]), 0)

    def test_validate_result_missing_field(self):
        """必須フィールドが欠けた結果の検証テスト"""
        invalid_result = self.successful_result.copy()
        del invalid_result["timings"]
        validation = self.validator.validate_result(invalid_result)
        self.assertFalse(validation["is_valid"])
        self.assertIn("Missing required field: timings", validation["errors"])

    def test_validate_result_high_variability(self):
        """結果のばらつきが大きい場合の警告テスト"""
        variable_timings = {"small": [0.1, 0.5, 0.9]} # CV > 0.5
        result = create_dummy_result(
            "variable_module", True, {"small": 0.5}, timings=variable_timings
        )
        validation = self.validator.validate_result(result)
        self.assertTrue(validation["is_valid"]) # 警告はエラーではない
        self.assertIn("high variability", validation["warnings"][0])

    def test_compare_results_improvement(self):
        """パフォーマンス改善時の比較テスト"""
        baseline = create_dummy_result("test", True, {"small": 0.2})
        current = create_dummy_result("test", True, {"small": 0.1})
        comparison = self.validator.compare_results(current, baseline)
        self.assertAlmostEqual(comparison["improvement_ratio"], 0.5) # 50%改善

    def test_compare_results_regression(self):
        """パフォーマンス悪化時の比較テスト"""
        baseline = create_dummy_result("test", True, {"small": 0.1})
        current = create_dummy_result("test", True, {"small": 0.15})
        comparison = self.validator.compare_results(current, baseline)
        self.assertAlmostEqual(comparison["improvement_ratio"], -0.5) # 50%悪化

    def test_detect_performance_regression(self):
        """パフォーマンス回帰の検出テスト"""
        baseline = {
            "fast_module": create_dummy_result("fast", True, {"small": 0.1}, timings={"small": [0.1]*5}),
            "slow_module": create_dummy_result("slow", True, {"small": 0.2}, timings={"small": [0.2]*5}),
        }
        current = {
            "fast_module": create_dummy_result("fast", True, {"small": 0.1}, timings={"small": [0.1]*5}),
            "slow_module": create_dummy_result("slow", True, {"small": 0.3}, timings={"small": [0.3]*5}), # 50%悪化
        }
        regressions = self.validator.detect_performance_regression(current, baseline)
        self.assertEqual(len(regressions), 1)
        self.assertIn("slow_module", regressions[0])
        self.assertIn("50.0% performance degradation", regressions[0])

    def test_detect_no_regression(self):
        """パフォーマンス回帰がない場合のテスト"""
        baseline = {
            "module1": create_dummy_result("m1", True, {"small": 0.1}, timings={"small": [0.1]*5}),
        }
        current = {
            "module1": create_dummy_result("m1", True, {"small": 0.105}, timings={"small": [0.105]*5}), # 5%の悪化は閾値(10%)以下
        }
        regressions = self.validator.detect_performance_regression(current, baseline)
        self.assertEqual(len(regressions), 0)


class TestBenchmarkResultAnalyzer(unittest.TestCase):
    """BenchmarkResultAnalyzerのテスト"""

    def setUp(self):
        self.analyzer = BenchmarkResultAnalyzer()
        self.results = {
            "fast_module": create_dummy_result("fast", True, {"small": 0.1, "medium": 0.2}),
            "slow_module": create_dummy_result("slow", True, {"small": 0.5, "medium": 1.0}),
            "failed_module": create_dummy_result("failed", False, {}),
        }

    def test_analyze_results(self):
        """結果分析の包括的テスト"""
        analysis = self.analyzer.analyze_results(self.results)
        self.assertIn("validation", analysis)
        self.assertIn("summary", analysis)
        self.assertIn("performance_ranking", analysis)
        self.assertIn("statistics", analysis)
        self.assertFalse(analysis["validation"]["is_valid"]) # failed_moduleがあるため

    def test_generate_summary(self):
        """サマリー生成のテスト"""
        summary = self.analyzer._generate_summary(self.results)
        self.assertEqual(summary["total_modules"], 3)
        self.assertEqual(summary["successful"], 2)
        self.assertEqual(summary["failed"], 1)
        self.assertAlmostEqual(summary["success_rate"], 2 / 3)
        self.assertAlmostEqual(summary["average_time"], (0.1 + 0.2 + 0.5 + 1.0) / 4)

    def test_rank_by_performance(self):
        """パフォーマンスランキングのテスト"""
        ranking = self.analyzer._rank_by_performance(self.results)
        self.assertEqual(len(ranking), 2)
        self.assertEqual(ranking[0][0], "fast_module") # 最速
        self.assertEqual(ranking[1][0], "slow_module") # 最遅


if __name__ == "__main__":
    unittest.main()
