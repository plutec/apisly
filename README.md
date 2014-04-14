# apisly

API desarrollada en Python para el uso de Series.ly sin la necesidad de token de autenticación.

Actualmente soporta los siguientes procedimientos:

 - Login/Logout
 - "Mis series".
 - "Mis películas"
 - Links (capítulos y películas)
 - Notificaciones
 - Búsqueda
 - Más valoradas por los usuarios
 - Críticas
 - Estadísticas de visionado

Esta API forma parte de un proyecto algo más grande (que todavía no ha sido liberado, pero lo será en breve), por lo que está en continuo desarrollo. :D

Decir que la documentación está en español porque ya que se trata de una página principalmente de uso de gente hispana, no he creído conveniente hacerla en inglés.

## ¿Cómo utilizarla?

### Instalación y ejemplo
Descomprimir la librería en la carpeta del proyecto. Simple, no?

Cambiar el nombre de usuario y la contraseña en **examples.py**

```python
#Ejecutar uno de los ejemplos
python examples.py
```

### Import sly.py
```python
import sly
```

### Crear una instancia + login
```python
api = sly.APISLY(username='nombredeusuario', password='contraseña')
```

### Mis series
```python
print api.my_series()
```

### Mis películas
```python
print api.my_movies()
```

### Información de una serie
```python
print api.get_serie_info('7HV4DXUHE5', 1)
```

### Información de una película
```python
print api.get_film_info('NE2FYXX5KE', 2)
```

### Buscar
```python
print api.search('anillos')
```

### Ver los links de una película
```python
print api.get_links(1653, 2)
```

### Actividad de mis amigos
```python
print api.get_activity()
```

## Requisitos

    1. Python2.7+
    2. Python requests (>0.10) - python-requests.org - pip install beautifulsoup4
    3. BeautifulSoup4 - http://www.crummy.com/software/BeautifulSoup/- pip install beautifulsoup4

## Tests

    Los tests todavía no se han desarrollado.

## Contribuciones

    Siéntete libre de hacer las mejoras que creas oportunas y hacer un pull-requests.
    Todo el trabajo realizado hasta ahora ha sido mirando el código fuente de la página y con la ayuda del depurador de Google Chrome! :D
