# Plan: boost-pickup test scene (not built yet)

Goal: a third test map where boost does **not** recharge on its own; the player refills it by driving through pickups.

## Scene
- New map `/Game/Car/Maps/CarTestBoostPickups`, made by duplicating `CarTestMoonGrav` (floor, lights, sky, ramps already there).
- Gravity: Moon by default (`Scripts/v2_moon_setup.py` with `NEW_SCENE` set and `MODE = "APPLY"` duplicates the map and applies the Moon settings). For Earth gravity instead, duplicate `CarTestTrack`.
- Make the floor larger (the Moon floor ends 300 m from the start; at 90 km/h the car drives off it in about 30 s).

## Boost rule per scene
- Add `BoostRegenEnabled` (bool, default true) to `BP_CarPawn`; the regen step in Tick only runs when it is true. All existing maps keep today's behavior.
- New game mode `BP_CarGameMode_Pickups` (child of `BP_CarGameMode_Moon`, or of `BP_CarGameMode` for Earth) that sets `BoostRegenEnabled = false` on the possessed car at BeginPlay. The pickup map uses this game mode, so no third car Blueprint is needed.
- Start the meter full (or at a set amount, e.g. 50%) so the first stretch is drivable.

## Pickup actor `BP_BoostPickup`
- Sphere trigger (~150 cm radius) plus a glowing mesh using the boost flame colors; slow spin and bob so it reads from a distance.
- On overlap with the car: add `RefillAmount` (default 0.25 of the bar) to `BoostAmount`, clamp to 1, play a short flash/burst.
- Then hide and disable collision; respawn after `RespawnTime` (default 8 s). Both values are editable per placed pickup.
- Ignore overlaps when the bar is already full (pickup stays for later).

## Placement
- A line of pickups down the main straight, a few on the approach to each ramp, and some in the air above the ramps (worth more under Moon gravity, where jumps last several seconds).
- One isolated pickup far off the path to test whether a detour is worth it.

## HUD
- Keep the current bar. Show "NO RECHARGE - COLLECT PICKUPS" under it on this map, and flash the bar when a pickup is collected.

## How it will be tested
- Same passive logger approach: boost meter stays flat when not boosting (no regen), jumps by the refill amount on each pickup, pickup respawns after the set time, other maps still recharge.
