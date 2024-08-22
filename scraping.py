import json
import pandas as pd
import requests
from bs4 import BeautifulSoup

FILE_NAME = "today_prices.json"
URL = "https://www.sharesansar.com/today-share-price"

float_columns = [
    "Conf.",
    "Low",
    "High",
    "Open",
    "Close",
    "Prev. Close",
    "VWAP",
    "Vol",
    "Turnover",
    "Trans.",
    "Diff",
    "Range",
    "Diff %",
    "Range %",
    "VWAP %",
    "120 Days",
    "180 Days",
    "52 Weeks Low",
    "52 Weeks High",
]

class ShareSansarScrapper:

    def fetch_html(self, url : str):
        data = requests.get(url)
        data = data.content
        return data
    
    def fetch_data(self) -> BeautifulSoup:
        response = self.fetch_html(URL)
        soup = BeautifulSoup(response, "html.parser")
        return soup
    
    def parse_columns(self, soup: BeautifulSoup) -> list:
        t_heads = soup.find_all("thead")
        columns = []
        for t_head in t_heads:
            for th in t_head.find_all("th"):
                columns.append(th.text.strip())
        return columns
    
    def parse_rows(self, soup: BeautifulSoup, columns: list) ->list[dict]:
        t_bodies = soup.find_all("tbody")
        today_prices = []
        for t_body in t_bodies:
            for tr in t_body.find_all("tr"):
                td_data = {}
                for i, td in enumerate(tr.find_all("td")):
                    if columns[i] == "Symbol":
                        td_data.update(
                            {
                                "Symbol" : td.a.text,
                                "name" : td.a.get("title"),
                            }
                        )
                    else:
                        td_data.update({columns[i]: td.text})
                today_prices.append(td_data)
        return today_prices
    
    def format_data(self, today_prices: list[dict]) -> pd.DataFrame:
        df: pd.DataFrame = pd.DataFrame.from_records(today_prices)
        df = df.drop(columns = ["S.No"], axis = 1)
        df[float_columns] = (
            df[float_columns]
            .replace(r"(-?[^\d\.])", "", regex = True)
            .replace("", float("0"))
            .astype(float)
        )
        df[["Vol"]] = (
            df[["Vol"]]
            .replace(r"(-?[^\d\.])", "", regex = True)
            .replace("", int("0"))
            .astype(int)
        )
        return df
    
    def save_as_json(self, FILE_NAME, today_prices: list[dict]):
        with open(FILE_NAME, "w") as f:
            json.dump(today_prices, f, indent = 2)

    def parse_data(self, soup: BeautifulSoup):
        columns = self.parse_columns(soup)
        today_prices = self.parse_rows(soup, columns)
        df = self.format_data(today_prices)
        today_prices = df.to_dict(orient = "records")
        self.save_as_json(FILE_NAME, today_prices)
        return today_prices
    
    def update_today_price(self):
        soup = self.fetch_data()
        today_prices = self.parse_data(soup)
        return today_prices
    
ShareSansarScrapper().update_today_price()
