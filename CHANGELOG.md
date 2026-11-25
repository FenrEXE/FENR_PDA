# Changelog

All notable changes to **Fenrir Industries PDA**, from v8.1 onward.

---

## v8.8 — Backend hardening and performance

### Security
- **Map names come from the server.** Markers are saved, synced and shown on the compass under the server's own map name; the client's map name is ignored, so a modified client can no longer create unlimited marker sets. Marker coordinates outside the map are dropped.
- **Contact online status** is checked against the logged-in player's stored contacts only. Clients can no longer ask about arbitrary Steam64 IDs.
- **Battery drain is decided by the server.** A powered PDA in hands drains at the "open" rate whatever the client reports; the client report can only add to it (map view). Note: holding a powered PDA in hands with the screen closed now drains too.
- **Request limits** on every PDA request (shared read and write limits, plus dedicated limits for admin search and broadcasts). Normal use never reaches them.
- **Admin search and player list** need the admin's own logged-in PDA, like the rest of the admin panel.
- Adding a contact by name needs a logged-in PDA.
- Direct messages only go to player IDs.

### Fixed
- **Group notifications** used display names to spot your own messages, so two players with the same name missed each other's toasts. The server now marks own messages by player ID.
- Rewriting or wiping an **Intel Drive** left its admin-written intel file in `IntelFiles.json` forever.
- A rejected **bounty** claimer could re-claim straight away and spam the poster. The rejected player can no longer claim that bounty.
- "No bounty on yourself" also checks the player behind the name, so renaming no longer gets around it.
- Completed bounties and closed listings no longer count toward the board limits (300 / 500); the oldest one makes room.
- Finding a player by name picks the most recently seen player with that name.

### Performance
- Player lookups use the identity's player directly instead of scanning every player.
- Live traffic, the network status counter, server bounty notices and the admin player list use the session map instead of scanning inventories. Network status used to scan every player's inventory on every request.
- The access check is computed once per request instead of up to three times.
- Admin message search keeps its results for a minute, so paging does not re-read the log.
- The log file registry uses a lookup table (it was scanned on every log line).
- Groups and group histories are saved every 30 s and when the server stops, instead of on every message and change. Group lookups use a table.
- VPP admin checks are cached for a minute.
- Per-player request state is cleared when a player disconnects.

### Removed
- **Developer test accounts** (`PDA_TEST_001`–`003`) and `TestAccountsEnabled`. Stored test contacts and group members are dropped on load.
- Duplicate online-status and test-account requests when the PDA opens.

### Changed
- Trade and bounty boards share one helper for text cleanup, IDs and paging.
- Server settings are read through one accessor.

> **Server owners:** nothing to migrate. `TestAccountsEnabled` disappears from `FenrirIndustriesPDA.json` on the next start. Clients and server must both run v8.8 (the group message format changed).

---

## v8.7 — Flash Drive removed

### Removed
- The plain **Flash Drive** item (`FENR_PDA_FlashDrive`) and its slot on the PDA. It is replaced by the Intel and Encrypted drives.
- The PDA now takes a 9V battery, an Intel Drive and an Encrypted Drive.

### Changed
- The Intel and Encrypted drives inherit from a new hidden base class, `FENR_PDA_DriveBase`, instead of the Flash Drive. Their model, damage textures, size and weight are unchanged.

> **Server owners:** remove `FENR_PDA_FlashDrive` from your `types.xml`. Flash drives already in the world or in storage are deleted on the next restart, because the item no longer exists. Intel and Encrypted drives are not affected.

---

## v8.6 — New mod folder and prefix

### Changed
- **PBO prefix is now `FENR_PDA\PDA`** (was `PDA`). The mod lives at `P:\FENR_PDA\PDA` on the work drive.
- Every asset path moved to `FENR_PDA\PDA\...`: models, damage materials, sounds, script modules and keybinds in `config.cpp`, all layouts, and every texture and layout path in the scripts.
- **Materials** (`data\*.rvmat`) are now plain-text configs with the new texture paths; pboProject binarizes them when packing.
- **Models** (`pda.p3d`, `flashdrive.p3d`) were re-pathed in place to `fenr_pda\pda\data\...`. Geometry and everything else in them is unchanged (verified byte for byte); the originals are kept in `tools/model_src_original`.
- Repository layout: the GitHub README, this changelog, the server guide and the build tools now sit beside the mod folder instead of inside it, so only `PDA\` is packed.

### Fixed
- The MINIMAL, BEZEL and SLIM compass styles still drew triangles instead of the new marker dots.
- The marker preview map in the Drives browser drew plain squares; it now uses the map pin icon.

### Removed
- Unused textures: `ic_file`, `ic_network`, `ic_self`, `ic_sos`, `ic_mark`, `cmp_tri`.
- Design notes from v3–v7 and other outdated documents and preview scripts.

> **Unchanged:** server data (`$profile:\PDA\...`) and player settings keep their paths. Nothing needs migrating.

---

## v8.5.1 — Compass marker dots

### Changed
- Compass markers are **amber dots on the strip itself**: in the middle of the bar for CLASSIC, TACTICAL and BEZEL, on the tick line for MINIMAL, SLIM and ARC, and around the dial for RADAR.
- The marker you are facing gets a larger dot. Names and distances stay in the row under the compass, closer to the strip.
- S.O.S beacons keep their own row under the compass.

---

## v8.5 — Sound muting

### Added
- **MUTE / UNMUTE** in every direct conversation, the Global channel and every group chat. A muted chat still pops up and counts unread messages; it just makes no sound. Muted chats show `MUTED` in the inbox and group list.
- **SYSTEM › SOUNDS** tab:
  - **CHAT SOUNDS** on/off to silence all chat traffic at once.
  - Per-type switches: direct messages, open channels (Global, Buy/Sell), group channels, announcements, bounty board, S.O.S alarm.
  - **MUTED CHATS** list with *Unmute selected* and *Unmute all*.
- The S.O.S alarm has its own switch and is never silenced by CHAT SOUNDS.

Sound settings are personal and saved on each player's computer, like the theme and compass. Read-only viewers can use them too.

---

## v8.4 — Map and sidebar (v8.4 – v8.4.2)

### Added
- The map **centres on you every time it opens** (at a close zoom the first time, afterwards keeping your zoom).
- Real map icons: amber **pins** with names for markers (the selected one highlighted), red **beacons** for S.O.S pings, and a green **arrow** for you that turns with your view (16 headings). These are native map marks using `.paa` icons (`map_pin`, `map_sos`, `map_self_00–15`).

### Changed
- The **sidebar is grouped**: COMMS (Announcements, Messages, Groups, Contacts), FIELD (Map, Drives), MARKET (Trade, Bounties), DEVICE (System, Admin). Disabled boards and the admin entry still drop out, and an empty section hides its heading.
- The GRID / ELEV readout moved into the map's title row.

### Fixed
- Map markers drew as plain squares (map marks can't use `.edds` icons).
- Anything layered over the map widget was hidden under it, including the GRID readout.
- Compass images (marker pins, beacons, radar dial, carets, fade band) did not draw; they are positioned as screen fractions again. A missing compass texture is now reported in the script log.

---

## v8.3 — Server branding

### Added
- Replace the PDA's name, tagline and logo from the server config, on the header and on the login screen:
  - `BrandName`, `BrandTagline`: shown as live text (long names shrink to fit).
  - `BrandLogo`: your own image, `""` for the built-in wolf, `"none"` for no logo.
  - `BrandLogoTinted`: colour the logo with each player's theme, or keep its own colours.
  - `BrandBanner`: one image replacing logo, name and tagline together.
  - `BrandNetwork`: the source label on pop-ups (`FENRIR SECURE NETWORK`).
- Branding is sent to players when they join and whenever a PDA is opened.

### Changed
- The wolf is its own texture (`brand_logo`); `brand` holds only the lettering. The default look is unchanged.

---

## v8.2 — Compass styles and screen bezel (v8.2 – v8.2.3)

### Added
- **SYSTEM › COMPASS › STYLE** with 7 looks:

  | Style | Look |
  |---|---|
  | **Classic** | The original boxed strip |
  | **Tactical** *(default)* | Open tape fading at both ends, 5° ticks, boxed heading, amber tag on the focused marker |
  | **Minimal** | No background; outlined letters and ticks float over the world |
  | **Bezel** | Framed instrument with corner brackets, heading on the left, map grid on the right |
  | **Arc** | Curved tape; ticks and letters shrink and drop away at the edges |
  | **Radar** | Round dial in the corner with a player arrow and markers all around you |
  | **Slim** | One thin line with small letters |

- Every style follows the theme or a custom hue, plus the size, opacity, position and marker / distance / bearing-number switches.
- Overlapping distance labels are hidden; the marker you face always shows its name and distance.

### Changed
- **Reworked frame art** (`pdaframe.edds`): the green glass rim and uneven bevel are replaced by one clean rounded screen opening with a machined lip.
- The screen sits in a **rounded, theme-coloured bezel** of exactly the same shape, with a thin rim line in the theme colour.
- The display is centred in the opening, 16 px from every edge.

---

## v8.1.3 — Fixes

### Fixed
- **Removed contacts came back.** Removing a test account now sticks, and removing a real contact also removes copies stored under the same player's older IDs. A removed player who messages you again shows up again, like a new number texting you.
- **Compass markers** use outlined pins and beacons readable on any background. The marker you face shows its full name and distance; names are no longer clipped.
- **Scrollbars can be dragged.** Grab the thumb, or click the bar to jump. This works on every list and chat.

### Added
- **Rename map markers:** select a marker, type the new name and press RENAME.

---

## v8.1.2 — Single-use Intel Drives

### Changed
- **READ INTEL** warns that a drive can only be decrypted once. After DECRYPT, a 10-second progress bar runs; ABORT before it finishes costs nothing.
- **Closing the decrypted file burns the drive out for good.** A drive decrypted but never closed (PDA closed, player disconnected) burns out the next time anyone looks at it.
- Admin-written intel works the same way and leaves the intel pool when its drive burns out.

### Added
- **Drive log:** every written drive, whether an Encrypted Drive (including clones of someone else's PDA) or admin intel, is recorded with its full contents in `$profile:\PDA\Logs\Drives_<day>.jsonl` and kept for `DriveLogsDays` (7).

---

## v8.1.1 — Intel Drive expiry

### Changed
- Decoded Intel Drives ruin after a set time. *Replaced in v8.1.2 by single-use decryption.*

---

## v8.1 — PDA login and player-owned memory

### Added
- **PDA login.** A PDA does nothing until someone logs in: no compass, no pop-ups, no S.O.S. Players choose a session length of 1–4 hours (`SessionMinHours` / `SessionMaxHours`).
- A session ends when:
  - the owner logs out (SYSTEM › LOG OUT);
  - the time runs out;
  - the owner logs in on another PDA (one session per player);
  - someone else logs in on that PDA;
  - the server restarts (sessions are never saved).
- **Disconnecting doesn't end a session:** a logged-in PDA left on a body or in a stash stays readable until it times out.
- **Read-only access.** Anyone holding a PDA logged in as someone else can read its messages, groups, markers, compass and live traffic, but cannot send or change anything. They can clone the owner's data onto an Encrypted Drive, or log in as themselves to take the PDA over.
- **ADMIN › INTEL** tab for writing custom intel to the Intel Drive in the admin's PDA, with a live preview, 1000 characters and `|` for a line break.
- **ADMIN › BROADCAST** has a large preview that shows the whole message while typing.

### Changed
- **Memory follows the player, not the PDA.** Contacts, markers, read marks, S.O.S settings and message history belong to the player (Steam64). Log in on any PDA and everything is there.
- Live messages go to whoever is using the recipient's logged-in PDA; otherwise they wait until the recipient logs in.
- **ANNOUNCEMENTS** is the top sidebar entry.
- `TradeEnabled` / `BountyEnabled` also hide their sidebar entries; `SosEnabled` hides the SOS button.
- Retention: Encrypted Drive data lasts **7 days** (`EncryptedDriveDays`) and message logs **14 days** (`MessageLogsDays`). Both are applied once to existing configs on update.
- A corrupted Encrypted Drive must be wiped before it can be written again.

### Migration
- v8.0 per-PDA memory (`Devices\`) moves to the player who used each PDA last (`Accounts\`) on first start.
