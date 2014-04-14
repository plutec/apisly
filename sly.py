# -*- coding: iso-8859-15 -*-
import requests
import pickle
import time
import json
import os
from bs4 import BeautifulSoup

#Constants
SERIE = 1
MOVIE = 2
DOCU = 3
TVSHOW = 4
EPISODE = 5
SEASON = 6
USER = 7
SUBCOMMENT = 8
LISTA = 9
WEBSERIE = 10
NOTICIA = 11

STATUS = {
    1: 'Favorite',
    2: 'Pending',
    3: 'Viewed',
}

LANGUAGES = {
    'Catalán':1,
    'Castellano': 2,
    'Latino': 3,
    'Euskera': 4,
    'Gallego': 5,
    'Inglés': 6,
    'VO': 7,
    'Sin audio': 8,
}




class APISLY(object):
    username = None
    password = None
    session = None
    """
    Constructor.
    Params:
        username: str con el nombre de usuario o email
        password: str con la contraseña del usuario.
    Return:
        Objeto APISLY
    """
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        if self.username and self.password:
            self.login()

    """
    Login de usuario
    Params:
        username: str con el nombre de usuario o email, si no se le proporcionó 
            en el constructor
        password: str con la contraseña del usuario, si no se le proporcionó 
            en el constructor
    """
    def login(self, username=None, password=None):
        if not self.username and username:
            self.username = username
        if not self.username:
            raise Exception("Necesito el nombre de usuario!")
        if not self.password and password:
            self.password = password
        if not self.password:
            raise Exception("Necesito la contraseña de usuario!")

        self.session = requests.Session()
        response = self.session.post(url='http://www.series.ly/scripts/login/login.php', params={
                'lg_login':self.username,
                'lg_pass':self.password,
                'recordar':1,
        })

    @staticmethod
    def get_between(original, init_str, end_str, iteration=None):
        if not iteration:
            iteration = 1
        for i in range(iteration):
            original = original[original.find(init_str)+len(init_str):]
            end = original.find(end_str)
            to_ret = original[:end]
            original = original[end:]
        return to_ret

    """
    Desloguea al usuario
    Params:
        self, el Objeto
    Return:
        None
    """
    def logout(self):
        try:
            self.session.get(url='http://series.ly/scripts/login/logout.php')
        except:
            pass

    """
    Método privado para desnormalizar el estado de las películas/capítulos
    """
    def _denormalize_status(self, mediaType, status):

        if mediaType == SERIE or mediaType == TVSHOW:
            return status #Sigue este patron
        else:
            try:
                status = int(status)
            except:
                status = None
            if status == 1:
                return 2 #Favorita
            elif status == 2:
                return 3 #Pendiente
            elif status == 3:
                return 1 #Vista

    """
    Método privado para normalizar el estado de las películas/capítulos
    """
    def _normalize_status(self, mediaType, status):
        """
        Vamos a seguir el patron de:
        - 1 Favorita
        - 2 Pendiente
        - 3 Vista
        """
        if mediaType == SERIE or mediaType == TVSHOW:
            pass #Sigue este patron
        else:
            if status == 1: 
                return 3 #'Viewed'
            elif status == 2: 
                return 1 #'Favorite'
            elif status == 3:
                return 2 #Pending
        return None

    """
    Obtiene el estado en versión cadena de un medio.
    Params:
        self, el objeto.
        status, int con el estado del vídeo.
    Return:
        - Favorita
        - Pendiente
        - Vista
    """
    def media_status(self, status, mediaType=None):
        """
        Vista
        Pendiente
        Favorita
        """
        return STATUS[int(status)]

        lang_status1 = 'Favorita'
        lang_status2 = 'Pendiente'
        lang_status3 = 'Vista'

        if status == 1:
            return lang_status1
        if status == 2:
            return lang_status2
        if status == 3:
            return lang_status3


    """
    Obtiene un listado de mis series
    Params:
        self, el objeto
    Return:
        list of dicts
    """
    def my_series(self):
        """
        Obtiene un listado de mis series marcadas
        """
        response = self.session.get(url='http://www.series.ly/my-series/')
        text = response.text
        series = self.get_between(original=text, init_str='var mediaList = ',
                                              end_str=';')
        series = json.loads(series)
        media_info = self.get_between(original=text, init_str='$myMedia = ',
                                  end_str=';')
        media_info = json.loads(media_info)
        media_info_dict = dict()
        for info in media_info:
            media_info_dict[info['idm']] = info
        image_pattern = 'http://cdn.opensly.com/series/%s.jpg'

        to_ret = list()
        for serie in series:
            id2 = serie['id2']
            try:
                serie.update(media_info_dict[id2])
            except:
                pass

            serie['name'] = serie['mN']
            del serie['mN']
            serie['mediaType'] = serie['mT']
            del serie['mT']
            serie['status'] = self._normalize_status(
                                                  mediaType=serie['mediaType'], 
                                                  status=serie['mS'])
            del serie['mS']
            serie['image'] = image_pattern % serie['id']
            to_ret.append(serie)
        
        return to_ret


    def change_status(self, idm, mediaType, newStatus):
        #Testing
        """
        newStatus 2
        mediaType = 2
        idm = 19647
        """
        #newstatus denormalize 
        #Pelicula, favorita, newStatus 2
        #Pelicula, vista, newStatus 1
        #Pelicula, Pendiente, newStatus 3

        #changeStatusMediaThumbs('12071', 1, mediaType)
        params = {'idm':idm,
                  'newStatus':self._denormalize_status(mediaType=mediaType,
                                                       status=newStatus),
                  'mediaType':mediaType}

        url = "http://series.ly/scripts/media/changeStatus.php"

        self.session.post(url=url,
                          data=params)

    """
    Obtiene un listado de mis películas
    Params:
        self, el objeto
    Return:
        list of dicts
    """
    def my_movies(self):
        """
        Obtiene mis peliculas
        """
        response = self.session.get(url='http://www.series.ly/my-movies/')
        #var mediaList = [{"id":"2V675K5Y2R","id2":589,"mN":"The Big Bang Theory","nS":7,"nE":169,"mT":1}];
        #nS es el status
        text = response.text
       
        movies = self.get_between(original=text, init_str='var mediaList = ',
                                              end_str=';')
        movies = json.loads(movies)
        media_info = self.get_between(original=text, init_str='$myMedia = ',
                                  end_str=';')
        media_info = json.loads(media_info)
        media_info_dict = dict()
        for info in media_info:
            media_info_dict[info['idm']] = info
        
        image_pattern = 'http://cdn.opensly.com/pelis/%s.jpg'
        to_ret = list()
        for movie in movies:
            #print "MOVIE: %s" % repr(movie)
            id2 = movie['id2']
            try:
                movie.update(media_info_dict[id2])
            except:
                pass

            movie['name'] = movie['mN']
            del movie['mN']
            movie['mediaType'] = movie['mT']
            del movie['mT']
            movie['status'] = self._normalize_status(
                                                mediaType=movie['mediaType'], 
                                                status=movie['mS'])
            del movie['mS']
            movie['image'] = image_pattern % movie['id']
            to_ret.append(movie)
        
        #mS es el status
        return to_ret

    """
    Obtiene la información de una serie.
    Params:
        self, el objeto.
        id_media, int que identifica a cada serie. Debe tener un formato 
            similar a 2V675K5Y2R.
        mediaType, int que indica el tipo de medio.
    Return:
        dict con información sobre la serie, temporadas y capítulos.
    """
    def get_serie_info(self, id_media, mediaType):
        """
        Obtiene informacion de una serie concreta
        """
        #id_media = 2V675K5Y2R
        timestamp = int(time.time())
        response = self.session.get(url='http://series.ly/scripts/media/mediaInfo.php',
            params = {'mediaType': mediaType,
                      'id_media': id_media,
                      'v': timestamp})
        to_ret = response.json()

        url = 'http://series.ly/series/serie-%s' % id_media
        response = self.session.get(url=url)
        ep_viewed = self.get_between(original=response.text, 
                                 init_str='var myEpViewed = \'', 
                                 end_str='\';')
        ep_viewed = json.loads(ep_viewed)
        
        for number, episodes in to_ret['episodes'].iteritems():
            counter = 0
            for episode in episodes:
                if ep_viewed.has_key(str(episode['idc'])):
                    new_episode = episode
                    #print "ENTRA"
                    new_episode['viewed'] = True
                    to_ret['episodes'][number][counter] = new_episode
                del episode['mediaType_media']
                counter += 1

        return to_ret
        

    """
    Permite realizar una búsqueda por palabras
    Params:
        self, el objeto.
        search_term, str del término a buscar. Puede ser completo o parcial.
    """
    def search(self, search_term):
        response = self.session.get(
                        url='http://series.ly/scripts/search/search.php',
                        params= {'s': search_term}
                    )

        text = response.text
        start_string = 'slySearch.init({"data":'
        end_string = ',"limit":25,"page":0});'
        start = text.find(start_string)
        text = text[start+len(start_string):]
        end = text.find(end_string)
        text = text[:end+len(end_string)]
        last_sign = text.rfind(']')
        text = text[:last_sign+1]
        json_content = json.loads(text)

        to_ret = list()
        for element in json_content:
            if element.has_key('id_media'):
                element['idMedia'] = element['id_media']
                del element['id_media']
            to_ret.append(element)

        return to_ret


    """
    Obtiene los detalles de una película.
    Params:
        self, el objeto.
        idMedia, str que identifica a la película. Tiene un formato 
            similar a 9WAS7NEHUX
        mediaType, str/int que identifica el tipo de medio.
    """
    def get_film_info(self, idMedia, mediaType):
        #id_media is 9WAS7NEHUX
        #mediaType is 2

        response = self.session.get(
                    url = 'http://www.series.ly/scripts/media/mediaInfo.php',
                    params = {'mediaType': mediaType,
                              'id_media': idMedia,
                              'v': int(time.time())})
        to_ret = response.json()
        to_ret['idMedia'] = to_ret['id_media']
        del to_ret['id_media']
        return to_ret

    """
    Marca un vídeo (película o capítulo) como visto o no visto.
    Params:
        self, el objeto
        idm, int que define el vídeo. Debe ser un número entero.
        view, bool. True marca como visto, False marca como no visto.
    Return:
        None
    """
    def toggle_view(self, idm, view):
        if view:
            view = 1
        else:
            view = 0
        self.session.post(url='http://series.ly/scripts/ajax/episodeToggle.php',
                          params={'idc':idm, 'check': view})

        return None
    """
    Obtiene el listado de enlaces de un episodio o una pelicula
    Params:
        self, el objeto
        idm, int que define el vídeo a ver. Debe ser un número entero.
        mediaType, int que identifica el tipo de medio.
    """
    def get_links(self, idm, mediaType):
        try:
            mediaType = int(mediaType)
        except:
            raise Exception("mediaType must be integer")

        if mediaType == SERIE or mediaType == TVSHOW:
            mediaType = 5

        url = 'http://www.series.ly/scripts/media/epLinks.php'
        params = {'mediaType' : mediaType,
                  'idc': idm,
                  'time' : '%d.txt' % int(time.time()) }

        response = self.session.get(url=url,
                                    params=params)
        json_value = response.json()
        to_ret = list()
        for element in json_value:
            element['idVideo'] = element['idv']
            del element['idv']
            to_ret.append(element)
        return to_ret

    """
    Obtiene el enlace del gestor de vídeos 
        (MagnoVideo, YouTube, allmyvideos, ...)
    Params:
        self, el objeto
        idVideo, int que identifica a cada vídeo
        mediaType, int tipo de medio.
    Return:
        str con el enlace.
    """
    def get_video_link(self, idVideo, mediaType): #Youtube link or similar
        """
        Obtiene el enlace del player
        """
        try:
            mediaType = int(mediaType)
        except:
            return "mediaType must be integer"
        if mediaType == SERIE or mediaType == TVSHOW:
            mediaType = 5
        response = self.session.get(
                            url='http://series.ly/scripts/media/gotoLink.php',
                            params= {'idv': idVideo, 'mediaType' : mediaType})

        return response.url

    """
    Obtiene las notificaciones del usuario, si las tuviera.
    Params:
        self, el objeto
    Return:
        dict con la información.
        None en caso de error.
    """
    def get_notifications(self):
        """
        Mira las notificaciones
        """
        try:
            url_query = 'http://www.series.ly/scripts/notifications/get.php'
            response = self.session.get(url=url_query)
            return response.json()
        except:
            return None

    """
    Obtiene la actividad de los amigos, películas vistas, series, ...
    Params:
        self, el objeto.
    Return:
        dict con el resultado.
    """
    def get_activity(self):
        
        response =self.session.get(
                     url='http://series.ly/scripts/activity/activitylist.php',
                     params={'type':'connections'})
        return response.json()


    def _parse_catalogue(self, content):
        pass

    """
    Obtiene los recursos más valorados por los usuarios
    Params:
        self, el objeto
        mediaType: int que representa el tipo de medio (SERIE, MOVIE, ...)
    Returns:
        Lista de diccionarios con el nombre, imagen, idMedia y mediaType
    """
    def get_most_valuated(self, mediaType):
        #mediaType = SERIE, MOVIE, ...
        try:
            mediaType = int(mediaType)
        except:
            raise Exception("MediaType must be an integer")

        url_base = 'http://series.ly/%s'

        url = 'http://series.ly/scripts/media/allMedia.php?show=%d' % mediaType
        response = self.session.get(url=url)
        soup = BeautifulSoup(response.text)
        ol = soup.find('ol', {'class':'thumbsList'})
        lis = ol.findAll('li')
        to_ret = list()
        for li in lis:
            to_insert = dict()
            to_insert['name'] = li.find('div', {'class':'thumbTitleName'}).text
            to_insert['thumbnail'] = li.find('img')['src']
            href = li.find('a', {'class':'ajaxSend'})['href']
            if mediaType == MOVIE:
                src = url_base % href
                response_movie = self.session.get(url=src)
                idMedia = self.get_between(original=response_movie.text,
                       init_str='id="stateMedia_0" onclick="changeStatusMedia(',
                       end_str=',0,')
                to_insert['idMedia'] = int(idMedia)
            to_insert['id'] = href.split('-')[1]
            to_insert['mediaType'] = mediaType
            to_ret.append(to_insert)
        return to_ret

    """
    Obtiene las críticas de una serie.
    Params:
        self, el objeto
        idMedia, int identificativo de la serie
        page, int (opcional) que indica el número de página. 
            Si no se indica, es la 0
    Returns:
        dict con las críticas de la serie.
    """
    def get_serie_reviews(self, idMedia, page=None):
        if not page:
            page = 0

        url = 'http://series.ly/scripts/comments/ajaxlist.php?id=1-%d&\
        type=media&sort=newest&page=%d' % (idMedia, page)
        response = self.session.get(url=url)
        return response.json()

    """
    Obtiene las estadísticas de visionado de los últimos 15 días de una serie 
        o película
    Params:
        self, el objeto
        idMedia, int identificador del contenido.
        mediaType, int identificador del tipo de contenido
    Returns:
        dict con los días y visionados.
    """
    def get_stats(self, idMedia, mediaType):
        
        url = 'http://series.ly/scripts/media/mediaStats.php'
        params = {'mediaType': mediaType,
                  'idm': idMedia}
        response = self.session.post(url=url, params=params)

        return response.json()

    """
    Obtiene las noticias para un contenido.
    Params:
        self, el objeto
        idMedia, int identificador del contenido.
        mediaType, int identificador del tipo de contenido.
    Returns:
        dict con las diferentes noticias relacionadas con el contenido.
    """
    def get_news(self, idMedia, mediaType):
        url = 'http://series.ly/scripts/news/ajaxlist.php'

        params = {'ac':'getFicha',
                  'tipo':mediaType,
                  'media':idMedia}
        response = self.session.post(url=url, data=params)

        return response.json()