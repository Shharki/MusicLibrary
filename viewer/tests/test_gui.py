import time
from unittest import skip

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By


class GuiTestWithSelenium(LiveServerTestCase):

    # GUI test spustíme zakomentováním/odstraněním @skip
    # Nelze commitnout do GITU, neprojde testy
    @skip
    def test_home_and_songs_page(self):
        drivers = [webdriver.Firefox(), webdriver.Chrome()]
        for driver in drivers:
            try:
                # Otevře hlavní stránku
                driver.get(f'{self.live_server_url}/')
                time.sleep(1)
                assert "Welcome to music database MusicLibrary." in driver.page_source

                # Otevře stránku se seznamem písní
                driver.get(f'{self.live_server_url}/songs/')
                time.sleep(1)
                assert "Song list" in driver.page_source

                # Zkontroluje, že tam je buď nějaká píseň, nebo prázdné hlášení
                assert (
                    "There is no song in the database."
                    in driver.page_source
                    or "<br>" in driver.page_source
                )
            finally:
                driver.quit()