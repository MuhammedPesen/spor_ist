import asyncio
import sys
from captcha_solver import CaptchaSolver

class SessionSelector:
    def __init__(self, page, api_key, logger):
        self.page = page
        self.logger = logger
        self.solver = CaptchaSolver(api_key=api_key)

    async def select_session(self, session_list):
        self.logger.debug("Displaying all sessions.")
        for session in session_list:
            status = "Available" if session['available'] else "Unavailable"
            self.logger.info(f"[{session['index']}] {session['name']} | Status: {status}")

        try:
            choice = int(input("Enter the index of the session to select: "))
        except ValueError:
            self.logger.error("Invalid input. Please enter a valid session index.")
            return None

        chosen_session = next((s for s in session_list if s['index'] == choice), None)
        if not chosen_session:
            self.logger.error("Chosen session not found. Possibly no longer listed.")
            return None

        self.logger.info(f"Selected session: [{chosen_session['index']}] {chosen_session['name']} | Status: {'Available' if chosen_session['available'] else 'Unavailable'}")
        return chosen_session
