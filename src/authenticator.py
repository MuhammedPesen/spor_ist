class Authenticator:
    def __init__(self, page, config, verbose=True):
        self.page = page
        self.config = config
        self.verbose = verbose

    async def login(self):
        await self.page.goto(self.config.LOGIN_URL)
        await self.page.wait_for_selector('input[name="txtTCPasaport"]')
        await self.page.fill('input[name="txtTCPasaport"]', self.config.TCKN)
        await self.page.fill('input[name="txtSifre"]', self.config.PASSWORD)
        await self.page.click('input[name="btnGirisYap"]')
        await self.page.wait_for_load_state("networkidle")
        await self.page.goto(self.config.DASHBOARD_URL)
        await self.page.wait_for_load_state("networkidle")
        if self.verbose:
            print("Logged in successfully.")
