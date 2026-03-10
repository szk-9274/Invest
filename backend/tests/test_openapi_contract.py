import sys
from pathlib import Path

_backend_dir = str(Path(__file__).parent.parent)
_python_dir = str(Path(__file__).parent.parent.parent / 'python')
if _backend_dir in sys.path:
    sys.path.remove(_backend_dir)
sys.path.insert(0, _backend_dir)
if _python_dir not in sys.path:
    sys.path.append(_python_dir)


def test_openapi_contains_expected_contract_schemas():
    from app import app

    schema = app.openapi()
    components = schema['components']['schemas']

    assert 'BacktestResults' in components
    assert 'BacktestMetadata' in components
    assert 'BacktestRunInfo' in components
    assert 'TopBottomTickers' in components
    assert 'ChartData' in components
    assert 'TradeMarkers' in components
    assert 'JobResponse' in components

    latest_schema_ref = schema['paths']['/api/backtest/latest']['get']['responses']['200']['content']['application/json']['schema']['$ref']
    jobs_schema_ref = schema['paths']['/api/jobs/{job_id}']['get']['responses']['200']['content']['application/json']['schema']['$ref']

    assert latest_schema_ref.endswith('/BacktestResults')
    assert jobs_schema_ref.endswith('/JobResponse')


def test_contract_export_generates_typescript_definitions(tmp_path):
    from backend.scripts.export_frontend_contracts import export_contracts

    output_path = tmp_path / 'contracts.ts'
    export_contracts(output_path)

    content = output_path.read_text(encoding='utf-8')
    assert 'export type BacktestResults' in content
    assert 'export type JobResponse' in content
    assert 'export type TradeMarkers' in content
    assert 'export type BacktestRunInfo' in content
    assert 'is_pinned?: boolean' in content
    assert 'available_runs?: number' in content
    assert 'run_metadata?: BacktestRunInfo | null' in content
