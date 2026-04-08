---
name: sc2data-wizard-advanced
description: Мастер-класс по созданию визардов StarCraft II Data Editor. Изучите синтаксис, паттерны и лучшие практики создания автоматизированных инструментов для генерации данных в XML.
---

# SC2 Data Wizard Authoring

Полное руководство по созданию визардов (.BlizWiz) для StarCraft II Data Editor. Этот скилл обобщает паттерны из 60+ готовых визардов проекта.

## Содержание

1. [Быстрый старт](#быстрый-старт)
2. [Структура файла](#структура-файла)
3. [Типы ввода](#типы-ввода)
4. [Условия и валидация](#условия-и-валидация)
5. [Макросы](#макросы)
6. [Создание записей](#создание-записей-entry)
7. [Продвинутые паттерны](#продвинутые-паттерны)
8. [Лучшие практики](#лучшие-практики)

---

## Быстрый старт

### Минимальный визард

```xml
<?xml version="1.0" encoding="UTF-8"?>
<wizardfile>
    <wizard id="SimpleUnitWizard">
        <name>Simple Unit Creator</name>
        <category>Data/Units</category>
        <objecttypes create="Unit;Actor"/>
        
        <input id="UnitName" type="CString">
            <name>Unit Name</name>
            <default value="MyUnit"/>
        </input>
        
        <entry catalog="Unit" type="CUnit">
            <id>^UnitName^</id>
            <field id="Name">
                <value>^UnitName^</value>
            </field>
        </entry>
        
        <entry catalog="Actor" type="CActorUnit">
            <id>^UnitName^Actor</id>
            <field id="UnitName">
                <value>^UnitName^</value>
            </field>
        </entry>
    </wizard>
</wizardfile>
```

### Основные понятия

| Понятие | Описание |
|---------|----------|
| `wizardfile` | Корневой элемент файла |
| `wizard` | Определение одного визарда |
| `input` | Поле ввода для пользователя |
| `entry` | Создаваемая запись в каталоге |
| `condition` | Условие видимости/выполнения |
| `validate` | Проверка корректности ввода |
| `macro` | Вычисляемая строка для переиспользования |

---

## Структура файла

### Корневой элемент

```xml
<?xml version="1.0" encoding="UTF-8"?>
<wizardfile>
    <!-- один или несколько wizard -->
</wizardfile>
```

### Определение визарда

```xml
<wizard id="UniqueWizardId">
    <name>Отображаемое имя</name>
    <category>Категория в редакторе</category>
    <objecttypes create="Unit;Actor;Effect"/>
    <instructions page="1">Инструкция для пользователя</instructions>
    
    <!-- inputs, conditions, entries -->
</wizard>
```

### Атрибуты objecttypes

```xml
<!-- Создаваемые типы каталогов -->
<objecttypes create="Unit;Actor;Effect;Ability;Behavior;Button;Requirement;Weapon;Mover"/>
<!-- Также поддерживается load для существующих данных -->
<objecttypes create="Unit" load="Upgrade"/>
```

---

## Типы ввода

### Базовые типы

| Тип | Описание | Пример |
|-----|----------|--------|
| `CString` | Текстовая строка | ID, имя |
| `CStringLink` | Текстовая ссылка | Локализованное имя |
| `int32` | Целое число | Количество |
| `real32` | Число с плавающей точкой | Радиус, урон |
| `CFixed` | Fixed-point число | Диапазон оружия |
| `CImagePath` | Путь к иконке | `.dds` файл |
| `CModelPath` | Путь к модели | `.m3` файл |
| `CModelLink` | Ссылка на модель | Из каталога |
| `CSoundLink` | Ссылка на звук | Из каталога |

### Типы ссылок на данные

```xml
<!-- Ссылка на юнит -->
<input id="UnitType" type="CUnitLink">
    <name>Unit Type</name>
</input>

<!-- Ссылка на способность -->
<input id="Ability" type="CAbilLink">
    <name>Ability</name>
</input>

<!-- Ссылка на эффект -->
<input id="EffectLink" type="CEffectLink">
    <name>Effect</name>
</input>

<!-- Ссылка на апгрейд -->
<input id="Upgrade" type="CUpgradeLink">
    <name>Upgrade</name>
</input>

<!-- Ссылка на поведение -->
<input id="Behavior" type="CBehaviorLink">
    <name>Behavior</name>
</input>
```

### Выбор из вариантов

```xml
<!-- Радиокнопки (выбор одного) -->
<input id="TargetType" type="WizardRadio">
    <name>Target Type</name>
    <item text="Single Target" value="0"/>
    <item text="Splash" value="1"/>
    <item text="Area" value="2"/>
    <default value="0"/>
</input>

<!-- Выпадающее меню -->
<input id="MoverType" type="WizardMenu">
    <name>Mover Type</name>
    <item text="Linear" value="Linear"/>
    <item text="Parabolic" value="Parabolic"/>
    <item text="Chasing" value="Chasing"/>
    <default value="Linear"/>
</input>

<!-- Чекбокс -->
<input id="CreateMover" type="WizardCheckbox">
    <name>Create Mover</name>
    <default value="1"/>
</input>

<!-- Текстовый блок -->
<input id="InfoText" type="WizardText">
    <default value="Instruction text"/>
    <color value="255,0,76,153"/>
</input>
```

### Layout (расположение)

```xml
<input id="Field1" type="CString">
    <name>Field 1</name>
    <layout page="1"/>           <!-- Страница 1 -->
    <layout page="2" column="2"/> <!-- Страница 2, колонка 2 -->
    <layout column="1"/>          <!-- Текущая страница, колонка 1 -->
    <layout minheight="60"/>      <!-- Минимальная высота -->
</input>
```

---

## Условия и валидация

### Простые условия

```xml
<!-- Проверка что поле не пустое -->
<condition id="HasInput" input="FieldName" empty="0"/>
<condition id="IsEmpty" input="FieldName" empty="1"/>

<!-- Проверка значения -->
<condition id="IsDirect" input="WeaponType" value="Direct"/>
<condition id="NotMissile" input="WeaponType" value="Missile" operator="not equal"/>

<!-- Проверка содержит текст -->
<condition id="IsResearch" input="Ability" match="contain" value="Research"/>
```

### Составные условия

```xml
<!-- Логическое И -->
<condition id="DirectAndSplash" logic="and">
    <condition input="TargetType" value="0"/>
    <condition input="WeaponType" value="Direct"/>
</condition>

<!-- Логическое ИЛИ -->
<condition id="SingleOrSplash" logic="or">
    <condition input="TargetType" value="0"/>
    <condition input="TargetType" value="1"/>
</condition>

<!-- Отрицание -->
<condition id="NotZero" logic="not">
    <condition input="Amount" value="0"/>
</condition>
```

### Валидация ввода

```xml
<!-- Ошибка (блокирует завершение) -->
<validate type="error">
    <condition input="UnitType" empty="0"/>
    <text>You must select a unit type</text>
</validate>

<!-- Предупреждение (позволяет продолжить) -->
<validate type="warning">
    <condition input="Model" empty="0"/>
    <text>Model is empty - visual effects won't work</text>
</validate>

<!-- Подтверждение -->
<validate type="confirm">
    <text>Create 10 entries?</text>
</validate>
```

### Условия в записях

```xml
<entry catalog="Mover" type="CMoverMissile">
    <id>^Id^Missile</id>
    <condition input="CreateMover" value="1"/>  <!-- Только если чекбокс включен -->
    <field id="Speed">
        <value>18.75</value>
    </field>
</entry>
```

---

## Макросы

### Базовые макросы

```xml
<!-- Простой макрос -->
<macro id="FullId">^Prefix^_^Suffix^</macro>

<!-- Вычисляемые значения -->
<macro id="Radius100">^SearchRadius^</macro>
<macro id="Radius75">^SearchRadius^ * 0.75</macro>
<macro id="Radius50">^SearchRadius^ * 0.5</macro>
<macro id="Radius25">^SearchRadius^ * 0.25</macro>

<!-- Ссылки на каталог -->
<macro id="UnitAbil0">ref=Unit,^UnitID^,AbilArray[0]</macro>
<macro id="WeaponName">ref=Weapon,^WeaponID^,Name</macro>
```

### Использование макросов

```xml
<entry catalog="Effect" type="CEffectDamage">
    <id>^Id^Damage</id>
    <field id="Name">
        <value>^FullId^ Damage</value>
    </field>
    <field id="AreaArray_Radius">
        <index>0</index>
        <value>^Radius100^</value>
    </field>
</entry>
```

---

## Создание записей (Entry)

### Базовая структура

```xml
<entry catalog="Effect" type="CEffectDamage">
    <id>^Id^Damage</id>              <!-- ID создаваемой записи -->
    <parentid>DU_WEAPON</parentid>   <!-- Родитель (наследование) -->
    <allowmodify/>                   <!-- Разрешить модификацию существующей -->
    
    <field id="Name">
        <value>Damage Effect</value>
    </field>
    
    <field id="Amount">
        <value>100</value>
    </field>
</entry>
```

### Массивы

```xml
<!-- Простой массив -->
<field id="EffectArray">
    <value>Effect1</value>
    <index>0</index>
</field>
<field id="EffectArray">
    <value>Effect2</value>
    <index>1</index>
</field>

<!-- Динамический размер -->
<field id="AssetArray">
    <value>ref=Sound,^SoundLink^,AssetArray[^VALUEINDEX^]</value>
    <count>30</count>
</field>
```

### Условные поля

```xml
<field id="Effect">
    <value>^Id^Damage</value>
    <condition id="DirectSingle"/>
</field>
<field id="Effect">
    <value>^Id^LaunchMissile</value>
    <condition id="MissileSingle"/>
</field>

<!-- Разные значения по условию -->
<field id="Magnitude">
    <condition input="PhysicsSize" value="1"/>
    <value>12,7</value>
</field>
<field id="Magnitude">
    <condition input="PhysicsSize" value="2"/>
    <value>20,8</value>
</field>
```

### Token (для актёров)

```xml
<entry catalog="Actor" type="CActorAction">
    <id>^Id^Action</id>
    <parentid>GenericAttack</parentid>
    <token id="effectAttack">
        <value>^Id^Damage</value>
    </token>
    <token id="unitName">
        <value>^Id^Missile</value>
    </token>
</entry>
```

### Модификация существующих записей

```xml
<!-- Добавление оружия к юниту -->
<entry catalog="Unit" type="CUnit">
    <id>^AddToUnit^</id>
    <allowmodify/>
    <field id="WeaponArray_Link">
        <index>ref=Unit,^AddToUnit^,WeaponArray#</index>
        <value>^WeaponID^</value>
    </field>
</entry>

<!-- Добавление способности -->
<entry catalog="Unit" type="CUnit">
    <id>^UnitID^</id>
    <allowmodify/>
    <field id="AbilArray_Link">
        <index>ref=Unit,^UnitID^,AbilArray#</index>
        <value>^AbilityID^</value>
    </field>
</entry>
```

---

## Продвинутые паттерны

### Паттерн: Создание оружия со снарядом

```xml
<!-- CWeaponLegacy + CEffectLaunchMissile + CActorMissile + CMoverMissile -->
<entry catalog="Weapon" type="CWeaponLegacy">
    <id>^WeaponID^</id>
    <field id="Name"><value>^WeaponName^</value></field>
    <field id="Range"><value>^Range^</value></field>
    <field id="Effect"><value>^WeaponID^LaunchMissile</value></field>
    <condition id="IsMissile"/>
</entry>

<entry catalog="Effect" type="CEffectLaunchMissile">
    <id>^WeaponID^LaunchMissile</id>
    <field id="AmmoUnit"><value>^WeaponID^Weapon</value></field>
    <field id="ImpactEffect"><value>^WeaponID^Damage</value></field>
    <condition id="IsMissile"/>
</entry>

<entry catalog="Effect" type="CEffectDamage">
    <id>^WeaponID^Damage</id>
    <field id="Amount"><value>^Damage^</value></field>
    <field id="Kind"><value>^DamageKind^</value></field>
</entry>

<entry catalog="Unit" type="CUnit">
    <id>^WeaponID^Weapon</id>
    <parentid>MISSILE</parentid>
    <condition id="IsMissile"/>
    <field id="Name"><value>^WeaponName^ Projectile</value></field>
    <field id="Mover"><value>^WeaponID^Missile</value></field>
</entry>

<entry catalog="Mover" type="CMoverMissile">
    <id>^WeaponID^Missile</id>
    <parentid>HydraliskImpaleMissile</parentid>
    <condition id="IsMissile"/>
</entry>

<entry catalog="Actor" type="CActorMissile">
    <id>^WeaponID^WeaponMissile</id>
    <parentid>GenericAttackMissile</parentid>
    <condition id="IsMissile"/>
    <token id="unitName"><value>^WeaponID^Weapon</value></token>
    <field id="Model"><value>^WeaponID^MissileModel</value></field>
</entry>

<entry catalog="Actor" type="CActorAction">
    <id>^WeaponID^Action</id>
    <parentid>GenericAttack</parentid>
    <field id="Missile"><value>^WeaponID^WeaponMissile</value></field>
    <field id="LaunchAssets_Sound"><value>^WeaponID^LaunchSound</value></field>
    <field id="ImpactMap_Sound"><index>0</index><value>^WeaponID^ImpactSound</value></field>
</entry>
```

### Паттерн: Цепочка эффектов для AoE урона

```xml
<!-- CEffectSet -> CEffectEnumArea -> CEffectDamage -->
<entry catalog="Effect" type="CEffectSet">
    <id>^Id^EffectSet</id>
    <field id="EffectArray">
        <value>^Id^Search</value>
        <index>0</index>
    </field>
</entry>

<entry catalog="Effect" type="CEffectEnumArea">
    <id>^Id^Search</id>
    <field id="AreaArray">
        <value>^Id^Damage</value>
        <index>0</index>
    </field>
    <field id="AreaArray_Radius">
        <index>0</index>
        <value>^SearchRadius^</value>
    </field>
    <field id="SearchFilters">
        <value>Visible,Enemy,Ground,Air;Self,Ally,Structure,Invulnerable</value>
    </field>
</entry>

<entry catalog="Effect" type="CEffectDamage">
    <id>^Id^Damage</id>
    <field id="Amount"><value>^Damage^</value></field>
    <field id="Kind"><value>Spell</value></field>
</entry>
```

### Паттерн: Визуальный эффект на эффект

```xml
<!-- CModel + CActorModel, привязанный к Effect.Start/Stop -->
<entry catalog="Model" type="CModel">
    <id>^Id^FX</id>
    <field id="Model"><value>^ModelPath^</value></field>
    <field id="Name"><value>^Name^ FX</value></field>
</entry>

<entry catalog="Actor" type="CActorModel">
    <id>^Id^FX</id>
    <parentid>ModelAnimationStyleContinuous</parentid>
    <field id="Host_Subject"><value>_Unit</value></field>
    <field id="HostSiteOps_Ops"><value>SOpAttachOrigin</value></field>
    <field id="On_Terms">
        <index>3</index>
        <value>Effect.^Id^Effect.Start</value>
    </field>
    <field id="On_Terms">
        <index>4</index>
        <value>Effect.^Id^Effect.Stop</value>
    </field>
    <field id="On_Send">
        <index>3</index>
        <value>Create</value>
    </field>
    <field id="On_Send">
        <index>4</index>
        <value>AnimBracketStop BSD</value>
    </field>
</entry>
```

### Паттерн: Создание кнопки для способности

```xml
<entry catalog="Button" type="CButton">
    <id>^Id^Button</id>
    <field id="Icon"><value>^IconPath^</value></field>
    <field id="AlertIcon"><value>^IconPath^</value></field>
    <field id="Name">
        <condition input="ButtonName" empty="0"/>
        <value>^ButtonName^</value>
    </field>
    <field id="Name">
        <condition input="ButtonName" empty="1"/>
        <value>^Id^</value>
    </field>
    <field id="Tooltip">
        <stringid>Button/Tooltip/^Id^Button</stringid>
        <value>^Tooltip^</value>
    </field>
</entry>

<entry catalog="Abil" type="CAbilEffectTarget">
    <id>^Id^</id>
    <field id="CmdButtonArray_DefaultButtonFace">
        <value>^Id^Button</value>
    </field>
    <field id="Effect">
        <value>^Id^EffectSet</value>
        <index>0</index>
    </field>
    <field id="Range">
        <value>^Range^</value>
    </field>
    <field id="Cost_Vital">
        <value>^EnergyCost^</value>
        <index>0;Energy</index>
    </field>
</entry>
```

### Паттерн: Требование (Requirement)

```xml
<!-- Learn requirement для апгрейда -->
<entry catalog="Requirement" type="CRequirement">
    <id>Learn^UpgName^</id>
    <field id="Name">
        <value>Learn ^UpgName^</value>
    </field>
    <field id="NodeArray_Link">
        <index>0</index>
        <value>CountUpgrade^UpgID^QueuedOrBetter</value>
    </field>
    <field id="NodeArray_Link">
        <index>1</index>
        <value>LTECountUpgrade^UpgID^QueuedOrBetter^MaxLevelMinus1^</value>
    </field>
</entry>

<entry catalog="RequirementNode" type="CRequirementCountUpgrade">
    <id>CountUpgrade^UpgID^QueuedOrBetter</id>
    <field id="Count_Link"><value>^UpgID^</value></field>
    <field id="Count_State"><value>QueuedOrBetter</value></field>
</entry>

<entry catalog="RequirementNode" type="CRequirementLTE">
    <id>LTECountUpgrade^UpgID^QueuedOrBetter^MaxLevelMinus1^</id>
    <field id="OperandArray">
        <index>0</index>
        <value>CountUpgrade^UpgID^QueuedOrBetter</value>
    </field>
    <field id="OperandArray">
        <index>1</index>
        <value>^MaxLevelMinus1^</value>
    </field>
</entry>
```

### Паттерн: Beam (луч) для канала

```xml
<entry catalog="Model" type="CModel">
    <id>^Id^Beam</id>
    <parentid>PersistentSpellFX</parentid>
    <field id="Model"><value>^BeamModel^</value></field>
</entry>

<entry catalog="Actor" type="CActorBeamSimple">
    <id>^Id^Beam</id>
    <parentid>BeamSimpleAnimationStyleContinuous</parentid>
    <field id="HostLaunch_Subject"><value>_Unit</value></field>
    <field id="HostLaunchSiteOps_Ops"><value>SOpAttachWeapon</value></field>
    <field id="HostImpactSiteOps_Ops"><value>SOpTargetUnit SOpAttachHead</value></field>
    <field id="On_Terms">
        <index>3</index>
        <value>Effect.^Id^Start</value>
    </field>
    <field id="On_Terms">
        <index>4</index>
        <value>Effect.^Id^Stop</value>
    </field>
    <field id="On_Send">
        <index>3</index>
        <value>Create</value>
    </field>
    <field id="On_Send">
        <index>4</index>
        <value>Destroy</value>
    </field>
</entry>
```

### Паттерн: Динамическая индексация

```xml
<!-- Получение текущего количества кнопок/способностей -->
<macro id="ButtonCount">ref=Unit,^UnitID^,CardLayouts[0].LayoutButtons#</macro>
<macro id="NextButtonIndex">^ButtonCount^-1</macro>
<macro id="OnCount">ref=Actor,^UnitID^,On#</macro>
<macro id="NextOnIndex">^OnCount^-1</macro>

<!-- Добавление кнопки на следующий слот -->
<entry catalog="Unit" type="CUnit">
    <id>^UnitID^</id>
    <allowmodify/>
    <field id="CardLayouts_LayoutButtons_Face">
        <value>^AbilityID^</value>
        <index>^NextButtonIndex^</index>
    </field>
    <field id="CardLayouts_LayoutButtons_Type">
        <value>AbilCmd</value>
        <index>^NextButtonIndex^</index>
    </field>
    <field id="CardLayouts_LayoutButtons_AbilCmd">
        <value>^AbilityID^,Execute</value>
        <index>^NextButtonIndex^</index>
    </field>
</entry>
```

---

## Лучшие практики

### 1. Всегда используйте parentid

```xml
<!-- Плохо -->
<entry catalog="Unit" type="CUnit">
    <id>^Id^</id>
    <field id="LifeMax"><value>1000</value></field>
    <!-- ... все поля вручную -->
</entry>

<!-- Хорошо -->
<entry catalog="Unit" type="CUnit">
    <id>^Id^</id>
    <parentid>MARINE</parentid>
    <field id="LifeMax"><value>1000</value></field>
    <!-- только переопределяем нужное -->
</entry>
```

### 2. Группируйте связанные условия

```xml
<!-- Создавайте именованные условия для логических групп -->
<condition id="IsMissileSplash" logic="and">
    <condition input="WeaponType" value="Missile"/>
    <condition input="TargetType" value="1"/>
</condition>

<!-- Затем используйте в entry -->
<entry catalog="Effect" type="CEffectEnumArea">
    <id>^Id^Search</id>
    <condition id="IsMissileSplash"/>
</entry>
```

### 3. Валидируйте критические поля

```xml
<!-- Всегда проверяйте обязательные поля -->
<validate type="error">
    <condition input="Id" empty="0"/>
    <text>ID is required</text>
</validate>

<validate type="warning">
    <condition input="Model" empty="0"/>
    <text>No model selected - no visual effects</text>
</validate>
```

### 4. Используйте макросы для повторяющихся выражений

```xml
<!-- Вместо повторения -->
<field id="EffectArray">
    <value>ref=Abil,^Ability^,InfoArray[0].Upgrade</value>
</field>
<field id="EffectArray">
    <value>ref=Abil,^Ability^,InfoArray[1].Upgrade</value>
</field>

<!-- Определите макрос -->
<macro id="Upg0">ref=Abil,^Ability^,InfoArray[0].Upgrade</macro>
<macro id="Upg1">ref=Abil,^Ability^,InfoArray[1].Upgrade</macro>

<!-- Используйте -->
<field id="EffectArray">
    <value>^Upg0^</value>
</field>
```

### 5. Добавляйте инструкции для пользователей

```xml
<instructions page="1">
    Выберите тип цели и способ нанесения урона.
    Direct - мгновенный урон (как Marine)
    Missile - снаряд (как Roach)
</instructions>
```

### 6. Поддерживайте load (загрузку из существующих данных)

```xml
<objecttypes create="Unit" load="Upgrade"/>

<input id="UpgradeID" type="CUpgradeLink">
    <loadvalue>^LOADID^</loadvalue>
</input>
```

### 7. Используйте префиксы/суффиксы для организации

```xml
<field id="EditorPrefix">
    <stringid>Unit/EditorPrefix/^Id^</stringid>
    <value>MyMod_</value>
</field>
<field id="EditorSuffix">
    <stringid>Unit/EditorSuffix/^Id^</stringid>
    <value>_Custom</value>
</field>
```

---

## Распространённые ошибки

### Ошибка: Забытые ^ в токенах

```xml
<!-- Не работает -->
<field id="Name"><value>Id Damage</value></field>

<!-- Работает -->
<field id="Name"><value>^Id^ Damage</value></field>
```

### Ошибка: Неправильный тип каталога

```xml
<!-- CEffectDamage - в каталог Effect -->
<entry catalog="Effect" type="CEffectDamage">

<!-- CBehaviorBuff - в каталог Behavior -->
<entry catalog="Behavior" type="CBehaviorBuff">

<!-- CActorUnit - в каталог Actor -->
<entry catalog="Actor" type="CActorUnit">
```

### Ошибка: Условие не определено

```xml
<!-- Определите условие до использования -->
<condition id="HasMover" input="CreateMover" value="1"/>

<entry catalog="Mover" type="CMoverMissile">
    <id>^Id^Missile</id>
    <condition id="HasMover"/>  <!-- Теперь работает -->
</entry>
```

---

## Примеры из проекта

| Файл | Описание |
|------|----------|
| `GeneralWizards/Create Units.BlizWiz` | Создание юнитов и актёров |
| `GeneralWizards/Create Buffs.BlizWiz` | Создание баффов/дебаффов |
| `GeneralWizards/Create Actors.BlizWiz` | Визуальные эффекты, лучи |
| `Fenix - Create Weapon v1.3.blizwiz` | Полное оружие со снарядами |
| `Fenix - Requirement v1.1.blizwiz` | Система требований |
| `AbilWizards/ChannelSnipe.BlizWiz` | Канальная способность |

---

## Дополнительные ресурсы

- [SC2Mapster Wiki - Wizards](https://sc2mapster.wiki.gg/wiki/Wizards)
- [Data Wizard Documentation](https://github.com/SC2Mapster/blizzard-tutorials/tree/master/docs/New_Tutorials/04_Data_Editor)
- [catalogsData.xsd](https://github.com/SC2Mapster/catalogsData.xsd) - Схема всех полей
