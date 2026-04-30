MEMORY_DIR = ".engram"
SESSION_DIR = ".engram/session"
EXPERIENCE_DIR = ".engram/experience"
ARCHIVE_DIR = ".engram/session/archive"
CATEGORIES = ["design", "technical", "business"]
ARCHIVE_DAYS = 7
DATE_FORMAT = "%Y-%m-%d %H:%M"

# Global experience library (cross-project, stored in user home directory)
import os
GLOBAL_EXPERIENCE_DIR = os.path.join(os.path.expanduser("~"), ".sengram", "experience")
