# District Administration Internal Management System

A production-ready desktop enterprise application engineered to streamline human resource workflows, inter-departmental meeting coordination, automated document parsing, and personnel tracking for local municipal administration.

The system features a **dual-architecture engine**: a distributed, peer-to-peer on-premise network mode engineered for air-gapped environments, and a cloud-synchronized mode backed by Google Firebase.

---

## 🎥 Video Demonstration
> **Watch System Walkthrough:** [Demo Video Link (Click to Watch)](#) *(Update this link after uploading your video to YouTube)*

---

## Key Technical Modules

- **Automated Document Ingestion (`doc_parser.py`):** 
  - Token-based parsing pipeline extracting complex biographical data from standardized Word resumes (`.docx` Ob'ektivka).
  - Automatically identifies, categorizes, and indexes personnel records, historical appointments, and familial matrices.
- **Meeting & Session Logistics (`main.py` / `main_tailscale.py`):** 
  - Real-time agenda dispatching, participant tracking, and dynamic Cyrillic-compliant Word report generation.
- **Attendance & KPI Engine:** 
  - Automated personnel activity logging with instantaneous Excel reporting (`openpyxl`) and visual departmental metrics (`matplotlib`).
- **Hybrid Networking Architecture:**
  - **Local Mesh Mode (`network.py`, `database_rpc.py`, `file_transfer.py`):** Peer discovery utilizing UDP broadcasts (`WHO_IS_SERVER`) over private virtual networks (Tailscale/Radmin/LAN) with chunked binary socket streaming for asset transfer. Operates on embedded SQLite with zero external dependencies.
  - **Cloud Mode (`database.py`):** Centralized cloud persistence powered by Google Cloud Firestore and Firebase Storage.

---

## System Architecture

```text
├── main.py                     # Entry point (Cloud / Firebase Edition)
├── main_tailscale.py           # Entry point (Local / On-Premise Mesh Edition)
├── database.py                 # Cloud abstraction (Firebase Firestore & Storage)
├── database_rpc.py             # Local storage engine (SQLite + Custom RPC)
├── network.py                  # UDP Discovery & Threaded Socket Server
├── file_transfer.py            # Stream-based chunked binary file client
├── doc_parser.py               # Word (.docx) document ingestion engine
├── requirements.txt            # Dependency manifest
└── serviceAccountKey.example.json  # Firebase credential blueprint
