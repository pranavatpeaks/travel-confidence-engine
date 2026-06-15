from apscheduler.schedulers.blocking import BlockingScheduler

from core.orchestrator import collect_fares_once


def scheduled_job():

    print("Running collection cycle...")

    collect_fares_once()

    print("Collection cycle finished.")


scheduler = BlockingScheduler()

scheduler.add_job(
    scheduled_job,
    trigger="interval",
    minutes=1,
)

print(
    "Scheduler started "
    "(collecting every 1 minute)"
)

scheduler.start()