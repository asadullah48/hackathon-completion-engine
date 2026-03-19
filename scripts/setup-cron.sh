#!/bin/bash
# Setup cron jobs for Personal AI Employee
# Usage: bash scripts/setup-cron.sh

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="$(which python3)"
VAULT_PATH="$PROJECT_DIR/vault"

echo "Setting up cron jobs for Personal AI Employee"
echo "  Project: $PROJECT_DIR"
echo "  Python:  $PYTHON"
echo "  Vault:   $VAULT_PATH"

# Create cron entries
CRON_ENTRIES=$(cat <<EOF
# Personal AI Employee - Automated Tasks
# CEO Briefing: Every Monday at 9 AM
0 9 * * 1 cd $PROJECT_DIR && $PYTHON watchers/ceo_briefing_generator.py --vault $VAULT_PATH --output-dir $VAULT_PATH/Briefings >> $VAULT_PATH/Logs/cron.log 2>&1

# Gmail check: Every 5 minutes (if token.json exists)
*/5 * * * * cd $PROJECT_DIR && test -f token.json && $PYTHON -c "
from watchers.gmail_watcher import GmailWatcher; from pathlib import Path
w = GmailWatcher(Path('$VAULT_PATH'))
msgs = w.check_for_updates()
for m in msgs:
    w.create_action_file(m)
    w.processed_ids.add(m['id'])
if msgs: w._save_state()
" >> $VAULT_PATH/Logs/cron.log 2>&1

# Dashboard update reminder: Every 6 hours
0 */6 * * * cd $PROJECT_DIR && echo "[$(date)] Dashboard update scheduled" >> $VAULT_PATH/Logs/cron.log 2>&1
EOF
)

# Check if already installed
if crontab -l 2>/dev/null | grep -q "Personal AI Employee"; then
    echo "Cron jobs already installed. Updating..."
    crontab -l 2>/dev/null | grep -v "Personal AI Employee" | grep -v "ceo_briefing" | grep -v "gmail_watcher" | grep -v "Dashboard update" > /tmp/cron_clean
    echo "$CRON_ENTRIES" >> /tmp/cron_clean
    crontab /tmp/cron_clean
    rm /tmp/cron_clean
else
    echo "Installing new cron jobs..."
    (crontab -l 2>/dev/null; echo "$CRON_ENTRIES") | crontab -
fi

echo ""
echo "Current cron jobs:"
crontab -l 2>/dev/null | grep -A1 "Personal AI"
echo ""
echo "Done! Cron jobs installed."
