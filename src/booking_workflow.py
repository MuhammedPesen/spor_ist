import os
import time

class BookingWorkflow:
    def __init__(self, page, authenticator, session_parser, session_selector, verbose=True):
        self.page = page
        self.authenticator = authenticator
        self.session_parser = session_parser
        self.session_selector = session_selector
        self.verbose = verbose

    async def run(self):
        # Login
        await self.authenticator.login()

        # Click seans button
        await self._invoke_postback()
        
        # Parse sessions
        session_list = await self.session_parser.parse_sessions()
        
        # Choose and check a session
        result = await self.session_selector.select_session(session_list)
        if result == "REPARSE":
            session_list = await self.session_parser.parse_sessions()
            await self.session_selector.select_session(session_list)

        # Finalize purchase
        await self._finalize_purchase()

        # Cleanup captcha files if they exist
        self._cleanup_captcha_files()

    async def _invoke_postback(self):
        await self.page.wait_for_load_state("networkidle")
        postback_call = "__doPostBack('ctl00$pageContent$rptListe$ctl01$lbtnSeansSecim','')"
        if self.verbose:
            print("Invoking __doPostBack...")
        await self.page.evaluate(postback_call)
        await self.page.wait_for_load_state("networkidle")
        time.sleep(3)
        if self.verbose:
            print("Postback invoked and page settled.")

    async def _finalize_purchase(self):
        close_button = await self.page.query_selector('#closeModal')
        if close_button:
            await close_button.click()
            time.sleep(1)
            if self.verbose:
                print("Closed the modal blocking the checkbox.")

        await self.page.wait_for_selector('#pageContent_cboxOnay')
        is_checked = await self.page.is_checked('#pageContent_cboxOnay')
        if not is_checked:
            await self.page.check('#pageContent_cboxOnay')
            if self.verbose:
                print("Checked the confirmation checkbox.")

        await self.page.wait_for_selector('#lbtnKaydet')
        await self.page.click('#lbtnKaydet')
        if self.verbose:
            print("Clicked the final Kaydet button.")
        await self.page.wait_for_load_state("networkidle")

    def _cleanup_captcha_files(self):
        for f in ["captcha.gif", "captcha.png"]:
            if os.path.exists(f):
                os.remove(f)
