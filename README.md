# SecureShare

A secure file sharing and storage system built with **AES-GCM encryption**, **ECDSA digital signatures**, and a **blockchain-inspired ledger**.  
The project was developed as part of a CSIT953 assignment to demonstrate secure storage, controlled access, and tamper-evident record keeping.

---

## Features

- End-to-end encryption — files are encrypted with AES-GCM before being uploaded.  
- Digital signatures — every upload is signed with the owner’s private key to guarantee authenticity.  
- Blockchain logging — every action (upload, request, key share) is recorded in an append-only, hash-chained ledger.  
- Secure key sharing — AES file keys are wrapped with the requester’s RSA public key so only they can decrypt.  
- GUI interface — Tkinter app with tabs for uploading, requesting, sharing, downloading, and viewing the log.  

---

## Project Structure

```
secureshare/
├── run.py                  # Entry point for the GUI
├── src/
│   ├── gui/                # Tkinter GUI (tabs: Upload, Requests, Share Key, Downloads, Ledger)
│   ├── services/           # Upload, sharing, verification logic
│   ├── core/               # Crypto operations (AES, ECDSA, RSA), keystore
│   ├── blockchain/         # Local blockchain ledger implementation
│   ├── storage/            # Cloud-like file storage and metadata
│   └── util/               # Utilities (JSON I/O, timestamps)
├── data/
│   ├── keys/               # User key pairs (generated on first run)
│   ├── cloud/              # Encrypted file blobs
│   └── ledger/             # Append-only JSON ledger
└── tests/                  # Pytest unit tests (crypto, services, ledger)
```

---

## Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd secureshare
   ```

2. Create a virtual environment and install requirements:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .venv\Scripts\activate      # Windows

   pip install -r requirements.txt
   ```

---

## Running the App

Start the GUI with:

```bash
python run.py
```

This will open the Tkinter window with tabs for all operations.

---

## Simulating Two Users (Owner & Requester)

1. Open two terminals and activate the virtualenv in both.  
2. In the first terminal:
   ```bash
   python run.py
   ```
   Use this as the Owner (uploads files, shares keys).  

3. In the second terminal:
   ```bash
   python run.py
   ```
   Use this as the Requester (requests access, downloads files).  

Both instances share the same `data/ledger` and `data/cloud` folders, so they interact like two users connected to the same system.

---

## Typical Workflow

1. Owner uploads file → it is encrypted and logged.  
2. Requester submits request for that file ID.  
3. Owner approves & shares key → AES key is securely wrapped with requester’s public key.  
4. Requester downloads & decrypts the file, verifying the owner’s signature.  
5. Blockchain log shows every step with tamper-evident hashes.  

---

## Running Tests

Unit tests are provided for crypto, services, and blockchain. Run them with:

```bash
pytest
```

---

## Notes

- Keys are automatically generated on first use under `data/keys/<userId>/`.  
- Ledger file: `data/ledger/ledger.json`.  
- Cloud storage: `data/cloud/`.  
- If you tamper with the ledger manually, the Blockchain Log tab will report the chain as invalid.

---

## License

Educational project for CSIT953. Not intended for production use.
