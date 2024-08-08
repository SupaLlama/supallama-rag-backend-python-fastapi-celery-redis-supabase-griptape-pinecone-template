from app import create_fastapi_app


app = create_fastapi_app()
celery = app.celery_app
