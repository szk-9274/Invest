from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


CONFIG_PATH = Path(__file__).resolve().parents[2] / 'python' / 'config' / 'params.yaml'


def _normalize_tags(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def load_strategy_profiles(config_path: Path | None = None) -> list[dict[str, Any]]:
    path = config_path or CONFIG_PATH
    payload = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    raw_profiles = payload.get('strategy_profiles', {})
    if not isinstance(raw_profiles, dict):
        return []

    profiles: list[dict[str, Any]] = []
    for index, (strategy_name, profile) in enumerate(raw_profiles.items()):
        if not isinstance(profile, dict):
            continue
        tags = _normalize_tags(profile.get('tags'))
        profiles.append(
            {
                'strategy_name': strategy_name,
                'display_name': str(profile.get('display_name') or strategy_name),
                'short_name': str(profile.get('short_name') or profile.get('display_name') or strategy_name),
                'title': str(profile.get('title') or profile.get('rule_profile') or strategy_name),
                'description': str(profile.get('description') or ''),
                'icon_key': profile.get('icon_key'),
                'result_strategy_name': str(profile.get('result_strategy_name') or strategy_name),
                'portrait_asset_key': profile.get('portrait_asset_key'),
                'experiment_name': profile.get('experiment_name'),
                'rule_profile': profile.get('rule_profile'),
                'tags': tags,
                'is_trader_strategy': 'trader-inspired' in tags,
                'is_current_baseline': bool(profile.get('is_current_baseline', False)),
                'sort_order': int(profile.get('sort_order', index)),
            }
        )

    return sorted(profiles, key=lambda item: (item['sort_order'], item['strategy_name']))
