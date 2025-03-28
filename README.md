# Django Ruck Logs Tracking System

## Overview
This Django project is designed to track ruck logs and manage workflow efficiently. It enables user management, company setup, driver and vehicle management, trip assignments, and activity tracking.

## Features
- User Management
- Company Management
- Driver and Vehicle Registration
- Trip Management
- Activity Logging

## Workflow
1. **Create User**
   - Register a new user in the system.
   - Assign appropriate roles and permissions.

2. **Create Company**
   - Add a company profile.
   - Assign company-specific details and preferences.

3. **Create Company Drivers**
   - Register drivers under a company.
   - Store driver details including license and contact information.

4. **Create Company Vehicles**
   - Register company vehicles.
   - Maintain records of vehicle details, including registration and status.

5. **Create Company Trips and Assign Drivers & Vehicles**
   - Create new trips and assign a driver and a vehicle.
   - Ensure that each vehicle and driver can have only one active trip at a time.

6. **Create Activities for the Trip**
   - Track activities such as driving, on-duty, breaks, and rest periods.
   - Log timestamps and status updates for each activity.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/ciremusyoka/trucks-log-book.git
   cd trucks-log-book
   ```
2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Apply database migrations:
   ```sh
   python manage.py migrate
   ```
5. Create a superuser:
   ```sh
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```sh
   python manage.py runserver
   ```

## API Endpoints

- **User Management:** `/api/v1/user/`
- **Company Management:** `/api/v1/companies/`
- **Driver Management:** `/api/v1/drivers/`
- **Vehicle Management:** `/api/v1/vehicles/`
- **Trip Management:** `/api/v1/trips/`
- **Activity Tracking:** `/api/v1/trip-logs/`

