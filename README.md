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
