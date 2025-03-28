# DIICSU Classroom Booking System BY SurperB

[![Live Demo](https://img.shields.io/badge/Demo-https://www.diicsu.top:8000-brightgreen)](https://www.diicsu.top:8000)

> Intelligent classroom reservation system for University of Dundee, powered by Alibaba Cloud

## 🚀 Project Overview
A full-stack solution designed to:
- ✅ Optimize classroom utilization
- ✅ Implement dual-end management (User & Admin)
- ✅ Enforce smart booking policies
- ✅ Support modern authentication methods

**Production URL**: https://www.diicsu.top:8000  
*Note: Service availability may vary due to maintenance*

## ✨ Key Features
### 👩💻 User Portal
- Secure Authentication:
  - Microsoft Account Login
  - @dundee.ac.uk Email OTP Verification
- Intelligent Room Filtering:
  - Time slots
  - Capacity requirements
  - Equipment availability
- Booking Management:
  - Real-time modifications
  - Cancellation restrictions
- Reputation System:
  - Auto-blacklist after 3+ same-day cancellations
  - Conflict detection

### 👨💼 Admin Dashboard
- Classroom CRUD Operations
- Policy Configuration:
  - Time restrictions
  - Occupancy limits
  - Blacklist management
- Usage Analytics Dashboard
- Audit Trail & Approval Workflows

## 🛠️ Tech Stack
- **Cloud**: Alibaba Cloud ECS (ICP Licensed)
- **Security**: HTTPS/SSL via Trustwave Certificate
- **Backend**: Python Flask
- **Database**: MySQL 5.7+
- **Frontend**: Bootstrap 5 + Vanilla JS

## 🖥️ Local Deployment
### Prerequisites
- Python 3.8+
- MySQL Server
- Port 8000 accessible

### Step-by-Step
```bash
# Clone repository
git clone https://github.com/ahang13147/SuperB.git

# Install dependencies
pip install -r requirements.txt

# Initialize database
mysql -u root -p < DBTEST/create.sql
mysql -u root -p < DBTEST/advanced.sql
mysql -u root -p < DBTEST/insert.sql

# Seed initial data
python initialize_room_availability_without_api.py
python syllabus_without_api.py

# Launch application
python app.py