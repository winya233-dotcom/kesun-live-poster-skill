# Templates are bundled

The six PSD files are stored in `../../asset-packs/`. Large ZIP files are split into approximately 8 MB `.partNNN` files to survive proxy and installer limits.

Before reporting missing templates, run this command from the Skill root:

```powershell
python scripts/install_bundled_assets.py
```

The command extracts local repository files only and does not download anything.
