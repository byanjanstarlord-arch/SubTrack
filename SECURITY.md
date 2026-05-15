Sensitive files and secrets
===========================

This repository should never contain secrets or credentials in the git history or commits. The following files/patterns are sensitive and must not be committed:

- `.env`, `.env.*`, `.env.local` — environment variables containing `SECRET_KEY`, DB credentials, API keys
- `.git-credentials`, `.pgpass`, `.aws/` — VCS/system credentials
- `*.pem`, `*.key`, `*.p12`, `*.pfx` — private keys and certificates
- `db.sqlite3`, `*.sqlite3` — local DB files

Local protections applied
-------------------------

- `.gitignore` updated to ignore the above patterns.
- A local Git pre-commit hook was added at `.git/hooks/pre-commit` to block accidental commits of these files. This hook is local to your repository clone and is not committed.

If you accidentally committed secrets
----------------------------------

1. Remove the file and commit the removal:

   git rm --cached .env
   git commit -m "Remove accidentally committed .env"

2. Rotate any credentials that may have been exposed (API keys, DB passwords, OAuth secrets).

3. If secrets were in earlier commits, rewrite history to remove them (use `git filter-repo` or `bfg`). Example with `git filter-repo` (install separately):

   git filter-repo --path .env --invert-paths

4. Force-push rewritten history to the remote (only if you understand consequences):

   git push --force

Need help rotating or purging secrets? I can guide you through the safe steps and commands.