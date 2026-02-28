from apscheduler.schedulers.background import BackgroundScheduler
from skillrot_app.db.database import SessionLocal
from skillrot_app.services.reminder_service import check_and_create_reminders

scheduler = BackgroundScheduler()


def start_scheduler():

    def job():
        db = SessionLocal()
        try:
            check_and_create_reminders(db)
        finally:
            db.close()

    # Run every 1 hour
    scheduler.add_job(job, "interval", hours=1)
    scheduler.start()