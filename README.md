# Skills MCP Server

An MCP (Model Context Protocol) server for loading skills on demand. This helps AI agents manage their context window by loading and unloading skills as needed.

## Overview
This project provides a flexible and dynamic way to provide "skills" to an AI agent. A skill is a piece of text, usually a document, that provides the AI with knowledge or capabilities. The server allows the agent to list available skills and load only the ones relevant to the current task, thus saving precious context window space.

## Setup

This project includes a setup script (`setup_mcp.py`) to manage the MCP server configuration, allowing for both local (project-specific) and global installations.

**Usage:**

```bash
# Install globally (checks existing config, appends or overwrites)
python setup_mcp.py install --global

# Install locally for this project only
python setup_mcp.py install --local

# Check current status of both local and global configs
python setup_mcp.py status

# Remove from global config (keeps other servers)
python setup_mcp.py uninstall --global

# Remove local config completely
python setup_mcp.py uninstall --local
```

Run `python setup_mcp.py --help` for more details on commands and options.

### Environment Setup with `uv`

This project uses `uv` for efficient dependency management and virtual environment creation.

1.  **Create Virtual Environment:**
    ```bash
    uv venv
    ```

2.  **Activate Environment:**
    -   macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```
    -   Windows (PowerShell):
        ```bash
        .venv\Scripts\Activate.ps1
        ```

3.  **Synchronize Dependencies and Create Lock File:**
    ```bash
    uv sync
    ```
    This command reads `pyproject.toml`, creates `uv.lock` (if it doesn't exist), and installs dependencies into `.venv`. Commit `uv.lock` to Git.

4.  **Regenerate Lock File:**
    If `pyproject.toml` is manually changed or branches are switched:
    ```bash
    uv lock
    ```

5.  **Deactivate Environment:**
    ```bash
    deactivate
    ```

## Skill Structure

Skills are organized in a directory structure. The server scans a `skills` directory (by default `~/.capl-skills/skills`, but this is ignored by git in the project).

Each skill must be in its own directory. The name of the directory is the name of the skill. Inside the skill directory, there must be a file named `SKILL.md`.

Example structure:
```
skills/
└── my-awesome-skill/
    ├── SKILL.md
    └── some-other-file.txt
```

In this example, the skill name is `my-awesome-skill`. The content of `SKILL.md` will be loaded as the skill's content. Any other files in the skill's directory are for reference and will not be loaded by the server.

The `SKILL.md` file can have a YAML frontmatter to provide metadata, for example:

```yaml
---
name: my-awesome-skill-override
title: My Awesome Skill
description: This is a skill that does awesome things.
keywords: [awesome, skill]
---

The rest of the file is the skill content.
```
If the `name` is provided in the frontmatter, it will override the folder name.

*This project is maintained by MohamedHamed19m.*