from apscheduler.schedulers.blocking import BlockingScheduler

from core.orchestrator import collect_fares_once


scheduler = BlockingScheduler()


scheduler.add_job(
    collect_fares_once,
    trigger="interval",
    minutes=1,
)


print(
    "Scheduler started "
    "(collecting every 1 minute)"
)

scheduler.start()