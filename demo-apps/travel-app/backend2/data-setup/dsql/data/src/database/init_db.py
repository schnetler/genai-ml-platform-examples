#!/usr/bin/env python3
"""Initialize and populate the travel demo database."""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.database.db_manager import DatabaseManager
from src.database.data_generator import DataGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Initialize and populate the database."""
    db_path = Path(__file__).parent.parent.parent / "travel_demo.db"
    
    # Remove existing database if it exists
    if db_path.exists():
        logger.info(f"Removing existing database at {db_path}")
        db_path.unlink()
    
    logger.info(f"Creating new database at {db_path}")
    
    with DatabaseManager(str(db_path)) as db:
        # Initialize schema
        logger.info("Initializing database schema...")
        db.init_database()
        
        # Generate data
        logger.info("Generating demo data...")
        generator = DataGenerator(db)
        generator.generate_all_data()
        
    logger.info("Database initialization complete!")
    logger.info(f"Database created at: {db_path}")
    
    # Verify data was created
    with DatabaseManager(str(db_path)) as db:
        cities = db.execute_query("SELECT COUNT(*) as count FROM cities")
        flights = db.execute_query("SELECT COUNT(*) as count FROM flights")
        hotels = db.execute_query("SELECT COUNT(*) as count FROM hotels")
        activities = db.execute_query("SELECT COUNT(*) as count FROM activities")
        
        logger.info(f"Created {cities[0]['count']} cities")
        logger.info(f"Created {flights[0]['count']} flights")
        logger.info(f"Created {hotels[0]['count']} hotels")
        logger.info(f"Created {activities[0]['count']} activities")


if __name__ == "__main__":
    main()