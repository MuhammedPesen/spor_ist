class Authenticator:
    def __init__(self, page, config, logger):
        self.page = page
        self.config = config
        self.logger = logger

    async def login(self):
        self.logger.debug("Navigating to login URL.")
        await self.page.goto(self.config.LOGIN_URL)
        await self.page.wait_for_selector('input[name="txtTCPasaport"]')
        self.logger.debug("Filling in TCKN.")
        await self.page.fill('input[name="txtTCPasaport"]', self.config.TCKN)
        self.logger.debug("Filling in password.")
        await self.page.fill('input[name="txtSifre"]', self.config.PASSWORD)
        self.logger.debug("Clicking login button.")
        await self.page.click('input[name="btnGirisYap"]')
        await self.page.wait_for_load_state("networkidle")
        self.logger.info("Logged in successfully.")
        # Navigate to dashboard
        self.logger.debug("Navigating to dashboard URL.")
        await self.page.goto(self.config.DASHBOARD_URL)
        await self.page.wait_for_load_state("networkidle")
