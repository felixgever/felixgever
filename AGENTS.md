# AGENTS.md

## Cursor Cloud specific instructions

This is a GitHub profile README repository containing only a `README.md` file. There is no application code, build system, test suite, or runtime service.

### Linting

Run `markdownlint README.md` to lint the markdown file. The tool is installed globally via npm.

### Preview

Run `grip README.md 0.0.0.0:6419` to start a GitHub-flavored markdown preview server at port 6419. Open `http://localhost:6419` in a browser to see the rendered README as it would appear on GitHub. Grip requires network access to download GitHub CSS on first run (cached after that in `~/.grip/cache-*`).

### Notes

- There are no dependencies to install, no tests to run, and no build steps.
- The repo has two pre-existing markdownlint warnings (MD041 missing top-level heading, MD013 line length) which are inherent to the profile README format and not bugs.
