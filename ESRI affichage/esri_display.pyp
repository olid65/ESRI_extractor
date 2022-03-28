import c4d, os, sys
import urllib.request
#from c4d import plugins, bitmaps, gui, documents, Vector
from c4d.plugins import GeLoadString as txt
from datetime import datetime

__version__ = 1.0
__date__    = "26/09/2021"


ID_ORTHO = 1059233
ID_TOPOMAP = 1059234
ID_STREETMAP = 1059235

DIC_WEB_SERVICES = {   'ortho':'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/',
                        'topomap': 'http://server.arcgisonline.com/arcgis/rest/services/World_Topo_Map/MapServer/',
                        'streetmap': 'http://server.arcgisonline.com/arcgis/rest/services/World_Street_Map/MapServer/',
                    }

CONTAINER_ORIGIN =1026473

NOT_SAVED_TXT = "Le document doit être enregistré pour pouvoir copier les textures dans le dossier tex, vous pourrez le faire à la prochaine étape\nVoulez-vous continuer ?"
DOC_NOT_IN_METERS_TXT = "Les unités du document ne sont pas en mètres, si vous continuez les unités seront modifiées.\nVoulez-vous continuer ?"


O_DEFAUT = c4d.Vector(2500000.00,0.0,1120000.00)


#ch.swisstopo.landeskarte-farbe-10

#ch.swisstopo.images-swissimage

#exemples de requetes:

#http://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=ch.swisstopo.landeskarte-farbe-10&STYLES=default&CRS=EPSG:2056&BBOX=2569660.0,1228270.0,2578660.0,1233270.0&WIDTH=900&HEIGHT=500&FORMAT=image/png
#http://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=ch.swisstopo.images-swissimage&STYLES=default&CRS=EPSG:2056&BBOX=2569660.0,1228270.0,2578660.0,1233270.0&WIDTH=900&HEIGHT=500&FORMAT=image/png

FORMAT = 'png'

NOM_DOSSIER_IMG = 'tex/__back_image'

def empriseVueHaut(bd,origine):

    dimension = bd.GetFrame()
    largeur = dimension["cr"]-dimension["cl"]
    hauteur = dimension["cb"]-dimension["ct"]

    mini =  bd.SW(c4d.Vector(0,hauteur,0)) + origine
    maxi = bd.SW(c4d.Vector(largeur,0,0)) + origine

    return  mini,maxi,largeur,hauteur

def display_esri_image(service_name):
    
    #le doc doit être en mètres
    doc = c4d.documents.GetActiveDocument()

    usdata = doc[c4d.DOCUMENT_DOCUNIT]
    scale, unit = usdata.GetUnitScale()
    if  unit!= c4d.DOCUMENT_UNIT_M:
        rep = c4d.gui.QuestionDialog(DOC_NOT_IN_METERS_TXT)
        if not rep : return
        unit = c4d.DOCUMENT_UNIT_M
        usdata.SetUnitScale(scale, unit)
        doc[c4d.DOCUMENT_DOCUNIT] = usdata

    #si le document n'est pas enregistré on enregistre
    path_doc = doc.GetDocumentPath()

    while not path_doc:
        rep = c4d.gui.QuestionDialog(NOT_SAVED_TXT)
        if not rep : return
        c4d.documents.SaveDocument(doc, "", c4d.SAVEDOCUMENTFLAGS_DIALOGSALLOWED, c4d.FORMAT_C4DEXPORT)
        c4d.CallCommand(12098) # Enregistrer le projet
        path_doc = doc.GetDocumentPath()

    dossier_img = os.path.join(path_doc,NOM_DOSSIER_IMG)

    origine = doc[CONTAINER_ORIGIN]
    if not origine:
        doc[CONTAINER_ORIGIN] = O_DEFAUT
        origine = doc[CONTAINER_ORIGIN]
    bd = doc.GetActiveBaseDraw()
    camera = bd.GetSceneCamera(doc)
    if not camera[c4d.CAMERA_PROJECTION]== c4d.Ptop:
        c4d.gui.MessageDialog("""Ne fonctionne qu'avec une caméra en projection "haut" """)
        return
    
    #pour le format de la date regarder : https://docs.python.org/fr/3/library/datetime.html#strftime-strptime-behavior
    dt = datetime.now()
    suffixe_time = dt.strftime("%y%m%d_%H%M%S")
    form = 'png'
    fn = f'{service_name}_{suffixe_time}.{form}'
    fn_img = os.path.join(dossier_img,fn)
    
    if not os.path.isdir(dossier_img):
            os.makedirs(dossier_img)
    
    mini,maxi,width_img,height_img = empriseVueHaut(bd,origine)
    #print (mini.x,mini.z,maxi.x,maxi.z)
    bbox = f'{mini.x},{mini.z},{maxi.x},{maxi.z}'

    url_base = DIC_WEB_SERVICES[service_name]
    
    sr = 2056
    
    url = f"{url_base}export?bbox={bbox}&format={form}&size={width_img},{height_img}&f=image&bboxSR={sr}&imageSR={sr}"
    #url = f'http://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS={layer}&STYLES=default&CRS=EPSG:2056&BBOX={bbox}&WIDTH={width_img}&HEIGHT={height_img}&FORMAT=image/png'
    #print(url)
    
    
    
    try:
        x = urllib.request.urlopen(url)
    
        with open(fn_img,'wb') as saveFile:
            saveFile.write(x.read())
            
    except Exception as e:
        print(str(e))
        
    #on récupère l'ancienne image
    old_fn = os.path.join(dossier_img,bd[c4d.BASEDRAW_DATA_PICTURE])

    bd[c4d.BASEDRAW_DATA_PICTURE] = fn
    bd[c4d.BASEDRAW_DATA_SIZEX] = maxi.x-mini.x
    bd[c4d.BASEDRAW_DATA_SIZEY] = maxi.z-mini.z


    bd[c4d.BASEDRAW_DATA_OFFSETX] = (maxi.x+mini.x)/2 -origine.x
    bd[c4d.BASEDRAW_DATA_OFFSETY] = (maxi.z+mini.z)/2-origine.z
    #bd[c4d.BASEDRAW_DATA_SHOWPICTURE] = False

    #suppression de l'ancienne image
    #TODO : s'assurer que c'est bien une image générée NE PAS SUPPRIMER N'IMPORTE QUOI !!!
    if os.path.exists(old_fn):
        try : os.remove(old_fn)
        except : pass
    c4d.EventAdd(c4d.EVENT_FORCEREDRAW)
    

class DisplayOrtho(c4d.plugins.CommandData):
    def Execute(self, doc) :
        display_esri_image('ortho')
        return True

class DisplayTopomap(c4d.plugins.CommandData):
    def Execute(self, doc) :
        display_esri_image('topomap')
        return True
class DisplayStreetmap(c4d.plugins.CommandData):
    def Execute(self, doc) :
        display_esri_image('streetmap')
        return True

def icone(nom) :
    bmp = c4d.bitmaps.BaseBitmap()
    dir, file = os.path.split(__file__)
    fn = os.path.join(dir, "res", nom)
    bmp.InitWith(fn)
    return bmp
    
if __name__=='__main__':
    c4d.plugins.RegisterCommandPlugin(id=ID_ORTHO, str="#$00"+"ESRI orthophoto",
                                      info=0, help="", dat=DisplayOrtho(),
                                      icon=icone("esri_display_ortho.png"))
                                      
    c4d.plugins.RegisterCommandPlugin(id=ID_TOPOMAP, str="#$01"+"ESRI carte topographique",
                                      info=0, help="", dat=DisplayTopomap(),
                                      icon=icone("esri_display_topomap.png"))

    c4d.plugins.RegisterCommandPlugin(id=ID_STREETMAP, str="#$02"+"ESRI carte rues",
                                      info=0, help="", dat=DisplayStreetmap(),
                                      icon=icone("esri_display_streetmap.png"))