# Security Policy

## Supported Versions

This project is maintained on the default branch.

## Reporting a Vulnerability

Please do not open public issues for secrets, credential leaks, or exploitable security problems. Report them privately to the repository owner.

## Secret Handling

- Store `HUGGINGFACEHUB_API_TOKEN` and `TAVILY_API_KEY` only in `.env` or your deployment secret manager.
- Never commit `.env`, logs containing secrets, or downloaded credentials.
- Rotate any API key that may have been committed or exposed.
