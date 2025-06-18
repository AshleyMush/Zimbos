# 🌍 Zimbos Portal
Zimbos Portal is a Flask web app designed to simplify and secure access to curated WhatsApp and online groups. Users can sign up, browse available groups, add them to a basket, and check out to receive private, time-limited invite links. Admins have full control to manage groups and users from a dedicated dashboard.

🧺 Browse and add groups.
✅ Check out with a limit.
🔗 Receive secure, token-based invites.
🎯 One user per group, no duplicates or link sharing.

🚀 Key Features
🔐 User Authentication
Handles sign-up, login, and CSRF protection using Flask-Login and Flask-WTF.

👑 Admin Dashboard
Admins can add, edit, and delete groups, manage users, and review activity.

🛒 Group Basket Checkout
Users select groups, add them to a basket, and check out within a set limit.

⏳ Tokenized Links
Secure links are unique per user and expire after a short period.

🧱 Database Management
Built with SQLAlchemy and migrations powered by Flask-Migrate.

⚙️ Setup Guide
Requirements
Python 3.9 or higher

Git and pip installed

Installation Steps
bash
Copy
Edit
# Clone the repository
git clone https://github.com/AshleyMush/zimbos_portal.git
cd zimbos_portal

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
Environment Configuration
Create a .env file or export variables manually:

env
Copy
Edit
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///zimbos_app.db
GROUP_CHECKOUT_LIMIT=3
Run the Database Migrations
bash
Copy
Edit
flask db upgrade
Start the Application
bash
Copy
Edit
python app.py
Visit the app at http://localhost:8003

The first account to register will automatically become an admin. Admin routes are available at /admin.

📌 Roadmap
Planned features listed in TODO.txt:

Email verification after registration

Password reset functionality

Advanced link expiry settings

Basic user analytics dashboard

🤝 Contributing
Have ideas to make the Zimbos experience better?
Fork the repo, open an issue, or submit a pull request.

🔗 Developer
Visit ashleytanaka.dev for more projects and updates.
