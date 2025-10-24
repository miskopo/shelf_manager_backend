# 🫙 Pantry Scanner

A small Python-based system for managing homemade preserves using barcode labels.
It allows you to **generate**, **scan**, and **track** jars and bottles (e.g., jams, pickles, spreads) in a local PostgreSQL database.

---

## Overview

This project provides:

* A **PostgreSQL database schema** for tracking preserves (`type`, `main_ingredient`, `year`, `quantity`)
* A **Python CRUD interface** for adding, removing, and querying preserves
* A **barcode format** and encoder/decoder based on Code39
* A **label generator** for printing new barcodes via CSV or one-off generation
* A **scanner service** that listens for barcode input from a USB HID scanner and updates the database automatically

---

##  Project Structure

```
pantry-scanner/
├── pantry/
│   ├── __init__.py
│   ├── barcode.py              # Barcode decoding (Code39 → structured JSON)
│   ├── db.py                   # Database operations
│   ├── service.py              # Background service reading USB barcode input
│   └── ...
├── sql/
│   └── init_pantry.sql         # Database initialization script
├── systemd/
│   └── pantry-scanner.service  # Systemd unit file for automatic startup
├── setup.py                    # Installer script
└── README.md
```

---

## Database Setup

1. Create the database:

   ```bash
   sudo -u postgres createdb pantrydb
   ```

2. Initialize the schema:

   ```bash
   psql -U postgres -d pantrydb -f sql/init_pantry.sql
   ```

3. Create a database user and grant privileges:

   ```sql
   CREATE USER pantryuser WITH PASSWORD 'yourpassword';
   GRANT ALL PRIVILEGES ON DATABASE pantrydb TO pantryuser;
   ```

4. In your `.env` file (in project root), configure connection details:

   ```
   DB_USER=pantryuser
   DB_PASS=yourpassword
   DB_URL=localhost
   ```

---

## Barcode System

Each preserve is encoded as a short Code39 barcode with this structure:

| Segment | Example | Meaning                     |
| ------- | ------- | --------------------------- |
| 1–3     | `apr`   | Main ingredient (`apricot`) |
| 4       | `j`     | Type (`jam`)                |
| 5–6     | `23`    | Year (`2023`)               |

Example:

```
aprj23 → apricot jam 2023
```

Mappings for ingredients and types are stored in the database:

* table `produce` — e.g., `"apr": "apricot"`, `"str": "strawberry"`
* table `preserve_types` — e.g., `"j": "jam"`, `"p": "pickle"`

This allows easy expansion without changing code.

---

## Installation

Install dependencies and set up the package:

```bash
sudo python3 setup.py install
```

This will:

* Install the Python package (`pantry`)
* Copy the systemd service to `/etc/systemd/system/pantry-scanner.service`
* Enable and reload it automatically

Then start the service:

```bash
sudo systemctl start pantry-scanner
```

To check the status:

```bash
systemctl status pantry-scanner
```

---

## Debugging & Manual Run

You can run the service directly (without systemd) for debugging:

```bash
python3 -m pantry.service
```

The service will attempt to read barcodes from the configured `/dev/hidrawX` device, decode them, and perform the corresponding database operation (add/remove).

---


## Future Improvements

###  Barcode Generation

#### Batch mode (CSV)

```bash
python3 -m pantry.barcode_generator input.csv output.csv
```

* `input.csv` contains: `main_ingredient,type,year`
* `output.csv` contains the same plus a generated barcode and image filename

#### Single label

```bash
python3 -m pantry.barcode_generator single apricot jam 2023
```

This will output the barcode string and optionally generate a PNG file.

---
* Automatic device detection for HID scanners
* Web dashboard for inventory overview
* Integration with Home Assistant via REST API
* RPM packaging for Fedora-based systems

---

## Author

@miskopo

**Acknowledgment**

Parts of this project were developed with the assistance of ChatGPT (OpenAI).