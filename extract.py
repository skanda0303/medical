import zipfile

zip_path = r"C:\Users\night\OneDrive\Desktop\postgre\DB_Dataset.zip"
extract_to = r"C:\Users\night\OneDrive\Desktop\postgre\DB_Dataset"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

print("Extracted!")
