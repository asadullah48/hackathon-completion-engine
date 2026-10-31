import json
import os
import requests
from typing import Dict, Any
from datetime import datetime


class DiscordIntegration:
    def __init__(self, config_path: str = "discord_config.json"):
        """
        Initialize Discord integration with configuration
        """
        self.config = self.load_config(config_path)
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file
        """
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def send_webhook_message(self, webhook_url: str, embed_data: Dict[str, Any]):
        """
        Send a message to a Discord webhook with embedded data
        """
        payload = {
            "embeds": [embed_data],
            "username": "GitHub Activity Bot",
            "avatar_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
        }
        
        response = requests.post(webhook_url, json=payload)
        
        if response.status_code == 204:
            print(f"Successfully sent message to Discord webhook")
        else:
            print(f"Failed to send message to Discord webhook: {response.status_code}")
            
        return response
    
    def handle_push_event(self, payload: Dict[str, Any]):
        """
        Handle GitHub push event
        """
        repository = payload.get('repository', {})
        commits = payload.get('commits', [])
        ref = payload.get('ref', '')
        
        # Extract branch name from ref
        branch = ref.split('/')[-1] if ref else 'unknown'
        
        for commit in commits:
            author = commit.get('author', {}).get('name', 'Unknown')
            message = commit.get('message', '')[:256]  # Limit message length
            url = commit.get('url', '')
            
            embed = {
                "title": f"Commit to {repository.get('name', 'unknown')} ({branch})",
                "description": f"**{author}** committed to `{branch}`\n\n{message}",
                "url": url,
                "color": 0x28a745,  # Green color for commits
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "GitHub Commit Notification"
                }
            }
            
            # Find the appropriate webhook for commits
            webhook_url = self.config['webhooks']['commits']['url']
            self.send_webhook_message(webhook_url, embed)
    
    def handle_issue_event(self, payload: Dict[str, Any]):
        """
        Handle GitHub issue event
        """
        action = payload.get('action', 'opened')
        issue = payload.get('issue', {})
        repository = payload.get('repository', {})
        
        # Determine color based on action
        color_map = {
            'opened': 0x28a745,  # Green
            'closed': 0xdc3545,  # Red
            'reopened': 0xfd7e14  # Orange
        }
        color = color_map.get(action, 0x007bff)  # Blue as default
        
        embed = {
            "title": f"Issue #{issue.get('number')} {action.title()}",
            "description": f"**{issue.get('title', 'No Title')}**\n\n{issue.get('body', '')[:512]}...",
            "url": issue.get('html_url', ''),
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "author": {
                "name": issue.get('user', {}).get('login', 'Unknown'),
                "icon_url": issue.get('user', {}).get('avatar_url', '')
            },
            "fields": [
                {
                    "name": "Repository",
                    "value": repository.get('name', 'Unknown'),
                    "inline": True
                },
                {
                    "name": "Labels",
                    "value": ", ".join([label.get('name', '') for label in issue.get('labels', [])]) or 'None',
                    "inline": True
                }
            ],
            "footer": {
                "text": "GitHub Issue Notification"
            }
        }
        
        # Find the appropriate webhook for issues
        webhook_url = self.config['webhooks']['issues']['url']
        self.send_webhook_message(webhook_url, embed)
    
    def handle_discussion_event(self, payload: Dict[str, Any]):
        """
        Handle GitHub discussion event
        """
        action = payload.get('action', 'created')
        discussion = payload.get('discussion', {})
        repository = payload.get('repository', {})
        
        # Determine color based on action
        color_map = {
            'created': 0x28a745,  # Green
            'closed': 0xdc3545,   # Red
        }
        color = color_map.get(action, 0x007bff)  # Blue as default
        
        embed = {
            "title": f"Discussion: {discussion.get('title', 'No Title')}",
            "description": f"{discussion.get('body', '')[:512]}...",
            "url": discussion.get('html_url', ''),
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "author": {
                "name": discussion.get('user', {}).get('login', 'Unknown'),
                "icon_url": discussion.get('user', {}).get('avatar_url', '')
            },
            "fields": [
                {
                    "name": "Repository",
                    "value": repository.get('name', 'Unknown'),
                    "inline": True
                },
                {
                    "name": "Category",
                    "value": discussion.get('category', {}).get('name', 'General'),
                    "inline": True
                },
                {
                    "name": "Comments",
                    "value": str(discussion.get('comments', 0)),
                    "inline": True
                }
            ],
            "footer": {
                "text": "GitHub Discussion Notification"
            }
        }
        
        # Find the appropriate webhook for discussions
        webhook_url = self.config['webhooks']['discussions']['url']
        self.send_webhook_message(webhook_url, embed)
    
    def handle_pull_request_event(self, payload: Dict[str, Any]):
        """
        Handle GitHub pull request event
        """
        action = payload.get('action', 'opened')
        pr = payload.get('pull_request', {})
        repository = payload.get('repository', {})
        
        # Determine color based on action
        color_map = {
            'opened': 0x28a745,      # Green
            'closed': 0xdc3545,      # Red
            'reopened': 0xfd7e14,    # Orange
            'merged': 0x6f42c1       # Purple
        }
        color = color_map.get(action, 0x007bff)  # Blue as default
        
        # Determine if merged
        if action == 'closed' and pr.get('merged', False):
            action = 'merged'
            color = color_map[action]
        
        embed = {
            "title": f"Pull Request #{pr.get('number')} {action.title()}",
            "description": f"**{pr.get('title', 'No Title')}**\n\n{pr.get('body', '')[:512]}...",
            "url": pr.get('html_url', ''),
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "author": {
                "name": pr.get('user', {}).get('login', 'Unknown'),
                "icon_url": pr.get('user', {}).get('avatar_url', '')
            },
            "fields": [
                {
                    "name": "Repository",
                    "value": repository.get('name', 'Unknown'),
                    "inline": True
                },
                {
                    "name": "From → To",
                    "value": f"`{pr.get('head', {}).get('ref', 'unknown')}` → `{pr.get('base', {}).get('ref', 'unknown')}`",
                    "inline": True
                },
                {
                    "name": "Status",
                    "value": "Merged" if pr.get('merged', False) else pr.get('state', 'open').title(),
                    "inline": True
                }
            ],
            "footer": {
                "text": "GitHub Pull Request Notification"
            }
        }
        
        # Find the appropriate webhook for pull requests
        webhook_url = self.config['webhooks']['pull_requests']['url']
        self.send_webhook_message(webhook_url, embed)


def handle_github_webhook(payload: Dict[str, Any], event_type: str):
    """
    Main function to handle incoming GitHub webhooks
    """
    discord_integration = DiscordIntegration()
    
    # Route to appropriate handler based on event type
    if event_type == 'push':
        discord_integration.handle_push_event(payload)
    elif event_type == 'issues':
        discord_integration.handle_issue_event(payload)
    elif event_type == 'discussion':
        discord_integration.handle_discussion_event(payload)
    elif event_type in ['pull_request', 'pull_request_review', 'pull_request_review_comment']:
        discord_integration.handle_pull_request_event(payload)
    else:
        print(f"Unsupported event type: {event_type}")
        return {"status": "ignored", "message": f"Event type {event_type} not supported"}
    
    return {"status": "success", "message": f"Processed {event_type} event"}