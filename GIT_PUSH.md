How to commit and push this Django project (PowerShell on Windows)

1. Create a repository on GitHub (or your Git remote) and copy the remote URL (e.g. git@github.com:you/repo.git or https://github.com/you/repo.git).

2. Initialize the repo locally (if not already a git repo):

```powershell
cd D:\FILES\safekeep\mou_manager
git init
git add .
git commit -m "Initial commit: Mou manager project"
```

3. Add remote and push (replace <REMOTE_URL> with your repo URL):

```powershell
git remote add origin <REMOTE_URL>
# Create main branch and push
git branch -M main
git push -u origin main
```

4. When you make changes later:

```powershell
git add -A
git commit -m "Describe the change"
git push
```

5. If you use a .env file, NEVER push it. Keep secrets out of git. Use the `.env.example` file as a template.

6. Common tips:
- Use feature branches: `git checkout -b feature/foo`
- Use `git status` and `git diff` to review changes before committing
- If you need to force push (be careful): `git push --force-with-lease`

