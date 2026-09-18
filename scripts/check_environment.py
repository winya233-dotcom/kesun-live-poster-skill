from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
MANIFEST_PATH = SKILL_DIR / "assets" / "kesun-blue-manifest.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check live-poster-generator runtime")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, object] = {}

    checks["platform"] = platform.platform()
    if os.name != "nt":
        errors.append("Photoshop automation requires Windows")

    if not MANIFEST_PATH.exists():
        errors.append(f"Missing manifest: {MANIFEST_PATH}")
        manifest = {}
    else:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    required_packages = ["PIL", "numpy", "cv2", "mediapipe", "rembg", "onnxruntime"]
    package_state = {name: importlib.util.find_spec(name) is not None for name in required_packages}
    checks["python_packages"] = package_state
    for name, present in package_state.items():
        if not present:
            errors.append(f"Missing Python package: {name}")

    assets: dict[str, bool] = {}
    for spec in manifest.get("templates", {}).values():
        relative = spec.get("file")
        if relative:
            path = SKILL_DIR / "assets" / relative
            assets[relative] = path.exists()
            if not path.exists():
                errors.append(f"Missing template asset: {relative}")
    for spec in manifest.get("fonts", {}).values():
        relative = spec.get("file")
        if relative:
            path = SKILL_DIR / "assets" / relative
            assets[relative] = path.exists()
            if not path.exists():
                errors.append(f"Missing font asset: {relative}")
    checks["assets"] = assets

    photoshop_registered = False
    if os.name == "nt":
        try:
            import winreg

            for hive in (winreg.HKEY_CLASSES_ROOT, winreg.HKEY_LOCAL_MACHINE):
                try:
                    with winreg.OpenKey(hive, r"Photoshop.Application"):
                        photoshop_registered = True
                        break
                except OSError:
                    pass
        except Exception as exc:  # pragma: no cover - platform-specific diagnostic
            warnings.append(f"Could not inspect Photoshop registration: {exc}")
    checks["photoshop_com_registered"] = photoshop_registered
    if os.name == "nt" and not photoshop_registered:
        warnings.append("Photoshop COM registration was not detected; run_photoshop.ps1 may fail")

    result = {
        "ok": not errors,
        "skill_dir": str(SKILL_DIR),
        "python": sys.version,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("OK" if result["ok"] else "FAILED")
        for item in errors:
            print(f"ERROR: {item}")
        for item in warnings:
            print(f"WARNING: {item}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
