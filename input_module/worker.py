from celery import Celery


celery_app = Celery('input_module',
                    broker='amqp://guest:guest@localhost:5672/',
                    backend='rpc://guest:guest@localhost:5672/',
                    include=["input_module.tasks"])

celery_app.conf.update(task_track_started=True)

if __name__ == "__main__":
    celery_app.start()

# celery -A input_module.worker:celery_app worker --without-heartbeat --without-gossip --without-mingle
