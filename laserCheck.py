from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Button


class LaserChecker:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)

    def skeleton(self, address: str):
        table = [500, 1000, 1500, 2000]
        self.realValue = []

        self.driver.get(f"http://{address}:3000/#/")  # use passed address
        self.driver.find_element(By.LINK_TEXT, "Controls").click()
        self.driver.find_element(By.LINK_TEXT, "XY Panel").click()
        self.driver.find_element(
            By.CSS_SELECTOR,
            "#sinterit_web > div > div.position-relative > div.container.position-relative > div > div > div > div > ul > div:nth-child(1) > li:nth-child(1) > div:nth-child(1) > div:nth-child(4) > div > button"
        ).click()
        self.laser(table)

    def laser(self, table):
        powerOverride = self.driver.find_element(
            By.CSS_SELECTOR,
            "#sinterit_web > div > div.position-relative > div.container.position-relative > div > div > div > div > ul > div:nth-child(1) > li:nth-child(3) > div > div:nth-child(2) > input"
        )
        for x in table:
            print(x)
            powerOverride.send_keys(Keys.CONTROL, "a")
            powerOverride.send_keys(x)
            self.driver.find_element(
                By.CSS_SELECTOR,
                "#sinterit_web > div > div.position-relative > div.container.position-relative > div > div > div > div > ul > div:nth-child(1) > li:nth-child(3) > div > div:nth-child(4) > button"
            ).click()
            self.realValue.append(input("Value from gauge: "))

            stat = statistic(self.realValue, table)      
            prec = stat.prec() 
            print("AVG:[%] " + prec)
            print("Sum AVG[%] "+stat.avgPrec(prec))        
            
            time.sleep(3)

        


class TextualGui(App):

    def compose(self) -> ComposeResult:
        self.static = Static("⚡ Laser Semi Manual Tester ⚡")
        yield self.static
        self.address_input = Input(placeholder="IP address of printer", id="ip_input")
        yield self.address_input
        yield Button("Turn Laser On", id="laser_button")

    def on_mount(self):
        self.static.styles.background = "blue"
        self.static.styles.border = ("solid", "white")
        self.static.styles.text_align = "center"
        self.static.styles.padding = (1, 1)
        self.static.styles.margin = (4, 4)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "laser_button":
            ip_address = self.address_input.value.strip()
            if ip_address:
                laser = LaserChecker()
                laser.skeleton(ip_address)
            else:
                print("No IP address entered!")

class statistic:
    def __init__(self, real, given):
        self.real = real
        self.given = given
        self.delta = None
    def difer(self):
        self.delta = []
        for i in range(len(self.given)):
            holder = self.real[i] - self.given[i]
            self.delta.append(holder)
    def prec(self):
        percents = []
        if self.delta is None:
            self.difer()
        for i in range(len(self.delta)):
            percHolder = (self.delta[i] / self.real[i] * 100)
            percents.append(percHolder)
        return(percents)
    def avgPrec(self, percTab):
        return(sum(percTab)/len(self.delta))
        


if __name__ == "__main__":
    app = TextualGui()
    app.run()
