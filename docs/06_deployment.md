# Deployment Notes

## Local (development)
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt
PYTHONPATH=. python database/init_db.py
PYTHONPATH=. python backend/run.py
```

## Production checklist
1. Set strong `SECRET_KEY` environment variable
2. Use PostgreSQL: `DATABASE_URL=postgresql://user:pass@host/db`
3. Run behind Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 "backend.app:create_app()"
   ```
4. Serve static files via Nginx
5. Enable HTTPS
6. Disable debug mode
7. Regular DB backups

## Environment variables
| Variable       | Purpose                  |
|----------------|--------------------------|
| SECRET_KEY     | Session & CSRF signing   |
| DATABASE_URL   | SQLAlchemy connection    |

## Demo credentials (change after first login)
- admin@The Cozy Knot.com / admin123
- customer@The Cozy Knot.com / cust123
