import csv, os, requests, re
from selenium import webdriver
from selenium.webdriver.common.by import By

web_url = "https://minecraft.wiki/w/Crafting"
html_filename = "page.html"
csv_filename = "data.csv"
directory = "data"
show_button_class = "jslink"


driver = webdriver.Chrome()


def get_html_str(url: str) -> str:
    driver.get(url)
    driver.implicitly_wait(5)
    buttons = driver.find_elements(By.CLASS_NAME, show_button_class)
    print(buttons)
    for i in range(11):
        buttons[i].click()
    return driver.page_source


def save_str_to_html(text: str, filename: str, directory: str) -> None:
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return


if __name__ == "__main__":
    html = get_html_str(web_url)
    save_str_to_html(html)


driver.close()