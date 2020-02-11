# -*- coding: utf-8 -*-

#import sys
#sys.path.append('../src/')
import unittest
from src.Modelo import Modelo
from src.Lexers import PosPersonajes as pp
from src.LecturaFicheros import LecturaEpub as lec
from src.Guiones import CrearDiccionario as cdguion
from src.PredictorEtniaSexo import EthneaGenni as eg

#print(sys.path)
m = Modelo.Modelo()
ethnea = eg.EthneaGenni()
poslex = pp.PosPersonajes(m)

class TestUnitarios(unittest.TestCase):
    '''
    Clase para realizar test unitarios
    '''
    
    def __init__(self,*args, **kwargs):
        super(TestUnitarios, self).__init__(*args, **kwargs)
        m.obtTextoEpub(r"E:\Users\Jorge\Desktop\Universidad\TFG\Versiones\NetExtractor\tst\epubPruebas.epub")
        m.vaciarDiccionario()
        m.crearDict()
    
    '''
    Se pone el número del test indicando el orden en el que se ejecutan debido a ser la solución
    más sencilla que se ha encontrado al problema que consiste en que los test
    se ejecutan en orden alfabético y no en el orden en el que están definidos
    '''
    
    def test_01_LecturaEpub(self):
        res = {'Pedro Pérez':['Pedro Pérez'], 'Josema':['Josema'], 'Pedro':['Pedro'], 'Pedro Rodríguez':['Pedro Rodríguez'],'Pérez':['Pérez'] ,'Ana':['Ana']}
        self.comprobarPersonajes(res)

    def test_02_AnadirPersonaje(self):
        m.anadirPersonaje('Andrea','Andrea')
        res = {'Pedro Pérez':['Pedro Pérez'], 'Josema':['Josema'], 'Pedro':['Pedro'], 'Pedro Rodríguez':['Pedro Rodríguez'],'Pérez':['Pérez'] ,'Ana':['Ana'], 'Andrea':['Andrea']}
        self.comprobarPersonajes(res)
        m.anadirPersonaje('Andres','Andre')
        res = {'Pedro Pérez':['Pedro Pérez'], 'Josema':['Josema'], 'Pedro':['Pedro'], 'Pedro Rodríguez':['Pedro Rodríguez'],'Pérez':['Pérez'] ,'Ana':['Ana'], 'Andrea':['Andrea'], 'Andres':['Andre']}
        self.comprobarPersonajes(res)

    def test_03_EliminarPersonaje(self):
        m.eliminarListPersonajes(['Josema', 'Andres'])
        res = {'Pedro Pérez':['Pedro Pérez'], 'Pedro':['Pedro'], 'Pedro Rodríguez':['Pedro Rodríguez'],'Pérez':['Pérez'] ,'Ana':['Ana'], 'Andrea':['Andrea']}
        self.comprobarPersonajes(res)

    def test_04_JuntarPersonajes(self):
        m.juntarListPersonajes(['Pedro Rodríguez','Pedro'])
        res = {'Pedro Pérez':['Pedro Pérez'], 'Pedro Rodríguez':['Pedro Rodríguez', 'Pedro'],'Pérez':['Pérez'] ,'Ana':['Ana'], 'Andrea':['Andrea']}
        self.comprobarPersonajes(res)

    def test_05_anadirReferenciaAPersonaje(self):
        m.anadirReferenciaPersonaje('Pedro Pérez','peperez')
        res = {'Pedro Pérez':['Pedro Pérez','peperez'], 'Pedro Rodríguez':['Pedro Rodríguez', 'Pedro'],'Pérez':['Pérez'] ,'Ana':['Ana'], 'Andrea':['Andrea']}
        self.comprobarPersonajes(res)

    def test_06_eliminarReferenciaAPersonaje(self):
        m.eliminarListRefs([['Ana','Ana']])
        res = {'Pedro Pérez':['Pedro Pérez','peperez'], 'Pedro Rodríguez':['Pedro Rodríguez', 'Pedro'],'Pérez':['Pérez'], 'Andrea':['Andrea']}
        self.comprobarPersonajes(res)
        m.eliminarListRefs([['Pedro Pérez','peperez']])
        res = {'Pedro Pérez':['Pedro Pérez'], 'Pedro Rodríguez':['Pedro Rodríguez', 'Pedro'],'Pérez':['Pérez'], 'Andrea':['Andrea']}
        self.comprobarPersonajes(res)

    def test_07_AnadirJuntarPersonajes(self):
        m.anadirPersonaje('María','María')
        res = {'Pedro Pérez':['Pedro Pérez'], 'Pedro Rodríguez':['Pedro Rodríguez', 'Pedro'],'Pérez':['Pérez'], 'Andrea':['Andrea'], 'María':['María']}
        self.comprobarPersonajes(res)
        m.juntarListPersonajes(['Andrea','María'])
        res = {'Pedro Pérez':['Pedro Pérez'], 'Pedro Rodríguez':['Pedro Rodríguez', 'Pedro'],'Pérez':['Pérez'], 'Andrea':['Andrea', 'María']}
        self.comprobarPersonajes(res)

    def comprobarPersonajes(self, res):
        obt = m.getPersonajes()
        self.assertEqual(len(res),len(obt))
        for k,j in zip(res.keys(),obt.keys()):
            per = obt[j].getPersonaje()
            self.assertEqual(k,j)
            self.assertEqual(len(per),len(res[k]))
            i = 0
            for sk, sj in zip(res[k][0],per.keys()):
                self.assertEqual(sk,res[k][0][i])
                i+=1

    def test_08_leerEpub(self):
        txt = list()
        txt.append('')
        texto = 'Esto es un documento de pruebas para comprobar que se obtienen'
        texto += ' bien las palabras en mayúsculas. Felipe, esto es texto de '
        texto += 'relleno Pedro Pérez, Josema esto es más texto de relleno para'
        texto += ' poder hacer pruebas Pedro esto sigue siendo relleno Pedro '
        texto += 'Rodríguez, Pedro, texto de relleno. María se fue a poner más '
        texto += 'texto de relleno. Pedro Pérez esto como no sigue siendo texto'
        texto += ' de pruebas Ana.. '
        txt.append(texto)
        l = lec.LecturaEpub('tst/epubPruebas.epub')
        it = l.siguienteArchivo()
        for i in txt:
            x = next(it)
            self.assertEqual(i,x)

    def test_09_getDictParsear(self):
        m.anadirPersonaje('Pedro','Pedro')
        res = ['Pedro Pérez', 'Pedro Rodríguez', 'Pedro', 'Pérez', 'Andrea', 'María']
        obt = m.getDictParsear()
        self.assertEqual(len(res),len(obt))
        for i in range(len(res)):
            self.assertEqual(res[i],obt[i])

    def test_10_posPalabrasDict(self):
        m.vaciarDiccionario()
        m.crearDict()
        m.anadirPersonaje('María','María')
        m.anadirPersonaje('relleno','relleno')
        m.obtenerPosPers()
        res = {'Pedro Pérez': {1:[], 2:[23, 54]}, 'Josema': {1:[], 2:[24]}, 'Pedro': {1:[], 2:[35, 41]}, 'Pedro Rodríguez': {1:[], 2:[40]}, 'Ana': {1:[], 2:[63]}, 'María': {1:[], 2:[45]}, 'relleno': {1:[], 2:[22, 30, 39, 44, 53]}, 'Pérez': {1:[], 2:[]}}
        x = m.getPersonajes()
        for i in x.keys():
            pers = x[i].getPersonaje()
            for n in pers.keys():
                self.assertEqual(pers[n],res[n])

    def test_11_esSubcadena(self):
        l = ["Alabardero", "Ala", "Alto", "Baje", "Asta", "Corzo", "lata"]
        res1 = ['Alabardero', 'Ala', 'Alto']
        res2 = ['lata']
        res3 = []
        self.assertEqual(res1,poslex.esSubcadena("Al",l))
        self.assertEqual(res2,poslex.esSubcadena("la",l))
        self.assertEqual(res3,poslex.esSubcadena("li",l))
        
    def test_12_juntarListas(self):
        m.juntarListPersonajes(['Pedro Pérez','Pedro'])
        m.juntarPosiciones()
        res = {'Pedro Pérez': {1:[], 2:[23, 35, 41, 54]}, 'Josema': {1:[], 2:[24]}, 'Pedro Rodríguez': {1:[], 2:[40]}, 'Ana': {1:[], 2:[63]}, 'María': {1:[], 2:[45]}, 'relleno': {1:[], 2:[22, 30, 39, 44, 53]}, 'Pérez':{1:[], 2:[]}}
        x = m.getPersonajes()
        for i in x.keys():
            self.assertEqual(res[i],x[i].getPosicionPers())
            
    def test_13_matrizAdyacencia(self):
        #La matriz de adyacencia no contiene al personaje Ana porque no tiene enlaces con ningun otro personaje
        res = [[0,1,2,1,6],[1,0,0,0,1],[2,0,0,1,2],[1,0,1,0,1],[6,1,2,1,0]]
        m.generarGrafo(5,1,True)
        obt = m.getMatrizAdyacencia().tolist()
        self.assertEqual(res,obt)
        
    def test_14_importarExportarCSV(self):
        m.vaciarDiccionario()
        m.importDict('tst/PruebasImpExp.csv')
        res = {'Pedro Ro':['Pedro Ro', 'Pedro', 'Pedro Rodríguez', 'Pedro R'], 'María':['María'], 'Jose':['Jose', 'Josema'], 'Pedrope':['Pedrope', 'Pedro Pérez'],'Ana':['Ana']}
        self.comprobarPersonajes(res)
        m.anadirPersonaje('relleno','relleno')
        m.exportDict('tst/dictexportado.csv')
        m.importDict('tst/dictexportado.csv')
        res = {'Pedro Ro':['Pedro Ro', 'Pedro', 'Pedro Rodríguez', 'Pedro R'], 'María':['María'], 'Jose':['Jose', 'Josema'], 'Pedrope':['Pedrope', 'Pedro Pérez'], 'Ana':['Ana'], 'relleno':['relleno']}
        self.comprobarPersonajes(res)
    
    def test_15_cambiarEtnia(self):
        m.crearDict()
        m.cambiarEtnia('HISPANIC','Josema')
        pers = m.getPersonajes()
        for x in pers.keys():
            if (x == 'Josema'):
                self.assertEqual(pers[x].getEtnia(),'HISPANIC')
        m.vaciarDiccionario()

    def test_16_cambiarSexo(self):
        m.crearDict()
        m.cambiarSexo('M','Josema')
        pers = m.getPersonajes()
        for x in pers.keys():
            if (x == 'Josema'):
                self.assertEqual(pers[x].getSexo(),'M')
        m.vaciarDiccionario()
        
    def test_17_formatoPeliculasBien(self):
        formato = m.scrapeWikiPelicula('https://www.imsdb.com/scripts/Joker.html')
        self.assertEqual(formato, 1)
        m.vaciarDiccionario()
    
    def test_18_formatoPeliculasMal(self):
        formato = m.scrapeWikiPelicula('https://www.imsdb.com/scripts/Alien.html')
        self.assertEqual(formato, 0)
        m.vaciarDiccionario()
    
    def test_19_probarNormalizar(self):
        cadena = 'orión'
        cadenaAux = ethnea.normalize(cadena)
        self.assertEqual(cadenaAux, 'orion')

    def test_20_separaNombres(self):
        nombre = 'Pepe González'
        name, apellido = ethnea.separaNombres(nombre)
        self.assertEqual(name, 'Pepe')
        self.assertEqual(apellido, 'Gonzalez')
    
    def test_21_separaNombresMasDeUnApellido(self):
        nombre = 'Pepe González Navarro'
        name, apellido = ethnea.separaNombres(nombre)
        self.assertEqual(name, 'Pepe')
        self.assertEqual(apellido, 'Gonzalez+Navarro')

if __name__ == '__main__':
    unittest.main()