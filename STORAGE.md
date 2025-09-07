# Storage Configuration

The application now supports configurable storage paths for crackmes and solutions through environment variables.

## Environment Variables

- `CRACKME_STORAGE_PATH` - Directory where uploaded crackme files are stored
- `SOLUTION_STORAGE_PATH` - Directory where uploaded solution files are stored

## Default Values

If environment variables are not set, the application uses these default paths:
- Crackmes: `tmp/crackme`
- Solutions: `tmp/solution`

## Usage Examples

### Docker/Container Environment
```bash
docker run -e CRACKME_STORAGE_PATH=/data/crackmes -e SOLUTION_STORAGE_PATH=/data/solutions crackmesone
```

### Systemd Service
```ini
[Service]
Environment=CRACKME_STORAGE_PATH=/var/lib/crackmesone/crackmes
Environment=SOLUTION_STORAGE_PATH=/var/lib/crackmesone/solutions
ExecStart=/usr/local/bin/crackmesone
```

### Development
```bash
export CRACKME_STORAGE_PATH=/home/user/dev/crackmes
export SOLUTION_STORAGE_PATH=/home/user/dev/solutions
./crackmesone
```

## Important Notes

- Ensure the specified directories exist and are writable by the application
- The application preserves all existing security validations (path traversal protection)
- File naming format remains unchanged: `username+++hexid+++filename`
- Changes take effect on application startup (requires restart to apply new paths)