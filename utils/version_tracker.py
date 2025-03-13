"""
Version tracking module for SR&ED documentation.

This module provides version tracking capabilities for SR&ED documentation,
allowing for proper recording of document revisions and changes over time.
"""

import json
from datetime import datetime
import hashlib
import os

class SREDVersionTracker:
    """
    Class for tracking versions of SR&ED documentation.
    """
    
    def __init__(self, version_file='assets/sred_visuals/version_history.json'):
        """
        Initialize the version tracker.
        
        Args:
            version_file (str): Path to the version history file
        """
        self.version_file = version_file
        self.version_data = self._load_version_data()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(version_file), exist_ok=True)
    
    def _load_version_data(self):
        """
        Load version data from file.
        
        Returns:
            dict: Version data or empty dict if file doesn't exist
        """
        try:
            with open(self.version_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'document_versions': [],
                'latest_version': '0.0.0',
                'last_updated': datetime.now().isoformat()
            }
    
    def _save_version_data(self):
        """Save version data to file."""
        with open(self.version_file, 'w') as f:
            json.dump(self.version_data, f, indent=2)
    
    def get_current_version(self):
        """
        Get the current version.
        
        Returns:
            str: Current version number
        """
        return self.version_data['latest_version']
    
    def get_version_history(self):
        """
        Get the version history.
        
        Returns:
            list: Version history
        """
        return self.version_data['document_versions']
    
    def increment_version(self, change_type='patch', changes=None):
        """
        Increment the version.
        
        Args:
            change_type (str): Type of change: 'major', 'minor', or 'patch'
            changes (list): List of changes
            
        Returns:
            str: New version number
        """
        current_version = self.version_data['latest_version']
        major, minor, patch = map(int, current_version.split('.'))
        
        if change_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif change_type == 'minor':
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        new_version = f"{major}.{minor}.{patch}"
        self.version_data['latest_version'] = new_version
        self.version_data['last_updated'] = datetime.now().isoformat()
        
        # Add to version history
        version_entry = {
            'version': new_version,
            'timestamp': datetime.now().isoformat(),
            'change_type': change_type,
            'changes': changes or [],
        }
        
        self.version_data['document_versions'].append(version_entry)
        self._save_version_data()
        
        return new_version
    
    def generate_version_markdown(self):
        """
        Generate markdown version history.
        
        Returns:
            str: Markdown version history
        """
        history = self.get_version_history()
        if not history:
            return "No version history available."
        
        markdown = "# Version History\n\n"
        
        for entry in reversed(history):
            version = entry['version']
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            change_type = entry['change_type'].capitalize()
            
            markdown += f"## Version {version} ({timestamp})\n\n"
            markdown += f"**Change Type:** {change_type}\n\n"
            
            if entry['changes']:
                markdown += "**Changes:**\n\n"
                for change in entry['changes']:
                    markdown += f"- {change}\n"
            else:
                markdown += "No specific changes recorded.\n"
            
            markdown += "\n---\n\n"
        
        return markdown
    
    def calculate_document_hash(self, content):
        """
        Calculate hash of document content.
        
        Args:
            content (str): Document content
            
        Returns:
            str: Document hash
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def generate_version_report(self):
        """
        Generate a detailed version report for SR&ED documentation.
        
        Returns:
            dict: Report data
        """
        latest_version = self.get_current_version()
        history = self.get_version_history()
        
        return {
            'current_version': latest_version,
            'version_count': len(history),
            'first_version_date': datetime.fromisoformat(history[0]['timestamp']).strftime('%Y-%m-%d') if history else None,
            'latest_version_date': datetime.fromisoformat(history[-1]['timestamp']).strftime('%Y-%m-%d') if history else None,
            'version_history': history
        }


def add_version_info(sred_type="Technical Documentation", changes=None):
    """
    Add version information for a SR&ED document.
    
    Args:
        sred_type (str): Type of SR&ED document
        changes (list): List of changes
        
    Returns:
        dict: Version information
    """
    tracker = SREDVersionTracker()
    new_version = tracker.increment_version('patch', changes)
    
    return {
        'version': new_version,
        'generated_at': datetime.now().isoformat(),
        'document_type': sred_type,
        'version_history_url': 'Visualizations/version_history.md'
    }


def generate_version_history_file():
    """
    Generate version history file.
    
    Returns:
        str: Markdown version history
    """
    tracker = SREDVersionTracker()
    return tracker.generate_version_markdown()