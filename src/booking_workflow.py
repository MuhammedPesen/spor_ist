import os, sys
import time
import asyncio

class BookingWorkflow:
    def __init__(self, page, authenticator, session_parser, session_selector, logger):
        self.page = page
        self.authenticator = authenticator
        self.session_parser = session_parser
        self.session_selector = session_selector
        self.logger = logger

    async def run(self):
        try:
            # Login
            await self.authenticator.login()

            # Click seans button
            await self._invoke_postback()

            # Initial session parsing
            session_list = await self.session_parser.parse_sessions()

            # Choose a session
            chosen_session = await self.session_selector.select_session(session_list)
            if not chosen_session:
                self.logger.error("No valid session selected. Exiting.")
                sys.exit(1)

            while True:
                if chosen_session['available']:
                    self.logger.info(f"Session '{chosen_session['name']}' is available. Attempting to book...")
                    success = await self._book_session(chosen_session)
                    if success:
                        self.logger.info("Booking finalized successfully.")
                        break
                    else:
                        self.logger.error("Failed to finalize booking. Will retry in 30 seconds.")
                else:
                    self.logger.info(f"Session '{chosen_session['name']}' is unavailable. Checking again in 30 seconds...")

                await asyncio.sleep(30)
                await self.page.reload()
                await self.page.wait_for_load_state("networkidle")
                session_list = await self.session_parser.parse_sessions()
                # Re-fetch the chosen session's availability
                chosen_session = next((s for s in session_list if s['index'] == chosen_session['index']), chosen_session)
                if not chosen_session:
                    self.logger.error("Chosen session no longer exists. Exiting.")
                    sys.exit(1)

            # Cleanup captcha files if they exist
            self._cleanup_captcha_files()

        except Exception as e:
            self.logger.error(f"An error occurred during the booking workflow: {e}")
            self._cleanup_captcha_files()
            sys.exit(1)

    async def _invoke_postback(self):
        await self.page.wait_for_load_state("networkidle")
        postback_call = "__doPostBack('ctl00$pageContent$rptListe$ctl01$lbtnSeansSecim','')"
        self.logger.info("Invoking __doPostBack...")
        await self.page.evaluate(postback_call)
        await self.page.wait_for_load_state("networkidle")
        time.sleep(3)
        self.logger.info("Postback invoked and page settled.")

    async def _book_session(self, session):
        if session['checkbox_id']:
            checkbox_selector = f'#{session["checkbox_id"]}'

            captcha_data = {"content": None, "url": None}

            def handle_response(response):
                if "seanssecimcaptcha" in response.url and response.status == 200:
                    asyncio.create_task(capture_captcha(response))

            async def capture_captcha(response):
                captcha_data["content"] = await response.body()
                self.logger.debug("Captured CAPTCHA content.")

            self.page.on("response", handle_response)

            await self.page.check(checkbox_selector)
            self.logger.info(f"Checked session '{session['name']}'.")

            # Wait for the CAPTCHA image
            await self.page.wait_for_selector('#pageContent_captchaImage')
            self.logger.debug("Waiting for CAPTCHA to appear.")

            # Wait until captcha_data is populated
            timeout = 10  # seconds
            for _ in range(timeout):
                if captcha_data["content"]:
                    break
                await asyncio.sleep(1)
            else:
                self.logger.error("Failed to capture CAPTCHA within timeout.")
                return False

            # Save CAPTCHA image
            captcha_path = "captcha.png" if captcha_data["content"].startswith(b'\x89PNG') else "captcha.gif"
            with open(captcha_path, "wb") as f:
                f.write(captcha_data["content"])
            self.logger.info(f"Saved CAPTCHA image as {captcha_path}.")

            # Solve CAPTCHA
            try:
                captcha_solution = self.session_selector.solver.solve_captcha(captcha_path)
                self.logger.info(f"CAPTCHA solution: {captcha_solution}")
            except Exception as e:
                self.logger.error(f"Error solving CAPTCHA: {e}")
                return False

            # Fill in CAPTCHA solution
            await self.page.fill('input[name="ctl00$pageContent$txtCaptchaText"]', captcha_solution)
            self.logger.info("Filled CAPTCHA solution.")

            # Finalize booking
            close_button = await self.page.query_selector('#closeModal')
            if close_button:
                await close_button.click()
                time.sleep(1)
                self.logger.info("Closed the modal blocking the checkbox.")

            await self.page.wait_for_selector('#pageContent_cboxOnay')
            is_checked = await self.page.is_checked('#pageContent_cboxOnay')
            if not is_checked:
                await self.page.check('#pageContent_cboxOnay')
                self.logger.info("Checked the confirmation checkbox.")

            await self.page.wait_for_selector('#lbtnKaydet')
            await self.page.click('#lbtnKaydet')
            self.logger.info("Clicked the final Kaydet button.")
            await self.page.wait_for_load_state("networkidle")
            self.logger.info("Finalization complete.")

            return True
        else:
            self.logger.warning(f"Session '{session['name']}' is available but no checkbox found.")
            return False

    def _cleanup_captcha_files(self):
        for f in ["captcha.gif", "captcha.png"]:
            if os.path.exists(f):
                os.remove(f)
                self.logger.debug(f"Removed {f}.")
