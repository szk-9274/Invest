import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest
from fastapi import HTTPException

_backend_dir = str(Path(__file__).parent.parent)
_python_dir = str(Path(__file__).parent.parent.parent / 'python')
if _backend_dir in sys.path:
    sys.path.remove(_backend_dir)
sys.path.insert(0, _backend_dir)
if _python_dir not in sys.path:
    sys.path.append(_python_dir)

from api import backtest as backtest_api


FIXTURE_DIR = Path(__file__).resolve().parents[2] / 'tests' / 'fixtures' / 'backtest_sample' / 'backtest_2026-01-01_to_2026-01-31_20260131-000000'


def _sample_results(timestamp: str = 'backtest_2026-01-01_to_2026-01-31') -> backtest_api.BacktestResults:
    return backtest_api.BacktestResults(
        timestamp=timestamp,
        summary=backtest_api.BacktestSummary(total_trades=2, winning_trades=1, losing_trades=1, win_rate=50, total_pnl=0),
        trades=[],
        ticker_stats=[],
        charts={},
    )


def test_run_backtest_task_creates_job(monkeypatch):
    captured = {}

    def fake_create_job(payload):
        captured['payload'] = payload
        return {'job_id': 'job-123'}

    monkeypatch.setattr(backtest_api.job_runner, 'create_job', fake_create_job)

    result = backtest_api.run_backtest_task('2026-01-01', '2026-01-31')

    assert captured['payload'] == {
        'command': 'backtest',
        'start_date': '2026-01-01',
        'end_date': '2026-01-31',
    }
    assert result['job_id'] == 'job-123'
    assert result['status'] == 'started'


def test_load_results_returns_empty_when_no_run(monkeypatch):
    class FakeStore:
        def __init__(self, *_args, **_kwargs):
            pass

        def get_latest_run(self):
            return None

    monkeypatch.setattr(backtest_api, 'ResultStore', FakeStore)

    result = backtest_api.load_results('/tmp/unused')

    assert result.has_results is False
    assert result.trade_log == []
    assert result.ticker_stats == []


def test_load_results_normalizes_records(monkeypatch):
    latest_run = SimpleNamespace(trade_log_path='trade_log.csv', trades_path='trades.csv', ticker_stats_path='ticker_stats.csv')

    class FakeStore:
        def __init__(self, *_args, **_kwargs):
            pass

        def get_latest_run(self):
            return latest_run

    monkeypatch.setattr(backtest_api, 'ResultStore', FakeStore)
    monkeypatch.setattr(
        backtest_api,
        'load_trade_log',
        lambda _path: [{'ticker': 'AAA', 'date': '2026-01-03', 'action': 'ENTRY', 'price': 100, 'shares': 2, 'pnl': 0}],
    )
    monkeypatch.setattr(
        backtest_api,
        'load_ticker_stats',
        lambda _path: [{'ticker': 'AAA', 'total_pnl': 20, 'trade_count': 1, 'num_trades': 1, 'win_rate': 1.0}],
    )

    result = backtest_api.load_results('/tmp/unused')

    assert result.has_results is True
    assert result.trade_log[0].ticker == 'AAA'
    assert result.ticker_stats[0].total_pnl == 20


def test_load_top_bottom_tickers_uses_latest_ticker_stats(monkeypatch):
    latest_run = SimpleNamespace(ticker_stats_path='ticker_stats.csv')

    class FakeStore:
        def __init__(self, *_args, **_kwargs):
            pass

        def get_latest_run(self):
            return latest_run

    monkeypatch.setattr(backtest_api, 'ResultStore', FakeStore)
    monkeypatch.setattr(
        backtest_api,
        'get_top_bottom_tickers',
        lambda path, top_n, bottom_n: {
            'top': [{'ticker': 'AAA', 'total_pnl': 20, 'trade_count': 1}],
            'bottom': [{'ticker': 'CCC', 'total_pnl': -20, 'trade_count': 1}],
        },
    )

    result = backtest_api.load_top_bottom_tickers('/tmp/unused', top_n=1, bottom_n=1)

    assert [item.ticker for item in result.top] == ['AAA']
    assert [item.ticker for item in result.bottom] == ['CCC']


def test_get_latest_results_returns_404_when_no_runs(monkeypatch):
    class FakeStore:
        def __init__(self, *_args, **_kwargs):
            pass

        def list_runs(self):
            return []

    monkeypatch.setattr(backtest_api, 'ResultStore', FakeStore)

    with pytest.raises(HTTPException) as exc:
        backtest_api.get_latest_results()

    assert exc.value.status_code == 404


def test_get_latest_results_uses_selected_range(monkeypatch):
    chosen = SimpleNamespace(result_dir=Path('/tmp/backtest'), dir_name='backtest_2026')

    class FakeStore:
        def __init__(self, *_args, **_kwargs):
            pass

        def list_runs(self):
            return [chosen]

        def get_run_by_range(self, requested_range):
            assert requested_range == '2026'
            return chosen

    loader = Mock(return_value=_sample_results('backtest_2026'))
    monkeypatch.setattr(backtest_api, 'ResultStore', FakeStore)
    monkeypatch.setattr(backtest_api, '_get_backtest_results_by_dir', loader)

    result = backtest_api.get_latest_results('2026')

    loader.assert_called_once_with('/tmp/backtest', 'backtest_2026', run=chosen)
    assert result.timestamp == 'backtest_2026'


def test_get_latest_results_returns_404_for_unknown_selector(monkeypatch):
    class FakeStore:
        def __init__(self, *_args, **_kwargs):
            pass

        def list_runs(self):
            return [SimpleNamespace(result_dir=Path('/tmp/backtest'), dir_name='backtest_2026')]

        def get_run_by_range(self, requested_range):
            assert requested_range == 'missing-period'
            return None

    monkeypatch.setattr(backtest_api, 'ResultStore', FakeStore)

    with pytest.raises(HTTPException) as exc:
        backtest_api.get_latest_results('missing-period')

    assert exc.value.status_code == 404
    assert exc.value.detail == 'No backtest results found for selector: missing-period'


def test_get_results_by_timestamp_wraps_unexpected_error(monkeypatch):
    class FakeStore:
        def __init__(self, *_args, **_kwargs):
            pass

        def get_run_by_timestamp(self, _timestamp):
            raise RuntimeError('boom')

    monkeypatch.setattr(backtest_api, 'ResultStore', FakeStore)

    with pytest.raises(HTTPException) as exc:
        backtest_api.get_results_by_timestamp('bad-ts')

    assert exc.value.status_code == 500
    assert exc.value.detail == 'boom'


def test_get_results_by_timestamp_returns_404_for_unknown_timestamp(monkeypatch):
    class FakeStore:
        def __init__(self, *_args, **_kwargs):
            pass

        def get_run_by_timestamp(self, _timestamp):
            return None

    monkeypatch.setattr(backtest_api, 'ResultStore', FakeStore)

    with pytest.raises(HTTPException) as exc:
        backtest_api.get_results_by_timestamp('missing-ts')

    assert exc.value.status_code == 404
    assert exc.value.detail == 'No backtest results found for timestamp: missing-ts'


def test_get_results_by_timestamp_passes_resolved_run(monkeypatch):
    matched = SimpleNamespace(result_dir=Path('/tmp/backtest-ts'), dir_name='backtest_20260131')

    class FakeStore:
        def __init__(self, *_args, **_kwargs):
            pass

        def get_run_by_timestamp(self, requested_timestamp):
            assert requested_timestamp == '20260131-000000'
            return matched

    loader = Mock(return_value=_sample_results('backtest_20260131'))
    monkeypatch.setattr(backtest_api, 'ResultStore', FakeStore)
    monkeypatch.setattr(backtest_api, '_get_backtest_results_by_dir', loader)

    result = backtest_api.get_results_by_timestamp('20260131-000000')

    loader.assert_called_once_with('/tmp/backtest-ts', 'backtest_20260131', run=matched)
    assert result.timestamp == 'backtest_20260131'


def test_get_backtest_results_by_dir_loads_charts_and_aliases(monkeypatch, tmp_path):
    result_dir = tmp_path / 'backtest_2026'
    charts_dir = result_dir / 'charts'
    charts_dir.mkdir(parents=True)

    (result_dir / 'trades.csv').write_text((FIXTURE_DIR / 'trades.csv').read_text(encoding='utf-8'), encoding='utf-8')
    (result_dir / 'ticker_stats.csv').write_text((FIXTURE_DIR / 'ticker_stats.csv').read_text(encoding='utf-8'), encoding='utf-8')
    (charts_dir / 'AAA_price_chart.png').write_bytes(b'aaa')
    (result_dir / 'equity_curve.png').write_bytes(b'equity')

    monkeypatch.setattr(
        backtest_api,
        'load_backtest_summary',
        lambda _path: {'total_trades': 2, 'winning_trades': 1, 'losing_trades': 1, 'win_rate': 50.0, 'total_pnl': 0.0},
    )
    monkeypatch.setattr(backtest_api, 'get_chart_as_base64', lambda chart_path: f'encoded:{Path(chart_path).stem}')

    result = backtest_api._get_backtest_results_by_dir(str(result_dir), 'backtest_2026')

    assert result.timestamp == 'backtest_2026'
    assert [trade.ticker for trade in result.trades] == ['AAA', 'CCC']
    assert result.charts['AAA_price_chart'] == 'encoded:AAA_price_chart'
    assert result.charts['AAA'] == 'encoded:AAA_price_chart'
    assert result.charts['equity_curve'] == 'encoded:equity_curve'


def test_get_backtest_results_by_dir_raises_for_missing_directory():
    with pytest.raises(HTTPException) as exc:
        backtest_api._get_backtest_results_by_dir('/tmp/does-not-exist', 'missing')

    assert exc.value.status_code == 404


def test_load_backtest_summary_falls_back_to_zero_when_ratios_are_none(tmp_path):
    from services.result_loader import load_backtest_summary

    result_dir = tmp_path / 'backtest_2026-01-01_to_2026-01-31_20260131-000000'
    result_dir.mkdir(parents=True, exist_ok=True)
    (result_dir / 'run_manifest.json').write_text(
        json.dumps(
            {
                'metrics': {
                    'total_trades': 1,
                    'total_pnl': 2.0,
                    'information_ratio': None,
                    'sharpe_ratio': None,
                },
            }
        ),
        encoding='utf-8',
    )

    summary = load_backtest_summary(str(result_dir))

    assert summary['information_ratio'] == 0


def test_get_ohlc_builds_response_from_yfinance_module(monkeypatch):
    history = pd.DataFrame(
        {
            'Date': pd.to_datetime(['2026-01-02', '2026-01-03']),
            'Open': [100.0, 101.0],
            'High': [110.0, 111.0],
            'Low': [95.0, 96.0],
            'Close': [108.0, 109.0],
            'Volume': [1000, 1200],
        }
    )

    class FakeTicker:
        def history(self, start, end):
            assert start == '2026-01-01'
            assert end == '2026-12-31'
            return history.copy()

    fake_module = ModuleType('ticker_charts_module')
    fake_module.YFINANCE_AVAILABLE = True
    fake_module.yf = SimpleNamespace(Ticker=lambda _ticker: FakeTicker())

    class FakeLoader:
        def exec_module(self, module):
            module.YFINANCE_AVAILABLE = fake_module.YFINANCE_AVAILABLE
            module.yf = fake_module.yf

    fake_spec = SimpleNamespace(loader=FakeLoader())

    monkeypatch.setattr(importlib.util, 'spec_from_file_location', lambda *_args, **_kwargs: fake_spec)
    monkeypatch.setattr(importlib.util, 'module_from_spec', lambda _spec: ModuleType('ticker_charts_module'))

    response = backtest_api.get_ohlc('AAA', range='2026')

    assert [item.time for item in response.data] == ['2026-01-02', '2026-01-03']
    assert response.data[0].open == 100.0
    assert response.data[1].volume == 1200


def test_get_ohlc_requires_date_range():
    with pytest.raises(HTTPException) as exc:
        backtest_api.get_ohlc('AAA')

    assert exc.value.status_code == 400


def test_get_ohlc_returns_empty_response_for_empty_history(monkeypatch):
    class FakeTicker:
        def history(self, start, end):
            return pd.DataFrame()

    class FakeLoader:
        def exec_module(self, module):
            module.YFINANCE_AVAILABLE = True
            module.yf = SimpleNamespace(Ticker=lambda _ticker: FakeTicker())

    fake_spec = SimpleNamespace(loader=FakeLoader())
    monkeypatch.setattr(importlib.util, 'spec_from_file_location', lambda *_args, **_kwargs: fake_spec)
    monkeypatch.setattr(importlib.util, 'module_from_spec', lambda _spec: ModuleType('ticker_charts_module'))

    response = backtest_api.get_ohlc('AAA', start_date='2026-01-01', end_date='2026-01-31')

    assert response.data == []


def test_get_ohlc_wraps_import_failures(monkeypatch):
    monkeypatch.setattr(importlib.util, 'spec_from_file_location', lambda *_args, **_kwargs: None)
    monkeypatch.setattr(importlib.util, 'module_from_spec', lambda _spec: (_ for _ in ()).throw(RuntimeError('missing spec')))

    with pytest.raises(HTTPException) as exc:
        backtest_api.get_ohlc('AAA', start_date='2026-01-01', end_date='2026-01-31')

    assert exc.value.status_code == 503
