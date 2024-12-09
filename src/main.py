import asyncio
import sys
import argparse
from config import Config
from browser_client import BrowserClient
from authenticator import Authenticator
from session_parser import SessionParser
from session_selector import SessionSelector
from booking_workflow import BookingWorkflow

def parse_args():
    parser = argparse.ArgumentParser(description="Run the booking workflow.")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--verbose", action="store_true", help="Print verbose output")
    return parser.parse_args()

async def main():
    args = parse_args()
    config = Config()

    async with BrowserClient(headless=args.headless) as page:
        authenticator = Authenticator(page, config, verbose=args.verbose)
        session_parser = SessionParser(page, verbose=args.verbose)
        session_selector = SessionSelector(page, config.API_KEY, verbose=args.verbose)
        workflow = BookingWorkflow(page, authenticator, session_parser, session_selector, verbose=args.verbose)
        
        await workflow.run()

if __name__ == "__main__":
    asyncio.run(main())
