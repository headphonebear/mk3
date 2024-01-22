import os
import config

class Filelist:
    mk3_source = ''
    def create_filelist(self):
        mk3_tree = os.walk(self.mk3_source)
        filelist = []
        for path, directories, files in mk3_tree:
            directories.sort()
            files = sorted(files)
            for file in files:
                element = path, file
                filelist.append(element)
        print(filelist[23456])
    def Filelist():
        pass

myfilelist = Filelist()
myfilelist.mk3_source = config.mk3_source
myfilelist.create_filelist()
