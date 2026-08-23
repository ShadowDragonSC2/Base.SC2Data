import sys
import os
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from os import path

PARENTS = {
        "Abil": [],
        
        "Button": [
            "UnitButton_OnlyGround",
            "UnitButton_OnlyAir",
            "UnitButton_GroundAir",
            "UnitButton_Detector",
            "UnitButton_OnlyGroundDetector",
            "UnitButton_OnlyAirDetector",
            "UnitButton_GroundAirDetector"
            ],
        
        "Weapon": [],
        
        "Unit": [],
        
        "Actor": [
            "AdvancedUnitStandard",
            "AdvancedStandard_Ground",
            "AdvancedUnitStandard_NoAttackAnim",
            "AdvancedUnitStandard_Ground_NoAttackAnim",
            ],
        
        "DataCollection": [
            "Weapon_Instant",
            "Weapon_Missile",
            "UnitGround",
            "UnitAir",
            "AbilityMisssile",
            "AbilityBuild",
            ]
    }

class Validate:
    def __init__(self, root: Element, file):
        self.filecontent = ""
        with open(file, "r", encoding="UTF-8") as open_file:
            self.filecontent = open_file.read()
            
        self.root = root
        self.requires = self.__extract_requires()
        
        self.unit: Element = self.root.find("CUnit")
        self.weapons: list[Element] = self.root.findall("CWeaponLegacy")
        
        # в случае если не найдено ни одной единицы, в таком случае id и race будут None
        self.unit_id: str = self.unit.get("id") if self.unit is not None else None
        self.attr_race = self.unit.get("race") if self.unit is not None else None
        
        self.unit_collection = self.root.find(f"CDataCollectionUnit[@id='{self.unit_id}']")
        self.weap_collection = self.root.find(f"CDataCollectionUnit[@id='{self.unit_id}_Weapon']")
        
        self.blocks_data: dict[str, list[Element]] = {
            "Units": [],
            "Weapons": [],
            "Behaviors": [],
            "Abilities": [],
        }
        self.models = {
            "Unit": self.root.find(f"CModel[@id='{self.unit_id}']"),
            "Death": self.root.find(f"CModel[@id='{self.unit_id}@Death']"),
            "Placement": self.root.find(f"CModel[@id='{self.unit_id}@Placement']"),
            "Portrait": self.root.find(f"CModel[@id='{self.unit_id}@Portrait']"),
        }
        self.errors = []
        self.lightportrait: Element = self.root.find(f".//CLight[@id='{self.unit_id}@Portrait']")
        
        
    def check_no_exist_hotkey_category(self):
        if self.unit.find("HotkeyCategory") is not None: 
            self.__add_error("с родителем, категория горячих клавиш не должна указываться!")
        return self

    def check_static_unit_portrait(self):
        portrait = self.root.find(f".//CModel[@id='{self.unit_id}@Portrait']")
        if portrait is None: return self
        if portrait.find("Image") is None:
            self.__add_error(f'не указан статический портрет для модели "{self.unit_id}@Portrait"')
        return self
    
    def check_unit_models(self):
        for model, elem in self.models.items():
            if elem is None:
                self.__add_error(f'не найдена модель "{self.unit_id}@{model}"!')
        return self
    
    def check_unit_sound_voices(self):
        sounds = {
            "Movement": "Movement",
            "Attack": "Voice",
            "Help": "Alert",
            "Pissed": "Pissed",
            "Yes": "Voice",
            "What": "Voice",
            "Ready": "Ready"
        }
    
        for sound, parent in sounds.items():
            elem = self.root.find(f".//CSound[@id='{self.unit_id}@{sound}']")
            if elem is None: continue
            if elem.get("parent") != parent: 
                self.__add_error(f'звук "{self.unit_id}@{sound}" должен создаваться по родителю "{parent}"')
        
        return self
    
    def check_exists_lightportrait(self):
        if self.lightportrait is None:
            self.__add_error(f'не найден CLight для портрета "{self.unit_id}@Portrait"')
            return self
        if self.lightportrait.get("parent") != "default":
            self.__add_error(f'неправильно указан родитель для CLight модели портрета "{self.unit_id}@Portrait"')
        return self
    
    def check_correctly_lightportrait(self):
        model = self.models["Unit"]
        if model.find("Lighting"): self.__add_error("освещение портрета освещение портрета не должно переопределяться в CModel")
        return self
    
    def check_race_editorcategories(self):
        """Проверяет корректность, указанной для объекта данных, категории редактора "Race".
            Для успешной проверки, категория расы для объекта должна соответствовать идентификатору расы, который обычно прописывается в атрибуте race:
            <CUnit id="..." race="Prot">
            
            Например, если у CUnit указано 'race="Tald"', значит во всех следующих объектах категория расы должна быть "Race:Taldarim"
        """
        
        objects = self.root.findall("CModel")
        objects += self.root.findall("CSound")
        objects += self.root.findall("CButton")
        objects += self.root.findall("CBehaviorBuff")
        objects += self.root.findall("CWeaponLegacy")
        objects += self.root.findall("CDataCollectionUnit")
        objects += self.root.findall("CUpgrade")
        if self.attr_race is None: return self
        
        for object in objects:
            ec = object.find(".//EditorCategories")
            if ec is None: 
                self.__add_error(f'объект <{object.tag} id="{object.get("id")}"> не имеет категорию редактора!')
                continue
            if self.attr_race not in ec.get("value"):
                self.__add_error(f'объект <{object.tag} id="{object.get("id")}"> имеет не корректную категорию редактора!')
        return self
    
    # проверки парентов
    
    def check_parent_unit(self):
        if self.unit is None:
            self.__add_error("основная единица не найдена!")
            return self
            
        if self.unit.get("parent") is None:
            self.__add_error(f'не указан родитель!')
            return self
            
        if self.attr_race is None:
            self.__add_error(f'не указан атрибут "race"!')
            return self
        
        return self
    
    def check_parent_in_requires(self):
        weap_collection_id = self.weap_collection.get("id")
        weap_collection_parent = self.weap_collection.get("parent")
        
        if weap_collection_parent is None:
            self.__add_error(f'коллекция данных оружия "{weap_collection_id}" не имеет родителя!')
        elif weap_collection_parent not in PARENTS["DataCollection"]:
            self.__add_error(f'', title=f'Коллекция оружия "{weap_collection_id}" имеет нестандартного родителя "{weap_collection_parent}"')
        
        return self
    
    # проверки наличия коллекций данных
    
    def check_exist_datacollection_unit(self):
        if self.unit_collection is None:
            self.__add_error(f'не определена коллекция данных <CDataCollectionUnit id="{self.unit_id}" parent="...">')
        return self
    
    def check_exist_datacollection_weap(self):
        if len(self.weapons) == 0: return self # если единица не имеет оружие, тогда надо игнорировать эту ошибку
        for weap in self.weapons:
            if self.root.find(f".//CDataCollectionUnit[@id='{weap.get("id")}']") is None:
                self.__add_error(f'не имеет коллекции данных <CDataCollectionUnit id="{weap.get("id")}" parent="...">', title=f"Оружие '{weap.get("id")}'")

        return self
    
    # Internal
    
    def __extract_requires(self) -> list:
        pattern = r"Requires:\s*(?P<type>\w+):(?P<id>[\w@]+)\[(?P<file>[\w.]+)]"
        matches = re.finditer(pattern, self.filecontent)

        result = {}
        for m in matches:
            result[f"{m.group("id")}"] = (f"{m.group("type")}", f"{m.group("file")}")
        return result
            
    def __add_error(self, message: str, title: str = ""):
        title = title if title != "" else f'Для единицы "{self.unit_id}"'
        self.errors.append(f'{title} {message}')


if __name__ == "__main__":
    
    listpath = []
    listerrors = []
    
    if len(sys.argv) < 2:
        print("Допустимые аргументы командной строки:\n\n"
              "- 'filepath' — Передать конкретный путь до файла\n"
              "- gamedata — Проверить все файла в директории 'GameData'\n")
        sys.exit(1)
    
    if sys.argv[1] == "gamedata":
        for faction in os.listdir("GameData"):
            if faction in ("basestats"): continue
            for dir in os.listdir(f"GameData/{faction}"):
                for file in os.listdir(f"GameData/{faction}/{dir}"):
                    if not file.endswith(".xml"): continue
                    listpath.append(f"GameData/{faction}/{dir}/{file}")     
    elif path.exists(sys.argv[1]):
        listpath.append(sys.argv[1])
    else:
        print("Допустимые аргументы командной строки:\n\n"
              "- 'filepath' — Передать конкретный путь до файла\n"
              "- gamedata — Проверить все файла в директории 'GameData'\n")
        sys.exit(1)
        
    for file in listpath:    

        tree = ET.parse(file)
        ROOT = tree.getroot()

        validator = Validate(ROOT, file)
        if validator.unit is None: continue
        # проверка юнита
        validator.check_no_exist_hotkey_category().check_exist_datacollection_unit()

        # проверка моделей
        validator.check_unit_models().check_static_unit_portrait().check_exists_lightportrait()

        # проверка звуков
        validator.check_unit_sound_voices()

        # проверки родителей
        validator.check_parent_unit().check_parent_in_requires()

        validator.check_race_editorcategories()

        # проверка оружий
        validator.check_exist_datacollection_weap()
        
        listerrors += validator.errors

    for error in listerrors:
        print(error)

    if not listerrors: print("✅ | Замечаний нет!")

    sys.exit(1 if listerrors else 0)
