# SimpleWebFolder

![Screenshot](http://grabs.lucasmouilleron.com/grab%202022-02-28%20at%2011.42.40.png)

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
- Pytohn 3.10.0
- `pip install -r _sf/requirements.txt`
- Copy `_sf/assets/style.sample.css` to `_sf/assets/style.css`
- Copy `_sf/config/config.sample.json` to `_sf/config/config.json` 
- Drop `_sf` folder in the root folder you want to expose 

## Customisation
- Edit `_sf/config.json`
- Edit `_sf/assets/style.css`
    
## TODO
- Clean shares
- Better locks
- Clean locks
- Track and clean tracking periodicly to file (and not on the fly)