"""Saved work survives a backend restart (Docker volume kept)."""
import subprocess
import time

import requests

from conftest import LIVE_API, ROOT


def test_lead_and_status_survive_backend_restart(test_prospects):
    pid = test_prospects["SAVE4"]
    lead = requests.post(f"{LIVE_API}/prospects/{pid}/save", timeout=15).json()["lead"]
    requests.post(f"{LIVE_API}/leads/{lead['id']}/status", json={"status": "qualified"}, timeout=15)

    subprocess.run(["docker", "compose", "restart", "backend"], cwd=ROOT, check=True, capture_output=True)
    for _ in range(60):
        try:
            if requests.get(f"{LIVE_API}/health", timeout=2).status_code == 200:
                break
        except requests.RequestException:
            pass
        time.sleep(1)

    after = requests.get(f"{LIVE_API}/prospects/{pid}", timeout=15).json()
    assert after["lead"]["id"] == lead["id"]
    assert after["lead"]["status"] == "qualified"
