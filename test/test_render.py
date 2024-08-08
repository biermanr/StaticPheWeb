"""Test rendering of HTML templates."""

from pathlib import Path
from typing import Any

from spheweb import process


def test_render(tmpdir: Any) -> None:
    """Test the render_html function with mock data."""
    d = Path(tmpdir)
    data = {
        "2023-01-01": 100,
        "2023-02-01": 20,
        "2023-03-01": 30,
        "2023-04-01": 40,
        "2023-05-01": 50,
        "2023-06-01": 60,
        "2023-07-01": 70,
        "2023-08-01": 80,
        "2023-09-01": 90,
        "2023-10-01": 100,
        "2023-11-01": 90,
        "2023-12-01": 80,
        "2024-01-01": 70,
    }

    process.render_html(d, {"name": "Dave", "data": data})
