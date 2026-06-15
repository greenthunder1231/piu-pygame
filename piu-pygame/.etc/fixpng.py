import os
from pathlib import Path
from PIL import Image

def fix_png_profiles(folder_path):
    # Track metrics
    fixed_count = 0
    L = []
    
    # Loop through all files in the directory
    for root, _, files in os.walk(folder_path):
        L.append((root, files))
    
    print('This operation will try to fix:')
    M = []
    for i in L:
        for j in i[1]:
            if str(j).endswith('.png'):
                M.append(j)
    
    print(*M, sep='\n')
    if not input('Continue? (y/n) ').lower() == 'y':
        return False
    
    for root, files in L:
        for file in files:
            if file.lower().endswith('.png'):
                file_path = os.path.join(root, file)
                try:
                    with Image.open(file_path) as img:
                        # Extract the metadata dictionary
                        info = img.info
                        
                        # Check if the problematic profile exists
                        if 'icc_profile' in info:
                            # Pop the bad profile out of the dictionary
                            info.pop('icc_profile', None)
                            
                            # Save back without the profile, keeping other metadata
                            img.save(file_path, "PNG", **info)
                            fixed_count += 1
                            print(f"Fixed: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    
    print(f"\nTask complete. Fixed {fixed_count} PNG files.")
    return True

# Change this path to your actual folder
fix_png_profiles(Path(__file__).parent)