# HOW TO ADD A UNIT?

1.  **Extract the map into components**
    - Go to **File → Save As...** in the SC2 Editor.
    - In the dialog, choose the file type **"StarCraft II Component Folder"**.
    - Give it a distinct name (different from the original map file) and save.

2.  **Navigate to the folder** where you saved your map's components.

3.  **Inside your map folder**, go to the path: `Base.SC2Data/GameData/`.  
    Copy the `.xml` file from the unit's archive into this folder.

4.  **Also inside `Base.SC2Data/GameData/`**, copy the required base files (`base.xml`, `protoss.xml`, `terran.xml`, `zerg.xml`).  
    To know exactly which files are needed, look for `<!-- Requires: -->` lines at the top of the unit's XML file.  
    For example, `<!-- Requires: Unit:UnitGround[base.xml] -->` means the unit needs `base.xml`.

5.  **Inside the `Base.SC2Data/` folder**, create or edit the `GameData.xml` file with content similar to this:

```xml
<?xml version="1.0" encoding="utf-8"?>
<Includes>
    <Catalog path="GameData/base.xml" />
    <Catalog path="GameData/protoss.xml"/>
    <Catalog path="GameData/terran.xml"/>
    <Catalog path="GameData/zerg.xml"/>
    <Catalog path="GameData/Path/To/Unit/Unit.xml"/>
</Includes>
```

6.  **Copy all `Assets` folders** into the root of your map folder.

7.  **Merge the text strings** from the localization files in the archive with your own localization files.  
    For example, copy the contents of `ruRU.SC2Assets/GameStrings.txt` from the archive into your `ruRU.SC2Assets/GameStrings.txt`.

8.  **Copy the necessary localized asset folders** (e.g., `ruRU.SC2Assets`, `enUS.SC2Assets`) into the root of your map folder.

---

# КАК ПОДКЛЮЧИТЬ ЕДИНИЦУ?

1. Разобрать карту на компоненты
   - Для этого переходим на вкладку "файл - Сохранить Как..."
   - Затем в окне указываем тип файла как "StarCraft II Папка компонентов"
   - Даём отличное название от основного названия файла и сохраняем

2. Переходим к папке, куда сохранили ваши компоненты
3. По пути внутри вашей карты (её папки) такому как "Base.SC2Data/GameData/" вставляем xml файл из архива единицы
4. По пути внутри вашей карты (её папки) такому как "Base.SC2Data/GameData/" вставляем xml файлы `base.xml`, `protoss.xml`, `terran.xml`, `zerg.xml` (Чтобы точно узнать какие именно файлы нужны, смотрим строки <-- Requires: --> в начале файла с юнитом. Запись `<!-- Requires: Unit:UnitGround[base.xml] -->` означает что для единицы необходим файл `base.xml`)
5. По пути внутри вашей карты (её папки) такому как "Base.SC2Data/" Добавляем файл GameData.xml с примерно таким содержимым
```xml
<?xml version="1.0" encoding="utf-8"?>
<Includes>
    <Catalog path="GameData/base.xml" />
    <Catalog path="GameData/protoss.xml"/>
    <Catalog path="GameData/terran.xml"/>
    <Catalog path="GameData/zerg.xml"/>
    <Catalog path="GameData/Путь/До/XML-файла/Единицы.xml"/>
</Includes>
```
6. Вставить все папки `Assets` в корень вашей карты (её папки)
7. Добавить все тексты из файлов локализации из архива в ваши соотствествующие файлы
   - Например, всё содержимое из файла ruRU.SC2Assets/GameStrings.txt вставляем в ваш файл ruRU.SC2Assets/GameStrings.txt
8. Вставить в корень вашей карты (её папки) все необходимые локализованные файлы ruRU.SC2Assets/enUS.SC2Assets

