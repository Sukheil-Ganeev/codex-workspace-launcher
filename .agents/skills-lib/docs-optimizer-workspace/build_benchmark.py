#!/usr/bin/env python3
"""
build_benchmark.py — Rebuild benchmark.json from grading.json files (iteration-2).
Merges new assertions data with existing timing/token data from iteration-1 benchmark.
"""

import json, os, re
from datetime import datetime

base = 'C:/Users/londo/.claude/skills/docs-optimizer-workspace/iteration-1/'
workspace = 'C:/Users/londo/.claude/skills/docs-optimizer-workspace/'

evals = [
    (1, 'analyze'), (2, 'tiered'), (3, 'audit'), (4, 'optimize'), (5, 'duplication'),
    (6, 'freshness'), (7, 'tokens'), (8, 'crossref'), (9, 'stale-issues'), (10, 'orphan-docs')
]

# Load existing benchmark for timing data
existing_bench_path = base + 'benchmark.json'
with open(existing_bench_path, encoding='utf-8') as f:
    existing = json.load(f)

# Build lookup for existing timing data
timing_lookup = {}
for run in existing.get('runs', []):
    eid = run['eval_id']
    cfg = run['configuration']
    timing_lookup[(eid, cfg)] = run.get('result', {})

# Build new runs from grading.json files
runs = []
with_skill_rates = []
without_skill_rates = []

for eval_id, slug in evals:
    eval_dir = f'{base}eval-{eval_id}-{slug}/'

    for config in ['with_skill', 'without_skill']:
        grading_path = f'{eval_dir}{config}/grading.json'
        with open(grading_path, encoding='utf-8') as f:
            grading = json.load(f)

        # Convert assertions to expectations format
        expectations = []
        for a in grading.get('assertions', []):
            expectations.append({
                'text': a['description'],
                'passed': a['passed'],
                'evidence': a.get('evidence', '')
            })

        # Get timing from existing benchmark if available
        existing_result = timing_lookup.get((eval_id, config), {})

        result = {
            'pass_rate': grading['pass_rate'],
            'passed': grading['passed'],
            'failed': grading['total'] - grading['passed'],
            'total': grading['total'],
            'time_seconds': existing_result.get('time_seconds', 0),
            'tokens': existing_result.get('tokens', 0),
            'tool_calls': existing_result.get('tool_calls', 0),
            'errors': 0
        }

        run = {
            'eval_id': eval_id,
            'configuration': config,
            'run_number': 1,
            'result': result,
            'expectations': expectations,
            'notes': []
        }
        runs.append(run)

        if config == 'with_skill':
            with_skill_rates.append(grading['pass_rate'])
        else:
            without_skill_rates.append(grading['pass_rate'])

# Compute summary
def mean(lst): return sum(lst) / len(lst) if lst else 0
def stddev(lst):
    m = mean(lst)
    return (sum((x - m) ** 2 for x in lst) / len(lst)) ** 0.5 if len(lst) > 1 else 0

ws_mean = mean(with_skill_rates)
wos_mean = mean(without_skill_rates)
delta = ws_mean - wos_mean
delta_str = f'+{delta:.2f}' if delta >= 0 else f'{delta:.2f}'

run_summary = {
    'with_skill': {
        'pass_rate': {
            'mean': round(ws_mean, 4),
            'stddev': round(stddev(with_skill_rates), 4),
            'min': round(min(with_skill_rates), 4),
            'max': round(max(with_skill_rates), 4)
        },
        'time_seconds': existing['run_summary']['with_skill'].get('time_seconds', {}),
        'tokens': existing['run_summary']['with_skill'].get('tokens', {})
    },
    'without_skill': {
        'pass_rate': {
            'mean': round(wos_mean, 4),
            'stddev': round(stddev(without_skill_rates), 4),
            'min': round(min(without_skill_rates), 4),
            'max': round(max(without_skill_rates), 4)
        },
        'time_seconds': existing['run_summary']['without_skill'].get('time_seconds', {}),
        'tokens': existing['run_summary']['without_skill'].get('tokens', {})
    },
    'delta': {
        'pass_rate': delta_str,
        'time_seconds': existing['run_summary'].get('delta', {}).get('time_seconds', '+0'),
        'tokens': existing['run_summary'].get('delta', {}).get('tokens', '+0')
    }
}

benchmark = {
    'metadata': {
        'skill_name': 'docs-optimizer',
        'skill_path': 'C:/Users/londo/.claude/skills/docs-optimizer',
        'executor_model': 'claude-sonnet-4-6',
        'analyzer_model': 'claude-sonnet-4-6',
        'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'iteration': 2,
        'note': 'Iteration 2 grading — 49 assertions, existing outputs from iteration-1',
        'evals_run': [e[0] for e in evals],
        'runs_per_configuration': 1
    },
    'runs': runs,
    'run_summary': run_summary,
    'notes': ['Iteration 2: new assertions graded on existing iteration-1 outputs']
}

out_path = base + 'benchmark.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(benchmark, f, ensure_ascii=False, indent=2)

print(f'benchmark.json written to: {out_path}')
print(f'\nSummary:')
print(f'  with_skill:    {ws_mean:.0%} ({len(with_skill_rates)} evals)')
print(f'  without_skill: {wos_mean:.0%} ({len(without_skill_rates)} evals)')
print(f'  delta:         {delta_str}')
print(f'\nPer-eval results:')
for i, (eval_id, slug) in enumerate(evals):
    ws = with_skill_rates[i]
    wos = without_skill_rates[i]
    d = ws - wos
    d_str = f'+{d:.0%}' if d >= 0 else f'{d:.0%}'
    print(f'  eval-{eval_id}-{slug:<14}: with={ws:.0%}  without={wos:.0%}  delta={d_str}')
