TextureUnpacker
========================

# Overview
Use this unpacker2Pixi.py script to unpack **.png** sprites from the sprite atlas (providing a **.plist** or **.json** data file and a **.png** file) packed by [TexturePacker](http://www.codeandweb.com/texturepacker/) then use texturepacker to packing these **.png** file  export to json and png files for pixi

Use this particle2Pixi.py script to convert plist file to pixi json file (providing a **.plist** file) packed by [ParticleDesinger](https://www.71squared.com/particledesigner) then use pixiparticle plugin to play paritcle animation.

# Dependencies
  - [Python](http://www.python.org)
  - [Pillow (PIL fork)](https://github.com/python-pillow/Pillow) 

# Usage
	
	$ python unpacker2Pixi.py <filename> [<format>] only support plist

    $ python particle2Pixi.py <filename> [<format>] only support plist 
	
## filename

- Filename of the sprite atlas image and data file without extensions.

## format 

*optional*

- Data file format. Valid values are **plist** and **json**. If omitted **plist** format is assumed.

# Examples

### example

We have a pair of sprite atlas files named **Sprite.plist** and **Sprite.png** packed by [TexturePacker](http://www.codeandweb.com/texturepacker/).
Put them in the same folder as the **unpacker.py** script and run one of the following commands:

    python unpacker2Pixi.py dir|file plist
    
or

    python particle2Pixi.py dir|file plist

then we will see the dir named out or file if you convert a file.

lilieminglook@gmail.com

