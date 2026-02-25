# Data Engineering Build Scripts

Python scripts for populating the PostgreSQL database from the Workwize API.

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure environment variables are set:**
   - `WORKWIZE_KEY` - Your Workwize API key
   - `DATABASE_URL` - PostgreSQL connection string
   - These should already be in the `.env` file at the project root

## Scripts

### populate_assets.py

Fetches asset data from the Workwize API and populates the `assets` table with PII scrubbing applied.

**Usage:**
```bash
python populate_assets.py
```

**Features:**
- ✅ Fetches all assets from Workwize API
- ✅ Applies PII scrubbing (emails, phones, SSNs, credit cards removed from notes)
- ✅ Scrubs location data to city/state only (no street addresses)
- ✅ Stores only employee IDs, not names (PII protection)
- ✅ Handles duplicate assets with ON CONFLICT UPDATE
- ✅ Shows summary statistics after completion

**PII Scrubbing:**
- `location` - Reduced to city/state only
- `notes` - Emails, phone numbers, SSNs, credit cards redacted
- `assignedToId` - Only ID stored, no employee names

**Output:**
```
Fetched 800+ assets
✅ Successfully inserted/updated 800 assets
📊 Total assets in database: 800
📈 Assets by status:
  Active: 650
  In Transit: 100
  Returned: 50
```

## Future Scripts

- `populate_employees.py` - Populate employees table with full PII scrubbing
- `populate_orders.py` - Populate orders table with address normalization
- `populate_products.py` - Populate products catalog
- `populate_warehouses.py` - Populate warehouse locations
- `populate_offboards.py` - Populate offboarding records
- `sync_all.py` - Full sync of all entities

## Notes

- All scripts respect PII scrubbing guidelines
- Uses upsert logic (INSERT ... ON CONFLICT UPDATE) to handle re-runs safely
- Reads from `.env` file in project root automatically
- Requires PostgreSQL container to be running
