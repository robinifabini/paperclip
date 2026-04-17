"""
scheduler.py – runs the digest generation on a schedule
and keeps the Flask web server alive.

Uses APScheduler so we only need one Railway process.
Default: every day at 08:00 UTC
"""
import os
import threading
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import main as paperclub
import server

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

CRON_HOUR   = int(os.environ.get("CRON_HOUR",   "8"))
CRON_MINUTE = int(os.environ.get("CRON_MINUTE", "0"))

def run_digest():
    log.info("⏰ Scheduled digest starting ...")
    try:
        paperclub.main()
        log.info("✅ Digest complete")
    except Exception as e:
        log.error(f"❌ Digest failed: {e}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_digest,
        CronTrigger(hour=CRON_HOUR, minute=CRON_MINUTE),
        id="daily_digest",
        replace_existing=True,
    )
    scheduler.start()
    log.info(f"📅 Scheduler started – digest runs daily at {CRON_HOUR:02d}:{CRON_MINUTE:02d} UTC")

    # Also run once on startup so there's immediate output
    RUN_ON_START = os.environ.get("RUN_ON_START", "true").lower() == "true"
    if RUN_ON_START:
        log.info("🚀 Running initial digest on startup ...")
        threading.Thread(target=run_digest, daemon=True).start()

if __name__ == "__main__":
    start_scheduler()
    port = int(os.environ.get("PORT", 5000))
    log.info(f"🌐 Starting web server on port {port}")
    server.app.run(host="0.0.0.0", port=port)
