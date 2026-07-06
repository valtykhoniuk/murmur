"""Elastic Beanstalk entrypoint (WSGIPath=application)."""
from app.main import app

application = app
