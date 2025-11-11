
from database import db
from main import app
import sqlalchemy as sa
from sqlalchemy import text

def migrate_courier_service():
    """Add courier_service column to orders table if it doesn't exist"""
    with app.app_context():
        try:
            # Check if courier_service column exists
            inspector = sa.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('orders')]
            
            if 'courier_service' not in columns:
                print("Adding courier_service column to orders table...")
                
                # Add the column
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE orders ADD COLUMN courier_service VARCHAR(50)'))
                    conn.commit()
                
                print("courier_service column added successfully!")
            else:
                print("courier_service column already exists.")
                
        except Exception as e:
            print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate_courier_service()
