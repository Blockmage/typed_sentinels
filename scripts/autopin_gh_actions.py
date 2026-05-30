#!/usr/bin/env -S uv run --python=3.13 --script

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "httpx>=0.28.1",
#     "ruamel-yaml>=0.19.1",
# ]
# ///

# pyright: reportMissingImports=none
# pyright: reportUnknownArgumentType=none
# pyright: reportUnknownMemberType=none
# pyright: reportUnknownVariableType=none

import os
import sys
from dataclasses import dataclass

import httpx
from ruamel.yaml import YAML


@dataclass(slots=True)
class ActionInfo:
    repo: str
    owner: str
    name: str
    current_ref: str


class GitHubActionPinner:
    __slots__ = ('__weakref__', 'client', 'yaml')

    def __init__(self, token: str | None = None) -> None:
        headers = {'Accept': 'application/vnd.github+json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.client = httpx.Client(
            base_url='https://api.github.com',
            headers=headers,
            follow_redirects=True,
            max_redirects=10,
            timeout=30,
        )

        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.width = 4096  # Prevent unwanted line wrapping

    def _get_latest_tag_and_sha(self, owner: str, repo: str) -> tuple[str, str]:
        """Fetch the latest release tag and its commit SHA."""
        # Get latest release
        resp = self.client.get(f'/repos/{owner}/{repo}/releases/latest')

        if resp.status_code == 200:
            tag = resp.json()['tag_name']
        else:
            # Fallback to tags if no 'release' exists
            resp = self.client.get(f'/repos/{owner}/{repo}/tags')
            resp.raise_for_status()
            tag = resp.json()[0]['name']

        # Get the SHA for that tag
        resp = self.client.get(f'/repos/{owner}/{repo}/commits/{tag}')
        resp.raise_for_status()
        return tag, resp.json()['sha']

    def update_workflow(self, file_path: str) -> None:
        with open(file_path) as f:
            data = self.yaml.load(f)

        if not data or 'jobs' not in data:
            return

        for job in data['jobs'].values():
            if 'steps' not in job:
                continue

            for step in job['steps']:
                if 'uses' in step and not step['uses'].startswith(('docker:', './')):
                    original_uses = step['uses']

                    # Parse owner/repo@ref
                    # Handles: actions/checkout@v4 or actions/checkout@sha # v4
                    base_part = original_uses.split('#')[0].strip()
                    repo_full, _ = base_part.split('@')
                    owner, repo = repo_full.split('/')

                    try:
                        tag, sha = self._get_latest_tag_and_sha(owner, repo)

                        # Update the 'uses' value to the SHA
                        step['uses'] = f'{owner}/{repo}@{sha}'

                        # Add or update the end-of-line comment with the tag
                        step.yaml_add_eol_comment(f'{tag}', key='uses')

                        print(f'Updated {repo_full}: {tag} -> {sha[:7]}')
                    except Exception as e:
                        print(f'Failed to update {repo_full}: {e}', file=sys.stderr)

        with open(file_path, 'w') as f:
            self.yaml.dump(data, f)


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: ./pin_actions.py <path_to_workflow.yml>')
        sys.exit(1)

    # Use GITHUB_TOKEN if available to avoid rate limits
    token = os.getenv('GITHUB_TOKEN')
    pinner = GitHubActionPinner(token=token)

    for arg in sys.argv[1:]:
        if os.path.isfile(arg):
            pinner.update_workflow(arg)


if __name__ == '__main__':
    main()
