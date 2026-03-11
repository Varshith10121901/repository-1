# Contributing to repository-1

Thank you for your interest in contributing! This project is a collection of AI/Gemini/NLP experiments and web UI demos. Contributions that improve code quality, fix bugs, or add new experiments are very welcome.

## Getting Started

1. **Fork** the repository and create a new branch for your feature or fix.
2. Make your changes following the guidelines below.
3. Open a **Pull Request** with a clear description of what you changed and why.

## Guidelines

### Code Style
- Follow [PEP 8](https://pep8.org/) for Python files.
- Use meaningful variable and function names.
- Include docstrings for modules and public functions.

### Secrets & API Keys
> ⚠️ **Never commit API keys, passwords, or other secrets.**
- Store sensitive values in environment variables or a `.env` file (already in `.gitignore`).
- Use `os.getenv("MY_API_KEY")` in your code instead of hardcoding values.

### Adding New Scripts
- Place Python scripts at the repository root or in a relevant subfolder.
- If your script requires additional packages, update `requirements.txt` (or create one if it doesn't exist) and mention the dependency in your PR description.

### HTML / JavaScript
- Keep front-end files alongside their companion Python backend files when possible.
- Test pages in at least one modern browser before submitting.

## Reporting Issues
- Use [GitHub Issues](../../issues) to report bugs or request features.
- Include steps to reproduce, expected behavior, and actual behavior.

## Code of Conduct
Be respectful and constructive in all interactions. Harassment of any kind will not be tolerated.
