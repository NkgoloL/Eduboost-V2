from __future__ import annotations

from scripts.final_gate_classifier import BETA_CRITICAL_IDS, FinalGateRefresh, build_refresh, write_refresh

__all__ = ["BETA_CRITICAL_IDS", "FinalGateRefresh", "build_refresh", "write_refresh"]

if __name__ == "__main__":
    result = write_refresh()
    print(result.beta_decision)
