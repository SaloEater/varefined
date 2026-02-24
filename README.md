[English version](#en)
## **РУ**
Мод добавляет озвучку ГГ голосами из EFT в зависимости от условий. В качестве кодовой базы использован мод [Voiced Actor Expanded 2.1](https://www.moddb.com/mods/stalker-anomaly/addons/voiced-actor-expanded) за авторством [LuxoSVK](https://www.moddb.com/members/luxosvk).
Использованы наработки других авторов: Ayykyu , Grokitach, Dhatri и других авторов сообщества STALKER ANOMALY (если увидели свою разработку в коде мода и я не упомянул вас - просьба написать мне в Дискорд werwolf969 и я исправлю это недоразумение. Мод рассчитан на работу со сборкой GAMMA.

**Новое по сравнению с Voiced Actor Expanded 2.1:**
Все файлы озвучки были нормализованы по уровню громкости в соответствии со стандартами, чтобы не вызывать дискомфорта при прослушивании.  Больше никаких резких выкриков выше громкости игры. 
Озвучка звуков при надетой маске/шлеме полностью переделана, чтобы передать эффект слышимости звуков изнутри маски, а не как нас слышал бы собеседник. Добавлены звуки при надетом маске/шлеме для всех файлов озвучки для обоих языков озвучки.
Изменена структура мода, изменения функций напарников вынесены за пределы axr_companions для лучшей совместимости.
Нативно поддерживается озвучка Doom like Weapons Inspections и BHS, меню напарников, BHSRO поддерживается через патч совместимости.
Добавлено MCM меню (VARefined) для тонкой настройки мода, возможности настройки:
- Регулировка громкости озвучки
- Выбор языка озвучки критериям: по-умолчанию для GAMMA (английская для ISG и Наемников, русская для всех остальных), только русская, только английская.
- Включение/выключение озвучки убийств.
- Включение/выключение озвучки клина оружия (при наличии WPO автоматически отключит озвучку клина в нем для избежания дублирования).
- Включение/выключение озвучки при перезарядке оружия.
- Включение/выключение озвучки при бросках гранат.
- Включение/выключение озвучки команд напарникам при наличии напарников.
- Включение/выключение озвучки боли ГГ из этого мода. Отключение опции поможет в случае, если вам кажется что персонаж издает слишком часто звуки при потере здоровья с включенным BHS/BHSRO.

- Включение/выключение "приглушенной" озвучки при надетой маске/шлеме.
- Клавиша ситуативных комментариев ГГ.
- Клавиша случайных выкриков ГГ.

Изменены веса для вероятности озвучки убийств, теперь они будут происходить реже.
Вся озвучка учитывает условия ГГ:
- ГГ один/в скваде, 
- ГГ в бою недавно/среднее время/длительное время,
- сквад близко/на средней дистанции/ далеко от ГГ,
- ГГ здоров/ранен/сильно ранен,
- уровень жажды/сонливости/пси здоровья/выносливости.

## **EN**
The mod adds Actor voice lines with voices from EFT, depending on the conditions. The mod [Voiced Actor Expanded 2.1](https://www.moddb.com/mods/stalker-anomaly/addons/voiced-actor-expanded) is used as the codebase authored by [LuxoSVK](https://www.moddb.com/members/luxosvk).
Other authors developments were used: Ayykyu, Grokitach, Dhatri and other authors of the STALKER ANOMALY community (if you saw your development in the mod code and I didn't mention you, please write to me in Discord werwolf969 and I will correct this misunderstanding. The mod made with GAMMA modpack in mind.

**New compared to Voiced Actor Expanded 2.1:**
All voice files have been normalized by loudness level in accordance with the standards, so as not to cause any discomfort when listening. No more harsh shouting above the game volume. 
The sounds when wearing a mask / helmet has been completely redesigned to convey the effect of hearing sounds from inside the mask, and not as the interlocutor would hear us. Added sounds when wearing a mask/helmet for all voice files for both voiced languages.
The mod structure has been changed, and changes to partner functions have been moved beyond axr_companions for better compatibility.
Natively supported voice acting of Doom like Weapons Inspections and BHS, companions menu, BHSRO is supported through the compatibility patch.
Added MCM menu (VARefined) for fine-tuning the mod, customization options:
- Adjust the voice output volume
- Select the voice language.: by default for GAMMA (English for ISG and Mercenaries, Russian for everyone else), Russian only, English only.
- Enable / disable voice-over of kills.
- Enable / disable weapon jam voiceover (if available, inside WPO will be automatically disabled the jam voiceover to avoid duplication).
- Enable / disable voice lines when reloading weapons.
- Enable / disable voice lines when throwing grenades.
- Enable / disable voice lines for companion commands if there are companions.
- Enable / disable voice lines for Actor in pain from this mod. Disabling this option will help if you think that the actor makes too many sounds when losing health with BHS/BHSRO enabled.

- Enable / disable "muffled" sounds when wearing a mask / helmet.
- Situational comments key voice lines.
- Random Actor shouting key voice lines.

Changed the weights for the probability of playing voice lines for kills, now they will occur less frequently.
All voice lines takes into account Actor conditions:
- actor alone/in squad, 
- actor in combat recently/average time/long time,
- squad close/medium distance/ far from actor,
- actor is healthy/injured/badly injured,
- thirst/sleepiness/psy health/stamina level of actor.

Implemented reactions:
<voice lines start here>

| Parent folder | Folder | Description |
|---|---|---|
|  | buttoncomments | Character comments about his wellbeing |
| buttoncomments | Bleed | Comment when character is bleeding out and squadmates can hear you or far from you |
| buttoncomments | Bleed_SquadNear | Comment when character is bleeding out and squadmates near you |
| buttoncomments | Enemy | Comment when there is an aggroed enemy far from you and squadmates far from you |
| buttoncomments | Enemy_squad | Comment when there is an aggroed enemy close and squadmates near you or can	hear you |
| buttoncomments | EnemyFar_squad | Comment when there is an aggroed enemy far from you and squadmates near you or can	hear you |
| buttoncomments | Hurt | Comment when character has low health and squadmates can hear you or far from you |
| buttoncomments | Hurt_SquadNear | Comment when character has low health and squadmates near you |
| buttoncomments | HurtBad | Comment when character has very low health and squadmates can hear you or far from you |
| buttoncomments | HurtBad_SquadNear | Comment when character has very low health and squadmates near you |
| buttoncomments | Mumble | Comment when character is not hurt enough and squadmates can hear	you or far from you |
| buttoncomments | Mumble_SquadNear | Comment when character is not hurt enough and squadmates near you |
| buttoncomments | Tired | Comment when character has low stamina and squadmates can hear you or far from you |
| buttoncomments | Tired_SquadNear | Comment when character has low stamina and squadmates near you |
|  | commands | Commands to companions |
| commands | DontLoot | When companions are ordered to don't loot |
| commands | FireAtWill | When companions are ordered to fire	at will |
| commands | Follow | When companions are ordered to follow |
| commands | IgnoreCombat | When companions are ordered to ignore combat |
| commands | IgnoreCombatButHelpMe | When companions are ordered to ignore	combat but help the player |
| commands | Loot | When companions are ordered to loot |
| commands | MoveToPoint | When companions are ordered to move to a point |
| commands | Patrol | When companions are ordered to patrol |
| commands | StayClose | When companions are ordered to stay close |
| commands | StayFar | When companions are ordered to stay far |
| commands | Stealth | When companions are ordered to stealth |
| commands | StopStealth | When companions are ordered to stop stealth |
| commands | Wait | When companions are ordered to wait |
|  | dialogs | Story IDs can be fetched from files like this https://github.com/Tosox/STALKER-Anomaly-gamedata/blob/v1.5.2/gamedata/configs/creatures/spawn_sections_bar.ltx |
| dialogs | end_regular | When player closes the dialog with non-unique NPC |
| dialogs | end_unique | When player closes the dialog with NPC that has story_id |
| dialogs | end_unique_bar_visitors_stalker_mechanic | When player closes the dialog with NPC that has story_id "bar_visitors_stalker_mechanic" |
| dialogs | start_regular | When player starts the dialog with non-unique NPC |
| dialogs | start_unique | When player starts the dialog with NPC that has story_id |
| dialogs | start_unique_bar_visitors_stalker_mechanic | When player starts the dialog with NPC that has story_id "bar_visitors_stalker_mechanic" |
|  | player | Character reactions |
| player | death | When character dies |
| player | exhausted | When character is exhausted |
| player | fear | When character has low psy health |
| player | grenade_throw | When grenade is thrown and enemy close and squadmates far |
| player | grenade_throw_squad | When grenade is thrown and enemy close and squadmates near or can hear you<br>When grenade is thrown and enemy far and squadmates near or can hear you |
| player | gun_jam | When gun jams and enemy is far or there is no enemy |
| player | gun_jam_alone | When enemy close and gun jams and squadmates are far<br>When combat intensity is medium and enemy is far and gun jams |
| player | gun_jam_squad | When enemy close and gun jams and squadmates near or can hear you |
| player | hit_by_burn | After some time after character was hit by damage with burn type |
| player | hit_by_chemical_burn | After some time after character was hit by damage with chemical burn type |
| player | hit_by_explosion | After some time after character was hit by damage with explosion type |
| player | hit_by_fire_wound | After some time after character was hit by damage with fire wound type |
| player | hit_by_light_burn | After some time after character was hit by damage with light burn type |
| player | hit_by_shock | After some time after character was hit by damage with shock type |
| player | hit_by_strike | After some time after character was hit by damage with strike type |
| player | hit_by_wound | After some time after character was hit by damage with wound type |
| player | hunger | Player voice (Russian) — hunger |
| player | hurt | When character is hungry |
| player | hurt_bad | When character has very low health |
| player | kill_comment_common_squad | While combat intensity is medium and when character kills anything far and squadmates near you |
| player | kill_comment_common_state1 | While combat intensity is low and when character kills anything far |
| player | kill_comment_common_state2 | While combat intensity is medium and when character kills anything far and squadmates can hear you or far from you |
| player | kill_comment_common_state3 | While combat intensity is high and when character kills anything far and squadmates are far |
| player | kill_comment_mutant_squad | While combat intensity is medium and when character kills a mutant far and squadmates near you |
| player | kill_comment_mutant_state1 | While combat intensity is low and when character kills a mutant far |
| player | kill_comment_mutant_state2 | While combat intensity is medium and when character kills a mutant far and squadmates can hear you or far from you |
| player | kill_comment_mutant_state3 | While combat intensity is high and when character kills a mutant far and squadmates are far |
| player | kill_comment_stalker_squad | While combat intensity is medium and when character kills an npc far and squadmates near you |
| player | kill_comment_stalker_state1 | While combat intensity is low and when character kills an npc far |
| player | kill_comment_stalker_state2 | While combat intensity is medium and when character kills an npc far and squadmates can hear you or far from you |
| player | kill_comment_stalker_state3 | While combat intensity is high and when character kills an npc far and squadmates are far |
| player | kill_confirm_common_squad | While combat intensity is low and when character kills anything close and squadmates near or can hear you<br>While combat intensity is high and when character kills anything far and squadmates near or can hear you |
| player | kill_confirm_common_state1 | While combat intensity is low and when character kills anything close and squadmates are far from you |
| player | kill_confirm_common_state2 | While combat intensity is medium and when character kills anything close |
| player | kill_confirm_common_state3 | While combat intensity is high and when character kills anything close |
| player | kill_confirm_mutant_squad | While combat intensity is low and when character kills a mutant close and squadmates near or can hear you<br>While combat intensity is high and when character kills a mutant far and squadmates near or can hear you |
| player | kill_confirm_mutant_state1 | While combat intensity is low and when character kills a mutant close and squadmates are far from you |
| player | kill_confirm_mutant_state2 | While combat intensity is medium and when character kills a mutant close |
| player | kill_confirm_mutant_state3 | While combat intensity is high and when character kills a mutant close |
| player | kill_confirm_stalker_squad | While combat intensity is low and when character kills an npc close and squadmates near or can hear you<br>While combat intensity is high and when character kills an npc far and squadmates near or can hear you |
| player | kill_confirm_stalker_state1 | While combat intensity is low and when character kills an npc close and squadmates are far from you |
| player | kill_confirm_stalker_state2 | While combat intensity is medium and when character kills an npc close |
| player | kill_confirm_stalker_state3 | While combat intensity is high and when character kills an npc close |
| player | pain | When character receives a hit |
| player | pain_bad | When character receives a hit and health	is low |
| player | reloading | When character is reloading and enemy close |
| player | sanity | When character has very low psy health |
| player | sleepiness | When character	is sleepy |
| player | thirst | When character is thirsty |
|  | random_shouts | Random shouts |
| random_shouts | random | Just random shouts |
|  | squad | Reactions to squad changes |
| squad | squadmate_died | When squadmate dies |
| squad | squadmate_hit | When squadmate receives damage |
| squad | squadmate_joined | When new squadmate joins |
| squad | squadmate_left | When squadmate left |
