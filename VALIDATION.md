# Release validation

Source syntax and notebook code cells are checked on Python 3.11 and 3.12 by the included workflow. These source checks do not run training, databases, paid model providers, or external simulations. Additional runtime checks are recorded below when executed.

Full historical experiment reproduction is separate from source validation. No new benchmark result is inferred from syntax checks.

## Complete notebook execution

Fresh execution completed the demonstration and both column-resolution and bounded-calculation regression checks.

All 11 code cells executed successfully in an isolated CPU process. No model-provider calls were made. Source/input hashes and dependency versions are recorded in `results/reproduction.json`. The raw inputs and raw execution logs are not distributed.

## Focused runtime checks

`python smoke_test.py` passed locally on Python 3.14.3. The checks exercise the model/function behavior described by the script, without fetching data, calling a model provider, or launching a simulation.
