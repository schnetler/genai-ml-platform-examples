#!/usr/bin/env python3
"""
Seed DSQL with comprehensive travel planning data.
This seeds base data (cities, airlines, hotels, activities, flight routes) 
and automatically generates flights and hotel availability data.
"""

import sys
import os
# Add parent directory to path to find the database modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
import seed_dsq2l
DSQLSeeder = seed_dsq2l.DSQLSeeder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main function to seed all data."""
    try:
        logger.info("=== Starting DSQL Database Seeding ===")
        logger.info("This will generate all travel planning data including:")
        logger.info("  • Cities and destinations")
        logger.info("  • Airlines and flight routes") 
        logger.info("  • Hotels and accommodations")
        logger.info("  • Activities and experiences")
        logger.info("  • Flights and hotel availability")
        logger.info("")
        
        # Use the comprehensive DSQLSeeder
        seeder = DSQLSeeder()
        seeder.run()
        
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        raise


if __name__ == "__main__":
    main()