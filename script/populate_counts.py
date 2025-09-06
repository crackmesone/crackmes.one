#!/usr/bin/env python3
"""
Migration script to populate nb_solutions and nb_comments for existing crackmes.

This script iterates over all crackmes in the database and calculates their
current solution and comment counts, then updates the database with these values.
"""

import pymongo
import sys
from bson import ObjectId

def connect_to_db():
    """Connect to MongoDB database."""
    try:
        # Default MongoDB connection - adjust if needed
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["crackmesone"]
        return db
    except pymongo.errors.ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

def get_crackme_counts(db, crackme_hexid):
    """Get solution and comment counts for a crackme."""
    
    # Count solutions for this crackme
    # First get the crackme to find its ObjectId
    crackme = db.crackme.find_one({"hexid": crackme_hexid})
    if not crackme:
        return 0, 0
    
    # Count visible solutions
    solution_count = db.solution.count_documents({
        "crackmeid": crackme["_id"],
        "visible": True
    })
    
    # Count visible comments
    comment_count = db.comment.count_documents({
        "crackmehexid": crackme_hexid,
        "visible": True
    })
    
    return solution_count, comment_count

def update_crackme_counts(db, crackme_hexid, nb_solutions, nb_comments):
    """Update the crackme with solution and comment counts."""
    result = db.crackme.update_one(
        {"hexid": crackme_hexid},
        {"$set": {
            "nb_solutions": nb_solutions,
            "nb_comments": nb_comments
        }}
    )
    return result.modified_count > 0

def main():
    """Main migration function."""
    print("Starting migration to populate crackme counts...")
    
    # Connect to database
    db = connect_to_db()
    
    # Get all crackmes
    crackmes = db.crackme.find({})
    
    total_crackmes = 0
    updated_crackmes = 0
    
    for crackme in crackmes:
        total_crackmes += 1
        hexid = crackme.get("hexid")
        
        if not hexid:
            print(f"Warning: Crackme {crackme.get('_id')} has no hexid, skipping...")
            continue
        
        # Get current counts
        nb_solutions, nb_comments = get_crackme_counts(db, hexid)
        
        # Update the crackme
        if update_crackme_counts(db, hexid, nb_solutions, nb_comments):
            updated_crackmes += 1
            print(f"Updated crackme {hexid}: {nb_solutions} solutions, {nb_comments} comments")
        else:
            print(f"Failed to update crackme {hexid}")
    
    print(f"\nMigration complete!")
    print(f"Total crackmes processed: {total_crackmes}")
    print(f"Successfully updated: {updated_crackmes}")

if __name__ == "__main__":
    main()