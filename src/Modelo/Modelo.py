# -*- coding: utf-8 -*-
from src.Modelo import Personaje as p
from src.Modelo import LectorGrafo as lg
from src.Lexers import CreaDict as cd
from src.Lexers import PosPersonajes as pp
from src.LecturaFicheros import Lectorcsv
from src.LecturaFicheros import LecturaEpub
from src.Guiones import CrearDiccionario as cdguion
from src.PredictorEtniaSexo import EthneaGenni as eg
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import collections
import numpy as np
import networkx as nx
import urllib
import json
import random
from bs4 import BeautifulSoup
import zipfile
from threading import Thread
import os
import secrets
import time
from flask_babel import gettext
from community import community_louvain

from matplotlib import animation, rc
from IPython.display import HTML
from operator import itemgetter
import dynetx as dn
import networkx as nx
import matplotlib.pyplot as plt

v = os.path.join(os.path.dirname( __file__ ), os.pardir)
x = os.path.join(v, os.pardir)
s = os.path.abspath(os.path.join(x, 'ffmpeg.exe'))
plt.rcParams['animation.ffmpeg_path'] = s
import time
import requests

##Generacion de Gexf dinámica

from gexfpy import stringify
from gexfpy import Gexf, Graph, Nodes, Edges, Node, Edge, Attribute, Attributes, Attvalue, Attvalues

import itertools
import time

import networkx as nx

class Modelo:
    """
    Clase que contiene la lógica de la aplicación
    
    Args:
        
    """ 
    def __init__(self):
        """
        Clase que contiene la lógica de la aplicación
        
        Args:
            Constructor de la clase
        """ 
        self.__csv = Lectorcsv.Lectorcsv(self)
        self.__texto = list()
        self.personajes= dict()
        self.__fincaps = list()
        self.__G = None
        self.__Gnoatt = None
        self.__Gdinamica = None
        self.urlPelicula = ""
        self.corpus = ""
        self.obra = ""
        self.diccionarioApariciones = dict()
        self.cambio = 0
        self.formato = 0
        self.apar=0
        self.rango=0
        self.minapar=0
        self.caps=False
        self.frames=0
        ## Variable para controlar la reproducción automática de la gráfica dinámica
        self.auto=0
     
        
    def cambiarPantallas(self, cambiopantalla):
        """
        Método para detectar cambio de pantalla para las 3 opciones: película(0) ,novela(1) y obra de teatro(2)

        Args:
            cambiopantalla - Int
        """
        self.cambio = cambiopantalla

    def getFormato(self):
        """
        Método para obtener si el formato es correcto o no, un 1 significa que si y un 0 significa que no se cumple el formato.

        Return:
            formato - Int
        """
        return self.formato
    
    def devolverCambio(self):
        """
        Método que devuelve el cambio de pantallas para poder avanzar en pantallas pertenecientes a películas o a novelas.

        Return:
            cambio - Int
        """
        return self.cambio
    
    def crearDict(self):
        """
        Método para crear un diccionario automaticamente
        
        Args:
            
        """ 
        creard = cd.CreaDict(self)
        txt = ''
        for i in self.__texto:
            txt += i
        d = Thread(target=creard.crearDict,args=(txt,))
        d.start()
        d.join()
        
    def scrapeWikiPelicula(self,url):
        """
        Método para obtener un diccionario de personajes haciendo web scraping
    
        Args:
            url: url donde hacer web scraping
        """
        self.urlPelicula = url
        crearDiccionario = cdguion.CrearDiccionario(self)
        self.formato = crearDiccionario.obtenerPersPelicula(self.urlPelicula)
        return self.formato
    
    def hayPersonajes(self):
        """
        Método para comporbar si hay personajes en el diccionario.
    
        Return:
            0 si no hay y 1 si hay
        """
        if (len(self.personajes.items())>0):
            return 1
        else:
            return 0
        
    def obtenerPosPers(self):
        """
        Método para obtener las posiciones de los personajes en caso de que se introduzca una novela
        
        Args:
            
        """ 
        self.pos = list()
        self.fin = list()
        posper = pp.PosPersonajes(self)
        pers = self.getDictParsear()
        self.__fincaps = list() 
        posiciones = list()
        txt = ''
        for f in self.__texto:
            txt = txt + f + "+ ---CAPITULO--- +"
        posper.obtenerPos(txt, pers)
        posiciones = self.pos
        self.__fincaps = self.fin
        for i in self.personajes.keys():
            self.personajes[i].lennombres = dict()
            pers = self.personajes[i].getPersonaje()
            self.personajes[i].resNumApariciones(self.personajes[i].getNumApariciones()[0])
            for n in pers.keys():
                c = 1
                apar = 0
                for posc in posiciones:
                    if(n in posc.keys()):
                        pers[n][c] = posc[n]
                        apar+=len(posc[n])
                    c+=1
                self.personajes[i].lennombres[n]=apar
                self.personajes[i].sumNumApariciones(apar)

    def obtenerNumApariciones(self):
        """
        Método para obtener las posiciones de los personajes en caso de que se introduzca un guion
        
        Args:
            
        """ 
        #diccionarioAp = dict()

        listapar = list()
        temp = list()
        contador = 0
        web = urllib.request.urlopen(self.urlPelicula)
        html = BeautifulSoup(web.read(), "html.parser")
        self.diccionarioApariciones = dict()
        for i in self.personajes.keys():
            self.personajes[i].lennombres = dict()
            pers = self.personajes[i].getPersonaje()
            self.personajes[i].resNumApariciones(self.personajes[i].getNumApariciones()[0])
            aux = 0
            for n in pers.keys():
                listapar = list()
                contador = 0
                for perso in html.find_all("b"):
                    if(not len(perso) == 0):
                        pn = perso.contents[0]
                        pn = str(pn)
                        pn = pn.strip()
                        if ('EXT.' in pn or 'INT.' in pn or 'EXT ' in pn or 'INT ' in pn):
                            contador = contador + 1
                        elif(pn == n):
                            if (not contador == 0):
                                if (not contador in listapar):
                                    listapar.append(contador)
                                #self.personajes[l].lennombres[n]=len(listapar)
                                if(aux == 0):
                                    self.diccionarioApariciones[i] = listapar
                                    aux+=1
                                else:
                                    temp = self.diccionarioApariciones.get(i)
                                    for x in listapar:
                                        if(not x in temp):
                                            temp.append(x)
                                    self.diccionarioApariciones[i] = temp
                            #diccionarioAp[l] = len(listapar)
                self.personajes[i].lennombres[n] = len(listapar)
                self.personajes[i].sumNumApariciones(len(listapar))
        return self.diccionarioApariciones

    def obtenerPosicionGeneroTeatro(self):
        diccionario = self.diccionarioGeneroApariciones()
        self.diccionarioApariciones = dict()
        for i in self.personajes.keys():
            self.personajes[i].resNumApariciones(self.personajes[i].getNumApariciones()[0])
            pers = self.personajes[i].getPersonaje()
            for n in pers.keys():
                self.personajes[i].lennombres[n] = diccionario[i][0]
                self.personajes[i].sumNumApariciones(diccionario[i][0])
                self.personajes[i].setSexo(diccionario[i][1])
                self.personajes[i].crearDictSE()
                self.diccionarioApariciones[i] = diccionario[i][2]

    def obtenerEthnea(self,flag):
        """
        Método para obtener etnia y sexo del personaje
    
        Args:
            
        """
        etnia = None
        sexo = None
        ethneagenni = eg.EthneaGenni()
        if(flag == False):
            for i in self.personajes.keys():
                etnia, sexo = ethneagenni.obtenerEtniaSexo(i)
                self.personajes[i].setEtnia(etnia)
                self.personajes[i].setSexo(sexo)
                self.personajes[i].crearDictSE()
        else:
            for i in self.personajes.keys():
                etnia, sexo = ethneagenni.obtenerEtniaSexo(i)
                self.personajes[i].setEtnia(etnia)
                self.personajes[i].crearDictSE()

    def getDictParsear(self):
        """
        Función que genera una lista de nombres para obtener su posición en el texto
    
        Args:
            
        Return:
            Set con los todos los nombres de personajes
        """
        l = list()
        for i in self.personajes.keys():
            for n in self.personajes[i].getPersonaje():
                if(n not in l):
                    l.append(n)
        return l

    def getPersonajes(self):
        """
        Función que devuelve el diccionario de personajes
    
        Args:
            
        Return:
            diccionario de personajes
        """
        return self.personajes

    def vaciarDiccionario(self):
        """
        Método que limpia el diccionario de personajes
    
        Args:
            
        """
        self.personajes = dict()

    def cambiarEtnia(self, etnia, pers):
        """
        Método para cambiar la etnia de un personaje.
    
        Args:
            etnia: string
            pers: string
        """
        self.personajes[pers].setEtnia(etnia)
        self.personajes[pers].crearDictSE()

    def cambiarSexo(self, sexo, pers):
        """
        Método para cambiar el sexo de un personaje.
    
        Args:
            sexo: string
            pers: string
        """
        self.personajes[pers].setSexo(sexo)
        self.personajes[pers].crearDictSE()

    def borrarDictPersonajes(self):
        """
        Método para borrar el diccionario.
    
        Args:
        
        """
        self.personajes = dict()

    def anadirPersonaje(self, idpers, pers):
        """
        Método para añadir un personaje al diccionario de personajes
    
        Args:
            idpers: id del nuevo personaje
            pers: nombre del personaje
        Return:
            string que dice si está aadido o no
        """
        if(idpers not in self.personajes):
            self.personajes[idpers] = p.Personaje()
            self.personajes[idpers].getPersonaje()[pers] = dict()
            return 'Personaje añadido correctamente'
        return 'La id de personaje ya existe'

    def __eliminarPersonaje(self, idPersonaje):
        """
        Método para eliminar personajes
    
        Args:
            idPersonaje: id del personaje a eliminar
        """
        if(idPersonaje in self.diccionarioApariciones):
            del self.diccionarioApariciones[idPersonaje]
        if(idPersonaje in self.personajes):
            del self.personajes[idPersonaje]

    def eliminarListPersonajes(self, personajes):
        """
        Método para eliminar una lista de personajes
    
        Args:
            idPersonaje: id del personaje a eliminar
        """
        for idp in personajes:
            self.__eliminarPersonaje(idp)
    
    def __juntarPersonajes(self, idPersonaje1, idPersonaje2):
        """
        Método para juntar personajes
    
        Args:
            idPersonaje1: id del primer personaje a juntar
            idPersonaje2: id del primer personaje a juntar
        """
        lista = list()
        lista2 = list()
        lista3 = list()
        if(idPersonaje2 in self.diccionarioApariciones):
            lista = self.diccionarioApariciones[idPersonaje2]
        if(idPersonaje1 in self.diccionarioApariciones):
            lista2 = self.diccionarioApariciones[idPersonaje1]
            for i in lista:
                lista2.append(i)
            lista3 = sorted(list(set(lista2)))
            self.diccionarioApariciones[idPersonaje1] = lista3
        if(idPersonaje1 in self.personajes and idPersonaje2 in self.personajes):
            pers1 = self.personajes[idPersonaje1].getPersonaje()
            pers2 = self.personajes[idPersonaje2].getPersonaje()
            apar1 = self.personajes[idPersonaje1].lennombres
            apar2 = self.personajes[idPersonaje2].lennombres
            for k in pers2.keys():
                if k not in pers1.keys():
                    pers1[k]=pers2[k]
                    if(k in apar2.keys()):
                        apar1[k] = apar2[k]
                        self.personajes[idPersonaje1].sumNumApariciones(apar2[k])
            self.__eliminarPersonaje(idPersonaje2)

    def juntarListPersonajes(self,lista):
        """
        Método para juntar una lista de personajes
    
        Args:
            lista: lista de personajes a juntar
        """
        for i in range(1,len(lista)):
            self.__juntarPersonajes(lista[0],lista[i])
    
    def anadirReferenciaPersonaje(self,idp,ref):
        """
        Método para añadir una referencia a un personaje
    
        Args:
            idp: id del personaje
            ref: nueva referencia
        """
        self.personajes[idp].getPersonaje()[ref]= dict()
    
    def __eliminarReferenciaPersonaje(self,idp,ref):
        """
        Método para eliminar una referencia a un personaje
    
        Args:
            idp: id del personaje
            ref: referencia a eliminar
        """
        if(idp in self.personajes.keys()):
            p = self.personajes[idp].getPersonaje()
            if(ref in p.keys()):
                if (len(p)>1):
                    del p[ref]
                    if(ref in self.personajes[idp].lennombres):
                        self.personajes[idp].resNumApariciones(self.personajes[idp].lennombres[ref])
                        del self.personajes[idp].lennombres[ref]
                else:
                    del self.personajes[idp]
    
    def eliminarListRefs(self,lista):
        """
        Método para eliminar una lista de referencias
    
        Args:
            lista: lista de referencias a eliminar
        """
        for l in lista:
            self.__eliminarReferenciaPersonaje(l[0],l[1])

    def modificarIdPersonaje(self,idact,newid):
        """
        Método para modificar los id de los personajes
    
        Args:
            idact: id a cambiar
            newid: nueva id
        """
        self.personajes[newid] = self.personajes.pop(idact)

    def juntarPosiciones(self):
        """
        Método para juntar los posiciones de las referencias de un personaje
    
        Args:
            
        """
        for i in self.personajes.keys():
            pers = self.personajes[i].getPersonaje()
            pos = {}
            for n in pers.keys():
                    for caps in pers[n].keys():
                        cont = 0
                        if(caps not in pos.keys()):
                            pos[caps]=list()
                        for j in pers[n][caps]:
                            while(cont<len(pos[caps]) and pos[caps][cont]<j):
                                cont+=1
                            pos[caps].insert(cont,j)
            self.personajes[i].setPosicionPers(pos)
       
    def prepararRed(self):
        """
        Método que obtiene las posiciones de los personajes y las junta
    
        Args:
            
        """
        if(self.cambio == 2):
            d = Thread(target=self.obtenerPosicionGeneroTeatro())
        elif(self.cambio == 1):
            d = Thread(target=self.obtenerPosPers)
        else:
            d = Thread(target=self.obtenerNumApariciones)
        d.start()
        d.join()
        self.juntarPosiciones()
        
    def getMatrizAdyacencia(self):
        """
        Método que devuelve la matriz de adyacencia de la red
    
        Args:
            
        Return:
            Matriz de adyacencia
        """
        return nx.adjacency_matrix(self.__G).todense()

    def generarGrafo(self,rango,minapar,caps):
        """
        Método para generar un grafo a partir de las relaciones de los personajes
    
        Args:
            rango: rango de palabras
            minapar: numero minimo de apariciones
            caps: si se tienen en cuenta los capitulos
        """
        self.rango=rango
        self.minapar=minapar
        self.caps=caps
        persk = list(self.personajes.keys())
        tam = len(persk)
        self.__G = nx.Graph()
        for i in range(tam):
            #Se comprueba que se cumple con el requisito mínimo de apariciones
            if(self.personajes[persk[i]].getNumApariciones()[0]>=self.minapar):
                #La red es no dirigida sin autoenlaces así que no hace falta medir el peso 2 veces ni consigo mismo
                for j in range(i+1,tam):
                    #Se comprueba que cumple el requisito mínimo de apariciones
                    if(self.personajes[persk[j]].getNumApariciones()[0]>=self.minapar):
                        peso=0
                        #Se recorren los capítulos
                        for cap in self.personajes[persk[i]].getPosicionPers().keys():
                            #Se obtienene las posiciones del personaje en el capítulo correspondiente
                            for posi in self.personajes[persk[i]].getPosicionPers()[cap]:
                                prev = False
                                post = False
                                #Si no se tienen en cuenta los capítulos
                                if(not self.caps):
                                    aux = posi-self.rango
                                    capaux = cap
                                    #Si aux negativo se ha pasado al capítulo anterior capaux minimo de 2 para no salirnos de la lista
                                    while(aux<0 and capaux>1):
                                        prev = True
                                        capaux-=1
                                        aux = self.__fincaps[capaux-1] + aux
                                        #Si aux menor que 0 nos hemos saltado más de un capítulo
                                        if(aux<0):
                                            #Como nos hemos saltado el capítulo entero consideramos todas las posiciones que tiene el 
                                            #segundo personaje en ese capítulo como relación
                                            peso+=len(self.personajes[persk[j]].getPosicionPers()[capaux])
                                        else:
                                            #Comprobamos todas las palabras del capítulo previo que no nos hemos saltado por completo y añadimos
                                            #las que se encuentren en el rango
                                            for posj in self.personajes[persk[j]].getPosicionPers()[capaux]:
                                                if(posj>=aux):
                                                    peso+=1
                                    #Se repite el proceso anterior pero para capítulos posteriores
                                    aux = posi + self.rango - self.__fincaps[cap-1]
                                    capaux = cap
                                    while(aux>0 and capaux<len(self.__fincaps)):
                                        capaux+=1
                                        post=True
                                        if(aux>self.__fincaps[capaux-1]):
                                            aux = aux - self.__fincaps[capaux-1]
                                            peso+=len(self.personajes[persk[j]].getPosicionPers()[capaux])
                                        else:
                                            for posj in self.personajes[persk[j]].getPosicionPers()[capaux]:
                                                if(posj<=aux):
                                                    peso+=1
                                                else:
                                                    break
                                #Si se ha pasado al capítulo previo y al posterior se añaden directamente todas las posiciones del actual
                                if(not self.caps and prev and post):
                                    peso+=len(self.personajes[persk[j]].getPosicionPers()[cap])
                                else:
                                    #Se comprueba en el capítulo actual las palabras que entran en el rango
                                    for posj in self.personajes[persk[j]].getPosicionPers()[cap]:
                                        if(posj>=(posi-self.rango)):
                                            if(posj<=(posi+self.rango)):
                                                peso+=1
                                            else:
                                                break
                        if(peso>0):
                            self.__G.add_edge(persk[i],persk[j],weight=peso)
        self.__Gnoatt = self.__G.copy()
        self.anadirAtributos()
    
    def elementosComunes(lista, lista1):
        """
        Método que obtiene los elementos comunes de dos listas
    
        Return:
            lista con los elementos comunes
        """
        return list(set(lista).intersection(lista1))

    def obtenerRed(self, apar):
        """
        Método para generar un grafo a partir de las relaciones de los personajes en guiones de películas y obras de teatro
    
        Args:
            apar: numero minimo de apariciones
        """
        
        self.apar=apar 
        self.__G = nx.Graph()
        lista = list()
        aux = 0
        if(self.cambio!=2):
            for key in self.diccionarioApariciones:
                aux = 0
                if(self.personajes[key].getNumApariciones()[0]>=self.apar):
                    for key1 in self.diccionarioApariciones:
                        if(self.personajes[key1].getNumApariciones()[0]>=self.apar):
                            if (not key == key1):
                                lista = Modelo.elementosComunes(self.diccionarioApariciones.get(key), self.diccionarioApariciones.get(key1))

                                if (not len(lista) == 0):
                                    #listaprueba.append((key,key1,len(lista)))
                                    peso = len(lista)
                                    self.__G.add_edge(key,key1,weight=int(peso))
                                    aux = 1
                    if(aux == 0):
                        self.__G.add_node(key)
                else:
                    if(self.__G.has_node(key)):
                        self.__G.remove_node(key)
            self.__Gnoatt = self.__G.copy()
            self.anadirAtributos()
        else:
            corpus = self.corpus
            obra= self.obra
            url = "https://dracor.org/api/corpora/"+corpus+"/play/"+obra+"/networkdata/gexf"
            corpora_metrics = requests.get(url)
            variable = lg.read_gexf(corpora_metrics.text)
            self.__G = variable.copy()
            for key in self.personajes:
                if(self.personajes[key].getNumApariciones()[0]<self.apar):
                    if(self.__G.has_node(key)):
                        self.__G.remove_node(key)
            self.simplificarGrafo()


    ## EL grafo que obtenemos de dracor nos da mucha información innecesaria, asi que con este método lo simplificamos
    def simplificarGrafo(self):  
        self.__Gnoatt = nx.Graph()
        for i in self.__G.nodes:
            if(i in self.personajes):
                nodo = list(self.personajes[i].getPersonaje().keys())[0].upper()
                self.__Gnoatt.add_node(nodo)
        for i in self.__G.edges(data=True):
            if(i[0] in self.personajes and i[1] in self.personajes ):
                nodo1 = list(self.personajes[i[0]].getPersonaje().keys())[0].upper()
                nodo2 = list(self.personajes[i[1]].getPersonaje().keys())[0].upper()
                self.__Gnoatt.add_edge(nodo1,nodo2,weight=i[2]['weight'])
        self.__G = self.__Gnoatt
        

    
    def anadirAtributos(self):
        """
        Método que añade ciertos atributos al nodo
    
        Args:
            
        """
        dictionary = dict()
        for i in self.__G.nodes:
            dictionary[i]=self.personajes[i].getDiccionario()
        nx.set_node_attributes(self.__G,dictionary)

    def visualizar(self):
        """
        Método para mandar a d3 la información para visualizar la red
    
        Args:
            
        """
        return json.dumps(nx.json_graph.node_link_data(self.__Gnoatt))

    def listaEnlacesFinalPelicula(self):
        """
        Método para crear una lista que contiene el id del enlace, los nodos que tienen el enlace, el tipo de enlace, 
        el intervalo de tiempo donde se crea el enlace y el peso del enlace. Está lista será para guiones de películas.

        Args:

        """
        listaEnlaces = list()
        listaFinalEnlaces=list()
        indice=0
        persk = list(self.diccionarioApariciones.keys())
        tam = len(persk)
        #Creamos una lista con los enlaces que hay. En la lista tenemos el nodo de origen y de destino, el peso (1), el tipo de
        #enlace (no dirigido) y en que capitulo se da dicho enlace.
        for i in range(tam):
            key = persk[i]
            if(len(self.diccionarioApariciones.get(key))>=self.apar):
                for j in range(i+1,tam):
                    key1 = persk[j]
                    if(len(self.diccionarioApariciones.get(key1))>=self.apar):
                        listaEnlaces = list(set(self.diccionarioApariciones.get(key)).intersection(self.diccionarioApariciones.get(key1))) 
                        if (not len(listaEnlaces) == 0):
                            for i in range(len(listaEnlaces)):
                                personaje1 = list(self.personajes[key].getPersonaje().keys())[0].upper()
                                personaje2 = list(self.personajes[key1].getPersonaje().keys())[0].upper()
                                r=[indice,personaje1,personaje2,'Undirected',listaEnlaces[i],'1.0']
                                listaFinalEnlaces.append(r)
                                indice=indice+1
        return listaFinalEnlaces

    def listaEnlacesFinalNovela(self,rango,minapar,caps):
        """
        Método para crear una lista que contiene el id del enlace, los nodos que tienen el enlace, el tipo de enlace, 
        el intervalo de tiempo donde se crea el enlace y el peso del enlace. Está lista será para novelas.
    
        Args:
            rango: rango de palabras
            minapar: numero minimo de apariciones
            caps: si se tienen en cuenta los capitulos
        """
        persk = list(self.personajes.keys())
        tam = len(persk)
        listaFinalEnlaces=list()
        for i in range(tam):
            #Se comprueba que se cumple con el requisito mínimo de apariciones
            if(self.personajes[persk[i]].getNumApariciones()[0]>=minapar):
                #La red es no dirigida sin autoenlaces así que no hace falta medir el peso 2 veces ni consigo mismo
                for j in range(i+1,tam):
                    #Se comprueba que cumple el requisito mínimo de apariciones
                    if(self.personajes[persk[j]].getNumApariciones()[0]>=minapar):
                        #Se recorren los capítulos
                        for cap in self.personajes[persk[i]].getPosicionPers().keys():
                            #Se obtienene las posiciones del personaje en el capítulo correspondiente
                            for posi in self.personajes[persk[i]].getPosicionPers()[cap]:
                                prev = False
                                post = False
                                #Si no se tienen en cuenta los capítulos
                                if(not caps):
                                    aux = posi-rango
                                    capaux = cap
                                    #Si aux negativo se ha pasado al capítulo anterior capaux minimo de 2 para no salirnos de la lista
                                    while(aux<0 and capaux>1):
                                        prev = True
                                        capaux-=1
                                        aux = self.__fincaps[capaux-1] + aux
                                        #Si aux menor que 0 nos hemos saltado más de un capítulo
                                        if(aux<0):
                                            #Como nos hemos saltado el capítulo entero consideramos todas las posiciones que tiene el 
                                            #segundo personaje en ese capítulo como relación
                                            for pesos in range(len(self.personajes[persk[j]].getPosicionPers()[capaux])):
                                                r=[i,persk[i],persk[j],'Undirected',cap,'1.0']
                                                listaFinalEnlaces.append(r)
                                        else:
                                            #Comprobamos todas las palabras del capítulo previo que no nos hemos saltado por completo y añadimos
                                            #las que se encuentren en el rango
                                            for posj in self.personajes[persk[j]].getPosicionPers()[capaux]:
                                                if(posj>=aux):
                                                    r=[i,persk[i],persk[j],'Undirected',cap,'1.0']
                                                    listaFinalEnlaces.append(r)
                                    #Se repite el proceso anterior pero para capítulos posteriores
                                    aux = posi + rango - self.__fincaps[cap-1]
                                    capaux = cap
                                    while(aux>0 and capaux<len(self.__fincaps)):
                                        capaux+=1
                                        post=True
                                        if(aux>self.__fincaps[capaux-1]):
                                            aux = aux - self.__fincaps[capaux-1]
                                            for pesos in range(len(self.personajes[persk[j]].getPosicionPers()[capaux])):
                                                r=[i,persk[i],persk[j],'Undirected',cap,'1.0']
                                                listaFinalEnlaces.append(r)
                                        else:
                                            for posj in self.personajes[persk[j]].getPosicionPers()[capaux]:
                                                if(posj<=aux):
                                                    #peso+=1
                                                    r=[i,persk[i],persk[j],'Undirected',cap,'1.0']
                                                    listaFinalEnlaces.append(r)
                                                else:
                                                    break
                                #Si se ha pasado al capítulo previo y al posterior se añaden directamente todas las posiciones del actual
                                if(not caps and prev and post):
                                    for pesos in range(len(self.personajes[persk[j]].getPosicionPers()[cap])):
                                        r=[i,persk[i],persk[j],'Undirected',cap,'1.0']
                                        listaFinalEnlaces.append(r)
                                else:
                                    #Se comprueba en el capítulo actual las palabras que entran en el rango
                                    for posj in self.personajes[persk[j]].getPosicionPers()[cap]:
                                        if(posj>=(posi-rango)):
                                            if(posj<=(posi+rango)):
                                                r=[i,persk[i],persk[j],'Undirected',cap,'1.0']
                                                listaFinalEnlaces.append(r)
                                            else:
                                                break
        
        return listaFinalEnlaces

    def ordenarRedDinamica(self,epub):
        """
        Método encargado de crear el grafo ordenado, calcular el intervalo de tiempo más alto y crear una lista para conocer los pesos en cada intervalo.
        
        Args:
            epub: variable para conocer si el diccionario es una pelicula o un guion
        """
        if(epub):
            listaFinalEnlaces=Modelo.listaEnlacesFinalNovela(self,self.rango,self.minapar,self.caps)
        else:
            listaFinalEnlaces=Modelo.listaEnlacesFinalPelicula(self)
        
        #Interacciones
        #G puede crecer agregando una interacción a la vez. Cada interacción se define unívocamente por
        #sus puntos finales, u y v, así como por su marca de tiempo t.
        listaOrdenada=sorted(listaFinalEnlaces, key=itemgetter(4), reverse=False)

          
        listaNueva=list()
        for i in range(len(listaOrdenada)):
            objetosNueva=[listaOrdenada[i][4],listaOrdenada[i][1],listaOrdenada[i][2]]
            listaNueva.append(objetosNueva)
        
        lista=list()
        tiempoMasAlto=0
        for i in range(len(listaOrdenada)):
            lista.append([listaOrdenada[i][1],listaOrdenada[i][2]])
            tiempoMasAlto=listaOrdenada[i][4]
        ## Lista que vamos a devolver con los enlaces y su respectivo peso, para cada instante 
        listaFinal=list()
        ## Lista para controlar que enlaces añadimos en cada escena y no repetir
        listaCheck=list()
        ## Diccionario en el que vamos almacenando el último peso registrado para los enlaces añadidos
        dictEnlPers=dict()
        for i in range(tiempoMasAlto):
            for j in range(len(listaNueva)):
                if listaNueva[j][0]==i+1:
                    ## Solo evaluamos en caso de que para la escena de ese enlace, no hayamos añadido el enlace contrario
                    ## (Ej. PersonajeA,PersonajeB su enlace contrario sería PersonajeB,PersonajeA)
                    if [listaNueva[j][0],listaNueva[j][2],listaNueva[j][1]] not in listaCheck:
                        ## Si existe en el diccionario aumentamos en uno el peso y añadimos el enlace con el peso actualizado a la lista final
                        if str([listaNueva[j][1],listaNueva[j][2]]) in dictEnlPers:
                            valorAntiguo=dictEnlPers.get(str([listaNueva[j][1],listaNueva[j][2]]))
                            dictEnlPers[str([listaNueva[j][1],listaNueva[j][2]])]=valorAntiguo+1
                            objNueva=[listaNueva[j][0],listaNueva[j][1],listaNueva[j][2],dictEnlPers.get(str([listaNueva[j][1],listaNueva[j][2]]))]
                            listaFinal.append(objNueva)
                            listaCheck.append([listaNueva[j][0],listaNueva[j][1],listaNueva[j][2]])
                        ## Si no existe en el diccionario, pero existe el contrario hacemos lo mismo con el contrario
                        elif str([listaNueva[j][2],listaNueva[j][1]]) in dictEnlPers:
                            valorAntiguo=dictEnlPers.get(str([listaNueva[j][2],listaNueva[j][1]]))
                            dictEnlPers[str([listaNueva[j][2],listaNueva[j][1]])]=valorAntiguo+1
                            objNueva=[listaNueva[j][0],listaNueva[j][2],listaNueva[j][1],dictEnlPers.get(str([listaNueva[j][2],listaNueva[j][1]]))]
                            listaFinal.append(objNueva)
                            listaCheck.append([listaNueva[j][0],listaNueva[j][1],listaNueva[j][2]])
                        ## Si no existe ninguno de los 2, lo añadimos con peso 1
                        else:
                            #print(listaNueva[j][2], listaNueva[j][1])
                            objNueva=[listaNueva[j][0],listaNueva[j][1],listaNueva[j][2],1]
                            listaFinal.append(objNueva)
                            dictEnlPers[str([listaNueva[j][1],listaNueva[j][2]])]=1
                            listaCheck.append([listaNueva[j][0],listaNueva[j][1],listaNueva[j][2]])

        ## Este grafo se usa para la exportación de la animación, lo generamos con los enlaces comprobamos aquellos nodos que aparecen antes de tener enlaces
        persk = list(self.personajes.keys())
        tam = len(persk)
        g = dn.DynGraph(edge_removal=True)
        for n in range(1,tiempoMasAlto+1):
            for i in range(len(listaFinal)):
                if listaFinal[i][0] == n:
                    g.add_interaction(u=listaFinal[i][1], v=listaFinal[i][2], t=listaFinal[i][0])
            if epub:
                for j in range(tam):
                    for cap in self.personajes[persk[j]].getPosicionPers().keys():
                        if n == cap:
                            if(self.personajes[persk[j]].getNumApariciones()[0]>=self.minapar):
                                if j not in g:
                                    g.add_node(persk[j])
            else:
                for j in self.diccionarioApariciones.keys():
                    if n in self.diccionarioApariciones.get(j):
                        if(len(self.diccionarioApariciones.get(j))>=self.apar):
                            personaje = list(self.personajes[j].getPersonaje().keys())[0].upper()
                            if personaje not in g:
                                g.add_interaction(u=personaje, v=personaje, t=n)
            
        return g, listaFinal, tiempoMasAlto



    def vistaDinamica(self, frames, epub): 
        """
        Método que creara la red dinámica.
        
        Args:
            frames: el intervalo de tiempo que queremos observar.
            epub: variable para conocer si el diccionario es una pelicula o un guion
        """
        g, listaFiNal, tiempoMasAlto = Modelo.ordenarRedDinamica(self,epub)
        self.frames=frames
        frame=0
        dInamico=nx.Graph()
        persk = list(self.personajes.keys())
        tam = len(persk)
        while(frames>frame):
            for i in range(len(listaFiNal)):
                if listaFiNal[i][0] == frame+1:
                    dInamico.add_edge(listaFiNal[i][1],listaFiNal[i][2],weight=int(listaFiNal[i][3]))
            if epub:
                for j in range(tam):
                    for cap in self.personajes[persk[j]].getPosicionPers().keys():
                        if frame+1 == cap:
                            if(self.personajes[persk[j]].getNumApariciones()[0]>=self.minapar):
                                if j not in dInamico:
                                    dInamico.add_node(persk[j])
            else:
                for j in self.diccionarioApariciones.keys():
                    if frame+1 in self.diccionarioApariciones.get(j):
                        if(len(self.diccionarioApariciones.get(j))>=self.apar):
                            personaje = list(self.personajes[j].getPersonaje().keys())[0].upper()
                            if personaje not in dInamico:
                                dInamico.add_node(personaje)

            frame=frame+1

        self.__Gdinamica = dInamico.copy()
        self.__G = dInamico.copy()

        return json.dumps(nx.json_graph.node_link_data(self.__Gdinamica))

    def exportGEXFdinamica(self,filename,frames,epub):
        """
        Método exportar la red dinámica a formato GEXF con la librería Gexfpy
        
        Args:
            filename: ruta del nuevo fichero
            frames: el intervalo de tiempo que queremos observar.
            epub: variable para conocer si el diccionario es una pelicula o un guion
        """
        g, listaFiNal, tiempoMasAlto = Modelo.ordenarRedDinamica(self,epub)

        ## Una vez tenemos todos los enlaces, obtenemos los nodos con su instante de aparicion y las variaciones de pesos que va teniendo cada enlace

        nodos = dict()
        enlaces = dict()
        frame=0
        persk = list(self.personajes.keys())
        tam = len(persk)
        while(frames>frame):
            for i in range(len(listaFiNal)):
                if listaFiNal[i][0] == frame+1:
                        ## Añadimos los nodos del enlace que no estén todavía en el diccionario
                        if listaFiNal[i][1] not in nodos.keys():
                            nodos[listaFiNal[i][1]]=listaFiNal[i][0]
                        if listaFiNal[i][2] not in nodos.keys():
                            nodos[listaFiNal[i][2]]=listaFiNal[i][0]

                        ## Para cada enlace tendremos una lista de tuplas (instante,peso) para cada modificación
                        if (listaFiNal[i][1],listaFiNal[i][2]) not in enlaces.keys():
                            enlaces[(listaFiNal[i][1],listaFiNal[i][2])] = list()
                            enlaces.get((listaFiNal[i][1],listaFiNal[i][2])).append((listaFiNal[i][0],listaFiNal[i][3]))
                        else:
                            enlaces.get((listaFiNal[i][1],listaFiNal[i][2])).append((listaFiNal[i][0],listaFiNal[i][3]))
            if epub:
                for j in range(tam):
                    for cap in self.personajes[persk[j]].getPosicionPers().keys():
                        if frame+1 == cap:
                            if(self.personajes[persk[j]].getNumApariciones()[0]>=self.minapar):
                                if j not in nodos.keys():
                                    nodos[persk[j]]=frame
            else:
                for j in self.diccionarioApariciones.keys():
                    if frame+1 in self.diccionarioApariciones.get(j):
                        if(len(self.diccionarioApariciones.get(j))>=self.apar):
                            personaje = list(self.personajes[j].getPersonaje().keys())[0].upper()
                            if personaje not in nodos.keys():
                                nodos[personaje]=frame

            frame=frame+1
        

        ## nodo único

        ## Creamos el fichero Gexf con formato dinámico
        gexf = Gexf()
        gexf.graph = Graph(mode = "dynamic",defaultedgetype="undirected")
        gexf.graph.attributes = Attributes(attribute = Attribute(id="weight", title="Weight", type="int"),class_value= "edge", mode="dynamic")

        ## Añadimos los nodos al gexf con su instante de aparición y final el límite indicado
        nodosGrafo = list()
        for i in nodos.keys():
            nodosGrafo.append(Node(id=i, label=i, start = nodos[i], end = frames))

        gexf.graph.nodes = [Nodes(node = nodosGrafo, count = len(nodosGrafo))]

        ## Para crear los enlaces, deberemos crear primero una lista con los pesos que van obteniendo a lo largo de los instantes. 
        ## Importante indicar final de un peso el inicio del siguiente para que Gephi no de problemas al exportar
        enlacesGrafo = list()
        for i in enlaces.keys():
            pesoEnlaces = list()
            pesos = enlaces[i]
            for a in range(len(pesos)-1):
                pesoEnlaces.append(Attvalue(for_value="weight",value=pesos[a][1], start=pesos[a][0], end=pesos[a+1][0]))
            ## El útlimo no tiene peso siguiente y el final será frames
            pesoEnlaces.append(Attvalue(for_value="weight",value=pesos[len(pesos)-1][1], start=pesos[len(pesos)-1][0], end=frames))
            enlacesGrafo.append(Edge( source = i[0], target = i[1], label = i[0]+i[1], start = pesos[0][0], end = frames, attvalues = Attvalues(pesoEnlaces)))

        
        gexf.graph.edges = [Edges(edge=enlacesGrafo, count = len(enlacesGrafo))]
        s = stringify(gexf)
        self.writeFile(filename,s)

    def elementosRed(self):
        """
        Método encargado de mostranos los nodos de la red.

        Args:

        """
        return self.__G.nodes()



    def descargarRed(self, frames, filename,epub): 
        """
        Método que exportará la animación de la red dinámica.
        
        Args:
            filename: ruta del nuevo fichero
            frames: el intervalo de tiempo que queremos observar.
            epub: variable para conocer si el diccionario es una pelicula o un guion
        """
        v = os.path.join(os.path.dirname( __file__ ), os.pardir)
        x = os.path.join(v, os.pardir)
        s = os.path.abspath(os.path.join(x, 'ffmpeg.exe'))
        plt.rcParams['animation.ffmpeg_path'] = s
        g, listaFiNal, tiempoMasAlto = Modelo.ordenarRedDinamica(self,epub)

        def update(frames):
            T=g.time_slice(t_from=frames, t_to=frames+1)
            nx.set_edge_attributes(T,0,"weight")
            widths = nx.get_edge_attributes(T, 'weight')
            
            for i in range(len(listaFiNal)):
                if listaFiNal[i][0] == frames+1:
                    if (listaFiNal[i][1],listaFiNal[i][2]) in T.edges():
                        widths[listaFiNal[i][1],listaFiNal[i][2]]=listaFiNal[i][3]    

            
            d = dict(T.degree())
            nx.draw_networkx_nodes(T,pos,ax=ax,node_size=[v * 1000 for v in d.values()], alpha=0.5,cmap=[v * 100 for v in d.values()])
            nx.draw_networkx_edges(T,pos,ax=ax, edgelist = widths.keys(), width=list(widths.values()))
            nx.draw_networkx_labels(T,pos,font_size=25,ax=ax)

        T=nx.Graph()
        T=g.time_slice(t_from=1, t_to=tiempoMasAlto)
        fig, ax = plt.subplots(figsize=(30,30)) 
        pos = nx.spring_layout(T,k=0.5)
        listaEncapsul=list()
        listaEncapsul.append(T.edges())
        nx.set_edge_attributes(T,0,"weight")

        ani = animation.FuncAnimation(fig, func=update, frames=frames, interval=10000)
        fps = 1
        if(frames>100):
            fps = 2
        writer = animation.FFMpegWriter(fps, bitrate=100)
        return ani.save(filename, writer = writer)


    def scrapeWiki(self,url):
        """
        Método para obtener un diccionario de personajes haciendo web scraping
    
        Args:
            url: url donde hacer web scraping
        """
        web = urllib.request.urlopen(url)
        html = BeautifulSoup(web.read(), "html.parser")
        for pers in html.find_all("a", {"class": "category-page__member-link"}):
            pn = pers.get('title')
            self.anadirPersonaje(pn,pn)		
	
    def importDict(self, fichero):
        """
        Método para importar un diccionario de personajes desde un fichero csv
    
        Args:
            fichero: ruta al fichero
        """
        self.__csv.importDict(fichero)
    
    def exportDict(self, fichero):
        """
        Método para exportar el diccionario de personajes a un fichero csv
    
        Args:
            fichero: ruta del nuevo fichero
        """
        self.__csv.exportDict(fichero)
         
    '''
    
    '''
    def obtTextoEpub(self, fich):
        """
        Método para obtener el texto del epub del que se quiere obtener la red de 
        personajes
        
        Args:
            fich: ruta al archivo epub
        """
        l = LecturaEpub.LecturaEpub(fich)
        self.__texto = list()
        for f in l.siguienteArchivo():
            self.__texto.append(". " + f)

    @staticmethod
    def esEpub(fich):
        """
        Método para comprobar si un archivo es un epub
        
        Args:
            fich: ruta al archivo epub
        """
        if(not zipfile.is_zipfile(fich)):
            return False
        x = zipfile.ZipFile(fich)
        try:
            x.read('META-INF/container.xml')
        except:
            return False
        else:
            return True

    def exportGML(self,filename):
        """
        Método exportar la red a formato GML
        
        Args:
            filename: ruta del nuevo fichero
        """
        self.writeFile(filename,nx.generate_gml(self.__G))
        
    def exportGEXF(self,filename):
        """
        Método exportar la red a formato GEXF
        
        Args:
            filename: ruta del nuevo fichero
        """
        self.writeFile(filename,nx.generate_gexf(self.__G))
    
    def exportPajek(self,filename):
        """
        Método exportar la red a formato GML
        
        Args:
            filename: ruta del nuevo fichero
        """
        nx.write_pajek(self.__G, filename)
        
    def writeFile(self,filename,text):
        """
        Método escribir un fichero
        
        Args:
            filename: ruta del nuevo fichero
            text: texto para generar el archivo
        """
        file = open(filename,"w")
        for r in text:
            file.write(r)
            
    def generarInforme(self, solicitud, direc):
        """
        Método que maneja las solicitudes de informes
        
        Args:
            solicitud: lista con las metricas
            direc: directorio donde guardar imagenes
        """
        switch = {'cbx cbx-nnod': self.nNodos,
                    'cbx cbx-nenl': self.nEnl,
                    'cbx cbx-nint': self.nInt,
                    'cbx cbx-gradosin': self.gSin,
                    'cbx cbx-gradocon': self.gCon,
                    'cbx cbx-distsin': self.dSin,
                    'cbx cbx-distcon': self.dCon,
                    'cbx cbx-dens': self.dens,
                    'cbx cbx-concomp': self.conComp,
                    'cbx cbx-exc': self.exc,
                    'cbx cbx-dia': self.diam,
                    'cbx cbx-rad': self.rad,
                    'cbx cbx-longmed': self.longMed,
                    'cbx cbx-locclust': self.locClust,
                    'cbx cbx-clust': self.clust,
                    'cbx cbx-trans': self.trans,
                    'cbx cbx-centg': self.centG,
                    'cbx cbx-centc': self.centC,
                    'cbx cbx-centi': self.centI,
                    'cbx cbx-ranwal': self.ranWal,
                    'cbx cbx-centv': self.centV,
                    'cbx cbx-para': self.paRa,
                    'cbx cbx-kcliperc': self.kCliPerc,
                    'cbx cbx-girnew': self.girNew,
                    'cbx cbx-greedy': self.greedyComunidad,
                    'cbx cbx-louvain': self.louvain,
                    'cbx cbx-roleskcliq': self.roleskclique,
                    'cbx cbx-rolesgirvan': self.rolesGirvan,
                    'cbx cbx-rolesgreedy': self.rolesGreedy,
                    'cbx cbx-roleslouvain': self.rolesLouvain}
        valkcliqper =  solicitud['valkcliqper']
        valkcliqperrol = solicitud['valkcliqperrol']
        del solicitud['valkcliqper']
        del solicitud['valkcliqperrol']
        self.informe = dict()
        self.dir = direc
        cont = 0
        for s in solicitud.keys():
            if('cbx cbx-kcliperc' == s):
                self.informe[s] = switch[s](valkcliqper)
            elif('cbx cbx-roleskcliq' == s):
                self.informe[s] = switch[s](valkcliqperrol)
            else:
                self.informe[s] = switch[s]()
    
    def generarInformeDinamico(self, solicitud, direc,epub):
        """
        Método que maneja las solicitudes de informes dinámica
        
        Args:
            solicitud: lista con las metricas
            direc: directorio donde guardar imagenes
            epub: variable para conocer si el diccionario es una pelicula o un guion
        """
        switch = {'cbx cbx-nnod': self.nNodosDinamico,
                    'cbx cbx-nenl': self.nEnlDinamico,
                    'cbx cbx-nint': self.nIntDinamico,
                    'cbx cbx-gradosin': self.gSinDinamica,
                    'cbx cbx-gradocon': self.gConDinamica,
                    'cbx cbx-dens': self.densDinamica,
                    'cbx cbx-concomp': self.conCompDinamica,
                    'cbx cbx-exc': self.excDinamica,
                    'cbx cbx-dia': self.diamDinamica,
                    'cbx cbx-rad': self.radDinamica,
                    'cbx cbx-longmed': self.longMedDinamica,
                    'cbx cbx-locclust': self.locClustDinamica,
                    'cbx cbx-clust': self.clustDinamica,
                    'cbx cbx-trans': self.transDinamica,
                    'cbx cbx-centg': self.centGDinamica,
                    'cbx cbx-centc': self.centCDinamica,
                    'cbx cbx-centi': self.centIDinamica,
                    'cbx cbx-ranwal': self.ranWalDinamica,
                    'cbx cbx-centv': self.centVDinamica,
                    'cbx cbx-para': self.paRaDinamica,
                    'cbx cbx-kcliperc': self.kCliPercDinamica,
                    'cbx cbx-girnew': self.girNewDinamica,
                    'cbx cbx-greedy': self.greedyComunidadDinamica,
                    'cbx cbx-louvain': self.louvainDinamica,
                    'cbx cbx-roleskcliq': self.roleskclique,
                    'cbx cbx-rolesgirvan': self.rolesGirvan,
                    'cbx cbx-rolesgreedy': self.rolesGreedy, 
                    'cbx cbx-roleslouvain': self.rolesLouvain}
        valkcliqper =  solicitud['valkcliqper']
        del solicitud['valkcliqper']
        self.informeDina = dict()
        self.dir = direc 
        ## No le tengo que pasar variable a estas opciones
        notEpub = ['cbx cbx-roleskcliq','cbx cbx-rolesgirvan','cbx cbx-rolesgreedy','cbx cbx-roleslouvain']
        for s in solicitud.keys():
            if('cbx cbx-kcliperc' == s):
                self.informeDina[s] = switch[s](valkcliqper,epub)
            elif(s in notEpub):
                self.informeDina[s] = switch[s]
            else:
                self.informeDina[s] = switch[s](epub)

    def generarValoresDescargaInforme(self):
        """
        Método que genera todas las solicitudes del informe dinámico para 
        que posteriormente se pueda descargar en excel el informe dinámico.

        Args:

        """
        contador=0
        listaSolicitud=list()
        for x in self.informeDina.keys():
            if x=="cbx cbx-nnod" or x=="cbx cbx-nenl" or x=="cbx cbx-nint" or x=="cbx cbx-dens" or x=="cbx cbx-clust" or x=="cbx cbx-trans" or x=="cbx cbx-dia" or x=="cbx cbx-rad" or x=="cbx cbx-longmed":
                if contador < 1:
                    nombre="tablaRedes"
                    listaSolicitud.append(nombre)
                    contador=1
            else:
                listaSolicitud.append(x)
        return listaSolicitud



        
    def nNodosDinamico(self,epub):
        """
        Método que devuelve el numero de nodos dinámico
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            Numero de nodos dinámico
        """
        guardarInforme=list()
        print('numero nodos')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            #guardarInforme[i+1]=nx.number_of_nodes(self.__G)
            guarda=nx.number_of_nodes(self.__G)
            todo=[i,guarda]
            guardarInforme.append(todo)
        #tuplas=set(guardarInforme)
        #nodosCount = collections.Counter(tuplas)
        return guardarInforme

    def nEnlDinamico(self,epub):
        """
        Método que devuelve el numero de enlaces dinámico
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            Numero de enlaces dinámico
        """
        guardarInforme=list()
        print('numero enlaces')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            guarda=nx.number_of_edges(self.__G)
            todo=[i,guarda]
            guardarInforme.append(todo)
        return guardarInforme

    def nIntDinamico(self,epub):
        """
        Método que devuelve el numero de interacciones dinámico
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion 

        Return:
            Numero de interacciones dinámico
        """
        guardarInforme=list()
        print('numero interacciones')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            guarda=self.__G.size(weight='weight')
            todo=[i,guarda]
            guardarInforme.append(todo)
        return guardarInforme

    def densDinamica(self,epub):
        """
        Método que devuelve la densidad de la red dinámico
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            Densidad de la red dinámico
        """
        guardarInforme=list()
        print('densidad')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            guarda=nx.density(self.__G)
            todo=[i,guarda]
            guardarInforme.append(todo)
        return guardarInforme

    def clustDinamica(self,epub):
        """
        Método que devuelve el clustering global de la red dinámico
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            clustering global dinámico
        """
        guardarInforme=list()
        print('clustering global')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            guarda=nx.average_clustering(self.__G)
            todo=[i,guarda]
            guardarInforme.append(todo)
        return guardarInforme

    def transDinamica(self,epub):
        """
        Método que devuelve la transitividad de la red dinámico
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            transitividad de la red dinámico
        """
        guardarInforme=list()
        print('transitividad')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            guarda=nx.transitivity(self.__G)
            todo=[i,guarda]
            guardarInforme.append(todo)
        return guardarInforme

    def diamDinamica(self,epub):
        """
        Método que devuelve el diametro de la red dinámico
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            diametro de la red dinámico
        """
        guardarInforme=list()
        print('diametro')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            if(nx.is_connected(self.__G)):
                guarda=nx.diameter(self.__G)
            else:
                guarda="No está conectado"
            todo=[i,guarda]
            guardarInforme.append(todo)
        return guardarInforme
        
    def radDinamica(self,epub):
        """
        Método que devuelve el radio de la red dinámico
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            radio de la red dinámico
        """
        guardarInforme=list()
        print('radio')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            if(nx.is_connected(self.__G)):
                guarda=nx.radius(self.__G)
            else:
                guarda="No está conectado"
            todo=[i,guarda]
            guardarInforme.append(todo)
        return guardarInforme
        
    def longMedDinamica(self,epub):
        """
        Método que devuelve la distancia media de la red dinámico
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            distancia media de la red dinámico
        """
        guardarInforme=list()
        print('distancia media')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            if(nx.is_connected(self.__G)):
                guarda=nx.average_shortest_path_length(self.__G)
            else:
                guarda="No está conectado"
            todo=[i,guarda]
            guardarInforme.append(todo)
        return guardarInforme

    def gSinDinamica(self,epub):
        """
        Método que devuelve el grado sin tener en cuenta el peso dinámico
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            Grado sin el peso dinámico
        """
        guardarInforme=list()
        print('grado sin peso')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            for x in nx.degree(self.__G):
                todo=[i,x[0],x[1]]
                guardarInforme.append(todo)
        return guardarInforme

    def gConDinamica(self,epub):
        """
        Método que devuelve el grado teniendo en cuenta el peso dinámico
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            Grado con el peso dinámico
        """
        guardarInforme=list()
        print('grado con peso')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            for x in nx.degree(self.__G,weight='weight'):
                todo=[i,x[0],x[1]]
                guardarInforme.append(todo)
        return guardarInforme

    def locClustDinamica(self,epub):
        """
        Método que devuelve el clustering de cada nodo dinámico
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            clustering de cada nodo dinámico
        """
        guardarInforme=list()
        print('clustering de cada nodo')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            for x in nx.clustering(self.__G):
                todo=[i,x,nx.clustering(self.__G)[x]]
                guardarInforme.append(todo)
        return guardarInforme

    def excDinamica(self,epub):
        """
        Método que devuelve la excentricidad de la red dinámica
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            excentricidad de la red dinámica
        """
        guardarInforme=list()
        print('excentricidad')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            if(nx.is_connected(self.__G)):
                for x in nx.eccentricity(self.__G):
                    todo=[i,x,nx.eccentricity(self.__G)[x]]
                    guardarInforme.append(todo)
            else:
                j="La red no está conectada"
                todo=[i,i,j]
                guardarInforme.append(todo)
        return guardarInforme

    def centGDinamica(self,epub):
        """
        Método que devuelve la centralidad de grado dinámica
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            centralidad de grado dinámica
        """
        guardarInforme=list()
        print('centralidad de grado')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            for x in nx.degree_centrality(self.__G):
                todo=[i,x,nx.degree_centrality(self.__G)[x]]
                guardarInforme.append(todo)
        return guardarInforme
        
    def centCDinamica(self,epub):
        """
        Método que devuelve la centralidad de cercania dinámica
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            centralidad de cercania dinámica
        """
        guardarInforme=list()
        print('centralidad de cercanía')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            for x in nx.closeness_centrality(self.__G):
                todo=[i,x,nx.closeness_centrality(self.__G)[x]]
                guardarInforme.append(todo)
        return guardarInforme
        
    def centIDinamica(self,epub):
        """
        Método que devuelve la centralidad de intermediacion dinámica
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            centralidad de intermediacion dinámica
        """
        guardarInforme=list()
        print('centralidad de intermediación')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            for x in nx.betweenness_centrality(self.__G):
                todo=[i,x,nx.betweenness_centrality(self.__G)[x]]
                guardarInforme.append(todo)
        return guardarInforme
        
    def ranWalDinamica(self,epub):
        """
        Método que devuelve la centralidad de intermediacion random walker dinámica
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            centralidad de intermediacion random walker dinámica
        """
        guardarInforme=list()
        print('random walk')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            if(len(self.__G.edges)>0):
                if(nx.is_connected(self.__G)):
                    for x in nx.current_flow_betweenness_centrality(self.__G):
                        todo=[i,x,nx.current_flow_betweenness_centrality(self.__G)[x]]
                        guardarInforme.append(todo)
                else:
                    j="La red no está conectada"
                    todo=[i,i,j]
                    guardarInforme.append(todo)
            else:
                j="Red sin enlaces"
                todo=[i,i,j]
                guardarInforme.append(todo)
        return guardarInforme
        
    def centVDinamica(self,epub):
        """
        Método que devuelve la centralidad de valor propio dinámica
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            centralidad de valor propio dinámica
        """
        guardarInforme=list()
        print('Valor propio')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            for x in nx.eigenvector_centrality(self.__G):
                todo=[i,x,nx.eigenvector_centrality(self.__G)[x]]
                guardarInforme.append(todo)
        return guardarInforme
        
    def paRaDinamica(self,epub):
        """
        Método que devuelve la centralidad de pagerank dinámica
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            centralidad de pagerank dinámica
        """
        guardarInforme=list()
        print('PageRank')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            for x in nx.pagerank_numpy(self.__G,alpha=0.85):
                todo=[i,x,nx.pagerank_numpy(self.__G,alpha=0.85)[x]]
                guardarInforme.append(todo)
        return guardarInforme

    def conCompDinamica(self,epub):
        """
        Método que devuelve todos los componentes conectados dinámicamente
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            lista de cada componente conectado dinámico
        """
        guardarInforme=list()
        maximo = 0
        print('componentes conectados')
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            componente=1
            for x in nx.connected_components(self.__G):
                todo=[i,componente, [x]]
                guardarInforme.append(todo)
                if(componente > maximo):
                    maximo = componente
                componente=componente+1
        return guardarInforme,maximo


    def louvainDinamica(self,epub):
        """
        Método que ejecuta el algoritmo de louvain dinámico
    
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion

        Return:
            lista con las particiones dinámicas.
        """
        guardarInforme=list()
        print('Com louvain')
        maximo = 0
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            if(len(self.__G.edges)>0):
                partition = community_louvain.best_partition(self.__G)
                particiones = self.ordenarFrozen(partition)
                tiempo=1
                for x in particiones:
                    todo=[i,tiempo, list(x)]
                    guardarInforme.append(todo)
                    if(tiempo>maximo):
                        maximo = tiempo
                    tiempo=tiempo+1 
            elif(len(self.__G.nodes)>0):
                todo=[i,1, list(self.__G.nodes)[0]]
                guardarInforme.append(todo)
            else:
                todo=[i,1, ["Red sin nodos"]]
                guardarInforme.append(todo)
        return guardarInforme,maximo


    def greedyComunidadDinamica(self,epub):
        """
        Método que devuelve las comunidades con el algoritmo greedy de Clauset-Newman-Moore dinámicamente

        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion

        Return:
            comunidades de Clauset-Newman-Moore dinámicas
        """
        guardarInforme=list()
        auxiliar = list()
        print('com greedy')
        maximo = 0
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            if(len(self.__G.edges)>0):
                tiempo=1
                for x in nx.algorithms.community.greedy_modularity_communities(self.__G):
                    todo=[i,tiempo, list(x)]
                    guardarInforme.append(todo)
                    if(tiempo>maximo):
                        maximo = tiempo
                    tiempo=tiempo+1
            elif(len(self.__G.nodes)>0):
                todo=[i,1, list(self.__G.nodes)[0]]
                guardarInforme.append(todo)
            else:
                todo=[i,1, ["Red sin nodos"]]
                guardarInforme.append(todo)
        return guardarInforme,maximo

    def kCliPercDinamica(self, k, epub):
        """
        Método que devuelve las comunidades de k-clique dinámicas
        
        Args:
            k: valor k del k-clique
            epub: variable para conocer si el diccionario es una pelicula o un guion
        Return:
            comunidades de k-clique dinámicas
        """
        guardarInforme=list()
        print('com kcliq')
        maximo = 0
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            tiempo=1
            for x in nx.algorithms.community.k_clique_communities(self.__G, int(k)):
                todo=[i,tiempo, list(x)]
                guardarInforme.append(todo)
                if(tiempo>maximo):
                    maximo = tiempo
                tiempo=tiempo+1
        return guardarInforme,maximo
        
    def girNewDinamica(self,epub):
        """
        Método que devuelve las comunidades de girvan-newman dinámicas
        
        Args:
        epub: variable para conocer si el diccionario es una pelicula o un guion
            
        Return:
            comunidades de girvan-newman dinámicas
        """
        guardarInforme=list()
        print('com girvan')
        maximo = 0
        for i in range(1,self.frames+1):
            Modelo.vistaDinamica(self, i, epub)
            d = nx.algorithms.community.girvan_newman(self.__G)
            lista = list(tuple(sorted(c) for c in next(d)))
            tiempo=1
            for x in lista:
                todo=[i,tiempo, x]
                guardarInforme.append(todo)
                if(tiempo>maximo):
                    maximo = tiempo
                tiempo=tiempo+1
        return guardarInforme,maximo


    def nNodos(self):
        """
        Método que devuelve el numero de nodos
        
        Args:
            
        Return:
            Numero de nodos
        """
        print('numero nodos')
        return nx.number_of_nodes(self.__G)
        
    def nEnl(self):
        """
        Método que devuelve el numero de enlaces
        
        Args:
            
        Return:
            Numero de enlaces
        """
        print('numero enlaces')
        return nx.number_of_edges(self.__G)
        
    def nInt(self):
        """
        Método que devuelve el numero de interacciones
        
        Args:
            
        Return:
            Numero de interacciones
        """
        print('numero interacciones')
        return self.__G.size(weight='weight')
    
    def gSin(self):
        """
        Método que devuelve el grado sin tener en cuenta el peso
        
        Args:
            
        Return:
            Grado sin el peso
        """
        print('grado sin peso')
        return nx.degree(self.__G)
        
    def gCon(self):
        """
        Método que devuelve el grado teniendo en cuenta el peso
        
        Args:
            
        Return:
            Grado con el peso
        """
        print('grado con peso')
        return nx.degree(self.__G,weight='weight')
        
    def dSin(self):
        """
        Método que devuelve la distribución de grado sin tener en cuenta el peso
        
        Args:
            
        Return:
            Distribucion de grado sin el peso
        """
        print('distribucion sin peso')
        degree_sequence = sorted([d for n, d in self.__G.degree()], reverse=True)  # degree sequence
        degreeCount = collections.Counter(degree_sequence)
        deg, cnt = zip(*degreeCount.items())
        fig, ax = plt.subplots(figsize=(14,8))
        plt.bar(deg, cnt, width=0.80, color='b')
        
        plt.title(gettext("Histograma de grado"))
        plt.ylabel(gettext("N nodos"))
        plt.xlabel(gettext("Grado"))
        ax.set_xticks([d + 0.4 for d in deg])
        ax.set_xticklabels(deg)
        
        plt.savefig(os.path.join(self.dir,'dsin.png'), format="PNG")
        return degreeCount
    
    def dCon(self):
        """
        Método que devuelve la distribución de grado teniendo en cuenta el peso
        
        Args:
            
        Return:
            Distribucion de grado con el peso
        """
        print('distribucion con peso')
        degree_sequence = sorted([d for n, d in self.__G.degree(weight='weight')], reverse=True)
        degreeCount = collections.Counter(degree_sequence)
        deg, cnt = zip(*degreeCount.items())
        fig, ax = plt.subplots(figsize=(14,8))
        plt.bar(deg, cnt, width=0.80, color='b')
        
        plt.title(gettext("Histograma de Interacciones"))
        plt.ylabel(gettext("N nodos"))
        plt.xlabel(gettext("Interacciones"))
        ax.set_xticks([d + 0.4 for d in deg])
        ax.set_xticklabels(deg)
        
        plt.savefig(os.path.join(self.dir,'dcon.png'), format="PNG")
        return degreeCount
        
    def dens(self):
        """
        Método que devuelve la densidad de la red
        
        Args:
            
        Return:
            Densidad de la red
        """
        print('densidad')
        return nx.density(self.__G)
        
    def conComp(self):
        """
        Método que devuelve todos los componentes conectados
        
        Args:
            
        Return:
            lista de cada componente conectado
        """
        print('componentes conectados')
        l = list()
        for x in nx.connected_components(self.__G):
            l.append(x)
        return l
        
    def exc(self):
        """
        Método que devuelve la excentricidad de la red
        
        Args:
            
        Return:
            excentricidad de la red
        """
        print('excentricidad')
        diccionario = dict()
        if(nx.is_connected(self.__G)):
            return nx.eccentricity(self.__G)
        diccionario['Grafo']="El grafo no está conectado"
        return diccionario
    
    def diam(self):
        """
        Método que devuelve el diametro de la red
        
        Args:
            
        Return:
            diametro de la red
        """
        print('diametro')
        if(nx.is_connected(self.__G)):
            return nx.diameter(self.__G)
        return "El grafo no está conectado"
        
    def rad(self):
        """
        Método que devuelve el radio de la red
        
        Args:
            
        Return:
            radio de la red
        """
        print('radio')
        if(nx.is_connected(self.__G)):
            return nx.radius(self.__G)
        return "El grafo no está conectado"
        
    def longMed(self):
        """
        Método que devuelve la distancia media de la red
        
        Args:
            
        Return:
            distancia media de la red
        """
        print('distancia media')
        if(nx.is_connected(self.__G)):
            return nx.average_shortest_path_length(self.__G)
        return "El grafo no está conectado"
        
    def locClust(self):
        """
        Método que devuelve el clustering de cada nodo
        
        Args:
            
        Return:
            clustering de cada nodo
        """
        print('clustering de cada nodo')
        return nx.clustering(self.__G)
        
    def clust(self):
        """
        Método que devuelve el clustering global de la red
        
        Args:
            
        Return:
            clustering global
        """
        print('clustering global')
        return nx.average_clustering(self.__G)
        
    def trans(self):
        """
        Método que devuelve la transitividad de la red
        
        Args:
            
        Return:
            transitividad de la red
        """
        print('transitividad')
        return nx.transitivity(self.__G)
        
    def centG(self):
        """
        Método que devuelve la centralidad de grado
        
        Args:
            
        Return:
            centralidad de grado
        """
        print('centralidad de grado')
        centg = nx.degree_centrality(self.__G)
        pesos = np.array(list(centg.values()))
        pos=nx.kamada_kawai_layout(self.__G)
        f = plt.figure(figsize=(12,12))
        nx.draw(self.__G,pos,with_labels=True, node_size = pesos*5000, ax=f.add_subplot(111))
        f.savefig(os.path.join(self.dir,'centg.png'), format="PNG")
        return centg
        
    def centC(self):
        """
        Método que devuelve la centralidad de cercania
        
        Args:
            
        Return:
            centralidad de cercania
        """
        print('centralidad de cercanía')
        centc = nx.closeness_centrality(self.__G)
        pesos = np.array(list(centc.values()))
        pos=nx.kamada_kawai_layout(self.__G)
        f = plt.figure(figsize=(12,12))
        nx.draw(self.__G,pos,with_labels=True, node_size = pesos*5000, ax=f.add_subplot(111))
        f.savefig(os.path.join(self.dir,'centc.png'), format="PNG")
        return centc
        
    def centI(self):
        """
        Método que devuelve la centralidad de intermediacion
        
        Args:
            
        Return:
            centralidad de intermediacion
        """
        print('centralidad de intermediación')
        centi = nx.betweenness_centrality(self.__G)
        pesos = np.array(list(centi.values()))
        pos=nx.kamada_kawai_layout(self.__G)
        f = plt.figure(figsize=(12,12))
        nx.draw(self.__G,pos,with_labels=True, node_size = pesos*10000, ax=f.add_subplot(111))
        f.savefig(os.path.join(self.dir,'centi.png'), format="PNG")
        return centi
        
    def ranWal(self):
        """
        Método que devuelve la centralidad de intermediacion random walker
        
        Args:
            
        Return:
            centralidad de intermediacion random walker
        """
        print('random walk')
        if(nx.is_connected(self.__G)):
            ranwal = nx.current_flow_betweenness_centrality(self.__G)
            pesos = np.array(list(ranwal.values()))
            pos=nx.kamada_kawai_layout(self.__G)
            f = plt.figure(figsize=(12,12))
            nx.draw(self.__G,pos,with_labels=True, node_size = pesos*10000, ax=f.add_subplot(111))
            f.savefig(os.path.join(self.dir,'ranwal.png'), format="PNG")
            return ranwal
        else:
            diccionario = dict()
            diccionario['Grafo']="El grafo no está conectado"
            return diccionario
        
    def centV(self):
        """
        Método que devuelve la centralidad de valor propio
        
        Args:
            
        Return:
            centralidad de valor propio
        """
        print('Valor propio')
        centv = nx.eigenvector_centrality(self.__G)
        pesos = np.array(list(centv.values()))
        pos=nx.kamada_kawai_layout(self.__G)
        f = plt.figure(figsize=(12,12))
        nx.draw(self.__G,pos,with_labels=True, node_size = pesos*5000, ax=f.add_subplot(111))
        f.savefig(os.path.join(self.dir,'centv.png'), format="PNG")
        return centv
        
    def paRa(self):
        """
        Método que devuelve la centralidad de pagerank
        
        Args:
            
        Return:
            centralidad de pagerank
        """
        print('PageRank')
        pr = nx.pagerank_numpy(self.__G,alpha=0.85)
        pesos = np.array(list(pr.values()))
        pos=nx.kamada_kawai_layout(self.__G)
        f = plt.figure(figsize=(12,12))
        nx.draw(self.__G,pos,with_labels=True, node_size = pesos*10000, ax=f.add_subplot(111))
        f.savefig(os.path.join(self.dir,'para.png'), format="PNG")
        return pr

    def ordenarFrozen(self, partition):
        """
        Método para ordenar el resultado de louvain de una forma genérica y que sea igual para todos los algoritmos
    
        Args:
            partition: resultado de la ejecución de louvain
        
        Return:
            particiones: lista que contiene las particiones de las comunidades
        """
        lista = list(partition.keys())
        lista2 = lista.copy()
        particiones = list()
        valores = list()
        for x in lista:
            valor = partition.get(x)
            lista2.remove(x)
            lista3=list()
            lista3.append(x)
            for y in lista2:
                if not partition.get(x) in valores:
                    if partition.get(y) == valor:
                        lista3.append(y)
                    frozen = frozenset(lista3)
            if not len(frozen) == 0:
                particiones.append(frozen)
            frozen = []
            valores.append(valor)
        return particiones
        
    def louvain(self):
        """
        Método que ejecuta el algoritmo de louvain y guarda la imagen de las comunidades generadas
    
        Return:
            lista con las particiones.
        """
        print('Com louvain')
        l = list()
        pos=nx.kamada_kawai_layout(self.__G)
        f = plt.figure(figsize=(12,12))
        nx.draw(self.__G,pos,with_labels=True)
        partition = community_louvain.best_partition(self.__G)
        particiones = self.ordenarFrozen(partition)
        for x in particiones:
            l.append(x)
            col = '#'+secrets.token_hex(3)
            nx.draw_networkx_nodes(self.__G,pos,nodelist=list(x),node_color=col)
        f.savefig(os.path.join(self.dir, 'louvain.png'), format="PNG")
        return l


    def greedyComunidad(self):
        """
        Método que devuelve las comunidades con el algoritmo greedy de Clauset-Newman-Moore

        Return:
            comunidades de Clauset-Newman-Moore
        """
        print('com greedy')
        l = list()
        pos=nx.kamada_kawai_layout(self.__G)
        f = plt.figure(figsize=(12,12))
        nx.draw(self.__G,pos,with_labels=True)
        for x in nx.algorithms.community.greedy_modularity_communities(self.__G):
            l.append(x)
            col = '#'+secrets.token_hex(3)
            nx.draw_networkx_nodes(self.__G,pos,nodelist=list(x),node_color=col)
        f.savefig(os.path.join(self.dir, 'greedyCom.png'), format="PNG")
        return l

    def kCliPerc(self, k):
        """
        Método que devuelve las comunidades de k-clique
        
        Args:
            k: valor k del k-clique
        Return:
            comunidades de k-clique
        """
        print('com kcliq')
        l = list()
        pos=nx.kamada_kawai_layout(self.__G)
        f = plt.figure(figsize=(12,12))
        nx.draw(self.__G,pos,with_labels=True)
        for x in nx.algorithms.community.k_clique_communities(self.__G, int(k)):
            l.append(x)
            col = '#'+secrets.token_hex(3)
            nx.draw_networkx_nodes(self.__G,pos,nodelist=list(x),node_color=col)
        f.savefig(os.path.join(self.dir,'kcliperc.png'), format="PNG")
        return l
        
    def girNew(self):
        """
        Método que devuelve las comunidades de girvan-newman
        
        Args:
            
        Return:
            comunidades de girvan-newman
        """
        print('com girvan')
        l = list()
        d = nx.algorithms.community.girvan_newman(self.__G)
        lista = list(tuple(sorted(c) for c in next(d)))
        pos=nx.kamada_kawai_layout(self.__G)
        f = plt.figure(figsize=(12,12))
        nx.draw(self.__G,pos,with_labels=True)
        for x in lista:
            l.append(x)
            col = '#'+secrets.token_hex(3)
            nx.draw_networkx_nodes(self.__G,pos,nodelist=list(x),node_color=col)
        f.savefig(os.path.join(self.dir,'girnew.png'), format="PNG")
        return l
        
    def roles(self,resul,nombre):
        """
        Método para detectar roles en comunidades de girvan-newman
        
        Args:
            
        Return:
            roles en comunidades de girvan-newman
        """
        z = self.obtenerZ(self.__G,resul)
        print('z obtenida')
        p, lista = self.obtenerP(self.__G, resul)
        print('p obtenida')
        pesos = self.__G.degree(weight='weight')
        zlist = list()
        plist = list()
        hubp = list()
        hubc = list()
        hubk = list()
        nhubu = list()
        nhubp = list()
        nhubc = list()
        nhubk = list()
        for t in pesos:
            k = t[0]
            pesoaux = list()
            aux = t[1]*12
            pesoaux.append(aux)
            nodo = list()
            nodo.append(k)
            if(not k in lista):
                zlist.append(z[k])
                plist.append(p[k])
                print('calculando a que rol pertenece...')
                if z[k] >= 2.5:
                    if(p[k] < 0.32):
                        hubp.append(k)
                        print('pertenece a hubp')
                    elif(p[k] < 0.75):
                        hubc.append(k)
                        print('pertenece a hubc')
                    else:
                        hubk.append(k)
                        print('pertenece a hubk')
                else:
                    if(p[k] > -0.02 and p[k] < 0.02):
                        nhubu.append(k)
                        print('pertenece a nhubu')
                    elif(p[k] < 0.625):
                        nhubp.append(k)
                        print('pertenece a nhubp')
                    elif(p[k] < 0.8):
                        nhubc.append(k)
                        print('pertenece a nhubc')
                    else:
                        nhubk.append(k)
                        print('pertenece a nhubk')
        roles = {'hubp':hubp,'hubc':hubc,'hubk':hubk,'nhubu':nhubu,'nhubp':nhubp,'nhubc':nhubc,'nhubk':nhubk, 'lista':lista}
        print('Obteniendo figura...')
        f = plt.figure(figsize=(10,10))
        plt.xlabel("Participation coefficient (P)",fontsize=15)
        plt.ylabel("Within-module degree (Z)",fontsize=15)

        y_min=-2 #valor mínimo del eje de la Y
        y_max=8 #valor máximo del eje de la Y

        limit_hub=2.5

        alpha=0.3

        plt.xlim(0, 1)
        plt.ylim(y_min,y_max)



        regiones_roles=[(y_min, limit_hub, 0, 0.05, 'black'),
                        (y_min, limit_hub, 0.05, 0.62, 'red'),
                        (y_min, limit_hub, 0.62, 0.8, 'green'),
                        (y_min, limit_hub, 0.8, 1, 'blue'),
                        (limit_hub, y_max, 0, 0.3, 'yellow'),
                        (limit_hub, y_max, 0.3, 0.75, 'purple'),
                        (limit_hub, y_max, 0.75, 1, 'grey')]

        for n_rol, (ymin, ymax, xmin, xmax, color) in enumerate(regiones_roles,1):
            
            plt.axhspan(ymin, ymax, xmin, xmax, facecolor=color, alpha=alpha, zorder=0)
            plt.text((xmax-xmin)/2+xmin,(ymax-ymin)/2+ymin,"R"+str(n_rol),
                    horizontalalignment='center',verticalalignment='center',fontsize=18, zorder=10)
            
        plt.scatter(plist,zlist, color='red', zorder=5)   
            
        f.savefig(os.path.join(self.dir,nombre), format="PNG")
        print('figura obtenida')
        return roles

    def rolesLouvain(self):
        """
        Método que ejecuta el algoritmo de Louvain para la detección de roles
    
        Return:
            diccionario con los roles generados
        """
        print('roles louvain')
        dictroles = dict()
        partition = community_louvain.best_partition(self.__G)
        print('particiones obtenidas')
        particiones = self.ordenarFrozen(partition)
        resul = self.devuelveComunidadesSeparadas(particiones, self.__G.copy())
        print('comunidades separadas obtenidas')
        dictroles = self.roles(resul,'roleslouvain.png')
        print('roles obtenidos')
        return dictroles
    
    def rolesGreedy(self):
        """
        Método que ejecuta el algoritmo de Clausset-Newman-Moore para la detección de roles
    
        Return:
            diccionario con los roles generados
        """
        print('roles greedy')
        dictroles = dict()
        particiones = list(nx.algorithms.community.greedy_modularity_communities(self.__G))
        print('particiones obtenidas')
        resul = self.devuelveComunidadesSeparadas(particiones, self.__G.copy())
        print('comunidades separadas obtenidas')
        dictroles = self.roles(resul,'rolesgreedy.png')
        print('roles obtenidos')
        return dictroles
    
    def roleskclique(self, k):
        """
        Método que ejecuta el algoritmo de K-clique para la detección de roles
    
        Return:
            diccionario con los roles generados
        """
        print('roles kcliq')
        dictroles = dict()
        particiones = list(nx.algorithms.community.k_clique_communities(self.__G, int(k)))
        print('particiones obtenidas')
        resul = self.devuelveComunidadesSeparadas(particiones, self.__G.copy())
        print('comunidades separadas obtenidas')
        dictroles = self.roles(resul,'roleskcliq.png')
        print('roles obtenidos')
        return dictroles
    
    def rolesGirvan(self):
        """
        Método que ejecuta el algoritmo de Girvan-Newman para la detección de roles
    
        Return:
            diccionario con los roles generados
        """
        print('roles girvan')
        dictroles = dict()
        d = nx.algorithms.community.girvan_newman(self.__G)
        particiones = list(tuple(sorted(c) for c in next(d)))
        print('particiones obtenidas')
        resul = self.devuelveComunidadesSeparadas(particiones, self.__G.copy())
        dictroles = self.roles(resul,'rolesgirvan.png')
        print('roles obtenidos')
        return dictroles

    def devuelveComunidadesSeparadas(self, resultado, grafo):
        """
        Método para generar un grafo a partir de las relaciones de los personajes en guiones de películas
    
        Args:
            resultado: lista con las particiones generadas en la detección de comunidades
            grafo: el grafo que tenemos creado
        
        Return:
            un grafo con todas las comunidades separadas unas de otras sin enlaces.
        """
        lista = list()
        resul = grafo.copy()
        contador = len(resultado)
        for i in range(0,contador):
            for j in resultado[i]:
                lista.append(j)
        for x in lista:
            for a in range(0,contador):
                if x in resultado[a]:
                    cont = a
            for y in lista:
                if not y in resultado[cont]:
                    if resul.has_edge(x,y):
                        resul.remove_edge(x,y)
        return resul

    def obtenerZ(self, grafo, resul):
        """
        Método para calcular el grado de la comunidad de cada nodo
        
        Args:
            grafo: red de personajes
        Return:
            grado de la comunidad de cada nodo
        """
        zi = dict()

        for c in nx.connected_components(resul):
            subgrafo = grafo.subgraph(c)
            pesos = subgrafo.degree()
            n = subgrafo.number_of_nodes()
            medksi = 0
            for peso in pesos:
                medksi = medksi + peso[1]/n
            desvksi = 0
            for peso in pesos:
                desvksi = desvksi + (peso[1]-medksi)**2
            desvksi = desvksi/n
            desvksi = desvksi**0.5
            if(desvksi == 0):
                for peso in pesos:
                    zi[peso[0]] = 0
            else:
                for peso in pesos:
                    zi[peso[0]] = (peso[1]-medksi)/desvksi
        return zi
    
    def obtenerP(self, grafo, resul):
        """
        Método para calcular el coeficiente de participacion de cada nodo
        
        Args:
            grafo: red de personajes
        Return:
            coeficiente de participacion de cada nodo
        """
        pi = dict()
        lista = list()
        pesos = grafo.degree()
        for peso in pesos:
            ki = peso[1]
            piaux = 0
            if(not ki == 0):
                for c in nx.connected_components(resul):
                    c.add(peso[0])
                    sub = grafo.subgraph(c)
                    pesosaux = sub.degree()
                    ksi = pesosaux[peso[0]]
                    piaux = piaux + (ksi/ki)**2 
                pi[peso[0]] = 1 - piaux
            else:
                lista.append(peso[0])
        return pi, lista
    '''
    DEMASIADO COSTE COMPUTACIONAL
    def modularidad(self,grafo, particion):
        """
        Método para calcular la modularidad
        
        Args:
            grafo: red de personajes
            particion: particion de nodos de la red
        Return:
            coeficiente de participacion de cada nodo
        """
        m = nx.number_of_edges(grafo)
        nodos = list(particion.keys())
        tot = 0
        for i in range(0,len(nodos)):
            for j in range(0,len(nodos)):
                if(particion[nodos[i]]==particion[nodos[j]]):
                    aux = (grafo.degree[nodos[i]]*grafo.degree[nodos[j]]/(2*m))
                    A = grafo.number_of_edges(nodos[i],nodos[j])
                    tot += A-aux
        return tot/(2*m)
    
    def girvan_newman(self,grafo):
        """
        Método para calcular la mejor comunidad por girvan-newman
        
        Args:
            grafo: red de personajes
        Return:
            mejor partincion
            modularidad
            numero de particiones
        """
        inicial = grafo.copy()
        mod = list()
        npart = list()
        part = dict()
        i=0
        for c in nx.connected_components(grafo):
            for j in c:
                part[j]=i
            i+=1
        npart.append(i)
        ultnpar = i
        modu = self.modularidad(inicial,part)
        mod.append(modu)
        mejormod = modu
        mejor = grafo.copy()
        while(nx.number_of_edges(grafo)>0):
            print("Calculando...")
            btwn = list(nx.edge_betweenness_centrality(grafo).items())
            mini = -1
            for i in btwn:
                if i[1]>mini:
                    enlaces = i[0]
                    mini=i[1]
            grafo.remove_edge(*enlaces)
            i=0
            part = dict()
            for c in nx.connected_components(grafo):
                for j in c:
                    part[j]=i
                i+=1
            if(i>ultnpar):
                ultnpar = i
                npart.append(i)
                modu = self.modularidad(inicial,part)
                mod.append(modu)
                if(modu>mejormod):
                    mejormod=modu
                    mejor = grafo.copy()
        return mejor,mod,npart
        '''
    ## Metodos para las obras de teatro
    def getCorpus(self):
        # obtenemos todas las metricas de los corpus
        metricas = requests.get("https://dracor.org/api/corpora?include=metrics").json()
        # iteramos por cada corpus, para seleccionar solamente aquellas que nos interesen
        lista=[]
        for i in metricas:
            corpus={}
            corpus["titulo"] = i['title']
            corpus["abr"] = i['name']
            corpus["obras"] = i['metrics']['plays']
            corpus["personajes"] = i['metrics']['characters']
            corpus["hombres"] = i['metrics']['male']
            corpus["mujeres"] = i['metrics']['female']
            corpus["fecha"] = i['metrics']['updated']
            lista.append(corpus)
        return lista

    def getPlays(self, corpus):
        # obtenemos todas las metricas de las obras
        metricas = requests.get("https://dracor.org/api/corpora/"+corpus+"/metadata").json()
        # iterate through corpus list and print information
        # add the number of plays to the print statement which is retrieved from the corpus metrics
        #print("Abbreviation: Corpus Name (Number of plays)")
        lista=[]
        for obra in metricas:
            diccionario={}
            diccionario["titulo"] = obra['title']
            
            '''
            if(corpus['normalizedGenre'] != None):
                print(corpus['normalizedGenre'])
                diccionario["genero"] = corpus['normalizedGenre']
            elif (corpus['subtitle'])!= None:
                diccionario["genero"] = corpus['subtitle']
            else:
                diccionario["genero"] = ""
            '''
            diccionario["autor"] = obra['firstAuthor']
            diccionario["personajes"] = obra['size']
            diccionario["fecha"] = obra['yearNormalized']
            diccionario["id"] = obra["playName"]
            lista.append(diccionario)
        return lista

    def diccionarioObras(self, corpus, obra):
        self.corpus = corpus
        self.obra = obra
        self.vaciarDiccionario()
        # obtenemos todas las metricas de los personajes de las obras 
        metricas = requests.get("https://dracor.org/api/corpora/"+corpus+"/play/"+obra+"/cast").json()
        # iterate through corpus list and print information
        # add the number of plays to the print statement which is retrieved from the corpus metrics
        #print("Abbreviation: Corpus Name (Number of plays)")
        for personaje in metricas:
            self.anadirPersonaje(personaje['id'],personaje['name'])
    
    def diccionarioGeneroApariciones(self):
        personajes = requests.get("https://dracor.org/api/corpora/"+self.corpus+"/play/"+self.obra+"/cast").json()
        diccionario={}
        escenas = requests.get("https://dracor.org/api/corpora/"+self.corpus+"/play/"+self.obra).json()
        for personaje in personajes:
            apariciones = list()
            for escena in escenas["segments"]:
                for nodo in escena["speakers"]:
                    if(nodo==personaje["id"]):
                        apariciones.append(escena["number"])
            diccionario[personaje['id']] = (int(personaje['numOfScenes']),personaje['gender'],apariciones)
        return diccionario
