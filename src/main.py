import asyncio
import sys
import argparse
import logging
from config import Config
from browser_client import BrowserClient
from authenticator import Authenticator
from session_parser import SessionParser
from session_selector import SessionSelector
from booking_workflow import BookingWorkflow

def parse_args():
    parser = argparse.ArgumentParser(description="Run the booking workflow.")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()

def setup_logging(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

async def main():
    args = parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        config = Config()
    except ValueError as e:
        logger.error(e)
        sys.exit(1)

    async with BrowserClient(headless=args.headless) as page:
        authenticator = Authenticator(page, config, logger)
        session_parser = SessionParser(page, logger)
        session_selector = SessionSelector(page, config.API_KEY, logger)
        workflow = BookingWorkflow(page, authenticator, session_parser, session_selector, logger)
        
        await workflow.run()

if __name__ == "__main__":
    asyncio.run(main())
