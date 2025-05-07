import os
import requests
import zipfile
import io

def download_fonts():
    """
    Download thin fonts and save them to the fonts directory.
    """
    fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)
    
    # URLs for thin fonts
    font_urls = [
        # Roboto Thin
        ("https://fonts.google.com/download?family=Roboto", "Roboto-Thin.ttf"),
        # Open Sans Light
        ("https://fonts.google.com/download?family=Open+Sans", "OpenSans-Light.ttf"),
        # Lato Thin
        ("https://fonts.google.com/download?family=Lato", "Lato-Thin.ttf")
    ]
    
    for url, font_name in font_urls:
        try:
            print(f"Attempting to download {font_name}...")
            response = requests.get(url)
            if response.status_code == 200:
                try:
                    # Try to extract font from zip file
                    z = zipfile.ZipFile(io.BytesIO(response.content))
                    font_files = [f for f in z.namelist() if font_name.lower() in f.lower()]
                    
                    if font_files:
                        for font_file in font_files:
                            z.extract(font_file, fonts_dir)
                            print(f"Successfully extracted {font_file}")
                    else:
                        print(f"Font {font_name} not found in zip file")
                except zipfile.BadZipFile:
                    # If it's not a zip file, save directly
                    font_path = os.path.join(fonts_dir, font_name)
                    with open(font_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded {font_name}")
            else:
                print(f"Failed to download {font_name}: {response.status_code}")
        except Exception as e:
            print(f"Error downloading {font_name}: {str(e)}")

if __name__ == "__main__":
    download_fonts()