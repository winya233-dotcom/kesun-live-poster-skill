from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_DIR / "scripts"
MANIFEST = SKILL_DIR / "assets" / "kesun-blue-manifest.json"


def run(command: list[str]) -> None:
    print("RUN", " ".join(command))
    subprocess.run(command, check=True)


def validate(request: dict[str, object]) -> None:
    required = ["suite_type", "title", "display_time", "program", "people"]
    missing = [key for key in required if not request.get(key)]
    if missing:
        raise ValueError("Missing request fields: " + ", ".join(missing))
    if request["suite_type"] not in {"enterprise_wechat", "wechat_channels"}:
        raise ValueError("suite_type must be enterprise_wechat or wechat_channels")
    if request["program"] not in {"玩转产品", "AI工作坊", "顺道聊聊"}:
        raise ValueError("Unsupported program")
    if not 1 <= len(request["people"]) <= 3:
        raise ValueError("The template supports one to three people")


def resolve_input_paths(request: dict[str, object], request_dir: Path) -> None:
    def resolve(value: str) -> str:
        path = Path(value)
        if not path.is_absolute():
            path = request_dir / path
        return str(path.resolve())

    if request.get("qr_code_path"):
        request["qr_code_path"] = resolve(str(request["qr_code_path"]))
    for person in request["people"]:
        for key in ("portrait_path", "cutout_path"):
            if person.get(key):
                person[key] = resolve(str(person[key]))


def main() -> None:
    parser = argparse.ArgumentParser(description="End-to-end Kesun livestream suite pipeline")
    parser.add_argument("request", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="Prepare layouts and Photoshop job without opening Photoshop")
    parser.add_argument("--skip-ppt", action="store_true")
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()

    request_path = args.request.resolve()
    request = json.loads(request_path.read_text(encoding="utf-8"))
    validate(request)
    resolve_input_paths(request, request_path.parent)
    output = args.output_dir.resolve()
    work = output / ".work"
    cutouts = work / "cutouts"
    labels = work / "labels"
    for folder in (output / "png", output / "pptx", work, cutouts, labels, work / "ppt-assets"):
        folder.mkdir(parents=True, exist_ok=True)

    for person in request["people"]:
        if person.get("cutout_path"):
            source = Path(person["cutout_path"])
            if not source.exists():
                raise FileNotFoundError(source)
            continue
        portrait = Path(person["portrait_path"])
        if not portrait.exists():
            raise FileNotFoundError(portrait)
        destination = cutouts / f"{person['id']}-birefnet.png"
        run([args.python, str(SCRIPTS / "remove_background.py"), str(portrait), str(destination)])
        person["cutout_path"] = str(destination.resolve())

    resolved_request = work / "request.resolved.json"
    resolved_request.write_text(json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8")
    layout = work / "portrait-layout.json"
    run([args.python, str(SCRIPTS / "analyze_portraits.py"), str(resolved_request), str(work), "--manifest", str(MANIFEST)])
    run([args.python, str(SCRIPTS / "render_labels.py"), str(layout), str(labels), "--manifest", str(MANIFEST)])
    run([
        args.python, str(SCRIPTS / "build_photoshop_job.py"), str(resolved_request), str(layout), str(output),
        "--manifest", str(MANIFEST), "--include-ppt-assets",
    ])
    job = work / "photoshop-job.json"

    if args.dry_run:
        print(f"Dry run complete: {job}")
        return

    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        raise RuntimeError("PowerShell is required to launch Photoshop")
    run([powershell, "-ExecutionPolicy", "Bypass", "-File", str(SCRIPTS / "run_photoshop.ps1"), "-Job", str(job)])

    if not args.skip_ppt:
        node = os.environ.get("RUNTIME_NODE") or shutil.which("node")
        if not node:
            raise RuntimeError("Node.js is required for PPTX output")
        run([
            node, str(SCRIPTS / "build_editable_ppt.mjs"),
            "--request", str(resolved_request), "--layout", str(layout), "--job", str(job),
            "--manifest", str(MANIFEST), "--output-dir", str(output / "pptx"),
        ])

    print(output)


if __name__ == "__main__":
    main()
