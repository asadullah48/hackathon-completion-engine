# vault/ (synthetic sample data)

This folder shows the folder layout the watchers and the approval flow use.
Every file here is invented sample data. The real vault is never committed.

| Folder | What goes here |
|---|---|
| Inbox/ | Raw items dropped in by a watcher |
| Needs_Action/ | Items the agent has triaged and needs to act on |
| Pending_Approval/ | Actions waiting for a human yes/no (human-in-the-loop) |
| Approved/, Rejected/, Done/ | Outcome of each approval |
| Briefings/ | Generated daily/weekly briefings |
| Conversation_Logs/, Logs/ | JSON activity logs |
| Student_Progress/, Course_Materials/, Hackathons/ | Course-companion notes |

Real vault data is blocked by .gitignore. Only files named SAMPLE_* or README.md are tracked.
