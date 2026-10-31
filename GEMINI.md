# GEMINI.md - Personal AI CTO

## Project Overview

This project, "Personal AI CTO," is a Python-based autonomous assistant designed to streamline workflows by monitoring a directory for new files. When a new file is detected, the assistant categorizes it, creates a corresponding action item in an Obsidian vault, and logs the activity. For sensitive actions, it employs a Human-in-the-Loop (HITL) approval process, ensuring user oversight.

The project is structured around a core `FileWatcher` class that manages file detection and processing. It uses a structured Obsidian vault for knowledge management, task tracking, and workflow orchestration. The HITL process is managed through Markdown files in a designated `Pending_Approval` directory within the vault.

### Key Technologies

*   **Language:** Python 3.11+
*   **Core Libraries:**
    *   `watchdog`: For file system monitoring.
    *   `pydantic`: For data validation.
    *   `jinja2`: For template rendering.
    *   `click`: For building the command-line interface.
*   **Workflow Management:** Obsidian vault.

### Architecture

The system is composed of several key components:

*   **`watchers/`**: Contains the file monitoring scripts, with `file_watcher.py` as the primary entry point.
*   **`vault/`**: An Obsidian vault that serves as the central hub for tasks, logs, and approvals. It is organized into directories such as `Needs_Action`, `Pending_Approval`, `Approved`, `Rejected`, and `Logs`.
*   **`skills/`**: Markdown files that define the behavior and workflows for the AI agent, such as the `hitl-approval-manager.md`.
*   **`config/`**: Contains configuration files, primarily `config.yaml`, which defines paths, file categories, and other settings.
*   **`tests/`**: Unit tests for ensuring the reliability of the system.

## Building and Running

### Prerequisites

*   Python 3.11+
*   pip (Python package installer)

### Installation

1.  **Install dependencies:**
    ```bash
    pip3 install -r requirements.txt
    ```

### Running the Application

The primary application is the file watcher, which monitors a specified directory for new files.

*   **Run in production mode:**
    ```bash
    python3 watchers/file_watcher.py --drop-folder /path/to/your/inbox --vault /path/to/your/vault
    ```

*   **Run in dry-run mode (for testing):**
    This will simulate the file watching process without making any changes to the vault.
    ```bash
    python3 watchers/file_watcher.py --dry-run
    ```

### Running Tests

To ensure the integrity of the codebase, run the unit tests:

```bash
python3 -m unittest discover tests/ -v
```

## Development Conventions

### Code Style

The project follows the `black` code style for consistent formatting. To format your code, run:

```bash
black .
```

### Type Checking

`mypy` is used for static type checking. To check for type errors, run:

```bash
mypy .
```

### Linting

`pylint` is used to enforce coding standards and identify potential errors. To lint the code, run:

```bash
pylint **/*.py
```

### Human-in-the-Loop (HITL) Workflow

When adding new features that require user approval, follow the HITL workflow defined in `skills/hitl-approval-manager.md`. This involves creating a Markdown file in the `vault/Pending_Approval/` directory with a structured request for the user to approve or reject.
