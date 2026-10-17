# Reproduction and benchmark scope

The reusable deterministic agent now uses full-input, dataset-scoped cache keys, persistent SQLite cache and append-only API audit records with hash-chain verification. Real4,177-row data passes the independent route/tool benchmark and restart checks.

## Execute a recorded profile

```sh
python run_reproduction.py --profile checks --output reproduced/checks
```

Use a new output directory for each run. The driver writes command logs, source/input SHA-256 values, versions and an explicit outcome. It does not silently download data or turn generated fixtures into dataset-performance claims.

| Profile | Actual scope | Required inputs |
|---|---|---|
| `checks` | Offline behavioral regressions; not a fresh dataset benchmark | None |
| `full-notebook` | Execute retained notebook against an explicitly supplied input; preserves the original experiment protocol | csv |
| `agent-benchmark` | Deterministic route/tool correctness, persistent cache and audit replay against supplied CSV | csv |

Supply named paths with `--input name=/absolute/path`. Exact commands are versioned in [reproduction.json](reproduction.json); direct training commands and preparation contracts are below.

## Evidence boundary

This is deterministic tool routing, not an LLM or iterative reasoning result. A privileged database owner remains outside the audit-integrity boundary.

Keep input acquisition and source credits in [DATA.md](DATA.md). Historical results, new reference runs and small contract fixtures have separate evidential scope.

## Recorded command definitions

### checks

```text
{python} smoke_test.py
{python} test_persistent_agent.py
```

### full-notebook

```text
{python} reproduce.py --input {input:csv} --output {output}/notebook
```

### agent-benchmark

```text
{python} benchmark.py {input:csv} --output {output}/agent
```

`{python}` is the current interpreter. `{output}` is the new run directory. `{input:name}` refers to a named absolute input path supplied to the driver. Install declared dependencies in a clean environment before executing. Never execute untrusted serialized models or notebooks.
