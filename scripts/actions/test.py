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

# корень мода: сам скрипт лежит в scripts/actions/
BASE_DIR = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
GAMEDATA_DIR = path.join(BASE_DIR, "GameData")
SKIP_DIRS = {"basestats"}

USAGE = ("Допустимые аргументы командной строки:\n\n"
         "- 'filepath' — Передать конкретный путь до файла (можно несколько путей)\n"
         "- gamedata — Проверить все файла в директории 'GameData'\n")


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
        self.unit_id: str | None = self.unit.get("id") if self.unit is not None else None
        self.attr_race: str | None = self.__extract_race()
        
        self.unit_collection = self.root.find(f"CDataCollectionUnit[@id='{self.unit_id}']")

        # коллекции данных оружия ищутся по id самого оружия, а не по "<unit_id>_Weapon"
        self.weap_collections: dict[str, Element | None] = {
            weap.get("id"): self.root.find(f".//CDataCollectionUnit[@id='{weap.get('id')}']")
            for weap in self.weapons
        }
        
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
        if self.unit is None: return self
        if self.unit.find("HotkeyCategory") is not None: 
            self.__add_error("при указанном родителе категория горячих клавиш не должна задаваться!")
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
                # для основной модели суффикс "@<model>" не используется
                model_id = self.unit_id if model == "Unit" else f"{self.unit_id}@{model}"
                self.__add_error(f'не найдена модель "{model_id}"!')
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
        model = self.models["Portrait"]
        if model is None: return self
        # find() возвращает Element, а пустой Element является "ложным" при проверке на истинность
        if model.find("Lighting") is not None: 
            self.__add_error("освещение портрета не должно переопределяться в CModel")
        return self

    
    def check_race_editorcategories(self):
        """Проверяет корректность, указанной для объекта данных, категории редактора "Race".
            Для успешной проверки, категория расы для объекта должна соответствовать идентификатору расы, который прописывается атрибутом race или элементом <Race>:
            <CUnit id="..." race="Prot">
            <CUnit id="..."><Race value="Prot"/></CUnit>
            
            Например, если у CUnit указано 'race="Tald"', значит во всех следующих объектах категория расы должна быть "Race:Taldarim" или "Race:Tald"
        """
        
        if self.attr_race is None: return self
        
        objects = self.root.findall("CModel")
        objects += self.root.findall("CSound")
        objects += self.root.findall("CButton")
        objects += self.root.findall("CBehaviorBuff")
        objects += self.root.findall("CWeaponLegacy")
        objects += self.root.findall("CDataCollectionUnit")
        objects += self.root.findall("CUpgrade")
        

        for object in objects:
            ec = object.find(".//EditorCategories")
            if ec is None: 
                self.__add_error(f'объект <{object.tag} id="{object.get("id")}"> не имеет категорию редактора!')
                continue
            if self.attr_race not in (ec.get("value") or ""):
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
            self.__add_error(f'не указана раса (атрибут "race" или элемент <Race value="..."/>)!')
            return self
        
        return self

    
    def check_parent_in_requires(self):
        for weap_id, collection in self.weap_collections.items():
            # отсутствие самой коллекции проверяется в check_exist_datacollection_weap
            if collection is None: continue
            
            collection_parent = collection.get("parent")
            
            if collection_parent is None:
                self.__add_error(f'коллекция данных оружия "{weap_id}" не имеет родителя!')
            elif collection_parent not in PARENTS["DataCollection"]:
                self.__add_error(f'', title=f'Коллекция оружия "{weap_id}" имеет нестандартного родителя "{collection_parent}"')
        
        return self
    
    # проверки требований
    
    def check_exist_unit_requirement(self):
        if self.root.find(f".//CRequirement[@id='{self.unit_id}']") is None:
            self.__add_error(f'не создано требование <CRequirement id="{self.unit_id}"/>')
        return self

        
    def check_exist_unit_requirement_have(self):
        req = self.root.find(f".//CRequirement[@id='{self.unit_id}@Have']")
        if req is None: 
            self.__add_error(f'не создано требование <CRequirement id="{self.unit_id}@Have"/>')
        
        
        return self
    
    # проверки наличия коллекций данных
    
    def check_exist_datacollection_unit(self):
        if self.unit_collection is None:
            self.__add_error(f'не определена коллекция данных <CDataCollectionUnit id="{self.unit_id}" parent="...">')
        return self
    
    def check_exist_datacollection_weap(self):
        if len(self.weapons) == 0: return self # если единица не имеет оружие, тогда надо игнорировать эту ошибку
        for weap_id, collection in self.weap_collections.items():
            if collection is None:
                self.__add_error(f'не имеет коллекции данных <CDataCollectionUnit id="{weap_id}" parent="...">', title=f'Оружие "{weap_id}"')

        return self
    
    # Internal
    
    def __extract_race(self) -> str | None:
        """Раса берётся из атрибута race="..." либо из дочернего элемента <Race value="..."/>."""
        if self.unit is None: return None
        
        return self.unit.get("race") or (self.unit.find("Race").get("value") if self.unit.find("Race") is not None else None)
        
        # race_element = self.unit.find("Race")
        # return race_element.get("value") if race_element is not None else None
    
    def __extract_requires(self) -> list:

        pattern = r"Requires:\s*(?P<type>\w+):(?P<id>[\w@]+)\[(?P<file>[\w.]+)]"
        matches = re.finditer(pattern, self.filecontent)

        result = {}
        for m in matches:
            result[m.group("id")] = (m.group("type"), m.group("file"))
        return result

            
    def __add_error(self, message: str, title: str = ""):
        title = title if title != "" else f'Для единицы "{self.unit_id}"'
        self.errors.append(f'{title} {message}')


if __name__ == "__main__":
    
    args = sys.argv[1:]
    listpath = []
    listerrors = []
    
    if not args:
        print(USAGE)
        sys.exit(1)
    
    if args[0] == "gamedata":
        # os.walk вместо ручного обхода: файлы могут лежать на любой глубине вложенности
        # сортировка нужна для одинакового порядка вывода при каждом запуске
        for current_dir, dirnames, filenames in os.walk(GAMEDATA_DIR):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for filename in sorted(filenames):
                if not filename.endswith(".xml"): continue
                listpath.append(path.join(current_dir, filename))
    else:
        # принимается любое количество путей до файлов
        listpath = sorted({arg for arg in args if path.exists(arg)})
        missing = sorted({arg for arg in args if not path.exists(arg)})
        if missing:
            for arg in missing:
                print(f'Файл не найден: {arg}')
            sys.exit(1)
        if not listpath:
            print(USAGE)
            sys.exit(1)
        
    for file in listpath:    


        try:
            tree = ET.parse(file)
        except ET.ParseError as error:
            listerrors.append(f'{path.relpath(file, BASE_DIR)}: не удалось разобрать XML — {error}')
            continue

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
        
        # путь до файла добавляется к каждой ошибке, чтобы было понятно, где искать
        listerrors += [f'{path.relpath(file, BASE_DIR)}: {error}' for error in validator.errors]

    for error in listerrors:
        print(error)

    if not listerrors:
        print(f"✅ | Замечаний нет! Проверено файлов: {len(listpath)}")
    else:
        print(f"❌ | Проверено файлов: {len(listpath)}, замечаний: {len(listerrors)}")

    sys.exit(1 if listerrors else 0)


