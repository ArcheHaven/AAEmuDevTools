Heightmap and Navmesh Viewer / Walking simulator
-------------------------------------------------

Before running, edit the "config.json" file in the "data_AAEmuGeoData_windows_x86_64" folder and add your game_pak (or unpacked folder of it) to the list of client sources.
Note that backslashes need to be escape or replaced by forward slashes in the path names.
In-App minimap is hardcoded from version 1.2 and might not reflect your actual world you are loading

Example file:

{
  "Sources": [
    "d:\\Games\\ArcheAge\\AA 1.2 - Trion - r208022 - 2014-10-14 - NoHS\\Games\\ArcheAge\\Beta\\game_pak",
    "ClientData",
    "ClientData/game_pak"
  ],
  "CameraMode": 0,
  "MainMap": "main_world",
  "MapX": 15200,
  "MapY": 13650,
  "MapZ": 300,
  "ChunkLoadRange": 2,
  "CellLoadRange": 1,
  "LoadAsyncCount": 5
}
