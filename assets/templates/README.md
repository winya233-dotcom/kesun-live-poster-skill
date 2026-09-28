# Templates are bundled

The six PSD files are stored in `../../asset-packs/*.zip` to stay below GitHub's per-file size limit.

Before reporting missing templates, run this command from the Skill root:

```powershell
python scripts/install_bundled_assets.py
```

The command extracts local repository files only and does not download anything.
