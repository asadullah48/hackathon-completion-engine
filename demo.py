#!/usr/bin/env python3
"""
Demo script to showcase H0 Personal AI CTO functionality
"""

import os
import time
from pathlib import Path
import tempfile
from datetime import datetime

def demo_file_monitoring():
    """Demonstrate the file monitoring functionality."""
    print("🚀 H0 Personal AI CTO Demo")
    print("=" * 50)
    
    # Import the FileWatcher
    from watchers.file_watcher import FileWatcher
    
    print("\n📁 Setting up demo environment...")
    
    # Create temporary directories for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        drop_folder = temp_path / "demo_drop_folder"
        vault_path = temp_path / "demo_vault"
        
        drop_folder.mkdir()
        vault_path.mkdir()
        
        # Create required subdirectories in vault
        (vault_path / "Needs_Action").mkdir()
        (vault_path / "Logs").mkdir()
        
        print(f"📂 Drop folder: {drop_folder}")
        print(f"📚 Vault: {vault_path}")
        
        # Initialize the FileWatcher in dry-run mode for demo
        watcher = FileWatcher(
            drop_folder=drop_folder,
            vault_path=vault_path,
            check_interval=1,
            dry_run=True
        )
        
        print("\n✅ FileWatcher initialized in dry-run mode")
        
        # Create sample files to demonstrate categorization
        sample_files = [
            ("report.pdf", b"PDF content"),
            ("script.py", b"print('Hello World')"),
            ("data.csv", b"name,age\nJohn,30"),
            ("image.png", b"PNG image data"),
            ("archive.zip", b"ZIP archive data"),
            ("document.txt", b"Plain text content"),
        ]
        
        print(f"\n📝 Creating {len(sample_files)} sample files...")
        
        for filename, content in sample_files:
            file_path = drop_folder / filename
            with open(file_path, 'wb') as f:
                f.write(content)
            print(f"   Created: {filename}")
        
        print(f"\n🔍 Demonstrating file categorization...")
        
        for filename, _ in sample_files:
            file_path = drop_folder / filename
            category = watcher._categorize_file(file_path)
            print(f"   {filename:<15} → {category}")
        
        print(f"\n📋 Demonstrating action item creation (dry-run)...")
        
        for filename, _ in sample_files[:3]:  # Just first 3 for demo
            file_path = drop_folder / filename
            print(f"   Processing: {filename}")
            
            # Create action item (will show what would be created in dry-run)
            action_path = watcher._create_action_item(file_path)
            if action_path is None:
                print(f"     → Would create action item in vault/Needs_Action/")
            else:
                print(f"     → Created: {action_path.name}")
        
        print(f"\n📊 Demonstrating activity logging...")
        
        # Log a sample activity
        watcher._log_activity('demo_event', {
            'demo_step': 'file_processing',
            'files_processed': len(sample_files),
            'timestamp': datetime.now().isoformat()
        })
        
        log_files = list((vault_path / "Logs").glob("*.json"))
        if log_files:
            print(f"   Activity logged to: {log_files[0].name}")
        
        print(f"\n📋 Vault structure:")
        for item in vault_path.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(vault_path)
                print(f"   {rel_path}")
        
        print(f"\n✅ Demo completed successfully!")
        print(f"🎯 The H0 Personal AI CTO is ready to monitor your files!")


def show_features():
    """Display the features of the H0 Personal AI CTO."""
    print("\n🌟 H0 Personal AI CTO Features:")
    print("   • File monitoring and categorization")
    print("   • Automatic action item generation")
    print("   • Activity logging and tracking")
    print("   • Human-in-the-Loop (HITL) approval workflow")
    print("   • Obsidian vault integration")
    print("   • Real-time dashboard updates")
    print("   • CEO briefing generation")
    print("   • Configuration management")
    print("   • Comprehensive testing")


if __name__ == "__main__":
    demo_file_monitoring()
    show_features()
    
    print(f"\n📖 To run the actual file watcher:")
    print(f"   python3 watchers/file_watcher.py --drop-folder /path/to/inbox --vault /path/to/vault")