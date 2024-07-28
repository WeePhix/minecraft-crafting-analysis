import csv, os, requests, re
from selenium import webdriver
from selenium.webdriver.common.by import By

web_url = "https://minecraft.wiki/w/Crafting"
html_filename = "page.html"
csv_filename = "data.csv"
directory = "data"
show_button_class = "jslink"

section_pattern = r'<table class="wikitable collapsible sortable jquery-tablesorter" data-description="Crafting recipes">(?s:.*?)</table>'
section_titles = ["Building blocks", "Decoration blocks", "Redstone", "Transportation", "Foodstuffs", "Tools", "Utilities", "Combat", "Brewing", "Materials", "Miscellaneous"]

driver = webdriver.Chrome()


def get_html_str(url: str) -> str:
    driver.get(url)
    # Instead of waiting 2 seconds every time, find a way to continue the code when the page is loaded
    driver.implicitly_wait(1)
    buttons = driver.find_elements(By.CLASS_NAME, show_button_class)
    for i in range(len(section_titles)):
        buttons[i].click()
        driver.implicitly_wait(1)
    return driver.page_source


def save_str_to_html(text: str, filename: str, directory: str) -> None:
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return


def separate_sections(text: str, pattern: str, number_of_sections: int) -> list:
    index = 0
    last_index = 0
    sections = []
    for i in range(number_of_sections):
        index = text.index(pattern)
        sections.append(text[last_index:index])
        text = text[index:]
        last_index = index
    return sections[1:]


def save_sections_to_files(html_fname: str, section_names: list, directory: str):
    path = os.path.join(directory, html_fname)
    with open(path, "r", encoding="utf8") as file:
        html = file.read()
    for i, section in enumerate(re.finditer(section_pattern, html)):
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, section_names[i] + ".txt")
        with open(path, "w", encoding="utf8") as file:
            file.write(section.group())


if __name__ == "__main__":
    html = get_html_str(web_url)
    save_str_to_html(html, html_filename, directory)
    save_sections_to_files(html_filename, section_titles, directory)
driver.close()