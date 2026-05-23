# Contributing to Rota AI

## Getting started

```bash
git clone https://github.com/krthik20050/rota-ai.git
cd rota-ai
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running the app

```bash
python desktop/app/main.py
```

Or use the launcher:

```bash
run.bat
```

## Running tests

```bash
cd desktop
python -m pytest tests/ -v
```

## API keys

Copy `.env.example` to `.env` and fill in your keys.  
**Never commit `.env` or `config.json` — both are gitignored.**

The app stores keys in `%APPDATA%\RotaAI\config.json` (user-local, not in repo).

## Pull requests

1. Fork and create a branch: `git checkout -b fix/your-fix`
2. Keep changes focused — one fix or feature per PR
3. Run tests before submitting
4. Reference any related issue in the PR description

## Security issues

Do **not** open a public issue for security vulnerabilities.  
Email directly or use GitHub's private security advisory feature.  
See [SECURITY.md](SECURITY.md) for the full policy.

## Code style

- Python — follow PEP 8, keep files under 500 lines
- No debug prints or `console.log` left in commits
- Validate input at system boundaries only
- Prefer editing existing files over creating new ones
