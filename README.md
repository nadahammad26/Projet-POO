# ClubConnect - Student Club Management Platform

A modern, glassmorphism-designed web application for managing student clubs, events, and memberships.

## Features
- **Strict OOP Implementation**: Encapsulation with private/protected attributes and properties, Polymorphism via method overriding, and Composition for event management.
- **Club Management**: Automated initialization of clubs:
  - **BDE**: Student life and event organization.
  - **Les Mains Solidaires**: Volunteering, humanitary, and charity activities.
  - **Bleu Hands**: Naval industry and marine ecosystem protection.
  - **TinkCraft**: Artificial Intelligence (AI) and innovation hub.
- **Member Roles**: Different roles for Presidents and Members.
- **Responsive UI**: Premium design with glassmorphism effects.

## Deployment

### Local Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

### Deploy to Railway
1. Connect your GitHub repository to [Railway](https://railway.app/).
2. Railway will automatically detect the `Procfile` and `requirements.txt`.
3. The database will be initialized automatically on the first run.
   - *Note: Since this uses SQLite, data will be ephemeral unless you configure a persistent volume on Railway.*

## Technology Stack
- **Backend**: Flask, Flask-SQLAlchemy (Python)
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism)
- **Database**: SQLite
