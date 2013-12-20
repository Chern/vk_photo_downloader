# vk_photo_downloader

Script that helps to download full-size photos from vk

## Installation

    python setup.py install
    
## Usage
```
vk_photo_downloader.py [-h] [-u] [-a [ALBUM [ALBUM ...]]] [-p PATH]
                       owner
```

Positional arguments:

* owner &#8212; name or id of user or community

Optional arguments:

*  -h, --help &#8212; show help message and exit
*  -u &#8212; specify that owner is user
*  -a [ALBUM [ALBUM ...]], --album [ALBUM [ALBUM ...]] &#8212; specify album ids to download. if it is empty, user
albums list will be printed
*  -p PATH, --path PATH &#8212; specify path to save photos

