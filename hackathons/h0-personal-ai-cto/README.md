# H0: Personal AI CTO - Autonomous Business Assistant

**Hackathon 0 - Panaversity AI Employee Project**

[![Status](https://img.shields.io/badge/status-silver%20tier-c0c0c0)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

> An autonomous AI assistant that monitors files, creates action items, and manages workflows with human-in-the-loop approval.

---

## 🎯 Overview

H0 (Personal AI CTO) is a local-first AI employee that:
- **Monitors** a drop folder for incoming files
- **Categorizes** files automatically (documents, code, data, images, videos, archives)
- **Creates** action items in Obsidian vault
- **Logs** all activities with timestamps
- **Implements** Human-In-The-Loop (HITL) approval for sensitive actions
- **Generates** weekly CEO briefings and progress reports

**Silver Tier Achieved:** ✅ Enhanced features operational

---

## 🏗️ Architecture

The system follows a modular architecture with the following components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Drop Folder   │───▶│  File Watcher   │───▶│   Obsidian      │
│ /AI-Employee-   │    │  (monitoring)   │    │     Vault       │
│    Inbox        │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Activity Log   │
                       │   (JSON format)  │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   HITL Workflow  │
                       │ (Human Approval) │
                       └──────────────────┘
```

### Core Components
- **File Watcher**: Monitors the drop folder for new files using polling
- **Categorizer**: Determines file type based on extension
- **Action Creator**: Generates markdown files in the vault
- **Logger**: Records all activities with timestamps
- **HITL Handler**: Manages human approval workflows
- **Dashboard Updater**: Maintains real-time system status
- **CEO Briefing Generator**: Creates weekly executive summaries

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip package manager

### Installation
```bash
cd /mnt/d/Personal-AI-Employee/hackathons/h0-personal-ai-cto
pip3 install -r requirements.txt
mkdir -p /mnt/d/AI-Employee-Inbox
```

### Running
```bash
# Dry-run mode (testing)
python3 watchers/file_watcher.py --dry-run --interval 5

# Production mode
python3 watchers/file_watcher.py \
    --drop-folder /mnt/d/AI-Employee-Inbox \
    --vault vault \
    --interval 10
```

---

## ⚙️ Configuration

### Command Line Options
- `--vault`: Path to the Obsidian vault (default: `vault`)
- `--drop-folder`: Path to the monitored folder (default: `/mnt/d/AI-Employee-Inbox`)
- `--interval`: Polling interval in seconds (default: 10)
- `--dry-run`: Test mode without making changes (default: False)

### Environment Variables
Create a `.env` file in the project root with the following variables:
```bash
# File watcher settings
VAULT_PATH=/mnt/d/Personal-AI-Employee/hackathons/h0-personal-ai-cto/vault
DROP_FOLDER=/mnt/d/AI-Employee-Inbox
CHECK_INTERVAL=10
DRY_RUN=false

# Logging settings
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/activity.log

# HITL workflow settings
HITL_ENABLED=true
APPROVAL_REQUIRED_EXTENSIONS=.pdf,.docx,.xlsx
```

### YAML Configuration
The system also supports configuration via `config/config.yaml`:
```yaml
watcher:
  default_interval: 10
  drop_folder: "/mnt/d/AI-Employee-Inbox"
  vault_path: "./vault"
  file_categories:
    document: [".pdf", ".docx", ".doc", ".txt", ".md", ".rtf"]
    code: [".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cpp", ".c", ".h"]
    data: [".csv", ".xlsx", ".xls", ".json", ".xml", ".sql", ".db"]
    image: [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"]
    video: [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv"]
    archive: [".zip", ".rar", ".7z", ".tar", ".gz"]
```

---

## 📋 How It Works

1. **Drop File** → `/mnt/d/AI-Employee-Inbox`
2. **Auto-Categorize** → Documents, Code, Data, Images, Videos, Archives, Other
3. **Create Action** → `vault/Needs_Action/FILE_*.md`
4. **Log Activity** → `vault/Logs/YYYY-MM-DD.json`
5. **HITL Review** → Human approves/rejects sensitive actions
6. **Update Dashboard** → Real-time status in `vault/Dashboard.md`
7. **Generate Reports** → Weekly CEO briefings in `vault/Briefings/`

---

## 📁 File Categories

| Category | Extensions | Description |
|----------|------------|-------------|
| Documents | .pdf, .docx, .txt, .md, .rtf | Text-based documents |
| Code | .py, .js, .ts, .tsx, .jsx, .java, .cpp, .c, .h | Programming source files |
| Data | .csv, .xlsx, .xls, .json, .xml, .sql, .db | Structured data files |
| Images | .png, .jpg, .jpeg, .gif, .svg, .webp, .bmp | Image files |
| Videos | .mp4, .mov, .avi, .mkv, .wmv, .flv | Video files |
| Archives | .zip, .rar, .7z, .tar, .gz | Compressed archive files |
| Other | Everything else | Files that don't match other categories |

---

## 🧪 Testing
```bash
# Run all tests
python3 -m unittest discover tests/ -v

# Run specific tests
python3 -m unittest tests.test_file_watcher -v

# Run with coverage
python3 -m pytest --cov=. --cov-report=html
```

**Expected:** All tests passing ✅

---

## 📊 Silver Tier Features (Complete)

✅ File monitoring system
✅ Automatic categorization
✅ Action item generation
✅ Activity logging
✅ HITL workflow implemented
✅ Real-time dashboard
✅ CEO briefing generator
✅ Comprehensive documentation
✅ Configuration management
✅ Test suite with coverage

---

## 🏆 Gold Tier Goals

- [ ] MCP server integration
- [ ] Email integration (Gmail watcher)
- [ ] Weekly business audit
- [ ] Error recovery system
- [ ] Real-time notifications
- [ ] Advanced analytics
- [ ] Multi-user support

---

## 🐛 Troubleshooting

### Files not detected?
1. Check drop folder exists: `ls -la /mnt/d/AI-Employee-Inbox`
2. Verify watcher running: `ps aux | grep file_watcher`
3. Check permissions: Files must be readable
4. Confirm interval is appropriate for your use case

### Action items not created?
1. Verify vault directory: `ls -la vault/Needs_Action`
2. Remove `--dry-run` flag
3. Check logs: `cat vault/Logs/*.json`
4. Ensure vault path is writable

### Performance issues?
1. Adjust polling interval based on file activity
2. Limit monitored file types if needed
3. Check system resources (CPU, disk I/O)

### Dashboard not updating?
1. Check if file watcher is running
2. Verify vault permissions
3. Look for errors in console output

---

## 🤝 Contributing

We welcome contributions to improve the Personal AI CTO! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow the existing code style
- Write tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting

---

## 🔐 Security

### Best Practices
- Never commit credentials or API keys
- Use environment variables for sensitive data
- Regularly update dependencies
- Monitor logs for suspicious activity

### Data Handling
- All file processing happens locally
- No external data transmission unless configured
- Logs are stored locally and can be encrypted

---

## 📚 Resources

### Related Projects
- [Hackathon Completion Engine](../../README.md) - The universal framework powering this project
- [Engine Components](../../engine/) - Core engine components
- [Skills Library](../../skills-library/) - Reusable agent skills

### Documentation
- [H0 Specification](../../specs/SPEC-H0-CORE.md) - Technical specification
- [Project Constitution](../../CONSTITUTION.md) - Project-wide rules
- [Engine Specification](../../specs/SPEC-ENGINE-CORE.md) - Framework specification

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

## 👥 Credits

- **Developer:** Asadullah Shafique
- **Hackathon:** Panaversity H0 - January 2026
- **Tools:** Python, Obsidian, Claude Code

---

**Built with ❤️ for Panaversity Hackathon 0**
