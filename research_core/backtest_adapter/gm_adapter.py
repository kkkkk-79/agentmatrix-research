from __future__ import annotations

import ast
import os
from pathlib import Path

from contracts.attribution import AttributionReport, AttributionSummary
from contracts.backtest import BacktestRequest, BacktestResult, PerformanceMetrics
from research_core.backtest_adapter.base import BacktestAdapter


class GMBacktestAdapter(BacktestAdapter):
    engine_name = "gm"

    def read_source(self, module_path: str) -> str:
        target = Path(module_path)
        if not target.exists():
            raise FileNotFoundError(f"Strategy module not found: {module_path}")
        return target.read_text(encoding="utf-8")

    def detect_entrypoint(self, module_path: str) -> tuple[str, list[str]]:
        source = self.read_source(module_path)
        tree = ast.parse(source)
        function_names = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
        if "start_backtest" in function_names:
            return "start_backtest", function_names
        if "run_strategy" in function_names:
            return "run_strategy", function_names
        if "start_strategy" in function_names:
            return "start_strategy", function_names
        raise AttributeError("Strategy module must expose start_backtest, run_strategy, or start_strategy")

    def build_gm_kwargs(self, request: BacktestRequest) -> dict[str, object]:
        return {
            "strategy_id": request.strategy_id,
            "backtest_start_time": request.start_time,
            "backtest_end_time": request.end_time,
            "backtest_initial_cash": request.initial_cash,
        }

    def build_execution_plan(self, request: BacktestRequest) -> dict[str, object]:
        self.validate(request)
        entrypoint, detected_functions = self.detect_entrypoint(request.module_path)
        return {
            "engine": self.engine_name,
            "module_path": request.module_path,
            "entrypoint": entrypoint,
            "detected_functions": detected_functions,
            "gm_kwargs": self.build_gm_kwargs(request),
            "strategy_params": request.strategy_params,
        }

    def run(self, request: BacktestRequest) -> BacktestResult:
        plan = self.build_execution_plan(request)
        metrics = PerformanceMetrics(
            total_return=0.0,
            annualized_return=0.0,
            benchmark_return=0.0,
            excess_return=0.0,
            max_drawdown=0.0,
            sharpe=0.0,
            volatility=0.0,
        )
        attribution = AttributionReport(
            summary=AttributionSummary(total_return=0.0),
            notes=["GM adapter scaffold created. Connect real GM backtest result parsing next."],
        )
        return BacktestResult(
            run_id=request.run_id,
            status="planned",
            engine=self.engine_name,
            strategy_id=request.strategy_id,
            strategy_version=request.strategy_version,
            benchmark=request.benchmark,
            metrics=metrics,
            attribution=attribution,
            diagnostics={"execution_plan": plan, "cwd": os.getcwd()},
        )
