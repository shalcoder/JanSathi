import os
import sys
from app import create_app
from app.models.models import db, Scheme

def check():
    app = create_app()
    with app.app_context():
        count = Scheme.query.count()
        print(f"Schemes in DB: {count}")
        if count > 0:
            for s in Scheme.query.limit(5).all():
                print(f" - {s.title}")

if __name__ == "__main__":
    check()
