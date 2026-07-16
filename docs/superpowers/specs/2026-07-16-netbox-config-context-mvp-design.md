# NetBox Config Context MVP Design

## Goal

Build a minimal, disposable demonstration that shows the same NetBox Config Context in three places:

1. The effective context attached to a device in the NetBox UI.
2. A rendered device configuration produced by a NetBox Jinja2 config template.
3. A GitHub Actions run in which Ansible retrieves and prints that device's effective context through the NetBox REST API.

The demo uses objects prefixed with `mvp-` so they are easy to identify and remove.

## Scope

The NetBox environment is currently empty of sites, devices, and config contexts. The demo will create only the dependencies required for one device:

- Site: `mvp-site`
- Manufacturer: `mvp-manufacturer`
- Device type: `mvp-router-type`
- Device role: `mvp-router-role`
- Platform: `mvp-ios`
- Device: `mvp-router-01`
- Config context: `mvp-base-context`
- Config template: `mvp-router-template`

The config context will target `mvp-site`, which makes the relationship visible and demonstrates how context is selected rather than embedding data directly on the device.

## Context Data

The context contains intentionally non-secret sample data:

```yaml
banner: Managed by NetBox Config Context MVP
dns_servers:
  - 1.1.1.1
  - 8.8.8.8
ntp_servers:
  - time.cloudflare.com
  - time.google.com
```

The config template will render a short Cisco-like configuration using the device name and these context values. It is illustrative output only and will not connect to or configure a network device.

## NetBox Data Flow

NetBox evaluates the device attributes when `mvp-router-01` is opened. Because the device belongs to `mvp-site`, NetBox merges `mvp-base-context` into the device's effective `config_context`. The device's Render Config view then passes the device object and effective context to `mvp-router-template`.

The rendered output will include:

- `hostname mvp-router-01`
- A generated banner
- One name-server line per DNS server
- One NTP server line per NTP server

## GitHub and Ansible Design

The repository will add:

- `.github/workflows/netbox-config-context.yml`
- `ansible/get_config_context.yml`
- `ansible/inventory.yml`
- A README section explaining how to run and interpret the demo

The workflow will be manually triggered with `workflow_dispatch`. A GitHub-hosted Ubuntu runner will install `ansible-core`, then execute the playbook locally.

The playbook will use `ansible.builtin.uri` rather than an external NetBox collection. It will:

1. Query the NetBox REST API for the device named `mvp-router-01`.
2. Assert that exactly one device is returned.
3. Retrieve the device detail endpoint.
4. Print only the effective `config_context` field.

This keeps the MVP small and exposes the underlying NetBox API response directly.

## Credentials and Security

A dedicated read-only NetBox API token will be created for the existing NetBox user. It will be stored only as the GitHub Actions secret `NETBOX_TOKEN` and will not be committed or printed.

The NetBox base URL will be stored as the GitHub Actions repository variable `NETBOX_URL`. The workflow will pass both values to Ansible through environment variables. Context values are deliberately non-sensitive and may appear in Actions output.

## Failure Handling

The workflow will fail with a clear assertion if the device query returns zero or multiple devices. HTTP errors and authentication failures will be surfaced by `ansible.builtin.uri` while the token remains masked by GitHub Actions.

The playbook will validate that the detail response contains `config_context` before printing it. TLS certificate verification will remain enabled.

## Verification

The demonstration is complete when all of the following are observed:

1. NetBox shows `mvp-base-context` as applicable to `mvp-router-01`.
2. NetBox renders the expected hostname, banner, DNS, and NTP lines.
3. The GitHub Actions workflow succeeds on a GitHub-hosted runner.
4. The Actions log shows the same banner, DNS servers, and NTP servers as the NetBox effective context.
5. No token value appears in repository files or Actions output.

## Non-Goals

This MVP will not push configuration to a real device, implement production inventory synchronization, introduce the `netbox.netbox` Ansible collection, schedule recurring runs, or model multiple context weights and merge precedence. Those are natural follow-up demonstrations after the basic data flow is understood.
