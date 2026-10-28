# VG Tech AI Support Operations Advisor

A Streamlit-based support operations decision-support prototype
built using Python and synthetic IT support ticket data.

## Overview

This project demonstrates how structured incident data can support
service reliability, recurring issue analysis, incident prioritisation
and operational governance.

## Features

- Support operations KPI dashboard
- Country and priority filters
- Recurring incident pattern analysis
- SLA breach and escalation monitoring
- Operational performance scorecard
- Active P1/P2 incident monitoring
- Business criticality assessment
- Problem investigation prioritisation
- Simulated temporary criticality overrides
- Fictional governance and approval scenarios

## Technology

- Python
- Streamlit
- Pandas

## Run locally

1. Install Python 3.10 or later.
2. Install dependencies:

   pip install -r requirements.txt

3. Start the application:

   streamlit run vgtech_dashboard.py

## Data

The application uses synthetic_tickets.csv, containing
100 fictional support tickets.

No real customer or production data is included.

## Important limitations

This is a demonstration prototype, not a production ITSM system.

- Prioritisation is rule-based, not powered by a live AI model.
- Approval and governance scenarios are fictional.
- Emergency overrides are simulated.
- No live ticketing system or approval database is connected.
- Operational metrics describe synthetic data, not proven
  real-world service improvements.

## Purpose

Developed to demonstrate practical application of data analytics,
incident management, service reliability and support operations
leadership.

## Author

Dr. Vithyatheri Govindan
VG Tech Consulting
