
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

def main():
    """Run administrative tasks."""
    # Get absolute paths
    current_dir = Path(__file__).resolve().parent
    parent_dir = current_dir.parent
    
    # Add paths to sys.path for proper imports
    paths_to_add = [
        str(current_dir),
        str(parent_dir),
        str(current_dir / 'chat_microservice'),
        str(current_dir / 'chat')
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # Set the correct Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_microservice.settings')
    
    # Debug: Print Django configuration
    if '--debug-config' in sys.argv:
        print(f"[DEBUG] Current directory: {os.getcwd()}")
        print(f"[DEBUG] Python path: {sys.path[:5]}...")
        print(f"[DEBUG] Django settings: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
        sys.argv.remove('--debug-config')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Enhanced error message
        print(f"[ERROR] Could not import Django from: {current_dir}")
        print(f"[ERROR] Python path: {sys.path}")
        print(f"[ERROR] Current working directory: {os.getcwd()}")
        
        # Try to give more specific help
        try:
            import django
            print(f"[INFO] Django found at: {django.__file__}")
        except ImportError:
            print("[ERROR] Django is not installed")
            
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? "
            f"Current working directory: {os.getcwd()}"
        ) from exc
    
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
