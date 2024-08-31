import csv, os, re
from selenium import webdriver
from selenium.webdriver.common.by import By

download_from_web = True

web_url = "https://minecraft.wiki/w/Crafting"
show_button_class = "jslink"

# Everything necessary for writing, reading files:
FILENAME_html = "page.html"
FILENAME_csv = "data.csv"
FILENAME_items = "items.txt"
directory = "data"
section_titles = ["Building_blocks", "Decoration_blocks", "Redstone", "Transportation", "Foodstuffs", "Tools", "Utilities", "Combat", "Brewing", "Materials", "Miscellaneous"]


# All the necessary regex patters:
PATTERN_section = r'<table class="wikitable collapsible sortable jquery-tablesorter" data-description="Crafting recipes">(.*?)</table>'
PATTERN_item = r'<tr><th><a href="/w/(.*?)</td></tr>'
PATTERN_item_name = r'^(.*?)"'
PATTERN_item_recipe = r'<span class="mcui-input">(.*?)<span class="mcui-arrow">'    
PATTERN_item_yield = r'">([0-9]+)</span></a></span></span></span></span></div></td>'
PATTERN_item_description = r'</div></td><td>(.*?)$'

PATTERN_slot = r'<span class="invslot.*?">(.*?)</span>'
PATTERN_full_slot = r'<span class="invslot-item invslot-item-image">.*?title="(.*?)"><img alt='
PATTERN_changing_slot = r'<span class="invslot animated animated-lazyloaded">.*?<a href="/w/(.*?)">.*?</a>'

DESCRIPTIONS_NOJAVA = ['"This statement only applies to Bedrock Edition"', '"This statement only applies to Bedrock Edition and Minecraft Education"']
GENERAL_items = {r'[Spruce|Dark_Oak|Oak|Birch|Jungle|Warped|Crimson|Cherry|Acacia|Mangrove]': '',
                 r'Bamboo_Planks': 'Planks', r'[Oxidized|Weathered|Exposed]': '',
                 r'[White|Light_Gray|Gray|Black|Brown|Red|Orange|Yellow|Lime|Green|Cyan|Light_Blue|Blue|Purple|Magenta|Pink]': ''}

item_dict = {}
# key is the name of the item, value is the corresponding Item object


class Item():
    def __init__(self, item_name, section) -> None:
        self.name = item_name
        self.section = section
        self.recipes = []
    
    def new_recipe(self, recipe: dict, ryield: int) -> None:
        if len(recipe) == 0:
            return
        ings = ''
        amms = ''
        keys = list(recipe.keys())
        keys.sort()
        for mat in keys:
            amms += str(recipe[mat]) + ';'
            ings += re.sub(" ", "_", mat) + ';'
        self.recipes.append((ings[:-1], amms[:-1], str(ryield)))
    
    # ('Cobblestone;Diorite', '1;1', '2')
    
    def __str__(self) -> str:
        out = self.section + ":" + self.name + "\nRecipes:\n"
        for recipe in self.recipes:
            out += recipe + "\n"
        return out


def save_url_to_file(url: str=web_url, show_class:str=show_button_class, filename: str=FILENAME_html, directory: str=directory) -> None:
    driver = webdriver.Chrome()
    driver.get(url)
    # Instead of waiting 4 seconds every time, find a way to continue the code when the page is loaded
    driver.implicitly_wait(4)
    buttons = driver.find_elements(By.CLASS_NAME, show_class)
    for i in range(len(section_titles)):
        buttons[i].click()
        driver.implicitly_wait(4)
    
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        no_nl = re.sub("\n", "", driver.page_source)
        file_out.write(re.sub(r'<span class="mw-headline" id="Removed_recipes">Removed recipes</span>.*', '', no_nl))
    driver.quit()
    return


def save_sections_to_files(html_fname: str=FILENAME_html, section_titles: list=section_titles, directory: str=directory) -> None:
    path = os.path.join(directory, html_fname)
    with open(path, "r", encoding="utf8") as file:
        html = file.read()
    for i, section in enumerate(re.findall(PATTERN_section, html)):
        print(i, section_titles[i])
        path = os.path.join(directory, section_titles[i] + ".txt")
        with open(path, "w", encoding="utf8") as file:
            file.write(section)


def distinguish_items_in_section(section_fname: str, directory: str=directory, item_pattern: str=PATTERN_item, no_java: str=DESCRIPTIONS_NOJAVA):
    fpath = os.path.join(directory, section_fname + ".txt")
    with open(fpath, "r", encoding="utf8") as file:
        section = file.read()
    
    items = re.findall(item_pattern, section)
    for item in items:
        name = re.search(PATTERN_item_name, item).group(1)
        recipe = re.search(PATTERN_item_recipe, item).group(1)
        ryield = re.search(PATTERN_item_yield, item)
        desc = re.search(PATTERN_item_description, item).group(1)
        if ryield:
            ryield = ryield.group(1)
        else:
            ryield = 1
        for d in no_java:
            if d in desc:
                break
        else:
            save_item_to_class(name, recipe, ryield, section_fname)


def save_item_to_class(item_name:str, item_html: str, recipe_yield: str, item_section: str, slot_pattern: str=PATTERN_slot, changing_pattern: str=PATTERN_changing_slot, full_pattern: str=PATTERN_full_slot, item_dict: dict=item_dict) -> None:
    recipe = {}
    
    for slot in re.findall(slot_pattern, item_html, re.DOTALL):
        mat = re.search(full_pattern, slot)
        if mat:
            if mat.group(1) in recipe.keys():
                recipe[mat.group(1)] += 1
            else:
                recipe[mat.group(1)] = 1
    
    for changing_slot in re.findall(changing_pattern, item_html, re.DOTALL):
        try:
            specific_mat = changing_slot.group(1)
        except:
            specific_mat = changing_slot
        
        for specific in GENERAL_items.keys():
            if re.search(specific, specific_mat):
                mat = re.sub(specific, GENERAL_items[specific], specific_mat)
                break
        
        if mat == '':
            mat = specific_mat
        
        if mat in recipe.keys():
            recipe[mat] += 1
        else:
            recipe[mat] = 1
            
            
    if recipe_yield == "":
        recipe_yield = 1
    else:
        recipe_yield = int(recipe_yield)
    
    if item_name not in item_dict.keys():
        item_dict[item_name] = Item(item_name, item_section)
    item_dict[item_name].new_recipe(recipe, recipe_yield)


def save_items_to_file(item_dict: dict = item_dict, directory: str = directory, file_name = FILENAME_items):
    path = os.path.join(directory, file_name)
    out = ''
    for item in item_dict.values():
        out += str(item) + "\n#" * 2 + "\n"
    with open(path, "w", encoding="utf8") as file:
        file.write(out)


def write_items_to_csv(csv_fname: str=FILENAME_csv) -> None:
    out = 'Section,Name,Ingredients,Ammounts,Yield\n'
    for item in item_dict.values():
        for i, recipe in enumerate(item.recipes):
            out += item.section + ',' + item.name + ',' + recipe[0] + ',' + recipe[1] + ',' + recipe[2] +'\n'
    path = os.path.join(directory, csv_fname)
    
    with open(path, "w", encoding="utf8") as file:
        file.write(out)


if __name__ == "__main__":
    if download_from_web:
        save_url_to_file()
        save_sections_to_files()
    
    for section in section_titles:
        distinguish_items_in_section(section)
    write_items_to_csv()