---
name: galaxy-game-systems
description: Bank save/load, spawner and wave systems, jungle/camp respawn, resource rewards, hero revive/death, tech tree upgrades, and game attribute lobby options in Galaxy script. Use when implementing persistent data storage, enemy wave spawners, neutral camp respawn timers, kill resource rewards, or player revive logic. Do not use for AI wave behavior (use galaxy-ai-and-techtree) or UI (use galaxy-ui-and-dialogs).
---

# Galaxy Scripting – Game Systems

## Key References

| Resource | URL |
|---|---|
| Native function reference | https://mapster.talv.space/galaxy/reference |
| Galaxy syntax definition | https://github.com/Talv/vscode-sc2-galaxy/blob/master/syntaxes/galaxy.json |
| Banks guide | https://s2editor-guides.readthedocs.io/New_Tutorials/03_Trigger_Editor/051_Banks/ |
| Custom Values guide | https://s2editor-guides.readthedocs.io/New_Tutorials/03_Trigger_Editor/050_Custom_Values/ |
| **SC2-IngameDevTools (PRIMARY — #1 codebase)** | https://github.com/abrahamYG/SC2-IngameDevTools/tree/main/DevToolsIngame.SC2Mod/Script |
| SSF codebase (secondary style) | https://github.com/Cristall/SC2-SwarmSpecialForces/tree/main/SwarmSpecialForces.SC2Map/scripts |
| Alcyone Frontlines codebase | https://github.com/KimPlaybit/Alcyone_Frontlines/tree/master/ProximaFrontlines.SC2Mod/scripts |
| NativeLib | `TriggerLibs/NativeLib.galaxy` (sc2galaxy VS Code extension) |
| SC2Mapster wiki | https://sc2mapster.wiki.gg/ |

---

## Bank System (Save / Load Player Data)

Banks persist data between sessions per player. One bank = one named file tied to one player slot.

```galaxy
// Open (create if missing) — use your map/mod name as the bank name
BankLoad("MyMapName", lv_player);
bank lv_bank = BankLastCreated();

// Wait for async load to complete (needed if called at game start)
BankWait(lv_bank);

// Check section/key existence
bool lv_has = BankKeyExists(lv_bank, "Stats", "TotalKills");

// Read values
int   lv_kills   = BankValueGetAsInt(lv_bank, "Stats", "TotalKills");
bool  lv_flag    = BankValueGetAsFlag(lv_bank, "Flags", "CompletedTutorial");
fixed lv_score   = BankValueGetAsFixed(lv_bank, "Stats", "BestScore");
text  lv_name    = BankValueGetAsText(lv_bank, "Profile", "Name");

// Write values
BankValueSetFromInt(lv_bank, "Stats", "TotalKills", lv_kills + 1);
BankValueSetFromFlag(lv_bank, "Flags", "CompletedTutorial", true);
BankValueSetFromFixed(lv_bank, "Stats", "BestScore", 9999.0);

// Save to disk
BankSave(lv_bank);

// Remove section
BankSectionRemove(lv_bank, "OldData");

// Remove a key
BankKeyRemove(lv_bank, "Stats", "OldKey");

// Enable signature/encryption (prevents tampering by the player)
// Call this immediately after BankLoad, before BankWait
BankSetOptionSignature(lv_bank, true);
```

> **Bank file location on disk (Windows):**
> `Documents\StarCraft II\StarCraftPlayer.ID@#\Banks\[MapAuthorID]\[BankName].SC2Bank`
>
> Signature-enabled banks are checksummed by the engine. Manually editing a signed bank file will invalidate it on next load, causing the engine to treat it as empty/corrupt.
>
> **Full reference:** [Banks guide](https://s2editor-guides.readthedocs.io/New_Tutorials/03_Trigger_Editor/051_Banks/)

### Bank structure (hierarchy)

```
Bank file
 └─ Section  (e.g. "Stats", "Flags", "Profile")
     └─ Key  (e.g. "TotalKills", "BestScore")
         └─ Value  (typed: Int, Fixed, Bool, String, Text, Point, Unit)
```

### SSF bank pattern (struct-based)

SSF stores the bank handle inside the per-player struct and uses a custom encode/decode layer for compact binary storage in a single bank string value:

```galaxy
// bank stored in player struct (GlobalVariables.galaxy)
struct PlayerStruct {
    bank bankfile;
    bool saveFlag_Any;
    bool saveFlag_Heavy;
    bool saveFlag_Options;
    // ...
};

// Bank_Save_RequestSave queues a debounced save per player
void Bank_Save_RequestSave(int playerID) {
    gv_PlayerStats[playerID].saveFlag_Any = true;
    TriggerExecute(Bank_Save_RequestQueueTrigger, false, false);
}

// Force-save all sections now
void Bank_Save_ForcedAll(int playerID) {
    bank b = gv_PlayerStats[playerID].bankfile;
    // encode all data into a compact string, store in one key
    BankStorageReset();
    BankStorageAddInt(gv_PlayerStats[playerID].points);
    BankStorageAddBool(gv_PlayerStats[playerID].tutorialCompleted);
    // ...
    BankValueSetFromString(b, "Data", "Core", BankStorageString);
    BankSave(b);
}
```

**SSF bank encoding pattern:** Rather than one bank key per variable, SSF concatenates all values into a single string using a custom `BankStorage*` helper set (`BankStorageAddInt`, `BankStorageAddBool`, `BankStorageRetrieveInt`, etc.) stored in `Bank.galaxy`. This avoids hitting the bank key limit and compresses save data.

---

## UserData System (Catalog-Driven Rewards)

SSF uses UserData tables defined in the editor to drive kill rewards and other game values, keeping design data out of code:

```galaxy
// Read from a UserData table by type identifier and field name
fixed baseExp     = UserDataGetFixed("KillRewards", unitType, "Exp", 1);
fixed baseBiomass = UserDataGetFixed("KillRewards", unitType, "Biomass", 1);
int enemyType     = UserDataGetInt("KillRewards", unitType, "EnemyType", 1);
int teamSizeMax   = UserDataGetInt("AcvReqSpeedruns", "P0D1", "TeamSizeMaxForSmall", 1);
```

The 4th parameter is the instance index (1-based). UserData tables are defined in the Galaxy Data editor.

---

## Spawner / Wave System

A common pattern for custom wave spawners in SC2 maps. Uses `UnitCreate` and a periodic trigger loop.

### Spawner structs (from _h.galaxy)

```galaxy
struct gs_Spawner {
    point spawnPoint;
    string unitType;
    int player;
}

struct gs_CreatedSpawner {
    unit spawner;
    point[11] movePoints;    // waypoints after spawn
    int lastIndexPoint;
    int amountOfUnits;
    string waveUnitType;
}
```

### Adding a spawner

```galaxy
int gf_AddSpawner(
    point lp_spawnPoint,
    string lp_unitType,
    string lp_waveType,
    int lp_amount,
    int lp_player
) {
    // stores in gv_spawners array, increments counter, returns index
}

void gf_AddNewWavePoint(point lp_wavePoint, int lp_spawnerIndex) {
    // appends to gv_createdSpawners[lp_spawnerIndex].movePoints
}
```

### Creating all spawners

```galaxy
void gf_CreateSpawners() {
    int lv_i = 1;
    for (; lv_i <= gv_spawnerCount ; lv_i += 1) {
        UnitCreate(1,
            gv_spawners[lv_i].unitType,
            c_unitCreateIgnorePlacement,
            gv_spawners[lv_i].player,
            gv_spawners[lv_i].spawnPoint,
            270.0
        );
        gv_createdSpawners[lv_i].spawner = UnitLastCreated();
        UnitSetState(gv_createdSpawners[lv_i].spawner,
            c_unitStateInvulnerable, true);
    }
}
```

### Enabling/disabling spawns

```galaxy
TriggerEnable(gt_SpawnUnits, true);   // start spawning
TriggerEnable(gt_SpawnUnits, false);  // pause spawning
```

---

## Jungle / Camp Respawn System

```galaxy
struct gs_UnitsToSpawn {
    string unitType;
    int count;
}

struct gs_Spawn {
    point spawnPoint;
    gs_UnitsToSpawn[5] units;
    int respawnTime;     // seconds until respawn
    int spawnTime;       // countdown (modified at runtime)
    trigger deathCallbackTrigger;
}

// Register a jungle camp
void gf_AddJungleSpawn(
    point lp_spawnPoint,
    string lp_unitType1, int lp_count1,
    int lp_respawnSeconds
) {
    // stores in gv_jungleSpawns[] array
}

// Respawn callback — attached as TriggerAddEventUnitDied
bool gf_JungleDeath_Func(bool testConds, bool runActions) {
    // record death time, start respawn timer
    Wait(gv_jungleSpawns[lv_idx].respawnTime * 1.0, c_timeGame);
    // recreate units at spawn point
    gf_Respawn(lv_idx);
    return true;
}
```

---

## Resource Rewards (Jungle Unit Kills)

```galaxy
struct gs_JG_PricePerUnit {
    string unitType;
    int minerals;
    int gas;
}

// Register a reward
void gf_AddUnitJunglePrice(
    string lp_unitType,
    int lp_minerals,
    int lp_gas
) {
    // stores in gv_junglePrices[] by index
}

// Distribute reward on kill
void gf_GiveResource(unit lp_killedUnit, int lp_killerPlayer) {
    int lv_i = 1;
    for (; lv_i <= gv_junglePricesCount ; lv_i += 1) {
        if (UnitGetType(lp_killedUnit) == gv_junglePrices[lv_i].unitType) {
            PlayerModifyPropertyInt(lp_killerPlayer, c_playerPropMinerals,
                c_playerPropOperAdd, gv_junglePrices[lv_i].minerals);
            PlayerModifyPropertyInt(lp_killerPlayer, c_playerPropVespene,
                c_playerPropOperAdd, gv_junglePrices[lv_i].gas);
            return;
        }
    }
}
```

---

## Tech Tree Upgrades

```galaxy
// Add an upgrade level to a player's tech tree
TechTreeUpgradeAddLevel(lv_player, "UpgradeName", 1);   // +1 level
TechTreeUpgradeAddLevel(lv_player, "UpgradeName", -1);  // -1 level (downgrade)

// Set level to a specific value
TechTreeUpgradeSetLevel(lv_player, "UpgradeName", 3);

// Get current level
int lv_lvl = TechTreeUpgradeGetLevel(lv_player, "UpgradeName");

// Query event for upgrade changes
TriggerAddEventUpgradeLevelChanged(myTrigger, c_playerAny);
// Inside handler:
string lv_upgrade = EventUpgradeName();
int    lv_delta   = EventUpgradeLevelDelta();

// Production restrictions
TechTreeRestrictionsEnable(lv_player, "Marine", false);   // allow
TechTreeRestrictionsEnable(lv_player, "Marine", true);    // restrict
```

---

## Melee Init (RTS Player Setup)

Initializes the default melee economy and unit placement for an AI/RTS player:

```galaxy
// Place starting units at startPoint for the given player and race
MeleeInitUnitsForPlayer(lv_player, PlayerRace(lv_player), lv_startPoint);

// Give standard starting resources
MeleeInitResourcesForPlayer(lv_player, PlayerRace(lv_player));

// Optionally set upgrade levels for the RTS player
libNtve_gf_SetUpgradeLevelForPlayer(lv_player, "UpgradeName", 1);
```

---

## Scoreboard / Per-Player Stat Tracking (SSF pattern)

SSF tracks per-player stats inside the `PlayerStruct` and reflects them through function calls:

```galaxy
// In player struct
struct PlayerStruct {
    int  kills;
    int  scientists;
    fixed acvScore;
};

// Award XP and resources on kill
void Player_KillReward(string unitType, point unitPosition) {
    fixed baseExp     = UserDataGetFixed("KillRewards", unitType, "Exp", 1);
    fixed baseBiomass = UserDataGetFixed("KillRewards", unitType, "Biomass", 1);
    int tmpInt = -1;
    while (true) {
        tmpInt = PlayerGroupNextPlayer(gv_ActivePG, tmpInt);
        if (tmpInt < 0) { break; }
        Player_AddExp(tmpInt, (baseExp * gv_PlayerStats[tmpInt].expBonusMult) + gv_PlayerStats[tmpInt].expBonusAdd);
        fixed biomass = (baseBiomass * gv_PlayerStats[tmpInt].biomassBonusMult) + gv_PlayerStats[tmpInt].biomassBonusAdd;
        PlayerModifyPropertyFixed(tmpInt, c_playerPropMinerals, c_playerPropOperAdd, biomass);
        Utility_DelayedTextTagCreate(StringToText("+") + FixedToText(biomass, 2), Color(0.00, 80.78, 0.00), unitPosition, PlayerGroupSingle(tmpInt), 1.0);
    }
}
```

---

## Death & Revive System (SSF pattern)

```galaxy
// In Player.galaxy
void Player_HeroDiesSwitch(int player) {
    gv_PlayerStats[player].lifes -= 1;
    if (gv_PlayerStats[player].lifes <= 0) {
        // trigger defeat or spectator mode
        return;
    }
    // schedule revive via UI
    ReviveUI_StartTimer(player);
}

void Player_Revive_ReleaseHero(int player, point position) {
    UnitCreate(1, UnitGetType(gv_PlayerStats[player].heroUnit),
        c_unitCreateIgnorePlacement, player, position, 270.0);
    gv_PlayerStats[player].heroUnit = UnitLastCreated();
}
```

---

## Heal Spots

```galaxy
// Find the closest healing structure for a unit (Zerg vs non-Zerg)
point gf_FindHealspot(unit lp_unit) {
    int   lv_player = UnitGetOwner(lp_unit);
    point lv_pos    = UnitGetPosition(lp_unit);

    if (IsZerg(lv_player)) {
        // Return position of allied town hall (hatchery)
        return UnitGetPosition(gv_healStructureZerg[lv_player]);
    } else {
        // Return position of nearest heal unit from the heal units group
        return UnitGetPosition(
            UnitGroupClosestToPoint(gv_healUnitsGroup, lv_pos)
        );
    }
}
```

---

## Game Attributes (Mode Detection)

```galaxy
// Read lobby options (set at game creation)
string lv_attr = GameAttributeGameValue("attrId");
// Example:
bool isHardMode = (GameAttributeGameValue("Difficulty") == "Hard");
```

---

## Game Time

```galaxy
fixed lv_elapsed  = GameGetMissionTime();   // seconds since map start
fixed lv_timeGame = TimerGetElapsed(lv_timer);

// Async delay in a trigger function
Wait(5.0, c_timeGame);     // 5 game seconds
Wait(1.0, c_timeReal);     // 1 real second
```
