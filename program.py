import csv, os, requests, re
from selenium import webdriver
from selenium.webdriver.common.by import By

web_url = "https://minecraft.wiki/w/Crafting"
show_button_class = "jslink"

# vse, potrebno za iskanje, branje in pisanje datotek
FILENAME_html = "page.html"
FILENAME_csv = "data.csv"
directory = "data"
section_titles = ["Building_blocks", "Decoration_blocks", "Redstone", "Transportation", "Foodstuffs", "Tools", "Utilities", "Combat", "Brewing", "Materials", "Miscellaneous"]


# Vsi razlicni vzorci za regex:
PATTERN_section = r'<table class="wikitable collapsible sortable jquery-tablesorter" data-description="Crafting recipes">(?s:.*?)</table>'
PATTERN_item = r'<th><a href="(?s:.*?)</td>(?s:.*?)<td>(?s:.*?)</tr>'
# the first group is the header (item) and the next cell (materials), the second group is the recipe layout, the third group is the description
PATTERN_row = r'<span class="mcui-row">(?s:.*?</span>)</span>' # the group contains everything within a row
PATTERN_slot = r'<span class="invslot">(?s:.*?)</span>'
PATTERN_full_slot = r'<span class="invslot-item invslot-item-image">(?s:.*?)title="(?s:.*?)"><img alt='


DESCRIPTION_bedrock_only = '&zwnj;<sup class="noprint nowrap Inline-Template" title="">[<i><span title="This statement only applies to Bedrock Edition"><a href="/w/Bedrock_Edition" title="Bedrock Edition">Bedrock Edition</a>  only</span></i>]</sup></td>'

item_list = []


class Item():
    def __init__(self, item_name) -> None:
        self.name = item_name
        self.recipes = set()
        self.materials = []
    
    def new_recipe(self, recipe: list) -> None:
        self.recipes.add(recipe)
        for item in recipe:
            item.new_material(self)
    
    def new_material(self, item):
        self.materials.append(item)
        self.materials.sort()
        mats = self.materials[0]
        for i in range(1, len(self.materials)):
            if self.materials[i] != self.materials[i-1]:
                mats.append(self.materials[i])
        self.materials = mats
    
    def __str__(self) -> str:
        out = 'Recipes:\n'
        for recipe in self.recipes:
            i = 0
            maxlen = max(len(material) for material in recipe[:9])
            for i, material in enumerate(recipe):
                out += material  + ' ' * (maxlen - len(material))
                if i == 5:
                    out += ' --> ' + recipe[9] + self.name
                if i % 3 == 2:
                    out += '\n'
        out += '\nIs a material for crafting: '
        for m in self.materials:
            out += m + ", "
        out = out[:-2]
        return out


driver = webdriver.Chrome()


def get_html_str(url: str, show_class:str = show_button_class) -> str:
    driver.get(url)
    # Instead of waiting 4 seconds every time, find a way to continue the code when the page is loaded
    driver.implicitly_wait(2)
    buttons = driver.find_elements(By.CLASS_NAME, show_class)
    for i in range(len(section_titles)):
        buttons[i].click()
        driver.implicitly_wait(2)
    out = driver.page_source
    return out


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
    for i, section in enumerate(re.finditer(PATTERN_section, html)):
        path = os.path.join(directory, section_names[i] + ".txt")
        with open(path, "w", encoding="utf8") as file:
            file.write(section.group())


def distinguish_items(section_fname: str, directory: str = directory, pattern: str = PATTERN_item, bedrock_only: str = DESCRIPTION_bedrock_only):
    path = os.path.join(directory, section_fname)
    with open(path, "r", encoding="utf8") as file:
        section = file.read()
    for item in re.finditer(pattern, section):
        if item.group(2) == bedrock_only:
            continue
        save_item_to_class(item.group(1))


def save_item_to_class(item_html: str, row_pattern:str = PATTERN_row, slot_pattern: str = PATTERN_slot, full_pattern: str = PATTERN_full_slot, item_list: list = item_list):
    recipe = []
    for row in re.finditer(row_pattern, item_html):
        for slot in re.finditer(slot_pattern, row.group()):
            if slot.group() == '':
                recipe.append(None)
            else:
                recipe.append(re.match(full_pattern, slot.group()).group(1))
            

if __name__ == "__main__":
    html = get_html_str(web_url)
    save_str_to_html(html, FILENAME_html, directory)
    save_sections_to_files(FILENAME_html, section_titles, directory)
driver.close()