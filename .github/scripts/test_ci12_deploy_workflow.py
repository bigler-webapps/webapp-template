"""Structural regression tests for CI-12: the deploy job publishes its own
image before pulling it, per the shared workflow-templates pattern.

Note: this repo's deploy job is skipped by the is_template guard, so it
cannot be verified by a green deploy -- these structural tests are the
only verification available here.

Run with: python .github/scripts/test_ci12_deploy_workflow.py
"""
from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
MAIN_WORKFLOW = (ROOT / ".github/workflows/main.yml").read_text(encoding="utf-8")


class CI12DeployWorkflowTests(unittest.TestCase):
    def test_publish_step_precedes_deploy_app_step(self):
        self.assertLess(
            MAIN_WORKFLOW.index("actions/publish-backend-image@"),
            MAIN_WORKFLOW.index("actions/deploy-app@"),
        )

    def test_both_pins_are_v2_9_0(self):
        self.assertIn("actions/publish-backend-image@v2.9.0", MAIN_WORKFLOW)
        self.assertIn("actions/deploy-app@v2.9.0", MAIN_WORKFLOW)

    def test_main_yml_grants_packages_write(self):
        """The most likely slip across eleven repos, per the WO's own risk
        list: the pin bumps but this permission doesn't, and the publish
        step fails to push on the very next deploy."""
        self.assertIn("packages: write", MAIN_WORKFLOW)

    def test_publish_and_deploy_reuse_the_same_resolved_sha(self):
        """image_tag must come from the SAME resolve_sha step for both the
        publish step and deploy-app -- a second independent resolution would
        defeat CI-11's whole point (build one commit, deploy under another
        commit's tag)."""
        self.assertEqual(
            MAIN_WORKFLOW.count("image_tag: ${{ steps.resolve_sha.outputs.sha }}"),
            2,
        )

    def test_publish_step_passes_the_mui_license_key(self):
        self.assertIn("vite_app_mui_license_key: ${{ secrets.VITE_APP_MUI_LICENSE_KEY }}", MAIN_WORKFLOW)

    def test_both_publish_and_deploy_receive_github_token(self):
        """Regression: deploy-app's OWN github_token input (for the remote
        GHCR login, separate from the publish step's) was missed across the
        whole rollout on the first pass -- deploy failed with 'GITHUB_TOKEN
        is required for pull-based deploys' despite the publish step
        succeeding. cockpit's proven shape passes it to both steps."""
        self.assertEqual(
            MAIN_WORKFLOW.count("github_token: ${{ secrets.GITHUB_TOKEN }}"),
            2,
        )


if __name__ == "__main__":
    unittest.main()
