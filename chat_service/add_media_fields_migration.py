
import os
import sys
import django
from pathlib import Path

# Add the chat_service directory to Python path
chat_service_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(chat_service_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_microservice.settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    # Change to chat service directory
    os.chdir(str(chat_service_dir))
    
    # Create new migration
    execute_from_command_line(['manage.py', 'makemigrations', 'chat', '--name', 'add_media_fields'])
    
    # Apply the migration
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("Media fields migration completed successfully!")
