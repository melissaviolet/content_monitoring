# Content Monitoring & Flagging System

##  Overview

This project is a simplified backend system built using **Django** and **Django REST Framework**.
It ingests content, matches it against user-defined keywords, generates flags, and supports a human review workflow with suppression logic.

---

##  Features

* Add and manage keywords
* Import external (mock) content
* Scan content against keywords
* Generate flags with match scores
* Review flags (pending, relevant, irrelevant)
* Suppress irrelevant results unless content changes

---

##  Tech Stack

* Python
* Django
* Django REST Framework
* SQLite (default)

---

##  Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/melissaviolet/content_monitoring.git
cd content_monitoring
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the server

```bash
python manage.py runserver
```

Server will run at:

```
http://127.0.0.1:8000/
```

---

## 🔗 API Endpoints

| Method | Endpoint               | Description                  |
| ------ | ---------------------- | ---------------------------- |
| POST   | `/api/keywords/`       | Create a keyword             |
| GET    | `/api/keywords/`       | List keywords                |
| POST   | `/api/import-content/` | Load mock content            |
| POST   | `/api/scan/`           | Run keyword-content matching |
| GET    | `/api/flags/`          | List generated flags         |
| PATCH  | `/api/flags/{id}/`     | Update flag status           |

---

##  Example Requests

### Create Keyword

```json
POST /api/keywords/
{
  "name": "django"
}
```

---

### Import Content

```
POST /api/import-content/
```

---

### Run Scan

```
POST /api/scan/
```

---

### Update Flag Status

```json
PATCH /api/flags/1/
{
  "status": "irrelevant"
}
```

---

## Matching Logic

The system uses a deterministic scoring mechanism:

- Exact keyword match in title → **100**
- Partial keyword match in title → **70**
- Keyword appears in body → **base score 40**

### Improvement:
- If a keyword appears multiple times in the body, the score increases slightly based on frequency.
- This allows more relevant content to rank higher while keeping the logic simple and explainable.

---

##  Suppression Logic

If a flag is marked as **irrelevant**, it will not appear in future scans unless the associated content item changes.

### Implementation Details:

* Each flag stores a `reviewed_at` timestamp.
* Each content item has a `last_updated` field.
* A suppressed flag is only reactivated if:

```
content.last_updated > flag.reviewed_at
```

---

##  Project Structure

```
monitoring/
│
├── models.py
├── serializers.py
├── views.py
├── urls.py
├── services/
│   ├── scanner.py
│   └── content_loader.py
```

---

##  Assumptions & Trade-offs

* A mock dataset is used instead of a live API for simplicity and reliability.
* Matching is case-insensitive and based on simple string checks.
* Duplicate flags are avoided using `get_or_create`.
* SQLite is used for quick local setup.
* Basic deduplication is enforced at both application and database level.


---
##  Bonus Improvements

The following enhancements were implemented to improve the system:

###  Deduplication
- Duplicate flags are prevented using `get_or_create`.
- Additionally, a database-level constraint ensures uniqueness of `(keyword, content_item)` pairs.

###  Improved Matching Logic
- Matching logic considers keyword frequency in the content body.
- More occurrences result in slightly higher scores.

###  Admin Interface Enhancements
- Django admin is configured for all models.
- Flags can be easily reviewed and filtered by status.
- This provides a simple UI for managing the review workflow.

###  Admin Access

A Django admin interface is available for managing data:

```text
http://127.0.0.1:8000/admin/
```
---
##  Conclusion

This project focuses on clean architecture, correct business logic, and maintainability rather than over-engineering.
The implementation demonstrates separation of concerns, proper API design, and handling of real-world edge cases like suppression.

---
