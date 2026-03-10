import json
import sys
from pathlib import Path
from types import SimpleNamespace


sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))


def test_run_manifest_store_writes_manifest_and_registry(tmp_path):
    from experiments.models import BacktestRunManifest, RunArtifacts, RunMetrics, RunSpec
    from experiments.store import ExperimentStore

    output_root = tmp_path / 'output' / 'backtest'
    result_dir = output_root / 'backtest_2026-01-01_to_2026-01-31_20260131-000000'
    result_dir.mkdir(parents=True, exist_ok=True)

    spec = RunSpec(
        mode='backtest',
        run_id=result_dir.name,
        run_label='baseline-run',
        start_date='2026-01-01',
        end_date='2026-01-31',
        use_benchmark=True,
        ticker_count=12,
        tickers=['AAA', 'BBB'],
        config_path='config/params.yaml',
        rule_profile='strict-auto-fallback',
        experiment_name='qlib-inspired',
        strategy_name='rule-based-stage2',
        tags=['baseline', 'cpu-friendly'],
        no_charts=False,
    )
    manifest = BacktestRunManifest(
        spec=spec,
        metrics=RunMetrics(total_trades=4, win_rate=0.5, total_pnl=123.4),
        artifacts=RunArtifacts(
            trades_csv='trades.csv',
            trade_log_csv='trade_log.csv',
            ticker_stats_csv='ticker_stats.csv',
            charts_dir='charts',
        ),
        diagnostics={'stage2_universe_size': 12},
        parameter_snapshot={'stage': {'strict': {'min_volume': 500000}}},
    )

    store = ExperimentStore(output_root)
    manifest_path = store.save_manifest(result_dir, manifest)
    registry_path = store.update_registry(manifest)

    saved_manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    saved_registry = json.loads(registry_path.read_text(encoding='utf-8'))

    assert manifest_path.name == 'run_manifest.json'
    assert saved_manifest['spec']['run_label'] == 'baseline-run'
    assert saved_manifest['metrics']['total_pnl'] == 123.4
    assert saved_manifest['parameter_snapshot']['stage']['strict']['min_volume'] == 500000

    assert saved_registry['runs'][0]['run_id'] == result_dir.name
    assert saved_registry['runs'][0]['experiment_name'] == 'qlib-inspired'
    assert saved_registry['runs'][0]['strategy_name'] == 'rule-based-stage2'
    assert saved_registry['runs'][0]['benchmark_enabled'] is True


def test_write_run_manifest_includes_cli_snapshot(tmp_path):
    from main import _write_run_manifest

    output_dir = tmp_path / 'output' / 'backtest' / 'backtest_2026-01-01_to_2026-01-31_20260131-000000'
    output_dir.mkdir(parents=True, exist_ok=True)

    config = {
        'benchmark': {'symbol': 'SPY', 'enabled': True},
        'stage': {'strict': {'min_volume': 500000}, 'relaxed': {'min_volume': 300000}},
        'entry': {'min_volume': 500000},
        'exit': {'sma_50_exit': True},
        'risk': {'risk_per_trade': 0.01},
        'backtest': {'initial_capital': 100000},
        'experiment': {
            'name': 'qlib-inspired',
            'strategy_name': 'rule-based-stage2',
            'rule_profile': 'strict-auto-fallback',
            'tags': ['baseline'],
        },
    }
    args = SimpleNamespace(
        start='2026-01-01',
        end='2026-01-31',
        tickers='AAA,BBB',
        no_charts=False,
        no_benchmark=False,
        run_label='baseline-run',
    )
    result = SimpleNamespace(
        total_trades=3,
        win_rate=2 / 3,
        total_return=120.0,
        winning_trades=2,
        losing_trades=1,
        avg_win=80.0,
        avg_loss=40.0,
        final_capital=10120.0,
        total_return_pct=0.012,
        max_drawdown_pct=-0.05,
        sharpe_ratio=1.2,
    )

    _write_run_manifest(
        config=config,
        args=args,
        tickers=['AAA', 'BBB'],
        start_date='2026-01-01',
        end_date='2026-01-31',
        output_dir=output_dir,
        use_benchmark=True,
        result=result,
        diagnostics={'stage2_universe_size': 2},
    )

    manifest = json.loads((output_dir / 'run_manifest.json').read_text(encoding='utf-8'))

    assert manifest['run_label'] == 'baseline-run'
    assert manifest['metrics']['total_trades'] == 3
    assert manifest['parameter_snapshot']['cli']['tickers'] == 'AAA,BBB'
    assert manifest['parameter_snapshot']['experiment']['name'] == 'qlib-inspired'
