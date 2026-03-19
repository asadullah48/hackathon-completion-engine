# H0: Personal AI CTO - Autonomous Business Assistant

**Hackathon 0 - Panaversity AI Employee Project**

[![Status](https://img.shields.io/badge/status-bronze%20tier-cd7f32)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

> An autonomous AI assistant that monitors files, creates action items, and manages workflows with human-in-the-loop approval for sensitive actions.

---

## 🎯 Overview

H0 (Personal AI CTO) is a local-first AI employee that:
- **Monitors** a drop folder for incoming files
- **Categorizes** files automatically (documents, code, data, images, videos, archives)
- **Creates** action items in Obsidian vault
- **Logs** all activities with timestamps
- **Implements** Human-In-The-Loop (HITL) approval for sensitive actions
- **Organizes** work using a structured vault system

**Bronze Tier Achieved:** ✅ All core features operational

---

## 📁 Project Structure
```
h0-personal-ai-cto/
├── watchers/              # File monitoring scripts
│   ├── base_watcher.py    # Base watcher class
│   ├── file_watcher.py    # Main file watcher
│   └── gmail_watcher.py   # Email watcher (future)
├── skills/                # AI agent skills
│   ├── hitl-approval-manager.md
│   ├── dashboard-updater.md
│   └── ceo-briefing-generator.md
├── vault/                 # Obsidian knowledge base
│   ├── Dashboard.md       # Status dashboard
│   ├── Handbook.md        # Operations manual
│   ├── Business_Goals.md  # Objectives & KPIs
│   ├── Needs_Action/      # Items requiring attention
│   ├── Pending_Approval/  # Awaiting human decision
│   ├── Approved/          # Human-approved actions
│   ├── Rejected/          # Declined actions
│   ├── Done/              # Completed items
│   ├── Logs/              # Activity logs (JSON)
│   └── Briefings/         # CEO summaries
├── tests/                 # Unit tests
├── config/                # Configuration files
└── requirements.txt       # Python dependencies
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Obsidian (optional, for viewing vault)
- WSL/Linux or Windows with Python

### Installation

1. **Navigate to project**
```bash
cd /mnt/d/Personal-AI-Employee/hackathons/h0-personal-ai-cto
```

2. **Install dependencies**
```bash
pip3 install -r requirements.txt
```

3. **Set up drop folder**
```bash
mkdir -p /mnt/d/AI-Employee-Inbox
```

4. **Configure environment (optional)**
```bash
cp .env.example .env
# Edit .env with your settings
```

### Running the File Watcher

**Dry-run mode (safe testing):**
```bash
python3 watchers/file_watcher.py --dry-run --interval 5
```

**Production mode:**
```bash
python3 watchers/file_watcher.py \
    --drop-folder /mnt/d/AI-Employee-Inbox \
    --vault vault \
    --interval 10
```

**With custom settings:**
```bash
python3 watchers/file_watcher.py \
    --drop-folder /path/to/inbox \
    --vault /path/to/vault \
    --interval 30
```

---

## 📋 How It Works

### 1. File Detection
Drop any file into `/mnt/d/AI-Employee-Inbox`

### 2. Automatic Categorization
Files are categorized by extension:

| Category | Extensions |
|----------|------------|
| **Documents** | .pdf, .docx, .txt, .md, .rtf |
| **Code** | .py, .js, .ts, .java, .cpp, .h |
| **Data** | .csv, .json, .xlsx, .xml, .sql, .db |
| **Images** | .png, .jpg, .gif, .svg, .webp, .bmp |
| **Videos** | .mp4, .mov, .avi, .mkv, .wmv, .flv |
| **Archives** | .zip, .rar, .7z, .tar, .gz |
| **Other** | everything else |

### 3. Action Item Creation
FileWatcher creates a markdown file in `vault/Needs_Action/`:
```markdown
# FILE DETECTED: document.pdf

**Detected:** 2026-01-23 10:30:00
**Category:** document
**Priority:** Medium

## File Information
- **Name:** document.pdf
- **Size:** 1.2 MB
- **Location:** /mnt/d/AI-Employee-Inbox/document.pdf

## Suggested Actions
- [ ] Review document content
- [ ] Extract key information
- [ ] File in appropriate project folder
- [ ] Update related documentation

## Status
- [x] File detected
- [ ] Action reviewed by human
- [ ] Action completed
```

### 4. Activity Logging
All activities logged to `vault/Logs/YYYY-MM-DD.json`:
```json
{
  "date": "2026-01-23",
  "activities": [
    {
      "timestamp": "2026-01-23T10:30:00",
      "type": "file_detected",
      "details": {
        "filename": "document.pdf",
        "category": "document",
        "action_item": "vault/Needs_Action/FILE_20260123_103000_document.md"
      }
    }
  ]
}
```

### 5. Human-In-The-Loop Workflow
For sensitive actions:
1. AI creates approval request in `vault/Pending_Approval/`
2. Human reviews and moves to `vault/Approved/` or `vault/Rejected/`
3. System executes approved actions
4. Completed items move to `vault/Done/`

---

## 🧪 Running Tests

**Run all tests:**
```bash
python3 -m unittest discover tests/ -v
```

**Run specific test:**
```bash
python3 -m unittest tests.test_file_watcher -v
```

**Expected output:**
```
test_categorize_file_code ... ok
test_categorize_file_data ... ok
test_categorize_file_document ... ok
test_categorize_file_other ... ok
test_initialization ... ok

Ran 5 tests in 0.015s

OK
```

---

## 🛠️ Configuration

### Command-Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--drop-folder` | `/mnt/d/AI-Employee-Inbox` | Folder to monitor |
| `--vault` | `vault` | Vault directory path |
| `--interval` | `10` | Check interval (seconds) |
| `--dry-run` | `False` | Test mode (no changes) |

### Environment Variables
Create `.env` file (see `.env.example`):
```bash
DROP_FOLDER=/mnt/d/AI-Employee-Inbox
VAULT_PATH=vault
CHECK_INTERVAL=10
DRY_RUN=False
```

---

## 📊 Bronze Tier Features (Complete)

✅ **Core Functionality**
- [x] File monitoring system
- [x] Automatic categorization (7 categories)
- [x] Action item generation
- [x] Activity logging
- [x] State persistence

✅ **HITL Workflow**
- [x] Approval request system
- [x] Human decision framework
- [x] Action execution tracking

✅ **Documentation**
- [x] Complete README
- [x] Usage examples
- [x] Troubleshooting guide

✅ **Testing**
- [x] Unit tests passing (5/5)
- [x] Integration tests passing
- [x] E2E workflow validated

---

## 🔮 Future Enhancements (Silver/Gold Tier)

### Silver Tier Roadmap
- [ ] Email integration (Gmail watcher)
- [ ] CEO briefing generator
- [ ] Advanced dashboard with auto-refresh
- [ ] Multiple watcher types

### Gold Tier Roadmap
- [ ] Cross-domain integration (Personal + Business)
- [ ] MCP server for external actions
- [ ] Weekly business audit
- [ ] Error recovery system
- [ ] Comprehensive audit logging

---

## 🐛 Troubleshooting

### FileWatcher not detecting files
**Issue:** Files dropped but no action items created

**Solutions:**
1. Check drop folder exists: `ls -la /mnt/d/AI-Employee-Inbox`
2. Verify watcher is running: `ps aux | grep file_watcher`
3. Check file permissions: Files must be readable
4. Increase interval: Try `--interval 30`

### Action items not created
**Issue:** Watcher running but no files in `vault/Needs_Action/`

**Solutions:**
1. Verify vault directory: `ls -la vault/Needs_Action`
2. Check dry-run mode: Remove `--dry-run` flag
3. Review logs: `cat vault/Logs/*.json`
4. Test manually with Python import

### Import errors
**Issue:** `ModuleNotFoundError` when running watcher

**Solutions:**
1. Install dependencies: `pip3 install -r requirements.txt`
2. Check Python version: `python3 --version` (need 3.11+)
3. Verify PYTHONPATH: Run from project root

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👥 Contributors

- **Asadullah Shafique** - Lead Developer
- **Panaversity** - Hackathon Organizers

---

## 🙏 Acknowledgments

- Panaversity Hackathon 0 organizers
- Claude Code for development assistance
- Obsidian community for vault inspiration

---

## 📞 Support

- **Issues:** Create issue in repository
- **Questions:** Join Wednesday Research Meeting
- **Feedback:** Submit via hackathon form

---

**Built with ❤️ for Panaversity Hackathon 0 - January 2026**
