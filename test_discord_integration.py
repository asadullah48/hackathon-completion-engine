import json
from discord_integration import DiscordIntegration

# Create a mock DiscordIntegration instance
discord_int = DiscordIntegration()

# Sample GitHub push event payload
sample_push_payload = {
    "ref": "refs/heads/main",
    "before": "abc123",
    "after": "def456",
    "repository": {
        "name": "Hackathon-Completion-Engine",
        "full_name": "user/Hackathon-Completion-Engine",
        "html_url": "https://github.com/user/Hackathon-Completion-Engine"
    },
    "pusher": {
        "name": "test-user"
    },
    "commits": [
        {
            "id": "def456",
            "message": "Add Discord integration for GitHub events\n\n- Implements webhook handlers for commits, issues, and discussions\n- Adds configuration for multiple Discord channels\n- Creates a Discord bot for interactive features",
            "author": {
                "name": "Test User",
                "email": "test@example.com"
            },
            "url": "https://github.com/user/Hackathon-Completion-Engine/commit/def456",
            "distinct": True
        }
    ]
}

# Sample GitHub issue event payload
sample_issue_payload = {
    "action": "opened",
    "issue": {
        "url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/issues/1",
        "number": 1,
        "title": "Test issue for Discord integration",
        "body": "This is a test issue to verify that GitHub issue events are properly sent to Discord.",
        "state": "open",
        "locked": False,
        "comments": 0,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "author_association": "OWNER",
        "active_lock_reason": None,
        "html_url": "https://github.com/user/Hackathon-Completion-Engine/issues/1",
        "labels": [
            {
                "id": 1,
                "node_id": "MDU6TGFiZWwx",
                "url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/labels/bug",
                "name": "enhancement",
                "color": "a2eeef",
                "default": False
            }
        ],
        "user": {
            "login": "test-user",
            "id": 1,
            "node_id": "MDQ6VXNlcjE=",
            "avatar_url": "https://github.com/images/error/test-user_happy.gif",
            "gravatar_id": "",
            "url": "https://api.github.com/users/test-user",
            "html_url": "https://github.com/test-user",
            "followers_url": "https://api.github.com/users/test-user/followers",
            "following_url": "https://api.github.com/users/test-user/following{/other_user}",
            "gists_url": "https://api.github.com/users/test-user/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/test-user/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/test-user/subscriptions",
            "organizations_url": "https://api.github.com/users/test-user/orgs",
            "repos_url": "https://api.github.com/users/test-user/repos",
            "events_url": "https://api.github.com/users/test-user/events{/privacy}",
            "received_events_url": "https://api.github.com/users/test-user/received_events",
            "type": "User",
            "site_admin": False
        }
    },
    "repository": {
        "id": 123456,
        "node_id": "MDEwOlJlcG9zaXRvcnkxMjM0NTY=",
        "name": "Hackathon-Completion-Engine",
        "full_name": "user/Hackathon-Completion-Engine",
        "private": False,
        "owner": {
            "login": "test-user",
            "id": 1,
            "node_id": "MDQ6VXNlcjE=",
            "avatar_url": "https://github.com/images/error/test-user_happy.gif",
            "gravatar_id": "",
            "url": "https://api.github.com/users/test-user",
            "html_url": "https://github.com/test-user",
            "followers_url": "https://api.github.com/users/test-user/followers",
            "following_url": "https://api.github.com/users/test-user/following{/other_user}",
            "gists_url": "https://api.github.com/users/test-user/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/test-user/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/test-user/subscriptions",
            "organizations_url": "https://api.github.com/users/test-user/orgs",
            "repos_url": "https://api.github.com/users/test-user/repos",
            "events_url": "https://api.github.com/users/test-user/events{/privacy}",
            "received_events_url": "https://api.github.com/users/test-user/received_events",
            "type": "User",
            "site_admin": False
        },
        "html_url": "https://github.com/user/Hackathon-Completion-Engine",
        "description": "A framework for completing hackathons efficiently",
        "fork": False,
        "url": "https://api.github.com/repos/user/Hackathon-Completion-Engine",
        "forks_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/forks",
        "keys_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/keys{/key_id}",
        "collaborators_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/collaborators{/collaborator}",
        "teams_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/teams",
        "hooks_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/hooks",
        "issue_events_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/issues/events{/number}",
        "events_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/events",
        "assignees_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/assignees{/user}",
        "branches_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/branches{/branch}",
        "tags_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/tags",
        "blobs_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/git/blobs{/sha}",
        "git_tags_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/git/tags{/sha}",
        "git_refs_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/git/refs{/sha}",
        "trees_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/git/trees{/sha}",
        "statuses_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/statuses/{sha}",
        "languages_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/languages",
        "stargazers_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/stargazers",
        "contributors_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/contributors",
        "subscribers_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/subscribers",
        "subscription_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/subscription",
        "commits_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/commits{/sha}",
        "git_commits_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/git/commits{/sha}",
        "comments_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/comments{/number}",
        "issue_comment_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/issues/comments{/number}",
        "contents_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/contents/{+path}",
        "compare_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/compare/{base}...{head}",
        "merges_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/merges",
        "archive_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/{archive_format}{/ref}",
        "downloads_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/downloads",
        "issues_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/issues{/number}",
        "pulls_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/pulls{/number}",
        "milestones_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/milestones{/number}",
        "notifications_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/notifications{?since,all,participating}",
        "labels_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/labels{/name}",
        "releases_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/releases{/id}",
        "deployments_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine/deployments"
    }
}

# Sample GitHub discussion event payload
sample_discussion_payload = {
    "action": "created",
    "discussion": {
        "repository_url": "https://api.github.com/repos/user/Hackathon-Completion-Engine",
        "category": {
            "id": 12345,
            "name": "General",
            "emoji": ":speech_balloon:",
            "description": "General discussions",
            "created_at": "2023-01-01T00:00:00Z"
        },
        "answer_html_url": None,
        "answer_chosen_at": None,
        "answer_chosen_by": None,
        "html_url": "https://github.com/user/Hackathon-Completion-Engine/discussions/1",
        "id": 123456,
        "node_id": "MDEwOkRpc2N1c3Npb24xMjM0NTY=",
        "number": 1,
        "title": "Testing Discord integration for discussions",
        "user": {
            "login": "test-user",
            "id": 1,
            "node_id": "MDQ6VXNlcjE=",
            "avatar_url": "https://github.com/images/error/test-user_happy.gif",
            "gravatar_id": "",
            "url": "https://api.github.com/users/test-user",
            "html_url": "https://github.com/test-user",
            "followers_url": "https://api.github.com/users/test-user/followers",
            "following_url": "https://api.github.com/users/test-user/following{/other_user}",
            "gists_url": "https://api.github.com/users/test-user/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/test-user/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/test-user/subscriptions",
            "organizations_url": "https://api.github.com/users/test-user/orgs",
            "repos_url": "https://api.github.com/users/test-user/repos",
            "events_url": "https://api.github.com/users/test-user/events{/privacy}",
            "received_events_url": "https://api.github.com/users/test-user/received_events",
            "type": "User",
            "site_admin": False
        },
        "state": "open",
        "locked": False,
        "comments": 0,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "author_association": "OWNER",
        "active_lock_reason": None,
        "body": "This is a test discussion to verify that GitHub discussion events are properly sent to Discord."
    },
    "repository": {
        "id": 123456,
        "node_id": "MDEwOlJlcG9zaXRvcnkxMjM0NTY=",
        "name": "Hackathon-Completion-Engine",
        "full_name": "user/Hackathon-Completion-Engine",
        "private": False,
        "owner": {
            "login": "test-user",
            "id": 1,
            "node_id": "MDQ6VXNlcjE=",
            "avatar_url": "https://github.com/images/error/test-user_happy.gif",
            "gravatar_id": "",
            "url": "https://api.github.com/users/test-user",
            "html_url": "https://github.com/test-user",
            "followers_url": "https://api.github.com/users/test-user/followers",
            "following_url": "https://api.github.com/users/test-user/following{/other_user}",
            "gists_url": "https://api.github.com/users/test-user/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/test-user/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/test-user/subscriptions",
            "organizations_url": "https://api.github.com/users/test-user/orgs",
            "repos_url": "https://api.github.com/users/test-user/repos",
            "events_url": "https://api.github.com/users/test-user/events{/privacy}",
            "received_events_url": "https://api.github.com/users/test-user/received_events",
            "type": "User",
            "site_admin": False
        },
        "html_url": "https://github.com/user/Hackathon-Completion-Engine",
        "description": "A framework for completing hackathons efficiently"
    }
}

def test_discord_integration():
    """
    Test the Discord integration with sample payloads
    """
    print("Testing Discord integration with sample payloads...")
    
    # Test push event
    print("\n1. Testing PUSH event:")
    try:
        discord_int.handle_push_event(sample_push_payload)
        print("✓ Push event handled successfully")
    except Exception as e:
        print(f"✗ Error handling push event: {e}")
    
    # Test issue event
    print("\n2. Testing ISSUE event:")
    try:
        discord_int.handle_issue_event(sample_issue_payload)
        print("✓ Issue event handled successfully")
    except Exception as e:
        print(f"✗ Error handling issue event: {e}")
    
    # Test discussion event
    print("\n3. Testing DISCUSSION event:")
    try:
        discord_int.handle_discussion_event(sample_discussion_payload)
        print("✓ Discussion event handled successfully")
    except Exception as e:
        print(f"✗ Error handling discussion event: {e}")
    
    print("\nTesting completed!")


if __name__ == "__main__":
    test_discord_integration()