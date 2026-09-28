from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
PACK_DIR = SKILL_DIR / "asset-packs"

PACKS = {
    "templates-background.zip": SKILL_DIR / "assets" / "templates",
    "templates-video-and-tag.zip": SKILL_DIR / "assets" / "templates",
    "templates-poster-and-enterprise.zip": SKILL_DIR / "assets" / "templates",
    "fonts.zip": SKILL_DIR / "assets" / "fonts",
    "models.zip": SKILL_DIR / "assets" / "models",
}

EXPECTED = [
    SKILL_DIR / "assets" / "templates" / "01 直播背景.psd",
    SKILL_DIR / "assets" / "templates" / "03 直播图(预留出血位版本).psd",
    SKILL_DIR / "assets" / "templates" / "常规蓝色-宣传海报.psd",
    SKILL_DIR / "assets" / "templates" / "集团直播标签贴tag.psd",
    SKILL_DIR / "assets" / "templates" / "直播封面【企微】-800x640.psd",
    SKILL_DIR / "assets" / "templates" / "直播封面【企微直播用】1080x2160.psd",
    SKILL_DIR / "assets" / "fonts" / "阿里妈妈数黑体.ttf",
    SKILL_DIR / "assets" / "fonts" / "AlimamaShuHeiTi-Bold.otf",
    SKILL_DIR / "assets" / "fonts" / "FZLTHJW.TTF",
    SKILL_DIR / "assets" / "fonts" / "FZLTTHJW.TTF",
    SKILL_DIR / "assets" / "models" / "blaze_face_short_range.tflite",
    SKILL_DIR / "assets" / "models" / "pose_landmarker_lite.task",
]


def safe_extract(archive_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            member_path = Path(member.filename)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise ValueError(f"Unsafe archive member: {member.filename}")
        archive.extractall(destination)


def install(force: bool = False) -> list[Path]:
    missing = [path for path in EXPECTED if force or not path.exists()]
    if not missing:
        return []

    for pack_name, destination in PACKS.items():
        archive_path = PACK_DIR / pack_name
        if not archive_path.exists():
            raise FileNotFoundError(f"Missing bundled asset pack: {archive_path}")
        safe_extract(archive_path, destination)

    remaining = [path for path in EXPECTED if not path.exists()]
    if remaining:
        names = "\n".join(str(path) for path in remaining)
        raise RuntimeError(f"Bundled assets were not restored:\n{names}")
    return EXPECTED


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore bundled templates, fonts, and models")
    parser.add_argument("--force", action="store_true", help="Overwrite assets from the bundled archives")
    args = parser.parse_args()
    restored = install(args.force)
    if restored:
        print(f"Restored {len(restored)} bundled assets")
    else:
        print("Bundled assets are already installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
