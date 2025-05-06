from pathlib import Path
import shutil

# Root dir where you want to replace the files (old client)
root_dir = Path(
    "D:/Game Development/Projects/AAEmu/_Client Files/1.2 Clients/TestDevClient/game/worlds/main_world/cells")

# Folder containing the updated versions of the files (new client)
source_dir = Path(
    "D:/Game Development/Projects/AAEmu/_Client Files/AA 10.8.1.0 - Kakao - r651328 - 2024-04-25 - Final-EU-NA/game/worlds/main_world/cells")

# Files to replace (relative to each cell's 'client/terrain' folder)
files_to_replace = ["cover.ctc", "heightmap.dat"]

# Loop through each cell folder in the source (new client)
for source_cell_dir in source_dir.iterdir():
    if not source_cell_dir.is_dir():
        continue  # Skip files, only process folders

    # Check if the same cell exists in the target (old client)
    target_cell_dir = root_dir / source_cell_dir.name
    if not target_cell_dir.exists():
        print(f"Skipping {source_cell_dir.name} (not found in target)")
        continue

    # Process each file in the 'client/terrain' folder
    for filename in files_to_replace:
        source_file = source_cell_dir / "client" / "terrain" / filename
        target_file = target_cell_dir / "client" / "terrain" / filename

        if not source_file.exists():
            print(f"⚠️ Missing in source: {source_file}")
            continue

        if not target_file.exists():
            print(f"⚠️ Missing in target: {target_file}")
            continue

        # Ensure the target directory exists
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Replace the file
        print(f"🔄 Updating {target_file}")
        shutil.copy2(source_file, target_file)

print("✅ File replacement complete!")