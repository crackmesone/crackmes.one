# Crackme Counts Migration Script

This script populates the `nb_solutions` and `nb_comments` fields for existing crackmes in the database.

## Prerequisites

- Python 3.x
- pymongo library: `pip install pymongo`
- MongoDB running with the crackmesone database

## Usage

```bash
cd script/
python3 populate_counts.py
```

## What it does

1. Connects to the MongoDB database
2. Iterates through all crackmes
3. Counts visible solutions and comments for each crackme
4. Updates the crackme record with the calculated counts

## Database Configuration

The script assumes:
- MongoDB is running on `localhost:27017`
- Database name is `crackmesone`

Modify the `connect_to_db()` function if your setup is different.

## Output

The script will show progress for each crackme updated and provide a summary at the end.