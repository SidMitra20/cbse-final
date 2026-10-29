import os

def interactive_renamer():
    print("=== Airbnb Project Image Renamer ===")
    print("Files currently ending with .png in this folder:")
    png_files = [f for f in os.listdir() if f.endswith('.png')]
    print(png_files)
    print("-" * 40)
    
    while True:
        old_name = input("Enter the current filename (e.g., photo1.png or 2.png) or type 'q' to quit: ").strip()
        if old_name.lower() == 'q':
            print("Exiting renamer. Good luck with your project!")
            break
            
        if not os.path.exists(old_name):
            print(f"❌ Error: '{old_name}' does not exist in this folder. Try again.\n")
            continue
            
        house_id = input(f"What is the correct House ID for '{old_name}'? (1 to 30): ").strip()
        
        if not house_id.isdigit():
            print("❌ Error: House ID must be a valid number.\n")
            continue
            
        new_name = f"{house_id}.png"
        
        try:
            # If the target filename already exists, handle it cleanly
            if os.path.exists(new_name):
                confirm = input(f"⚠️ '{new_name}' already exists. Overwrite? (y/n): ")
                if confirm.lower() != 'y':
                    continue
                os.remove(new_name)
                
            os.rename(old_name, new_name)
            print(f"✅ Success! Renamed '{old_name}' -> '{new_name}'\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    interactive_renamer()