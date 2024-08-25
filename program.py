import csv, os, re
from selenium import webdriver
from selenium.webdriver.common.by import By

web_url = "https://minecraft.wiki/w/Crafting"
show_button_class = "jslink"

# Everything necessary for writing, reading files:
FILENAME_html = "page.html"
FILENAME_csv = "data.csv"
FILENAME_items = "items.txt"
directory = "data"
section_titles = ["Building_blocks", "Decoration_blocks", "Redstone", "Transportation", "Foodstuffs", "Tools", "Utilities", "Combat", "Brewing", "Materials", "Miscellaneous"]


# All the necessary regex patters:
PATTERN_section = r'<table class="wikitable collapsible sortable jquery-tablesorter" data-description="Crafting recipes">(?s:.*?)</table>'
PATTERN_item = r'th><a href="/w/(.*?)".*?<span class="mcui-input">(.*?)</span><span class="mcui-arrow">.*?<span class="invslot-stacksize" title=".*?">(\d*?)</span></a></span></span></span></span></div></td><td>(.*?)</td></tr>'
# groups follow like this: item name, recipe layout, recipe yield, description

PATTERN_row = r'<span class="mcui-row">(?s:.*?</span>)</span>'
PATTERN_slot = r'<span class="invslot">(?s:.*?)</span>'
PATTERN_full_slot = r'<span class="invslot-item invslot-item-image">?s:.*?title="(?s:.*?)"><img alt='


DESCRIPTIONS_NOJAVA = ['"This statement only applies to Bedrock Edition"', '"This statement only applies to Bedrock Edition and Minecraft Education"']

item_dict = {}
# key is the name of the item, value is the corresponding Item object


class Item():
    def __init__(self, item_name, section) -> None:
        self.name = item_name
        self.section = section
        self.recipes = set()
    
    def new_recipe(self, recipe: dict) -> None:
        out = ''
        keys = recipe.keys()
        keys.sort()
        for mat in keys:
            if mat != "yield":
                out += str(recipe[mat]) + mat
        out += recipe["yield"]
        self.recipes.add(out)
    
    def __str__(self) -> str:
        out = self.section + ":" + self.name + "\nRecipes:\n"
        for recipe in self.recipes:
            out += recipe + "\n"
        return out


def save_url_to_file(url: str=web_url, show_class:str=show_button_class, filename: str=FILENAME_html, directory: str=directory) -> None:
    driver = webdriver.Chrome()
    driver.get(url)
    # Instead of waiting 4 seconds every time, find a way to continue the code when the page is loaded
    driver.implicitly_wait(2)
    buttons = driver.find_elements(By.CLASS_NAME, show_class)
    for i in range(len(section_titles)):
        buttons[i].click()
        driver.implicitly_wait(2)
    
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(driver.page_source)
    driver.close()
    return


def save_sections_to_files(html_fname: str=FILENAME_html, section_titles: list=section_titles, directory: str=directory) -> None:
    path = os.path.join(directory, html_fname)
    with open(path, "r", encoding="utf8") as file:
        html = file.read()
    for i, section in enumerate(re.finditer(PATTERN_section, html)):
        path = os.path.join(directory, section_titles[i] + ".txt")
        with open(path, "w", encoding="utf8") as file:
            file.write(section.group())


def distinguish_items_in_section(section_fname: str, directory: str=directory, pattern: str=PATTERN_item, no_java: str=DESCRIPTIONS_NOJAVA):
    print("checking through section: " + section_fname)
    path = os.path.join(directory, section_fname + ".txt")
    with open(path, "r", encoding="utf8") as file:
        section = file.read()
        print("file read")
    
    items = re.finditer(pattern, section, re.DOTALL)
    print("items in section: " + sum(1 for _ in items))
    for item in items:
        print("checking item: ", item.group(1))
        #for nojava in no_java:
            #if nojava in item.group(3):
                #continue
        save_item_to_class(item.group(0), item.group(1), section_fname, item.group(2))


def save_item_to_class(item_name:str, item_html: str, item_section: str, recipe_yield: str, row_pattern:str=PATTERN_row, slot_pattern: str=PATTERN_slot, full_pattern: str=PATTERN_full_slot, item_dict: dict=item_dict) -> None:
    print("saving recipe of " + item_name)
    recipe = {}
    for row in re.finditer(row_pattern, item_html):
        # checks each slot in the recipe. If it is not empty, the crafting material is added to the recipe dict
        for slot in re.finditer(slot_pattern, row.group()):
            if slot.group() == '':
                continue
            else:
                mat_name = re.match(full_pattern, slot.group()).group(1)
                if mat_name not in recipe.keys():
                    recipe[mat_name] = 0
                recipe[mat_name] += 1
    if recipe_yield == "":
        recipe["yield"] = 1
    else:
        recipe["yield"] = int(recipe_yield)
    
    if item_name in item_dict.keys():
        item_dict[item_name] = Item(item_name, item_section)
    item_dict[item_name].new_recipe(recipe)


def save_items_to_file(item_dict: dict = item_dict, directory: str = directory, file_name = FILENAME_items):
    for item in item_dict.keys():
        print(item_dict[item])
    path = os.path.join(directory, file_name)
    out = ''
    for item in item_dict.values():
        print("saving to file: " + item.name)
        out += item.name + "\n" + str(item) + "\n#" * 2 + "\n"
    with open(path, "w", encoding="utf8") as file:
        file.write(out)


if __name__ == "__main__":
    if False:
        save_url_to_file()
        save_sections_to_files()
    for section in section_titles:
        distinguish_items_in_section(section)
    save_items_to_file()