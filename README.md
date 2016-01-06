# vk_photo_downloader

Script that helps to download full-size photos from vk

## Installation

    python setup.py install
    
## Usage
```
vk_photo_downloader.py [-h] [-u] [-a [ALBUMS [ALBUMS ...]]]
                       [--download-all] [-p PATH]
                       owner
```

Positional arguments:

* owner &#8212; name or id of user or community

Optional arguments:

*  -h, --help &#8212; show help message and exit
*  -u &#8212; specify that owner is user
*  -a [ALBUMS [ALBUMS ...]], --albums [ALBUMS [ALBUMS ...]] &#8212; specify album ids to download. if it is empty and
`--download-all` is not provided, user albums list will be printed
*  --download-all &#8212; download all available photos
*  -p PATH, --path PATH &#8212; specify path to save photos
