How to add and push `db.sqlite3` and `media/` to your Git repo (PowerShell)

Warning: Storing your DB and uploaded media in git may expose sensitive data and can make your repo large. Consider using secure transfer (share externally) or Git LFS for large files.

If you're sure you want to track them, follow these steps.

1. Unignore the files (already done in `.gitignore` as comments). If `.gitignore` still lists them, remove those lines or uncomment them.

2. If these files were previously ignored, you may need to force-add them:

```powershell
cd D:\FILES\safekeep\mou_manager
# Stage the db and media explicitly
git add -f db.sqlite3
git add -f media/
# Stage remaining files
git add -A
# Commit
git commit -m "Add database and media files for sharing"
# Push
git push origin main
```

3. (Optional but recommended) Use Git LFS for large media files
- Install Git LFS: https://git-lfs.github.com/

```powershell
# Install and initialize
git lfs install
# Track common media types
git lfs track "media/**"
# Update git index
git add .gitattributes
# Now add, commit and push as usual
git add db.sqlite3 media/
git commit -m "Add db + media using Git LFS"
git push origin main
```

4. If you only want to temporarily share and then remove DB from Git:

```powershell
# After pushing, remove from git history (careful):
git rm --cached db.sqlite3
git commit -m "Remove db from repo (cached)"
git push
# Consider rewriting history if you want to remove sensitive data completely (use BFG or git filter-branch)
```

5. Troubleshooting
- Large push size: you may hit repo limits on GitHub for large files. Use Git LFS or share via cloud storage instead.
- If `git add` still refuses to add files, confirm there is no separate global gitignore that excludes them.

