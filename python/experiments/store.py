from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import BacktestRunManifest


MANIFEST_FILENAME = 'run_manifest.json'
REGISTRY_FILENAME = 'registry.json'


class ExperimentStore:
    def __init__(self, output_root: str | Path):
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)

    def save_manifest(self, result_dir: str | Path, manifest: BacktestRunManifest) -> Path:
        result_path = Path(result_dir)
        result_path.mkdir(parents=True, exist_ok=True)
        manifest_path = result_path / MANIFEST_FILENAME
        manifest_path.write_text(
            json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2),
            encoding='utf-8',
        )
        return manifest_path

    def update_registry(self, manifest: BacktestRunManifest) -> Path:
        registry_path = self.output_root / REGISTRY_FILENAME
        payload = self._load_registry(registry_path)
        entry = self._build_registry_entry(manifest)
        runs = [item for item in payload.get('runs', []) if item.get('run_id') != entry['run_id']]
        runs.insert(0, entry)
        payload['runs'] = sorted(
            runs,
            key=lambda item: item.get('created_at', ''),
            reverse=True,
        )
        registry_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )
        return registry_path

    @staticmethod
    def _load_registry(registry_path: Path) -> dict[str, Any]:
        if not registry_path.exists():
            return {'runs': []}
        try:
            return json.loads(registry_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            return {'runs': []}

    @staticmethod
    def _build_registry_entry(manifest: BacktestRunManifest) -> dict[str, Any]:
        spec = manifest.spec
        metrics = manifest.metrics
        return {
            'run_id': spec.run_id,
            'created_at': spec.created_at,
            'run_label': spec.run_label,
            'experiment_name': spec.experiment_name,
            'strategy_name': spec.strategy_name,
            'rule_profile': spec.rule_profile,
            'benchmark_enabled': spec.use_benchmark,
            'start_date': spec.start_date,
            'end_date': spec.end_date,
            'ticker_count': spec.ticker_count,
            'tags': list(spec.tags),
            'total_trades': metrics.total_trades,
            'total_pnl': metrics.total_pnl,
            'win_rate': metrics.win_rate,
        }
