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
