from celery import current_app as current_celery_app

from app.config import settings


def create_celery():
    """Factory function that configures and returns the current Celery instance"""
    celery_app = current_celery_app
    
    # Note: All Celery-related config keys should be prefixed with "CELERY_"
    celery_app.config_from_object(settings, namespace="CELERY")

    return celery_app
