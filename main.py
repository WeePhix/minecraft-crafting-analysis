import os, re
from selenium import webdriver
from selenium.webdriver.common.by import By
import resources as r

# Decides if the download script runs or not
download_from_web = True


FILENAME_html = "page.html"
web_url = "https://minecraft.wiki/w/Crafting"
show_button_class = "jslink"


item_dict = {}
# The key is the name of the item, the value is the corresponding Item object


class Item():
    def __init__(self, item_name, section) -> None:
        self.name = re.sub("%27", "'", item_name)
        if self.name == "Boat":
            self.name = "Oak_Boat"
        self.section = section
        # The basic info of an item
        
        self.recipes = []
    
    def new_recipe(self, recipe: dict, ryield: int) -> None:
        if len(recipe) == 0:
            return
        ings = ''
        ams = ''
        keys = list(recipe.keys())
        keys.sort()
        for mat in keys:
            if '=' in mat:
                continue
            else:
                ams += str(recipe[mat]) + ';'
                ings += re.sub(" ", "_", mat) + ';'
        if self.name in ings:
            return
        self.recipes.append((ings[:-1], ams[:-1], str(ryield)))
        # Saves a recipe for the item in the following format: tuple('ingredient1;ingredient2;...' , 'amount1;amount2;...', 'yield')
    
    def __str__(self) -> str:
        out = self.section + ":" + self.name + "\nRecipes:\n"
        for recipe in self.recipes:
            out += recipe + "\n"
        return out
        # returns the item data for debug purposes (OUTDATED)


def save_url_to_file(url: str=web_url, show_class:str=show_button_class, filename: str=FILENAME_html, directory: str=r.directory) -> None:
    driver = webdriver.Chrome()
    driver.get(url)
    # Instead of waiting 4 seconds every time, find a way to continue the code when the page is loaded
    driver.implicitly_wait(4)
    buttons = driver.find_elements(By.CLASS_NAME, show_class)
    for i in range(len(r.section_titles) + 1):
        buttons[i].click()
        driver.implicitly_wait(4)
    # Clicks all the buttons, to reveal the necessary sections
    
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        no_nl = re.sub("\n", "", driver.page_source)
        file_out.write(re.sub(r'<span class="mw-headline" id="Removed_recipes">Removed recipes</span>.*', '', no_nl))
    # Saves the relevant part of the HTML
    driver.quit()
    return


def save_sections_to_files(html_fname: str=FILENAME_html, section_pattern: str=r.PATTERN_section, section_titles: list=r.section_titles, directory: str=r.directory) -> None:
    path = os.path.join(directory, html_fname)
    with open(path, "r", encoding="utf8") as file:
        html = file.read()
    for i, section in enumerate(re.findall(r.PATTERN_section, html)):
        # Finds the sections and saves each to its own file
        path = os.path.join(directory, section_titles[i] + ".txt")
        with open(path, "w", encoding="utf8") as file:
            file.write(section)


def save_items_to_file(item_dict: dict = item_dict, directory: str = r.directory, file_name = r.FILENAME_items):
    path = os.path.join(directory, file_name)
    out = ''
    for item in item_dict.values():
        out += str(item) + "\n#" * 2 + "\n"
    with open(path, "w", encoding="utf8") as file:
        file.write(out)
    # Saves all the items to a .txt file for debugging purposes (OUTDATED)


# Saves all the files to a CSV table
def write_items_to_csv(csv_fname: str=r.FILENAME_csv, directory: str=r.directory) -> None:
    out = 'Section,Name,Ingredients,Amounts,Yield\n'
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
    
    for section in r.section_titles:
        r.distinguish_items_in_section(section, item_dict)
    write_items_to_csv()