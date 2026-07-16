# NetBox Config Context MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Demonstrate one effective NetBox Config Context in the NetBox UI, a rendered device configuration, and a GitHub Actions run where Ansible retrieves the same context.

**Architecture:** NetBox stores one site-targeted context and applies it to one demo device. A platform-level config template renders that effective context. A manually triggered GitHub Actions workflow installs `ansible-core` and runs a localhost playbook that reads the device through the NetBox REST API with `include=config_context`.

**Tech Stack:** NetBox Cloud 4.6.4, NetBox REST API, Jinja2, Ansible Core, GitHub Actions, Python `unittest`, Chrome.

## Global Constraints

- Prefix every created NetBox object with `mvp-`.
- Use only the non-secret context values specified in the approved design.
- Use `ansible.builtin.uri`; do not install the `netbox.netbox` collection.
- Store the token only in GitHub Actions secret `NETBOX_TOKEN`.
- Store `https://jlrj8132.cloud.netboxapp.com` in GitHub Actions variable `NETBOX_URL`.
- Keep TLS certificate verification enabled.
- Do not connect to or configure a real network device.
- Run the workflow only through `workflow_dispatch`.

---

## File Map

- `tests/test_netbox_mvp_contract.py`: Static contract tests for the workflow, inventory, playbook, and secret hygiene.
- `ansible/inventory.yml`: Localhost-only Ansible inventory.
- `ansible/get_config_context.yml`: NetBox REST query, response assertions, and context output.
- `.github/workflows/netbox-config-context.yml`: Manual GitHub-hosted runner entry point.
- `README.md`: Operator-facing explanation and demo instructions.

### Task 1: Add Failing Repository Contract Tests

**Files:**
- Create: `tests/test_netbox_mvp_contract.py`

**Interfaces:**
- Consumes: Approved file names and environment variable contracts.
- Produces: `python -m unittest tests/test_netbox_mvp_contract.py` as the repository-level verification command.

- [ ] **Step 1: Create the contract test**

```python
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class NetBoxMvpContractTest(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_inventory_is_localhost_only(self):
        inventory = self.read("ansible/inventory.yml")
        self.assertIn("localhost:", inventory)
        self.assertIn("ansible_connection: local", inventory)

    def test_playbook_uses_rest_api_and_requests_config_context(self):
        playbook = self.read("ansible/get_config_context.yml")
        self.assertIn("ansible.builtin.uri", playbook)
        self.assertIn("include=config_context", playbook)
        self.assertIn("NETBOX_TOKEN", playbook)
        self.assertIn("NETBOX_URL", playbook)
        self.assertIn("device_detail.json.config_context", playbook)
        self.assertNotIn("validate_certs: false", playbook)

    def test_workflow_is_manual_and_installs_ansible_core(self):
        workflow = self.read(".github/workflows/netbox-config-context.yml")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("pip install ansible-core", workflow)
        self.assertIn("secrets.NETBOX_TOKEN", workflow)
        self.assertIn("vars.NETBOX_URL", workflow)
        self.assertNotIn("schedule:", workflow)

    def test_credentials_are_not_committed(self):
        for relative_path in (
            "ansible/get_config_context.yml",
            ".github/workflows/netbox-config-context.yml",
        ):
            text = self.read(relative_path)
            self.assertNotIn("Token nb", text)
            self.assertNotIn("Authorization: Token ", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify it fails because implementation files do not exist**

Run: `python -m unittest tests/test_netbox_mvp_contract.py -v`

Expected: four errors containing `FileNotFoundError` for files under `ansible/` and `.github/workflows/`.

- [ ] **Step 3: Commit the failing test**

```bash
git add tests/test_netbox_mvp_contract.py
git commit -m "test: define NetBox MVP automation contract"
```

### Task 2: Implement the Ansible Playbook and GitHub Workflow

**Files:**
- Create: `ansible/inventory.yml`
- Create: `ansible/get_config_context.yml`
- Create: `.github/workflows/netbox-config-context.yml`
- Test: `tests/test_netbox_mvp_contract.py`

**Interfaces:**
- Consumes: Environment variables `NETBOX_URL` and `NETBOX_TOKEN`; device name `mvp-router-01`.
- Produces: Successful localhost playbook output containing `device_detail.json.config_context`.

- [ ] **Step 1: Create the localhost inventory**

```yaml
---
all:
  hosts:
    localhost:
      ansible_connection: local
```

- [ ] **Step 2: Create the playbook**

```yaml
---
- name: Read effective NetBox config context
  hosts: localhost
  gather_facts: false
  vars:
    netbox_url: "{{ lookup('ansible.builtin.env', 'NETBOX_URL') | regex_replace('/$', '') }}"
    netbox_token: "{{ lookup('ansible.builtin.env', 'NETBOX_TOKEN') }}"
    device_name: mvp-router-01
  tasks:
    - name: Validate required environment variables
      ansible.builtin.assert:
        that:
          - netbox_url | length > 0
          - netbox_token | length > 0
        fail_msg: NETBOX_URL and NETBOX_TOKEN must both be set

    - name: Find the demo device
      ansible.builtin.uri:
        url: "{{ netbox_url }}/api/dcim/devices/?name={{ device_name | urlencode }}"
        method: GET
        headers:
          Authorization: "Token {{ netbox_token }}"
          Accept: application/json
        return_content: true
        status_code: 200
        validate_certs: true
      register: device_query

    - name: Require exactly one demo device
      ansible.builtin.assert:
        that:
          - device_query.json.count == 1
        fail_msg: >-
          Expected exactly one device named {{ device_name }},
          found {{ device_query.json.count | default('unknown') }}

    - name: Read the device with effective config context
      ansible.builtin.uri:
        url: "{{ device_query.json.results[0].url }}?include=config_context"
        method: GET
        headers:
          Authorization: "Token {{ netbox_token }}"
          Accept: application/json
        return_content: true
        status_code: 200
        validate_certs: true
      register: device_detail

    - name: Require the effective context field
      ansible.builtin.assert:
        that:
          - device_detail.json.config_context is defined
        fail_msg: NetBox did not return config_context for the demo device

    - name: Show the effective config context
      ansible.builtin.debug:
        var: device_detail.json.config_context
```

- [ ] **Step 3: Create the manually triggered workflow**

```yaml
name: NetBox Config Context MVP

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  get-config-context:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Install Ansible Core
        run: python -m pip install ansible-core

      - name: Validate repository contract
        run: python -m unittest tests/test_netbox_mvp_contract.py -v

      - name: Validate playbook syntax
        run: ansible-playbook -i ansible/inventory.yml ansible/get_config_context.yml --syntax-check
        env:
          NETBOX_URL: ${{ vars.NETBOX_URL }}
          NETBOX_TOKEN: ${{ secrets.NETBOX_TOKEN }}

      - name: Retrieve effective config context
        run: ansible-playbook -i ansible/inventory.yml ansible/get_config_context.yml
        env:
          NETBOX_URL: ${{ vars.NETBOX_URL }}
          NETBOX_TOKEN: ${{ secrets.NETBOX_TOKEN }}
```

- [ ] **Step 4: Run the contract tests**

Run: `python -m unittest tests/test_netbox_mvp_contract.py -v`

Expected: four tests pass.

- [ ] **Step 5: Install Ansible Core and run the syntax check locally**

Run: `python -m pip install ansible-core`

Run: `ansible-playbook -i ansible/inventory.yml ansible/get_config_context.yml --syntax-check`

Expected: `playbook: ansible/get_config_context.yml`. The syntax check must not make an HTTP request.

- [ ] **Step 6: Commit the automation**

```bash
git add ansible .github/workflows/netbox-config-context.yml
git commit -m "feat: retrieve NetBox config context with Ansible"
```

### Task 3: Document the Demonstration

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: Object names, secret names, variable names, and commands from Task 2.
- Produces: A concise operator guide for running and interpreting the demo.

- [ ] **Step 1: Replace the README with the following content**

````markdown
# k8s-test

## NetBox Config Context MVP

This demo shows how NetBox applies structured context data to a device, uses that data in a Jinja2 configuration template, and exposes the same effective context through the REST API for Ansible.

### Demo objects

- Device: `mvp-router-01`
- Site: `mvp-site`
- Config context: `mvp-base-context`
- Config template: `mvp-router-template`

The context supplies a banner, two DNS servers, and two NTP servers. The template renders them into a small Cisco-like configuration. It does not configure a real device.

### GitHub Actions setup

The repository uses:

- Repository variable `NETBOX_URL`
- Repository secret `NETBOX_TOKEN`

Run **Actions → NetBox Config Context MVP → Run workflow**. The runner installs `ansible-core`, validates the playbook, retrieves `mvp-router-01` with `include=config_context`, and prints only its effective context.

### Run locally

```bash
export NETBOX_URL=https://jlrj8132.cloud.netboxapp.com
export NETBOX_TOKEN='replace-with-a-read-only-token'
python -m pip install ansible-core
ansible-playbook -i ansible/inventory.yml ansible/get_config_context.yml
```

Never commit a real API token.
````

- [ ] **Step 2: Re-run repository tests**

Run: `python -m unittest tests/test_netbox_mvp_contract.py -v`

Expected: four tests pass.

- [ ] **Step 3: Commit the documentation**

```bash
git add README.md
git commit -m "docs: explain NetBox config context demo"
```

### Task 4: Create and Verify the NetBox Demo Objects in Chrome

**Files:** None.

**Interfaces:**
- Consumes: NetBox administrator session and the exact names/data below.
- Produces: Device `mvp-router-01` with an effective context and rendered configuration.

- [ ] **Step 1: Create the dependency objects**

Create the following through the NetBox UI, keeping unspecified optional fields at their defaults:

| Object | Required values |
|---|---|
| Site | Name `mvp-site`, slug `mvp-site`, status `Active` |
| Manufacturer | Name `mvp-manufacturer`, slug `mvp-manufacturer` |
| Device type | Manufacturer `mvp-manufacturer`, model `mvp-router-type`, slug `mvp-router-type`, height `1` |
| Device role | Name `mvp-router-role`, slug `mvp-router-role`, color `9e9e9e` |
| Config template | Name `mvp-router-template`, template code from Step 2 |
| Platform | Name `mvp-ios`, slug `mvp-ios`, config template `mvp-router-template` |

After each save, verify the object detail page shows the expected name before proceeding.

- [ ] **Step 2: Use this exact Jinja2 config template**

```jinja2
hostname {{ device.name }}
!
banner motd ^
{{ banner }}
^
!
{% for server in dns_servers %}
ip name-server {{ server }}
{% endfor %}
!
{% for server in ntp_servers %}
ntp server {{ server }}
{% endfor %}
```

- [ ] **Step 3: Create the config context**

Create `mvp-base-context` with weight `1000`, active enabled, Site assignment `mvp-site`, and this JSON data:

```json
{
  "banner": "Managed by NetBox Config Context MVP",
  "dns_servers": ["1.1.1.1", "8.8.8.8"],
  "ntp_servers": ["time.cloudflare.com", "time.google.com"]
}
```

Verify its detail page shows `mvp-site` under assignments and all three keys under data.

- [ ] **Step 4: Create the demo device**

Create device `mvp-router-01` with device role `mvp-router-role`, device type `mvp-router-type`, site `mvp-site`, platform `mvp-ios`, and status `Active`.

- [ ] **Step 5: Verify effective context and rendered configuration**

Open `mvp-router-01` and verify its Config Context view contains the expected banner, DNS list, and NTP list. Open Render Config and verify the rendered text contains:

```text
hostname mvp-router-01
Managed by NetBox Config Context MVP
ip name-server 1.1.1.1
ip name-server 8.8.8.8
ntp server time.cloudflare.com
ntp server time.google.com
```

If the template does not render, inspect the visible NetBox validation error and correct only the field or Jinja expression named by that error before re-verifying.

### Task 5: Configure Credentials, Push, and Run the Workflow

**Files:** None beyond committed work from Tasks 1-3.

**Interfaces:**
- Consumes: Read-only NetBox API token; committed workflow; GitHub repository settings.
- Produces: A successful Actions run whose log shows the expected effective context.

- [ ] **Step 1: Create a read-only NetBox API token**

In the logged-in NetBox user's API Tokens page, create a token named `github-actions-netbox-context-mvp` with write permission disabled. Copy the token once for immediate transfer to GitHub; never print it in tool output or write it to disk.

- [ ] **Step 2: Create the GitHub repository variable**

In `ivanzhangbo/k8s-test` Settings → Secrets and variables → Actions → Variables, create:

```text
Name: NETBOX_URL
Value: https://jlrj8132.cloud.netboxapp.com
```

- [ ] **Step 3: Create the GitHub repository secret**

In the same Actions settings under Secrets, create `NETBOX_TOKEN` with the read-only token value. Verify only that the secret name appears in the list; do not attempt to read it back.

- [ ] **Step 4: Verify repository state and push all local commits**

Run: `git status --short --branch`

Expected: `main` is ahead of `origin/main` and the working tree is clean.

Run: `git push origin main`

Expected: Git reports that `main` was updated on `origin`.

- [ ] **Step 5: Run the workflow in Chrome**

Open Actions → NetBox Config Context MVP → Run workflow, choose `main`, and confirm the run. Wait for the `get-config-context` job to complete.

- [ ] **Step 6: Verify the workflow output**

Open the `Retrieve effective config context` step and verify the output contains:

```yaml
banner: Managed by NetBox Config Context MVP
dns_servers:
  - 1.1.1.1
  - 8.8.8.8
ntp_servers:
  - time.cloudflare.com
  - time.google.com
```

Search the repository files for token-like literals:

Run: `rg -n "NETBOX_TOKEN|Authorization: Token|github-actions-netbox-context-mvp" . -g '!docs/superpowers/**'`

Expected: only environment-variable and secret references; no actual token value.

- [ ] **Step 7: Preserve the three demonstration pages**

Leave these Chrome pages open as deliverables:

1. NetBox `mvp-router-01` Config Context view.
2. NetBox `mvp-router-01` Render Config view.
3. Successful GitHub Actions run log.

- [ ] **Step 8: Final verification checkpoint**

Run: `python -m unittest tests/test_netbox_mvp_contract.py -v`

Expected: four tests pass.

Run: `git status --short --branch`

Expected: `## main...origin/main` with no changed files.
