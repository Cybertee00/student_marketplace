"""
Scheduled tasks for the Student Marketplace application
"""
import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import get_db
from utils.notification_utils import NotificationUtils

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationScheduler:
    """Handles scheduled notification cleanup tasks"""
    
    def __init__(self):
        self.running = False
        self.cleanup_interval = 24 * 60 * 60  # 24 hours in seconds
    
    async def start_cleanup_scheduler(self):
        """Start the notification cleanup scheduler"""
        if self.running:
            logger.warning("Cleanup scheduler is already running")
            return
        
        self.running = True
        logger.info("Starting notification cleanup scheduler")
        
        while self.running:
            try:
                await self._cleanup_expired_notifications()
                logger.info(f"Next cleanup scheduled in {self.cleanup_interval} seconds")
                await asyncio.sleep(self.cleanup_interval)
            except Exception as e:
                logger.error(f"Error in cleanup scheduler: {e}")
                # Wait 1 hour before retrying on error
                await asyncio.sleep(3600)
    
    async def _cleanup_expired_notifications(self):
        """Clean up expired notifications"""
        try:
            # Get a database session
            db = next(get_db())
            try:
                deleted_count = NotificationUtils.cleanup_expired_notifications(db)
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired notifications")
                else:
                    logger.debug("No expired notifications to clean up")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error cleaning up notifications: {e}")
    
    def stop_cleanup_scheduler(self):
        """Stop the notification cleanup scheduler"""
        logger.info("Stopping notification cleanup scheduler")
        self.running = False

# Global scheduler instance
notification_scheduler = NotificationScheduler()

async def start_background_tasks():
    """Start all background tasks"""
    logger.info("Starting background tasks")
    
    # Start notification cleanup scheduler
    await notification_scheduler.start_cleanup_scheduler()

def stop_background_tasks():
    """Stop all background tasks"""
    logger.info("Stopping background tasks")
    notification_scheduler.stop_cleanup_scheduler()

# Manual cleanup function for testing
async def manual_cleanup():
    """Manually trigger notification cleanup"""
    try:
        db = next(get_db())
        try:
            deleted_count = NotificationUtils.cleanup_expired_notifications(db)
            logger.info(f"Manual cleanup: Deleted {deleted_count} expired notifications")
            return deleted_count
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error in manual cleanup: {e}")
        return 0
