from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pickle, os, time


class BSF:
    ORDER_FORM = "//div[@name='orderForm']/"

    XPATH = {
        "tab-LIMIT": {
            "all_in_25": f"{ORDER_FORM}div[4]/form/div[3]/div[1]/div/div[6]",
            "all_in_50": f"{ORDER_FORM}div[4]/form/div[3]/div[1]/div/div[7]",
            "all_in_75": f"{ORDER_FORM}div[4]/form/div[3]/div[1]/div/div[8]",
            "all_in_100": f"{ORDER_FORM}div[4]/form/div[3]/div[1]/div/div[9]",
            "TPSL_select": f"{ORDER_FORM}div[4]/form/div[4]/div/label/div[1]/input",
            "TPSL_click": f"{ORDER_FORM}div[4]/form/div[4]/div/label/div[1]",
            "TP": f"{ORDER_FORM}div[4]/form/div[4]/div[2]/div/input",
            "SL": f"{ORDER_FORM}div[4]/form/div[4]/div[3]/div/input",
            "BUY": f"{ORDER_FORM}div[4]/form/div[6]/button[1]",
            "SELL": f"{ORDER_FORM}div[4]/form/div[6]/button[2]",
            "PRICE": f"{ORDER_FORM}div[4]/form/div[1]/div/input",
        },
        "tab-MARKET": {
            "all_in_25": f"{ORDER_FORM}div[4]/form/div[2]/div[1]/div/div[6]",
            "all_in_50": f"{ORDER_FORM}div[4]/form/div[2]/div[1]/div/div[7]",
            "all_in_75": f"{ORDER_FORM}div[4]/form/div[2]/div[1]/div/div[8]",
            "all_in_100": f"{ORDER_FORM}div[4]/form/div[2]/div[1]/div/div[9]",
            "TPSL_select": f"{ORDER_FORM}div[4]/form/div[3]/div/label/div[1]/input",
            "TPSL_click": f"{ORDER_FORM}div[4]/form/div[3]/div/label/div[1]",
            "TP": f"{ORDER_FORM}div[4]/form/div[3]/div[2]/div/input",
            "SL": f"{ORDER_FORM}div[4]/form/div[3]/div[3]/div/input",
            "BUY": f"{ORDER_FORM}div[4]/form/div[4]/button[1]",
            "SELL": f"{ORDER_FORM}div[4]/form/div[4]/button[2]",
        },
    }

    def __init__(self, driver, order_type="tab-LIMIT"):
        self.driver = driver
        self.driver.get("https://accounts.binance.com/en/login")
        self.order_type = order_type # tab-LIMIT / tab-MARKET

    def __del__(self):
        self.close()

    def close(self):
        self.driver.close()

    def refresh(self):
        self.driver.refresh()

    def save_cookies(self, email):
        filename = f"cookies/{email}.pkl"
        pickle.dump(
            self.driver.get_cookies(),
            open(filename, "wb")
        )

    def set_futures(self):
        self.driver.get("https://www.binance.com/en/futures/BTCUSDT")
        self.set_order_type(self.order_type)

    def set_order_type(self, order_type):
        self.driver.find_element_by_id(order_type).click()
        self.order_type = order_type

    def set_leverage(self, leverage):
        actual_leverage = int(
            self.driver.find_element_by_xpath(
                f"""{self.ORDER_FORM}div[1]/div[1]/div[1]/a[2]"""
            ).text[:-1])
        if actual_leverage != leverage:
            self.driver.find_element_by_xpath(
                f"""{self.ORDER_FORM}div[1]/div[1]/div[1]/a[2]"""
            ).click()
            pas = actual_leverage - leverage
            if pas > 0:
                for i in range(pas):  # Plus
                    self.driver.find_element_by_xpath(
                        "//button[@class=' css-vc3jb5']"
                    ).click()
            else:
                for i in range(-pas):  # Moins
                    self.driver.find_element_by_xpath(
                        "//button[@class=' css-1ri8vxv']"
                    ).click()
            self.driver.find_element_by_xpath(
                "//button[@class=' css-1fds4m2']"
            ).click()

    def get_avbl(self):
        return float(self.driver.find_element_by_xpath(
            f"""{self.ORDER_FORM}div[4]/div/div[1]/div/span"""
        ).text.split()[0])

    def _set_value(self, xpath, value):
        # Erase Actual Value
        element = self.driver.find_element_by_xpath(
            xpath
        )
        element.click()
        for i in range(10):
            element.send_keys(Keys.DELETE)
            element.send_keys(Keys.BACKSPACE)
        # Set Value
        element.send_keys(str(value))

    def all_in(self, percent=100): # percent = [25, 50, 75, 100]
        # Using 25%, 50%, 75%, 100% of Avbl
        self.driver.find_element_by_xpath(
            self.XPATH[self.order_type][f"all_in_{percent}"]
        ).click()

    def set_price(self, price):
        # Set price only for Limit
        self._set_value(
            self.XPATH[self.order_type]["PRICE"],
            price
        )

    def set_TPSL(self, TP, SL):
        # Make TP SL available
        if not self.driver.find_element_by_xpath(
            self.XPATH[self.order_type]["TPSL_select"]
        ).is_selected():
            self.driver.find_element_by_xpath(
                self.XPATH[self.order_type]["TPSL_click"]
            ).click()

        # Set TP
        self._set_value(
            self.XPATH[self.order_type]["TP"],
            TP
        )
        # Set SL
        self._set_value(
            self.XPATH[self.order_type]["SL"],
            SL
        )

    def buy(self):
        self.driver.find_element_by_xpath(
            self.XPATH[self.order_type]["BUY"]
        ).click()

    def sell(self):
        self.driver.find_element_by_xpath(
            self.XPATH[self.order_type]["SELL"]
        ).click()

    def donation(self):
        print("Make a P2P donation to bataillondereussite@gmail.com account")
        print("Or send Litecoin (LTC) directly to LTb9de9CPVZBnPHvp29jr134LoVu9QJCFe")
        self.driver.get("https://www.binance.com/en/my/wallet/account/c2c/send")
        time.sleep(2)
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[2]/main/main/div[2]/div/div/div/div/div/div[2]/div/div[1]/div/div[1]/div[3]/div/div[2]/div/div/input"
        ).send_keys("bataillondereussite@gmail.com")

