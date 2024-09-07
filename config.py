import os
from datetime import timedelta
from flask import Flask
from celery import Celery, Task
from flask_mysqldb import MySQL

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name) # , task_cls=FlaskTask
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.Task = FlaskTask
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def create_app() -> Flask:
    # Create Flask application
    app = Flask(__name__)

    global mysql
    mysql = MySQL(app)
    
    app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
    app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'password')
    app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'parkinson_diagnosis_fyp')

    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

    app.config['SECRET_KEY'] = os.urandom(24)

    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://127.0.0.1:6379/0",
            result_backend="redis://127.0.0.1:6379/0",
            task_ignore_result=True,
            imports=("tasks",),
        ),
    )

    app.config.from_prefixed_env()
    celery_init_app(app)
    return app, mysql
