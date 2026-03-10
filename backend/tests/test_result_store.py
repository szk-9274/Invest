import sys
from pathlib import Path

import pandas as pd

_backend_dir = str(Path(__file__).parent.parent)
_python_dir = str(Path(__file__).parent.parent.parent / 'python')
if _backend_dir in sys.path:
    sys.path.remove(_backend_dir)
sys.path.insert(0, _backend_dir)
if _python_dir not in sys.path:
    sys.path.append(_python_dir)


FIXTURE_ROOT = Path(__file__).resolve().parents[2] / 'tests' / 'fixtures' / 'backtest_sample'


def _write_result_set(base_dir: Path, dir_name: str) -> Path:
    result_dir = base_dir / dir_name
    result_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {'ticker': 'AAA', 'entry_date': '2026-01-01', 'entry_price': 10, 'exit_date': '2026-01-05', 'exit_price': 12, 'exit_reason': 'rule', 'shares': 1, 'pnl': 2, 'pnl_pct': 20},
        ]
    ).to_csv(result_dir / 'trades.csv', index=False)
    pd.DataFrame(
        [
            {'date': '2026-01-01', 'action': 'ENTRY', 'ticker': 'AAA', 'price': 10, 'shares': 1, 'pnl': 0},
            {'date': '2026-01-05', 'action': 'EXIT', 'ticker': 'AAA', 'price': 12, 'shares': 1, 'pnl': 2},
        ]
    ).to_csv(result_dir / 'trade_log.csv', index=False)
    pd.DataFrame(
        [
            {'ticker': 'AAA', 'total_pnl': 2, 'trade_count': 1, 'num_trades': 1, 'win_rate': 1.0},
        ]
    ).to_csv(result_dir / 'ticker_stats.csv', index=False)
    (result_dir / 'charts').mkdir(exist_ok=True)
    return result_dir


def _write_manifest(
    result_dir: Path,
    *,
    run_label: str = 'baseline-run',
    experiment_name: str = 'minervini-stage2-baseline',
    strategy_name: str = 'stage2-rule-stack',
    benchmark_enabled: bool = True,
) -> None:
    import json

    manifest = {
        'run_id': result_dir.name,
        'run_label': run_label,
        'experiment_name': experiment_name,
        'strategy_name': strategy_name,
        'benchmark_enabled': benchmark_enabled,
        'rule_profile': 'strict-auto-fallback',
        'tags': ['baseline', 'qlib-inspired'],
        'artifacts': {
            'trades_csv': 'trades.csv',
            'trade_log_csv': 'trade_log.csv',
            'ticker_stats_csv': 'ticker_stats.csv',
        },
        'metrics': {
            'total_trades': 1,
            'win_rate': 1.0,
            'total_pnl': 2.0,
            'annual_return_pct': 0.18,
            'information_ratio': 1.25,
            'max_drawdown_pct': -0.08,
        },
    }
    (result_dir / 'run_manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )


def test_get_backtest_output_dir_uses_env_override(monkeypatch, tmp_path):
    from services.result_store import get_backtest_output_dir

    custom_output = tmp_path / 'custom-output'
    custom_output.mkdir()
    monkeypatch.setenv('INVEST_OUTPUT_DIR', str(custom_output))

    assert get_backtest_output_dir() == custom_output


def test_result_store_lists_backtests_from_fixture_dir():
    from services.result_store import ResultStore

    store = ResultStore(FIXTURE_ROOT)

    backtests = store.list_backtests()
    assert len(backtests) == 1
    assert backtests[0]['timestamp'] == '20260131-000000'
    assert backtests[0]['start_date'] == '2026-01-01'
    assert backtests[0]['end_date'] == '2026-01-31'
    assert backtests[0]['trade_count'] == 3


def test_result_store_resolves_latest_and_timestamp(tmp_path):
    from services.result_store import ResultStore

    _write_result_set(tmp_path, 'backtest_2025-01-01_to_2025-01-31_20250131-000000')
    _write_result_set(tmp_path, 'backtest_2026-01-01_to_2026-01-31_20260131-000000')

    store = ResultStore(tmp_path)
    latest = store.get_latest_run()
    exact = store.get_run_by_timestamp('20250131-000000')
    year_match = store.get_run_by_range('2025')

    assert latest is not None
    assert latest.dir_name.endswith('20260131-000000')
    assert exact is not None
    assert exact.dir_name.endswith('20250131-000000')
    assert year_match is not None
    assert year_match.dir_name.endswith('20250131-000000')


def test_result_store_latest_run_prefers_displayable_artifacts(tmp_path):
    from services.result_store import ResultStore

    _write_result_set(tmp_path, 'backtest_2025-01-01_to_2025-01-31_20250131-000000')
    empty_result_dir = tmp_path / 'backtest_2026-01-01_to_2026-01-31_20260131-000000'
    (empty_result_dir / 'charts').mkdir(parents=True, exist_ok=True)

    store = ResultStore(tmp_path)
    latest = store.get_latest_run()

    assert latest is not None
    assert latest.dir_name.endswith('20250131-000000')


def test_result_store_requires_exact_timestamp_and_known_selectors(tmp_path):
    from services.result_store import ResultStore

    _write_result_set(tmp_path, 'backtest_2025-01-01_to_2025-01-31_20250131-000000')
    _write_result_set(tmp_path, 'backtest_2025-02-01_to_2025-02-28_20250228-000000')

    store = ResultStore(tmp_path)

    assert store.get_run_by_timestamp('20250131-000000') is not None
    assert store.get_run_by_timestamp('2025') is None

    exact_period = store.get_run_by_range('2025-02-01 to 2025-02-28')
    assert exact_period is not None
    assert exact_period.dir_name.endswith('20250228-000000')
    assert store.get_run_by_range('does-not-exist') is None


def test_result_store_manifest_contains_expected_paths():
    from services.result_store import ResultStore

    store = ResultStore(FIXTURE_ROOT)
    run = store.get_latest_run()

    assert run is not None
    assert run.result_dir.name == 'backtest_2026-01-01_to_2026-01-31_20260131-000000'
    assert run.trade_log_path is not None
    assert run.trade_log_path.name == 'trade_log.csv'
    assert run.trades_path is not None
    assert run.trades_path.name == 'trades.csv'
    assert run.ticker_stats_path is not None
    assert run.ticker_stats_path.name == 'ticker_stats.csv'


def test_result_store_pins_target_periods_and_uses_latest_run_per_period(tmp_path):
    from services.result_store import ResultStore

    _write_result_set(tmp_path, 'backtest_2020-01-01_to_2020-12-31_20201231-000000')
    _write_result_set(tmp_path, 'backtest_2024-01-01_to_2024-12-31_20241231-000000')
    _write_result_set(tmp_path, 'backtest_2024-01-01_to_2024-12-31_20251231-000000')
    (tmp_path / 'backtest_2024-01-01_to_2024-12-31_20261231-000000').mkdir(parents=True, exist_ok=True)
    _write_result_set(tmp_path, 'backtest_2025-01-01_to_2025-12-31_20251231-235959')
    _write_result_set(tmp_path, 'backtest_2026-01-01_to_2026-12-31_20261231-000000')

    store = ResultStore(tmp_path)

    backtests = store.list_backtests()

    assert [backtest['period'] for backtest in backtests[:3]] == [
        '2025-01-01 to 2025-12-31',
        '2024-01-01 to 2024-12-31',
        '2020-01-01 to 2020-12-31',
    ]
    assert backtests[0]['is_pinned'] is True
    assert backtests[1]['is_pinned'] is True
    assert backtests[1]['available_runs'] == 2
    assert backtests[1]['timestamp'] == '20251231-000000'
    assert backtests[3]['period'] == '2026-01-01 to 2026-12-31'
    assert backtests[3]['is_pinned'] is False


def test_result_store_skips_periods_with_only_empty_runs(tmp_path):
    from services.result_store import ResultStore

    (tmp_path / 'backtest_2020-01-01_to_2020-12-31_20201231-000000').mkdir(parents=True, exist_ok=True)
    _write_result_set(tmp_path, 'backtest_2025-01-01_to_2025-12-31_20251231-235959')

    store = ResultStore(tmp_path)
    backtests = store.list_backtests()

    assert [backtest['period'] for backtest in backtests] == ['2025-01-01 to 2025-12-31']


def test_result_store_reads_run_manifest_metadata(tmp_path):
    from services.result_store import ResultStore

    result_dir = _write_result_set(tmp_path, 'backtest_2026-01-01_to_2026-01-31_20260131-000000')
    _write_manifest(
        result_dir,
        run_label='comparison-a',
        experiment_name='qlib-inspired',
        strategy_name='rule-based-stage2',
        benchmark_enabled=False,
    )

    store = ResultStore(tmp_path)
    run = store.get_latest_run()
    backtests = store.list_backtests()

    assert run is not None
    assert run.manifest_path is not None
    assert run.manifest_path.name == 'run_manifest.json'
    assert run.run_label == 'comparison-a'
    assert run.experiment_name == 'qlib-inspired'
    assert run.strategy_name == 'rule-based-stage2'
    assert run.benchmark_enabled is False
    assert run.tags == ['baseline', 'qlib-inspired']

    assert backtests[0]['run_label'] == 'comparison-a'
    assert backtests[0]['experiment_name'] == 'qlib-inspired'
    assert backtests[0]['strategy_name'] == 'rule-based-stage2'
    assert backtests[0]['benchmark_enabled'] is False
    assert backtests[0]['headline_metrics']['annual_return_pct'] == 0.18
    assert backtests[0]['headline_metrics']['information_ratio'] == 1.25
    assert backtests[0]['headline_metrics']['max_drawdown_pct'] == -0.08
