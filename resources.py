import re, os


# Everything necessary for writing, reading files:
FILENAME_csv = "data.csv"
FILENAME_items = "items.txt"
directory = "data"
section_titles = ["Building_blocks", "Decoration_blocks", "Redstone", "Transportation", "Foodstuffs", "Tools", "Utilities", "Combat", "Brewing", "Materials", "Miscellaneous"]


# All the necessary regex patters:
PATTERN_section = r'<table class="wikitable collapsible sortable.*?" data-description="Crafting recipes">(.*?)</table>'
PATTERN_item = r'<tr><th><a href="/w/(.*?)</td></tr>'
PATTERN_item_name = r'^(.*?)"'
PATTERN_item_recipe = r'<span class="mcui-input">(.*?)<span class="mcui-arrow">'    
PATTERN_item_yield = r'">([0-9]+)</span></a></span></span></span></span></div></td>'
PATTERN_item_description = r'</div></td><td>(.*?)$'
PATTERN_slot = r'<span class="invslot.*?">(.*?)</span>'
PATTERN_full_slot = r'<span class="invslot-item invslot-item-image">.*?title="(.*?)"><img alt='
PATTERN_changing_slot = r'<span class="invslot animated animated-lazyloaded">.*?<a href="/w/(.*?)">.*?</a>'

# Desctiptions of items, that are not in the Java edition of Minecraft
DESCRIPTIONS_NOJAVA = ['"This statement only applies to Bedrock Edition"', '"This statement only applies to Bedrock Edition and Minecraft Education"']
# List of unimportant item details (wood and copper types and colours)
GENERAL_items = {r'[Spruce|Dark_Oak|Oak|Birch|Jungle|Warped|Crimson|Cherry|Acacia|Mangrove|White|Light_Gray|Gray|Black|Brown|Red|Orange|Yellow|Lime|Green|Cyan|Light_Blue|Blue|Purple|Magenta|Pink|Oxidized|Weathered|Exposed]': '',
                 r'Bamboo_Planks': 'Planks'}



class Item():
    def __init__(self, section: str, name: str) -> None:
        self.name = name
        self.section = section
        self.recipes = []
        self.material_for = []
        self.is_primary = False
        self.is_final = False
        self.max_depth = 0
        self.primary_ingredients = []
        # For each primary material, there is a tuple in the form of (Ingredient, Amount)
        self.items_crafted = []
        # A list of all the items, that can be crafted from this (directly or indirectly)
        self.recipe_chains = []
        # Contains lists of items, ranging from this item to its primary materials
        self.max_depth = 0
    
    
    def new_recipe(self, ings: str, ams: str, y: str):
        recipe = {}
        ings = ings.split(";")
        ams = ams.split(";")
        for i in range(len(ams)):
            recipe[ings[i]] = ams[i]
        recipe["yield"] = y
        self.recipes.append(recipe)
    
    def new_material(self, item: str):
        if item not in self.material_for:
            self.material_for.append(item)
    
    def __str__(self) -> str:
        out = self.name + " is "
        if self.is_final:
            out += "final" 
        elif self.is_primary:
            out += "primary"
        else:
            out +="intermediate"
        out += "\nItems crafted from this are: "
        for item in self.items_crafted:
            out += f"{item}, "
        out = out[:-2] + "\nThe necessary primary materials for this item are: (material, amount per produced item)\n"
        for material in self.primary_ingredients:
            out += f"({material[0]}, {str(round(material[1], 3))})\n"
        out += f"The longest chain of crafting operations for this item is {self.max_depth} operations long.\n"
        out += "#" * 100
        return out


class Recipe():
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



def search_for_circular_chains(items: dict) -> str:
    out = ''
    for item in items.values():
        for recipe in item.recipes:
            for ingredient in recipe.keys():
                if ingredient not in items.keys():
                    continue
                for recipe2 in items[ingredient].recipes:
                    if item.name in recipe2.keys():
                        out += item.name + '\n'
    return out


def find_recipes_of_materials(items: dict, primaries: list) -> dict:
    materials = {}
    for item in items.keys():
        for recipe in items[item].recipes:
            for material in recipe.keys():
                if material == "yield":
                    continue
                if material not in items.keys():
                    # Če material v receptu še ni v slovarju predmetov, to pomeni,
                    # da nima recepta, ki bi naredil ta predmet, torej je primarni material
                    materials[material] = Item("Primary", material)
                    materials[material].is_primary = True
                    if material not in primaries:
                        primaries.append(material)
                    materials[material].new_material(item)
                elif material in primaries:
                    items[material].is_primary = True
                    items[material].new_material(item)
                # Vsakem material v vsakem receptu zabeležimo, da je iz njega mogoče narediti predmet, ki je posledica tega recepta
                else:
                    items[material].new_material(item)
    return materials | items


def recursive_recipe_search(name: str, items: dict, multiplier: float=1) -> list:
    if items[name].is_primary:
        return []
    out = []
    for i, recipe in enumerate(items[name].recipes):
        out.append([])
        if len(recipe.keys()) == 0:
            continue
        for material in recipe.keys():
            if material == None:
                return []
            if material == "yield":
                continue
            mult = multiplier * int(recipe[material]) / int(recipe["yield"])
            if mult == None:
                return []
            out[i].append((material, mult))
            out[i] += recursive_recipe_search(material, items, mult)
    return out


def recursive_material_search(material: str, items: dict) -> set:
    out = set()
    if items[material].is_final:
        return set()
    
    for item in items.values():
        if item.is_primary:
            continue
        for recipe in item.recipes:
            if material in recipe.keys():
                out.add(item.name)
                out = out.union(recursive_material_search(item.name, items))
    return out


def find_primaries_and_depth(recipe_chain: list, items: dict, depth: int=0):
    out = []
    for link in recipe_chain:
        if type(link) == type([]):
            temp = find_primaries_and_depth(link, items)
            out += temp[0]
            depth = temp[1]
        else:
            if items[link[0]].is_primary:
                out.append(link)
    return out, depth + 1


def all_primaries_and_depths(items: dict) -> dict:
    for item in items.values():
        out = []
        for chain in item.recipe_chains:
            temp = find_primaries_and_depth(chain, items)
            out += temp[0]
            item.max_depth = max(item.max_depth, temp[1])
        for i, tup in enumerate(out):
            for j in range(i):
                if out[j][0] == tup[0]:
                    if out[j][1] > tup[1]:
                        out.pop(i)
                    else:
                        out.pop(j)
        for mat, amt in out:
            amt = float.as_integer_ratio(amt)
        item.primary_ingredients = out
    return items


def write_extracted_to_csv(items: dict):
    out = "Item,Position,Primaries,Primary_Amounts,Crafts,Chain,Ingredient_Count,Craft_Count\n"
    for item in items.values():
        out += item.name + ","
        out += "Primary" if item.is_primary else ("Final" if item.is_final else "Intermediate")
        out += ","
        if item.is_primary:
            out += "_,_,"
            for craft in item.items_crafted:
                out += craft
                out += ";"
            if out[-1] == ",":
                out += "__"
            out = out[:-1] + ",0"
        elif item.is_final:
            for primary in item.primary_ingredients:
                out += primary[0] + ";"
            out = out[:-1] + ","
            for primary in item.primary_ingredients:
                amt_rounded = round(primary[1], 3)
                if amt_rounded % 1 == 0:
                    amt_rounded = int(amt_rounded)
                out += str(amt_rounded) + ";"
            out = out[:-1] + ",_," 
            out += str(item.max_depth) if type(item.max_depth) == type(0) else "0"
        else:
            for primary in item.primary_ingredients:
                out += primary[0] + ";"
            out = out[:-1] + ","
            for primary in item.primary_ingredients:
                amt_rounded = round(primary[1], 3)
                if amt_rounded % 1 == 0:
                    amt_rounded = int(amt_rounded)
                out += str(amt_rounded) + ";"
            out = out[:-1] + ","
            for craft in item.items_crafted:
                out += craft
                out += ";"
            if out[-1] == ",":
                out += "__"
            out = out[:-1]
            out += "," + str(int(item.max_depth))
        out += "," + str(len(item.primary_ingredients)) + "," + str(len(item.items_crafted))
        out += "\n"
    out.strip("\n")
    with open("data/extracted.csv", "w", encoding="utf8") as file:
        file.write(out)


def distinguish_items_in_section(section_fname: str, item_dict: dict, directory: str=directory, item_pattern: str=PATTERN_item, item_name: str=PATTERN_item_name, item_recipe: str=PATTERN_item_recipe, item_yield: str=PATTERN_item_yield, item_description: str=PATTERN_item_description, no_java: str=DESCRIPTIONS_NOJAVA):
    fpath = os.path.join(directory, section_fname + ".txt")
    with open(fpath, "r", encoding="utf8") as file:
        section = file.read()
    
    items = re.findall(item_pattern, section)
    # Finds all the item recipes in a section and separates its different data sets (name, recipe, yield and description)
    for item in items:
        name = re.search(item_name, item).group(1)
        recipe = re.search(item_recipe, item).group(1)
        ryield = re.search(item_yield, item)
        desc = re.search(item_description, item).group(1)
        if ryield:
            ryield = ryield.group(1)
            # If the yield field is empty, it is considered as 1
        else:
            ryield = 1
        # Checks if the item is not in Java edition. If so, it skips saving it
        for d in no_java:
            if d in desc:
                break
        else:
            item_dict = save_item_to_class(name, recipe, ryield, section_fname, item_dict)
    return item_dict


def save_item_to_class(item_name:str, item_html: str, recipe_yield: str, item_section: str, item_dict: dict, slot_pattern: str=PATTERN_slot, changing_pattern: str=PATTERN_changing_slot, full_pattern: str=PATTERN_full_slot, general_items: str=GENERAL_items) -> None:
    recipe = {}
    
    # Checks all the slots in a crafting recipe and if they have an item inside, it saves the material to a dictionary called 'recipe'
    for slot in re.findall(slot_pattern, item_html, re.DOTALL):
        mat = re.search(full_pattern, slot)
        if mat:
            if mat.group(1) in recipe.keys():
                recipe[mat.group(1)] += 1
            else:
                recipe[mat.group(1)] = 1
    # This is only for the slots with one item
    
    # This does the same, but for slots where the item is changing (different wood types, etc.) and generalizes them
    for changing_slot in re.findall(changing_pattern, item_html, re.DOTALL):
        try:
            specific_mat = changing_slot.group(1)
        except:
            specific_mat = changing_slot
        
        for specific in general_items.keys():
            if re.search(specific, specific_mat):
                mat = re.sub(specific, general_items[specific], specific_mat)
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
        item_dict[item_name] = Recipe(item_name, item_section)
    item_dict[item_name].new_recipe(recipe, recipe_yield)
    # Saves the recipe to the item class
    return item_dict