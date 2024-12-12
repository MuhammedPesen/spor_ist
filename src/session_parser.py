from bs4 import BeautifulSoup
import time

class SessionParser:
    def __init__(self, page, logger):
        self.page = page
        self.logger = logger

    async def parse_sessions(self):
        self.logger.debug("Checking for and closing any blocking modal.")
        close_button = await self.page.query_selector('#closeModal')
        if close_button:
            await close_button.click()
            time.sleep(1)
            self.logger.info("Closed the blocking modal.")

        self.logger.debug("Parsing session elements.")
        session_elements = await self.page.query_selector_all('#dvScheduler .col-md-1 .panel-body .well')
        session_list = []

        for index, session in enumerate(session_elements):
            html = await session.evaluate("(node) => node.outerHTML")
            soup = BeautifulSoup(html, 'html.parser')

            salon_label = soup.find('label', title="Salon Adı")
            time_span = soup.find('span', id=lambda x: x and 'lblSeansSaat' in x)
            kalan_kontenjan = soup.find('span', title="Kalan Kontenjan")

            if not (salon_label and time_span and kalan_kontenjan):
                continue

            salon_name = salon_label.get_text(strip=True)
            time_range = time_span.get_text(strip=True)
            remaining_spots = kalan_kontenjan.get_text(strip=True)

            input_checkbox = soup.select_one('.cboxStyle input[id]')
            checkbox_id = input_checkbox['id'] if input_checkbox else None

            try:
                spots = int(remaining_spots)
                available = spots > 0
            except ValueError:
                available = False

            session_name = f"{salon_name} | {time_range} | Kalan: {remaining_spots}"
            session_list.append({
                'index': index,
                'name': session_name,
                'available': available,
                'checkbox_id': checkbox_id
            })

        self.logger.info(f"Parsed {len(session_list)} sessions.")
        return session_list
