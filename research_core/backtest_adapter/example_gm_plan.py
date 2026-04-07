from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from contracts.backtest import BacktestRequest
from research_core.backtest_adapter.gm_adapter import GMBacktestAdapter


def build_example_plan(module_path: str) -> dict:
    request = BacktestRequest(
        run_id=f"run_{uuid.uuid4().hex[:12]}",
        strategy_id="bigquant-sample",
        strategy_version="v1",
        strategy_params={"rebalance": "monthly"},
        module_path=module_path,
        start_time="2024-01-01 09:30:00",
        end_time="2025-12-31 15:00:00",
        benchmark="SHSE.000300",
        initial_cash=1000000,
        execution_engine="gm",
    )
    adapter = GMBacktestAdapter()
    result = adapter.run(request)
    return result.diagnostics


if __name__ == "__main__":
    sample_module = REPO_ROOT / ".." / "quant" / "risk" / "26-3-26matrix_fund_manage_method.py"
    payload = build_example_plan(str(sample_module.resolve()))
    print(json.dumps(payload, ensure_ascii=False, indent=2))
