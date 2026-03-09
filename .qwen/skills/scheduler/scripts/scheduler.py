"""
Scheduler - Task scheduling for AI Employee.

Provides scheduling capabilities using APScheduler for cross-platform support.

Usage:
    python scheduler.py --vault /path/to/vault
"""

import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIScheduler:
    """AI Employee task scheduler."""
    
    def __init__(self, vault_path: str, config: Dict[str, Any] = None):
        """
        Initialize scheduler.
        
        Args:
            vault_path: Path to Obsidian vault
            config: Scheduler configuration
        """
        self.vault_path = Path(vault_path).resolve()
        self.config = config or {}
        
        if not APSCHEDULER_AVAILABLE:
            logger.warning("APScheduler not available. Install with: pip install apscheduler")
            self.scheduler = None
            return
        
        self.scheduler = BlockingScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Setup scheduled jobs."""
        if not self.scheduler:
            return
        
        # Daily Briefing at 8:00 AM
        if self.config.get('enable_daily_briefing', True):
            self.scheduler.add_job(
                self.daily_briefing,
                CronTrigger(hour=8, minute=0),
                id='daily_briefing',
                name='Daily CEO Briefing',
                replace_existing=True
            )
            logger.info("Scheduled: Daily Briefing at 08:00")
        
        # Hourly Queue Processing
        if self.config.get('enable_hourly_check', True):
            self.scheduler.add_job(
                self.hourly_check,
                CronTrigger(minute=0),
                id='hourly_check',
                name='Hourly Queue Processing',
                replace_existing=True
            )
            logger.info("Scheduled: Hourly Check at :00")
        
        # Weekly Audit on Sunday at 10:00 PM
        if self.config.get('enable_weekly_audit', True):
            self.scheduler.add_job(
                self.weekly_audit,
                CronTrigger(day_of_week='sun', hour=22, minute=0),
                id='weekly_audit',
                name='Weekly Business Audit',
                replace_existing=True
            )
            logger.info("Scheduled: Weekly Audit on Sunday at 22:00")
        
        # Monthly Review on 1st at 9:00 AM
        if self.config.get('enable_monthly_review', True):
            self.scheduler.add_job(
                self.monthly_review,
                CronTrigger(day=1, hour=9, minute=0),
                id='monthly_review',
                name='Monthly Accounting Review',
                replace_existing=True
            )
            logger.info("Scheduled: Monthly Review on 1st at 09:00")
    
    def daily_briefing(self):
        """Generate daily CEO briefing."""
        logger.info("Generating daily briefing...")
        try:
            from orchestrator import Orchestrator
            orch = Orchestrator(str(self.vault_path))
            orch.generate_daily_briefing()
            logger.info("Daily briefing completed")
        except Exception as e:
            logger.error(f"Daily briefing failed: {e}")
    
    def hourly_check(self):
        """Process Needs_Action queue."""
        logger.info("Processing queue...")
        try:
            from orchestrator import Orchestrator
            orch = Orchestrator(str(self.vault_path))
            orch.process_queue()
            logger.info("Queue processing completed")
        except Exception as e:
            logger.error(f"Queue processing failed: {e}")
    
    def weekly_audit(self):
        """Generate weekly business audit."""
        logger.info("Running weekly audit...")
        try:
            from orchestrator import Orchestrator
            orch = Orchestrator(str(self.vault_path))
            orch.weekly_audit()
            logger.info("Weekly audit completed")
        except Exception as e:
            logger.error(f"Weekly audit failed: {e}")
    
    def monthly_review(self):
        """Generate monthly accounting review."""
        logger.info("Running monthly review...")
        try:
            from orchestrator import Orchestrator
            orch = Orchestrator(str(self.vault_path))
            orch.monthly_review()
            logger.info("Monthly review completed")
        except Exception as e:
            logger.error(f"Monthly review failed: {e}")
    
    def start(self):
        """Start the scheduler."""
        if not self.scheduler:
            logger.error("Scheduler not initialized (APScheduler not available)")
            return
        
        logger.info("Starting scheduler...")
        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
    
    def add_job(self, func, trigger: str, **kwargs):
        """
        Add custom scheduled job.
        
        Args:
            func: Function to call
            trigger: Trigger type ('cron', 'interval', 'date')
            **kwargs: Trigger-specific arguments
        """
        if not self.scheduler:
            return
        
        if trigger == 'cron':
            cron_trigger = CronTrigger(**kwargs)
            self.scheduler.add_job(func, cron_trigger)
        elif trigger == 'interval':
            interval_trigger = IntervalTrigger(**kwargs)
            self.scheduler.add_job(func, interval_trigger)
        elif trigger == 'date':
            from apscheduler.triggers.date import DateTrigger
            date_trigger = DateTrigger(run_date=kwargs.get('run_date'))
            self.scheduler.add_job(func, date_trigger)
        
        logger.info(f"Added job: {func.__name__}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='AI Employee Scheduler')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--config', help='Path to config.json')
    parser.add_argument('--no-daily', action='store_true', help='Disable daily briefing')
    parser.add_argument('--no-hourly', action='store_true', help='Disable hourly check')
    parser.add_argument('--no-weekly', action='store_true', help='Disable weekly audit')
    parser.add_argument('--no-monthly', action='store_true', help='Disable monthly review')
    
    args = parser.parse_args()
    
    # Build config
    config = {
        'enable_daily_briefing': not args.no_daily,
        'enable_hourly_check': not args.no_hourly,
        'enable_weekly_audit': not args.no_weekly,
        'enable_monthly_review': not args.monthly
    }
    
    # Load config file if provided
    if args.config and Path(args.config).exists():
        import json
        file_config = json.loads(Path(args.config).read_text())
        config.update(file_config)
    
    # Create and start scheduler
    scheduler = AIScheduler(args.vault, config)
    scheduler.start()


if __name__ == '__main__':
    main()
