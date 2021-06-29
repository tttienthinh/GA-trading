from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pickle, os

class BSF:
    ORDER_FORM = "//div[@name='orderForm']/"

    def __init__(self, executable_path="chromedriver91") -> None:
        self.driver = webdriver.Chrome(executable_path=executable_path)
        self.driver.get("https://accounts.binance.com/en/login")
        if not os.path.isdir("cookies"):
            os.mkdir("cookies")
        self.driver.maximize_window()

    def __del__(self):
        self.close()

    def close(self):
        self.driver.close()

    def refresh(self):
        self.driver.refresh()

    def connect(self, email, password):
        filename = f"cookies/{email}.pkl"
        cookies_saved = False
        if os.path.isfile(filename):
            print("Found Cookies, loading it")
            cookies_saved = True
            cookies = pickle.load(open(filename, "rb"))
            for cookie in cookies: 
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass
        self.driver.find_element_by_name("email").send_keys(email)
        self.driver.find_element_by_name("password").send_keys(password)
        self.driver.find_element_by_id("click_login_submit").click()
        input("Click 'ENTER' when connected !")
        if not cookies_saved:
            self.save_cookies(email)
        self.get_futures()

    def save_cookies(self, email):
        filename = f"cookies/{email}.pkl"
        pickle.dump( 
                self.driver.get_cookies(), 
                open(filename,"wb")
            )

    def get_futures(self):
        self.driver.get("https://www.binance.com/en/futures/BTCUSDT")
        self.driver.find_element_by_id("tab-LIMIT").click()

    def get_avbl(self):
        return float(self.driver.find_element_by_xpath(
                f"""{self.ORDER_FORM}div[4]/div/div[1]/div/span"""
            ).text.split()[0])
    
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
                for i in range(pas): # Plus
                    self.driver.find_element_by_xpath(
                        "//button[@class=' css-vc3jb5']"
                    ).click()
            else:
                for i in range(-pas): # Moins
                    self.driver.find_element_by_xpath(
                        "//button[@class=' css-1ri8vxv']"
                    ).click()
            self.driver.find_element_by_xpath(
                "//button[@class=' css-1fds4m2']"
            ).click()

    def _set_value(self, xpath, value):
        # Erase Actual Value
        element = self.driver.find_element_by_xpath(
            f"{self.ORDER_FORM}{xpath}"
        )
        element.click()
        for i in range(10):
            element.send_keys(Keys.DELETE)
            element.send_keys(Keys.BACKSPACE)
        # Set Value
        element.send_keys(value)

    def set_price(self, price):
        # Set price
        self._set_value(
            "div[4]/form/div[1]/div/input",
            price
        )
        # Using 100% of Avbl
        self.driver.find_element_by_xpath(
            f"""{self.ORDER_FORM}div[4]/form/div[3]/div[1]/div/div[9]"""
        ).click()

    def set_TPSL(self, TP, SL):
        # Make TP SL available
        if not self.driver.find_element_by_xpath(
            f"""{self.ORDER_FORM}div[4]/form/div[4]/div/label/div[1]/input"""
        ).is_selected():
            self.driver.find_element_by_xpath(
                f"""{self.ORDER_FORM}div[4]/form/div[4]/div/label/div[1]"""
            ).click()

        # Set TP
        self._set_value(
            "div[4]/form/div[4]/div[2]/div/input",
            TP
        )
        # Set SL
        self._set_value(
            "div[4]/form/div[4]/div[3]/div/input",
            SL
        )

    def buy(self):
        self.driver.find_element_by_xpath(
            f"""{self.ORDER_FORM}div[4]/form/div[6]/button[1]"""
        ).click()

    def sell(self):
        self.driver.find_element_by_xpath(
            f"""{self.ORDER_FORM}div[4]/form/div[6]/button[2]"""
        ).click()
            

    