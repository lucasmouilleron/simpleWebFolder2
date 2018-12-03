# SimpleWebFolder

## Features
- List files and folders
- Nice layout
- Password protection: 
    - drop a `.password` file containing the desired password in folders (and subfolders) you want to protect
    - drop a `.nopassword` file in folders (and subfolders) you want to deprotect (in case of protected parent)
- Listing protection: drop a `.nolist` file in folders you want to forbid the listing of
- Show protection: drop a `.noshow` file in folders you don't want to appear in their parents
- Download folder as a zip
- `README.md` files in folders are interpreted and displayed on top
- Shares: expiration, path obfuscation, tracking
- Tracking: optional tracking

## Install
- Pytohn 3
- `pip install -r _sf/requirements.txt`
- Drop `_sf` folder in the root folder you want to expose 

## Customisation
- Edit `_sf/config.json`
- Edit `_sf/assets/style.css`
    
## TODO
- Clean shares
- Download limit