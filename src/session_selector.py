import asyncio
import sys
from captcha_solver import CaptchaSolver

class SessionSelector:
    def __init__(self, page, api_key, verbose=True):
        self.page = page
        self.verbose = verbose
        self.solver = CaptchaSolver(api_key=api_key)

    async def select_session(self, session_list):
        print("\nAvailable Sessions:")
        for session in session_list:
            status = "Available" if session['available'] else "Unavailable"
            print(f"[{session['index']}] {session['name']} | Status: {status}")

        choice = int(input("Enter the index of the session to select: "))
        
        while True:
            chosen_session = next((s for s in session_list if s['index'] == choice), None)
            if chosen_session is None:
                if self.verbose:
                    print("Chosen session not found. Possibly no longer listed.")
                return

            if chosen_session['available']:
                if chosen_session['checkbox_id']:
                    checkbox_selector = f'#{chosen_session["checkbox_id"]}'

                    captcha_data = {"content": None, "url": None}
                    def handle_response(response):
                        if "seanssecimcaptcha" in response.url and response.status == 200:
                            captcha_data["url"] = response.url
                            captcha_data["content"] = response.body()

                    self.page.on("response", handle_response)

                    await self.page.check(checkbox_selector)
                    if self.verbose:
                        print(f"Session '{chosen_session['name']}' has been checked.")

                    
                    await self.page.reload()
                    await self.page.wait_for_selector('#pageContent_captchaImage')

                    if captcha_data["content"]:
                        with open("captcha.gif", "wb") as f:
                            f.write(await captcha_data["content"])
                        if self.verbose:
                            print(f"CAPTCHA saved from network request: {captcha_data['url']}")

                        captcha_solution = self.solver.solve_captcha("captcha.gif")
                        if self.verbose:
                            print("CAPTCHA solution:", captcha_solution)
                        await self.page.fill('input[name="ctl00$pageContent$txtCaptchaText"]', captcha_solution)

                        if self.verbose:
                            print(f"Session '{chosen_session['name']}' confirmed with CAPTCHA solved.")
                    else:
                        print("Failed to capture CAPTCHA.")
                        sys.exit("CAPTCHA capture failed.")
                    break
                else:
                    if self.verbose:
                        print(f"Session '{chosen_session['name']}' is available but no checkbox found.")
                    break
            else:
                if self.verbose:
                    print(f"Session '{chosen_session['name']}' is unavailable. Checking again in 30 seconds...")
                await asyncio.sleep(30)
                await self.page.reload()
                await self.page.wait_for_load_state("networkidle")
                return "REPARSE"
