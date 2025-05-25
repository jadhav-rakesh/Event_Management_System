# 📅 Collaborative Event Management System

A backend system built using **FastAPI** and **PostgreSQL** to manage collaborative events, including **user authentication**, **event creation**, **role-based permissions**, and **event sharing**.

---

## 🗂️ Entity Relationship Diagram (ERD)

The system is designed with four core entities:

- **Users**: Represents registered users.
- **Events**: Represents events created by users.
- **Permissions**: Defines specific permissions (e.g., read, write, share).
- **UserPermissions**: Links users to their permissions.

![ERD](./images/erd.png)

---

## 🔧 Features

- 🧑 User registration & login
- 🔐 Password hashing & authentication
- 📅 Full CRUD for events
- 🔄 Share events with users based on permission levels
- 🛡️ Role-based access control via `permissions` and `user_permissions`
- 🕒 Timestamps for creation and updates
- ✅ Basic RBAC enforced on event sharing and access

---

## 🛠️ Tech Stack

| Layer       | Technology     |
|-------------|----------------|
| Backend     | FastAPI        |
| Database    | PostgreSQL     |
| Auth        | OAuth2 + JWT   |
| ORM         | SQLAlchemy     |

---

## 🧱 Database Schema Overview

### `users`
| Column            | Type           |
|-------------------|----------------|
| id                | Serial (PK)    |
| email             | Varchar        |
| hashed_password   | Varchar        |
| full_name         | Varchar        |
| is_active         | Boolean        |
| created_at        | Timestamp      |
| updated_at        | Timestamp      |

### `events`
| Column            | Type           |
|-------------------|----------------|
| id                | Serial (PK)    |
| title             | Varchar        |
| description       | Varchar        |
| start_time        | Timestamp      |
| end_time          | Timestamp      |
| location          | Varchar        |
| owner_id          | ForeignKey → users.id |

### `permissions`
| Column            | Type           |
|-------------------|----------------|
| id                | Serial (PK)    |
| name              | Varchar        |
| description       | Varchar        |

### `user_permissions`
| Column            | Type           |
|-------------------|----------------|
| id                | Serial (PK)    |
| user_id           | ForeignKey → users.id |
| permission_id     | ForeignKey → permissions.id |

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/collab-event-manager.git
cd collab-event-manager
```

### 2. Create `.env` file

```env
DATABASE_URL=postgresql://username:password@localhost:5432/event_db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
uvicorn main:app --reload
```

---

## 📡 API Endpoints (Sample)

| Method | Endpoint              | Description                  |
|--------|------------------------|------------------------------|
| POST   | /users/register        | Register a new user         |
| POST   | /users/login           | Login and get JWT token     |
| GET    | /events/               | Get all user events         |
| POST   | /events/               | Create a new event          |
| PUT    | /events/{id}           | Update an event             |
| DELETE | /events/{id}           | Delete an event             |
| POST   | /events/{id}/share     | Share event with a user     |

---

## OPENAPI UI

![OPENAPI UI](./images/openapi_ui.png)

---

## 📄 License

MIT License. Feel free to fork and use.
