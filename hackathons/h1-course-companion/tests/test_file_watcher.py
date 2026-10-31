import unittest
from pathlib import Path
import json
import tempfile
from watchers.file_watcher import FileWatcher


class TestFileWatcher(unittest.TestCase):
    """Test suite for FileWatcher class."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directories for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        self.drop_folder = self.temp_dir / "drop_folder"
        self.vault_path = self.temp_dir / "vault"
        
        self.drop_folder.mkdir(exist_ok=True)
        self.vault_path.mkdir(exist_ok=True)
        
        # Create required subdirectories in vault
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
        (self.vault_path / "Logs").mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_categorize_file_document(self):
        """Test that documents are categorized correctly."""
        watcher = FileWatcher(self.drop_folder, self.vault_path, dry_run=True)
        
        # Create a test document file
        test_file = self.drop_folder / "test.pdf"
        test_file.touch()
        
        category = watcher._categorize_file(test_file)
        self.assertEqual(category, "document")

    def test_categorize_file_code(self):
        """Test that code files are categorized correctly."""
        watcher = FileWatcher(self.drop_folder, self.vault_path, dry_run=True)
        
        # Create a test code file
        test_file = self.drop_folder / "test.py"
        test_file.touch()
        
        category = watcher._categorize_file(test_file)
        self.assertEqual(category, "code")

    def test_categorize_file_data(self):
        """Test that data files are categorized correctly."""
        watcher = FileWatcher(self.drop_folder, self.vault_path, dry_run=True)
        
        # Create a test data file
        test_file = self.drop_folder / "test.csv"
        test_file.touch()
        
        category = watcher._categorize_file(test_file)
        self.assertEqual(category, "data")

    def test_categorize_file_image(self):
        """Test that image files are categorized correctly."""
        watcher = FileWatcher(self.drop_folder, self.vault_path, dry_run=True)
        
        # Create a test image file
        test_file = self.drop_folder / "test.png"
        test_file.touch()
        
        category = watcher._categorize_file(test_file)
        self.assertEqual(category, "image")

    def test_categorize_file_video(self):
        """Test that video files are categorized correctly."""
        watcher = FileWatcher(self.drop_folder, self.vault_path, dry_run=True)
        
        # Create a test video file
        test_file = self.drop_folder / "test.mp4"
        test_file.touch()
        
        category = watcher._categorize_file(test_file)
        self.assertEqual(category, "video")

    def test_categorize_file_archive(self):
        """Test that archive files are categorized correctly."""
        watcher = FileWatcher(self.drop_folder, self.vault_path, dry_run=True)
        
        # Create a test archive file
        test_file = self.drop_folder / "test.zip"
        test_file.touch()
        
        category = watcher._categorize_file(test_file)
        self.assertEqual(category, "archive")

    def test_categorize_file_other(self):
        """Test that unrecognized files are categorized as 'other'."""
        watcher = FileWatcher(self.drop_folder, self.vault_path, dry_run=True)
        
        # Create a test file with unrecognized extension
        test_file = self.drop_folder / "test.xyz"
        test_file.touch()
        
        category = watcher._categorize_file(test_file)
        self.assertEqual(category, "other")


if __name__ == '__main__':
    unittest.main()