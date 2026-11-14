import os
from pathlib import Path

import pandas as pd
import pytest

from src.openads_reanalysis import compute_results, load_snapshot


@pytest.mark.skipif(not os.getenv("OPENADS_TEST_DATA"), reason="author-held ADS snapshot not configured")
def test_full_record_level_replay():
    data, _ = load_snapshot(Path(os.environ["OPENADS_TEST_DATA"]), strict_expected=True)
    results = compute_results(data)
    assert results["report"]["raw_assignments"] == 10317
    assert results["report"]["unique_bibcodes"] == 9513
    assert results["report"]["metadata_conflicts"] == 0
    expected = pd.read_csv(Path(__file__).resolve().parents[1] / "results/canonical/target_metrics.csv")
    pd.testing.assert_frame_equal(results["target_metrics"], expected, check_exact=False, rtol=1e-12, atol=1e-12)
