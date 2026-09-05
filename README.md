# District Administration Internal Management System

A desktop management software built with Python to digitize human resources, meeting attendance tracking, and automated document parsing for local government administration.

## Key Features

- **Automated Document Ingestion:** Custom regex and token-based engine parsing `.docx` standard personnel profiles (Ob'ektivka), auto-extracting personal data, military status, and employment histories directly into the database.
- **Meeting & Session Logistics:** Real-time tracking of inter-departmental representatives, state agency attendees, and automatic generation of Cyrillic-compliant Word reports.
- **Attendance & KPI Engine:** Comprehensive monthly attendance tracking with Excel (`openpyxl`) reporting and performance distribution visualization (`matplotlib`).
- **Hybrid Networking Architecture:** 
  - **On-Premise Mode:** Decentralized local deployment using UDP Broadcast discovery and custom RPC/Socket file transfers designed for restricted intranets and Tailscale mesh-networking.
  - **Cloud Mode:** Centralized state storage powered by Firestore.

## Tech Stack

- **GUI:** CustomTkinter (Modern Dark-Themed Desktop UI)
- **Networking:** Python `socket`, `ThreadingHTTPServer`, UDP Broadcast, Tailscale Mesh Integration
- **Office Automation:** `python-docx`, `openpyxl`
- **Data & Charts:** SQLite / Firebase Firestore, `matplotlib`

## Setup & Running

1. Clone this repository:
   ```bash
   git clone [https://github.com/icoyecimi688-sudo/district-management-system.git](https://github.com/icoyecimi688-sudo/district-management-system.git)
   cd district-management-system
