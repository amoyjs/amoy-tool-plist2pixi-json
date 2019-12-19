#!/usr/bin/env python
# contact:lilieminglook@gmail.com
import os
import os.path
import sys
from PIL import Image 
from xml.etree import ElementTree
import json
import shutil
import random
import gzip
import base64 
import zlib
from io import BytesIO


cacheDict = {}

def tree_to_dict(tree):
    d = {}
    for index, item in enumerate(tree):
        if item.tag == 'key':
            if tree[index + 1].tag == 'string':
                d[item.text] = tree[index + 1].text
            elif tree[index + 1].tag == 'true':
                d[item.text] = True
            elif tree[index + 1].tag == 'false':
                d[item.text] = False
            elif tree[index + 1].tag == 'integer':
                d[item.text] = int(tree[index + 1].text);
            elif tree[index + 1].tag == 'real':
                d[item.text] = float(tree[index + 1].text);
            elif tree[index + 1].tag == 'dict':
                d[item.text] = tree_to_dict(tree[index + 1])
    return d

def hex2string(hex):
    hex = hex.toString(16)
    hex = '000000'.substr(0, 6 - hex.length) + hex
    return '#'+hex

def rgb2hex(argb):
    hex = "#{:02x}{:02x}{:02x}{:02x}".format(int(argb[0]*255),int(argb[1]*255),int(argb[2]*255),int(argb[3]*255))
    return hex

def hex2rgb(hexcode):
    return tuple(map(ord,hexcode[1:].decode('hex')))

def gen_json_from_data(filename, ext):
    rootjson = {}
    pixijson = {}
    data_filename = filename + ext
    print("processing::",filename)
    if ext == '.plist':
        root = ElementTree.fromstring(open(data_filename, 'r').read())
        plist_dict = tree_to_dict(root[0])
        # print(plist_dict)
        #alpha
        pixijson["alpha"] = {"start":plist_dict["startColorAlpha"]-plist_dict["startColorVarianceAlpha"], "end":plist_dict["finishColorAlpha"]-plist_dict["finishColorVarianceAlpha"]}
        path, _ = os.path.split(filename)

        w=1.0
        h=1.0
        if(os.path.exists(path+"/"+plist_dict["textureFileName"])):
            img = Image.open(path+"/"+plist_dict["textureFileName"])
            w, h = img.size
        #scale

        pixijson["scale"] = {
            "start":plist_dict["startParticleSize"] / w,
            "end":plist_dict["finishParticleSize"] / h,
            "minimumScaleMultiplier": 1,
            'viriance':plist_dict["finishParticleSizeVariance"] / h
        }

        #color
        pixijson["color"] = {
            "start": rgb2hex([plist_dict["startColorAlpha"], plist_dict["startColorRed"], plist_dict["startColorGreen"], plist_dict["startColorBlue"]]),
            "end": rgb2hex([plist_dict["finishColorAlpha"], plist_dict["finishColorRed"], plist_dict["finishColorGreen"], plist_dict["finishColorBlue"]]),
            "viriance":rgb2hex([plist_dict["finishColorVarianceAlpha"], plist_dict["finishColorVarianceRed"], plist_dict["finishColorVarianceGreen"], plist_dict["finishColorVarianceBlue"]])
        }

        #speed
        pixijson['speed'] = {
            "start": plist_dict['speed'],
            "end": plist_dict['speed']+plist_dict['speedVariance'],
            "minimumSpeedMultiplier": 1,
            "viriance":plist_dict['speedVariance']
        }
        
        #acceleration
        pixijson["acceleration"] = {
            "x": plist_dict["gravityx"],
            #坐标系相反
            "y": 0 - plist_dict["gravityy"] 
        }
        
        #maxSpeed
        pixijson["maxSpeed"] = plist_dict['speed']+plist_dict['speedVariance']

        pixijson['startRotation'] = {
            #旋转方向不一样
            "min": 360-(plist_dict["angle"] - plist_dict["angleVariance"]),
            "max": 360-(plist_dict["angle"] + plist_dict["angleVariance"])
        }

        pixijson['lifetime'] = {
            "min": plist_dict["particleLifespan"],
            "max": plist_dict["particleLifespan"] + plist_dict["particleLifespanVariance"]
        }

        pixijson["noRotation"] = False
        if(int(plist_dict["blendFuncDestination"]) == 1):
            pixijson["blendMode"] = "add" 
        else:
            pixijson["blendMode"] = "normal" 

        pixijson["frequency"] = plist_dict["particleLifespan"] / plist_dict["maxParticles"] 
        pixijson["emitterLifetime"] = plist_dict["duration"]
        pixijson["maxParticles"] = plist_dict["maxParticles"]
        pixijson["pos"] = {
            "x": 0,
            "y": 0
        }
        
        pixijson["addAtBack"] = False

        pixijson["spawnType"] = "rect"
        pixijson["spawnRect"] = {
            "x": 0,
            "y": 0,
            "w": 2*plist_dict["sourcePositionVariancex"],
            "h": 2*plist_dict["sourcePositionVariancey"],
        }

        rootjson={'config':pixijson, "texture":plist_dict["textureFileName"]}

        path, _ = os.path.split(filename)
        imageName = plist_dict["textureFileName"]
        notExits = not os.path.exists(path+"/"+imageName)

        if(("textureImageData" in plist_dict.keys()) and plist_dict["textureImageData"] and notExits):
            print("create a textureFileName", plist_dict["textureFileName"])
            imgdata = gzip.decompress(base64.b64decode(plist_dict["textureImageData"]))
            image_data = BytesIO(imgdata)
            img = Image.open(image_data)
            img.save(path+"/"+imageName)

        cacheDict[filename] = plist_dict["textureFileName"]

    elif ext == '.json':
        # Todo
        # json_data = open(data_filename)
        # data = json.load(json_data)

        
        pixijson =  ""
    else:
        print("Wrong data format on parsing: '" + ext + "'!")
        exit(1)

    with open(filename+'.json', 'w') as json_file:
        json.dump(rootjson, json_file)



def endWith(s,*endstring):
    array = map(s.endswith,endstring)
    if True in array:
        return True
    else:
        return False


# Get the all files & directories in the specified directory (path).   
def get_file_list(path):
    current_files = os.listdir(path)
    all_files = []  
    for file_name in current_files:
        full_file_name = os.path.join(path, file_name)
        if endWith(full_file_name,'.plist'):
            full_file_name = full_file_name.replace('.plist','')
            all_files.append(full_file_name)
        if endWith(full_file_name,'.json'):
            full_file_name = full_file_name.replace('.json','')
            all_files.append(full_file_name)
        if os.path.isdir(full_file_name):
            next_level_files = get_file_list(full_file_name)
            all_files.extend(next_level_files)
    return all_files


def get_sources_file(filename):
    data_filename = filename + ext
    if os.path.exists(data_filename):
        gen_json_from_data(filename, ext)
    else:
        print("Make sure you have both " + data_filename  + " files in the same directory")

def copyFile(file0):
    if not os.path.isdir("out"):
        os.mkdir("out")
    fileName = file0+".json"
    if(os.path.exists(fileName)):
        path, fn = os.path.split(file0)
        # print("copy json::",file0+".json")
        shutil.move(file0+".json", "out/"+fn+".json")
        # print("copy::",path + "/" +cacheDict[file0])
        if(os.path.exists(path +"/"+ cacheDict[file0])):
            shutil.copy(path +"/"+ cacheDict[file0], "out/"+fn+".png")
    #    shutil.rmtree(path)

def copyJsonFile(path_or_name):
    if os.path.isdir(path_or_name):
        files = get_file_list(path_or_name)
        for file0 in files:
            copyFile(file0)
    else:
        copyFile(path_or_name)


# Use like this: python unpacker.py [Image Path or Image Name(but no suffix)] [Type:plist or json]
if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("You must pass filename as the first parameter!")
        exit(1)
    # filename = sys.argv[1]
    path_or_name = sys.argv[1]
    ext = '.plist'
    if len(sys.argv) < 3:
        print("No data format passed, assuming .plist")
    elif sys.argv[2] == 'plist':
        print(".plist data format passed")
    elif sys.argv[2] == 'json':
        ext = '.json'
        print(".json data format passed")
    else:
        print("Wrong data format passed '" + sys.argv[2] + "'!")
        exit(1)

    if(os.path.exists("out")):
        shutil.rmtree("out")

    # supports multiple file conversions
    if os.path.isdir(path_or_name):
        files = get_file_list(path_or_name)
        for file0 in files:
            get_sources_file(file0)
    else:
        get_sources_file(path_or_name)
    #copy all exported json's files and png's files
    copyJsonFile(path_or_name)
