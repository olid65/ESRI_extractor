import c4d, os, sys

sys.path.append(os.path.dirname(__file__))

import od_esri_image_extractor as img_extractor
import od_esri_terrain_extractor as terrain_extractor

ID_IMAGE_EXTRACTOR = 1059238
ID_TERRAIN_EXTRACTOR = 1059237    

class ImageExtractor(c4d.plugins.CommandData):
    def Execute(self, doc) :
        img_extractor.main()
        return True

class TerrainExtractor(c4d.plugins.CommandData):
    def Execute(self, doc) :
        terrain_extractor.main()
        return True

def icone(nom) :
    bmp = c4d.bitmaps.BaseBitmap()
    dir, file = os.path.split(__file__)
    fn = os.path.join(dir, "res", nom)
    bmp.InitWith(fn)
    return bmp
    
if __name__=='__main__':
    c4d.plugins.RegisterCommandPlugin(id=ID_IMAGE_EXTRACTOR, str="#$00"+"ESRI extracteur d'images",
                                      info=0, help="", dat=ImageExtractor(),
                                      icon=icone("esri_import_image.png"))
    c4d.plugins.RegisterCommandPlugin(id=ID_TERRAIN_EXTRACTOR, str="#$01"+"ESRI extracteur de terrain",
                                      info=0, help="", dat=TerrainExtractor(),
                                      icon=icone("esri_import_terrain.png"))