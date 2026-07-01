# Base.SC2Data

Модульная переупаковка стандартных данных **StarCraft II** для использования в пользовательских картах и модификациях. Позволяет подключать отдельные юниты без необходимости импортировать все данные кампании.

## 📋 Описание

**Base.SC2Data** — это переструктурированная версия официальных данных StarCraft II, разделённая по отдельным юнитам и компонентам. Проект решает главную проблему разработки SC2 модов:

> **Проблема**: При использовании юнита из кампании приходится подтягивать огромные файлы с кучей ненужных данных, что раздувает размер карты/мода и усложняет поддержку.

> **Решение**: Base.SC2Data предоставляет чистые, отдельные XML-файлы каждого юнита с необходимыми зависимостями, без лишнего балласта.

### Преимущества:

✅ **Модульность** — подключай только нужные юниты  
✅ **Чистота** — без ненужных данных кампании  
✅ **Переиспользование** — используй один раз, применяй везде  
✅ **Лёгкая поддержка** — обновления одного юнита не влияют на остальные  
✅ **Открытость** — MIT лицензия, всё в GitHub  

## 🗂️ Структура данных

```
Base.SC2Data/
├── GameData/
│   ├── basestats/                 # Базовые конфигурации рас
│   │   ├── protoss.xml           # Generic_Protoss_Unit, шилды, рефлексы
│   │   ├── terran.xml            # Generic_Terran_Unit
│   │   └── zerg.xml              # Generic_Zerg_Unit, регенерация
│   │
│   ├── Khalai/                    # Юниты Khalai (Protoss фракция)
│   ├── Nerazim/                   # Юниты Nerazim (Protoss фракция)
│   ├── Purifier/                  # Юниты Purifier (Protoss фракция)
│   ├── Taldarim/                  # Юниты Taldarim (Protoss фракция)
│   │   ├── Alarak/
│   │   ├── Ascendant/
│   │   ├── Destroyer/
│   │   ├── Vanguard/
│   │   ├── Wrathwalker/
│   │   ├── Mothership/
│   │   └── Buildings/
│   │
│   ├── Terran/                    # Юниты Терана
│   │   └── Custom/
│   │       └── BMP/              # Пример кастомного юнита
│   │
│   ├── Stukov/                    # Инфестированные юниты (Stukov)
│   ├── Infested Terrans/          # Инфестированные терраны
│   ├── Marauders Mira's/          # Наёмники (Assault Galleon)
│   ├── Primal Zerg/               # Примитивные зергов
│   ├── Zeratul/                   # Юниты Zeratul (Protoss)
│   ├── terran_coop/               # Co-op кампания (Терран)
│   └── Protoss/                   # Стандартные протоссы
│
├── GameData.xml                   # Главный конфиг подключения
├── ruRU.SC2Data/                  # Локализация (русский)
├── enUS.SC2Assets/                # Ассеты (английский)
├── ruRU.SC2Assets/                # Ассеты (русский)
└── Assets/                        # Модели и текстуры юнитов
```

## 🚀 Как использовать

### Базовый сценарий: Добавить юнита в карту

#### 1. Подготовка карты
1. Откройте карту в **SC2 Editor**
2. **File → Save As... → "StarCraft II Component Folder"**
3. Дайте карте новое имя и сохраните

#### 2. Копирование юнита
Допустим, вы хотите добавить юнита **Wrathwalker** (Taldarim):

1. Перейдите в папку вашей карты: `YourMap.SC2Map/Base.SC2Data/GameData/`
2. Скопируйте папку из Base.SC2Data:
   ```
   GameData/Taldarim/Wrathwalker/ → YourMap.SC2Map/Base.SC2Data/GameData/Taldarim/Wrathwalker/
   ```

#### 3. Добавление зависимостей
Откройте файл юнита (например `Wrathwalker.xml`) и проверьте комментарий в начале:
```xml
<!-- Requires: Unit:Generic_Unit_Ground[base.xml] -->
```

Скопируйте указанные базовые файлы в `GameData/basestats/`:
```
basestats/protoss.xml      (для Protoss юнитов)
basestats/terran.xml       (для Terran юнитов)
basestats/zerg.xml         (для Zerg юнитов)
```

#### 4. Регистрация в GameData.xml
Отредактируйте `Base.SC2Data/GameData.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<Includes>
    <!-- Базовые данные рас -->
    <Catalog path="GameData/basestats/protoss.xml"/>
    
    <!-- Ваши юниты -->
    <Catalog path="GameData/Taldarim/Wrathwalker/Wrathwalker.xml"/>
</Includes>
```

#### 5. Копирование ассетов (модели, текстуры, звуки)
```
Assets/ → YourMap.SC2Map/Assets/
ruRU.SC2Assets/ → YourMap.SC2Map/ruRU.SC2Assets/    (если используете русскую локализацию)
```

#### 6. Обновление локализации (если нужно)
Скопируйте текстовые строки юнита:
```
ruRU.SC2Data/LocalizedData/GameStrings.txt → YourMap.SC2Map/ruRU.SC2Data/LocalizedData/GameStrings.txt
```

### Продвинутый сценарий: Использование нескольких юнитов

```xml
<?xml version="1.0" encoding="utf-8"?>
<Includes>
    <!-- Базовые данные -->
    <Catalog path="GameData/basestats/protoss.xml"/>
    <Catalog path="GameData/basestats/terran.xml"/>
    
    <!-- Taldarim юниты -->
    <Catalog path="GameData/Taldarim/Mothership/Mothership.xml"/>
    <Catalog path="GameData/Taldarim/Wrathwalker/Wrathwalker.xml"/>
    <Catalog path="GameData/Taldarim/Alarak/Alarak.xml"/>
    
    <!-- Nerazim юниты -->
    <Catalog path="GameData/Nerazim/Carrier/Carrier.xml"/>
    <Catalog path="GameData/Nerazim/Annihilator/Annihilator.xml"/>
    
    <!-- Кастомные юниты -->
    <Catalog path="GameData/Terran/Custom/BMP/BMP.xml"/>
</Includes>
```

## 📦 Содержимое репозитория

### Основные расы:

- **Protoss**: Khalai, Nerazim, Purifier, Taldarim, Zeratul
- **Terran**: Стандартные юниты, кастомные модели (BMP), наёмники Marauders
- **Zerg**: Primal Zerg, инфестированные виды (Stukov)

### Примеры юнитов:

| Юнит | Раса | Тип | Файл |
|------|------|------|------|
| Wrathwalker | Taldarim | Ground | `GameData/Taldarim/Wrathwalker/Wrathwalker.xml` |
| Mothership | Taldarim | Air | `GameData/Taldarim/Mothership/Mothership.xml` |
| Energizer | Purifier | Ground | `GameData/Purifier/Energizer/Energizer.xml` |
| Carrier | Nerazim | Air | `GameData/Nerazim/Carrier/Carrier.xml` |
| BMP | Terran | Ground | `GameData/Terran/Custom/BMP/BMP.xml` |
| Zeratul Hero | Zeratul | Ground | `GameData/Zeratul/Enforcer.xml` |

## 🛠️ Требования

- **StarCraft II Editor** (входит в состав игры)
- Понимание структуры SC2 XML (опционально для модификаций)
- Windows / Mac / Linux

## 📝 Лицензия

MIT License — свободное использование в коммерческих и личных проектах.

Copyright © 2026 DesigneDragon

[Полный текст лицензии](LICENSE)

## 📌 Дополнительные ресурсы

- **CurseForge Data Library**: https://www.curseforge.com/sc2/assets/data-library-taldarim-forces
- **StarCraft II**: https://starcraft2.com/
- **SC2 Editor Documentation**: https://wiki.sc2mapster.com/
- **SC2 Modding Community**: https://www.sc2mapster.com/

## 🤝 Вклад в проект

Поправки, дополнения и оптимизации приветствуются!

1. **Fork** репозитория
2. Создайте ветку для изменений: `git checkout -b feature/add-unit-x`
3. Отправьте **Pull Request** с описанием

### Идеи для развития:
- Добавление новых юнитов из кампании
- Оптимизация размера файлов
- Расширение локализации
- Примеры для скриптинга

## ❓ Часто задаваемые вопросы

**Q: Какой размер добавляет один юнит к карте?**  
A: Обычно 50-500 KB в зависимости от сложности, моделей и звуков. Намного меньше, чем весь набор кампании.

**Q: Совместимо ли это с последней версией SC2?**  
A: Данные основаны на стандартной версии SC2. Обновления Blizzard требуют переупаковки.

**Q: Можно ли модифицировать юниты?**  
A: Да! Отредактируйте XML-файл перед подключением в карту. Это основная идея модульности.

**Q: Почему не просто использовать Dependency?**  
A: Dependency подтягивает ВСЕ данные кампании, что раздувает карту. Base.SC2Data — это минималистичная версия.

## 📋 Заметки о структуре

- Каждый юнит находится в отдельной папке со своим XML-файлом
- Базовые конфигурации рас в `basestats/`
- Ассеты (модели, текстуры) в папке `Assets/`
- Локализация разделена по языкам (`ruRU`, `enUS`)

## 🎮 Примеры использования

Этот репозиторий идеален для:
- 🗺️ Создания кастомных карт для Arcade
- 🎬 Разработки пользовательских кампаний
- 🤖 Создания модов и вариантов
- 🎨 Экспериментов с балансом юнитов
- 📚 Обучения структуре SC2 данных

---

**Спасибо за использование Base.SC2Data! Удачи в создании карт и модов! 🎮✨**

Вопросы? Создавайте Issues или обращайтесь в SC2 модкоммьюнити.
