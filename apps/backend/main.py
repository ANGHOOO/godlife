from __future__ import annotations

import os
import sys
from pathlib import Path


def _ensure_backend_source_on_path() -> None:
    project_candidates = (
        Path(__file__).resolve().parent / "src",
        Path(__file__).resolve().parent / ".." / "backend" / "src",
        Path(__file__).resolve().parent.parent / "src",
        Path(__file__).resolve().parents[2] / "apps" / "backend" / "src",
        Path.cwd() / "apps" / "backend" / "src",
        Path.cwd() / "src",
    )

    for src_root in project_candidates:
        if src_root.exists():
            src_root = src_root.resolve()
            if str(src_root) not in sys.path:
                sys.path.insert(0, str(src_root))
            return


def main() -> None:
    _ensure_backend_source_on_path()
    from godlife_backend.adapter.webapi.app import app

    uvicorn = __import__("uvicorn")

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
