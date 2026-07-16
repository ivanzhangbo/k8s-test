# Task 5A Report: NetBox v2 Token Authentication

## Status

Implemented the isolated NetBox v2 authentication fix on `main` using a RED/GREEN TDD cycle. The playbook now sends both API requests with the required Bearer scheme, and the contract test prevents regression to the legacy Token scheme.

## Scope of changes

- `tests/test_netbox_mvp_contract.py`: added the two exact required assertions to `test_playbook_uses_rest_api_and_requests_config_context`.
- `ansible/get_config_context.yml`: changed exactly two authorization header prefixes from `Token` to `Bearer`.
- No workflow, inventory, README, URL, or TLS-setting changes were made.

## RED evidence

Command:

```powershell
& 'C:\Users\ivanz\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_netbox_mvp_contract.NetBoxMvpContractTest.test_playbook_uses_rest_api_and_requests_config_context
```

Result: exit code 1; one focused test ran and failed for the expected missing behavior.

```text
F
FAIL: test_playbook_uses_rest_api_and_requests_config_context
AssertionError: 'Authorization: "Bearer {{ netbox_token }}"' not found in ...
Ran 1 test in 0.001s
FAILED (failures=1)
```

The failure output showed both existing `Authorization: "Token {{ netbox_token }}"` headers, confirming that the test reproduced the reported legacy-header bug before production changes.

## GREEN evidence

Command:

```powershell
& 'C:\Users\ivanz\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests/test_netbox_mvp_contract.py
```

Result: exit code 0.

```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.001s

OK
```

## Self-review

- `git diff --check` returned no output (clean whitespace).
- Pre-report source diff contained only the two intended files: 4 insertions and 2 deletions.
- The test includes the exact required positive Bearer assertion and negative legacy Token assertion.
- Header inspection found Bearer at playbook lines 22 and 42 and found no legacy Token match.
- The playbook diff changes only the authentication scheme; URLs, methods, response handling, and `validate_certs: true` remain unchanged.
