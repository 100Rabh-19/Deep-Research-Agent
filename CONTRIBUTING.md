# Contributing

Thanks for improving this project.

## Local Development

1. Create a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and add your local API keys.
4. Run the app with `streamlit run main.py`.

## Pull Request Checklist

- Keep API keys and generated files out of commits.
- Update the README when setup, behavior, or commands change.
- Verify Python files compile before opening a pull request:

```bash
python -m compileall Agent.py Pipeline.py main.py tools.py
```

## Style

- Keep changes focused.
- Prefer clear function names and straightforward control flow.
- Add comments only when they clarify non-obvious behavior.
