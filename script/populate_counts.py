#!/usr/bin/env python3
"""
Populate NbSolutions and NbComments counts for all crackmes.

This script iterates through all crackmes and calculates the correct counts
for solutions and comments, then updates the database.

Usage:
    python populate_counts.py                    # Dry-run mode (shows planned updates)
    python populate_counts.py --apply            # Apply updates to database
    python populate_counts.py --uri mongodb://host:port --db dbname
"""

import argparse
import sys
from pymongo import MongoClient
from bson import ObjectId


def count_solutions_for_crackme(solutions_collection, crackme_id):
    """Count visible solutions for a crackme by ObjectId."""
    return solutions_collection.count_documents({
        'crackmeid': crackme_id,
        'visible': True
    })


def count_comments_for_crackme(comments_collection, hex_id):
    """Count visible comments for a crackme by hexid."""
    return comments_collection.count_documents({
        'crackmehexid': hex_id,
        'visible': True
    })


def main():
    parser = argparse.ArgumentParser(
        description='Populate solution and comment counts for all crackmes'
    )
    parser.add_argument('--apply', action='store_true',
                        help='Apply changes to the database (default: dry-run mode)')
    parser.add_argument('--uri', default='mongodb://localhost:27017',
                        help='MongoDB URI (default: mongodb://localhost:27017)')
    parser.add_argument('--db', default='crackmesone',
                        help='Database name (default: crackmesone)')

    args = parser.parse_args()

    if args.apply:
        print("Running in APPLY mode - changes will be written to the database")
    else:
        print("Running in DRY-RUN mode - no changes will be made")
        print("Use --apply flag to apply changes")
    print()

    # Connect to MongoDB
    try:
        client = MongoClient(args.uri, serverSelectionTimeoutMS=5000)
        client.server_info()  # Trigger connection
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

    db = client[args.db]
    crackme_collection = db['crackme']
    solutions_collection = db['solution']
    comments_collection = db['comment']

    # Find all crackmes
    crackmes = list(crackme_collection.find({}))
    print(f"Found {len(crackmes)} crackmes to process\n")

    updated_count = 0
    total_solutions = 0
    total_comments = 0

    for i, crackme in enumerate(crackmes, 1):
        hexid = crackme.get('hexid', '')
        name = crackme.get('name', 'Unknown')
        object_id = crackme.get('_id')

        current_nb_solutions = crackme.get('nbsolutions', 0)
        current_nb_comments = crackme.get('nbcomments', 0)

        # Count actual solutions and comments
        actual_solutions = count_solutions_for_crackme(solutions_collection, object_id)
        actual_comments = count_comments_for_crackme(comments_collection, hexid)

        total_solutions += actual_solutions
        total_comments += actual_comments

        # Check if update is needed
        needs_update = (
            current_nb_solutions != actual_solutions or
            current_nb_comments != actual_comments
        )

        if needs_update:
            updated_count += 1
            print(f"[{i}] Crackme: {name} ({hexid})")

            if current_nb_solutions != actual_solutions:
                print(f"  Solutions: {current_nb_solutions} -> {actual_solutions}")

            if current_nb_comments != actual_comments:
                print(f"  Comments: {current_nb_comments} -> {actual_comments}")

            if args.apply:
                try:
                    crackme_collection.update_one(
                        {'_id': object_id},
                        {'$set': {
                            'nbsolutions': actual_solutions,
                            'nbcomments': actual_comments
                        }}
                    )
                    print("  ✅ Updated")
                except Exception as e:
                    print(f"  ❌ Failed to update: {e}")

            print()

    # Print summary
    print("=" * 60)
    print("Summary:")
    print(f"  Total crackmes: {len(crackmes)}")
    print(f"  Crackmes needing updates: {updated_count}")
    print(f"  Total solutions: {total_solutions}")
    print(f"  Total comments: {total_comments}")

    if not args.apply and updated_count > 0:
        print("\nTo apply these changes, run with --apply flag")
    elif args.apply and updated_count > 0:
        print("\n✅ Changes have been applied to the database")
    elif updated_count == 0:
        print("\n✅ All counts are already correct")

    if updated_count > 0 and not args.apply:
        sys.exit(1)


if __name__ == '__main__':
    main()
