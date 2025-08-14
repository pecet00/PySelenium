from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Static, Button, Input
from textual import on
import asyncio

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MyLog(Static):
    def on_mount(self):
        self.lines = []

    def write(self, text: str):
        self.lines.append(text)
        self.update("\n".join(self.lines))


class TerminalAppGui(App):
    CSS = """
    Screen { layout: vertical; }
    #top { height: 3; background: darkgreen; text-align: center; text-style: bold; }
    #main { layout: horizontal; }
    #left { width: 30%; background: #444; align: center middle; }
    #right { width: 70%; background: #222; }
    #bottom { height: 3; background: darkblue; text-align: center; }
    Button, Input { width: 90%; margin: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Static("⚡ LisaX laser checker ⚡", id="top")

        with Container(id="main"):
            with VerticalScroll(id="left"):
                yield Input(placeholder="IP address of printer!", id="ip_input")
                yield Button("Run Laser !", id="run_btn")

            with VerticalScroll(id="right"):
                yield MyLog(id="log_panel")

        yield Static("by FK dev Squad", id="bottom")

    @on(Button.Pressed, "#run_btn")
    async def run_laser(self) -> None:
        log_panel = self.query_one("#log_panel", MyLog)
        ip = self.query_one("#ip_input", Input).value.strip()

        if not ip:
            log_panel.write("[ERROR] Nie podano IP!")
            return

        log_panel.write(f"[START] Uruchamiam laser dla IP: {ip}")

        asyncio.create_task(self.run_selenium(ip, log_panel))

    async def run_selenium(self, ip: str, log_panel: MyLog):
        await asyncio.to_thread(self.selenium_task, ip, log_panel)

    def selenium_task(self, ip: str, log_panel: MyLog):
        try:
            table = [500, 1000, -1]
            driver = webdriver.Chrome()
            driver.implicitly_wait(30)

            log_panel.write(f"[INFO] Otwieram stronę: http://{ip}:3000/#/")
            driver.get(f"http://{ip}:3000/#/")

            driver.find_element(By.LINK_TEXT, "Controls").click()
            driver.find_element(By.LINK_TEXT, "XY Panel").click()
            driver.find_element(By.CSS_SELECTOR,
                "#sinterit_web > div > div.position-relative > div.container.position-relative > "
                "div > div > div > div > ul > div:nth-child(1) > li:nth-child(1) > div:nth-child(1) "
                "> div:nth-child(4) > div > button"
            ).click()

            powerOverride = driver.find_element(By.CSS_SELECTOR,
                "#sinterit_web > div > div.position-relative > div.container.position-relative > "
                "div > div > div > div > ul > div:nth-child(1) > li:nth-child(3) > div > div:nth-child(2) > input"
            )

            for x in table:
                log_panel.write(f"[ACTION] Ustawiam moc lasera na: {x}")
                powerOverride.send_keys(Keys.CONTROL, "a")
                powerOverride.send_keys(str(x))
                driver.find_element(By.CSS_SELECTOR,
                    "#sinterit_web > div > div.position-relative > div.container.position-relative > "
                    "div > div > div > div > ul > div:nth-child(1) > li:nth-child(3) > div > div:nth-child(4) > button"
                ).click()
                time.sleep(3)

            log_panel.write("[DONE] Operacja zakończona, zamykam przeglądarkę...")
            time.sleep(2)
            driver.quit()

        except Exception as e:
            log_panel.write(f"[ERROR] {e}")


if __name__ == '__main__':
    TerminalAppGui().run()
