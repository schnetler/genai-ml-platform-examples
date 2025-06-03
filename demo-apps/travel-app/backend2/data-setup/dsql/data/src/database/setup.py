"""Database setup utilities for testing and initialization."""

import sqlite3
from pathlib import Path
from .db_manager import DatabaseManager
from .data_generator import DataGenerator
from .activity_generator import ActivityDataGenerator


def setup_database(db_path: str = ":memory:") -> sqlite3.Connection:
    """Set up a test database with schema and optionally with data."""
    # Read schema
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, 'r') as f:
        schema = f.read()
    
    # Create connection
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Execute schema
    conn.executescript(schema)
    conn.commit()
    conn.close()
    
    # Use DatabaseManager for data generation
    db_manager = DatabaseManager(db_path)
    db_manager.connect()
    
    # Generate flight and hotel data
    generator = DataGenerator(db_manager)
    generator.generate_all_data()
    
    # Generate activity data
    activity_gen = ActivityDataGenerator(db_path)
    activity_gen.generate_activities()
    
    # Close the manager
    db_manager.close()
    
    # Return a new connection
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def reset_database(db_path: str = "travel_demo.db"):
    """Reset the database to a clean state."""
    conn = setup_database(db_path)
    conn.close()
    return True