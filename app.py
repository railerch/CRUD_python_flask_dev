# SE IMPORTAN LOS MODULOS PARA CREAR LA APLICACION
# render_template: para renderizar los archivos html
# send_from_directory: para servir los archivos locales de la aplicacion ya que no se accede a ellos con la url sino mediante una ruta
# request: para el manejo de peticiones HTTP
# redirect: para redireccionar hacia una ruta en especifico
# url_for: una alternativa a las rutas
# Ejm 1: <img src="{{ url_for('uploads', imagen=dato[3]) }}" alt=""/>
# Ejm 2: url_for('editar', variable=valor)
# flash: enviar mensajes de validacion

from flask import Flask
from flask import render_template, send_from_directory, request, redirect, url_for, flash
from flaskext.mysql import MySQL

from datetime import datetime
import os
from os.path import exists

# SE CREA UNA INSTANCIA DE FLASK EN LA VARIABLE APP
app = Flask(__name__)
app.secret_key = 'test'

# SE CREA EL ENLACE CON LA BD
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sistema'
mysql.init_app(app)

# SE CREA LA RUTA A LA CARPETA DE IMAGENES PARA RENDERIZARLAS CON FLASK AL INVOCARLAS
@app.route('/uploads/<imagen>')
def uploads(imagen):
    return send_from_directory('uploads', imagen)

# RUTA PARA LA CARPETA DE ESTILOS LOCALES
@app.route('/css/<archivo>')
def estilos(archivo):
    return send_from_directory('css', archivo)

# RUTA PARA LA CARPETA DE FUENTES
@app.route('/font/<fuente>')
def fuente(fuente):
    return send_from_directory('font', fuente)

# SE INDICA LA RUTA RAIZ DE LA APP
@app.route('/')
def index():

    sql = 'SELECT * FROM empleados;'
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)

    # OBTENER DATOS DE LA CONSULTA
    empleados = cursor.fetchall()

    conn.commit()

    return render_template('empleados/index.html', empleados=empleados)

# SE CREA UNA RUTA PARA CADA ACCION QUE DEVUELVA UN TEMPLATE
@app.route('/crear')
def crear():
    return render_template('empleados/crear.html')

# UNA RUTA PARA LA ACCION QUE INSERTE EL REGISTRO Y QUE LUEGO RENDERICE EL TEMPLATE INDICADO
@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['nombre']
    _correo = request.form['correo']
    _foto = request.files['foto']

    if _nombre == '' or _correo == '' or _foto == '':
        flash('Por favor complete todos los campos')
        return redirect(url_for('crear'))

    # NOMBRE PARA EL ARCHIVO DE IMAGEN
    now = datetime.now()
    tiempo = now.strftime('%Y%H%M%S')

    # CARGAR LA IMAGEN A LA CARPETA UPLOADS
    if _foto.filename != '':
        nuevoNombreFoto = tiempo + '_' + _foto.filename
        _foto.save('uploads/'+nuevoNombreFoto)

    # ARMAR QUERY CON UN BIND DE DATOS
    sql = 'INSERT INTO empleados (id, nombre, correo, foto) VALUES (NULL, %s, %s, %s);'
    datos = (_nombre, _correo, nuevoNombreFoto)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)  # EJECUTAR QUERY
    conn.commit()

    # return render_template('empleados/index.html')
    return redirect('/')

# EDITAR REGISTRO
@app.route('/editar/<int:id>')
def editar(id):

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM empleados WHERE id = %s', (id))
    empleado = cursor.fetchall()
    conn.commit()
    return render_template('empleados/editar.html', empleado=empleado)

# ACTUALIZAR REGISTRO
@app.route('/update', methods=['POST'])
def update():
    _id = request.form['id']
    _nombre = request.form['nombre']
    _correo = request.form['correo']
    _foto = request.files['foto']

    if _foto.filename != '':

        now = datetime.now()
        tiempo = now.strftime('%Y%H%M%S')

        _imagen = tiempo + '_' + _foto.filename
        _foto.save('uploads/' + _imagen)

    else:
        _imagen = request.form['imagenActual']

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('UPDATE empleados SET  nombre = %s, correo = %s, foto= %s WHERE id = %s',
                   (_nombre, _correo, _imagen, _id))
    conn.commit()

    return redirect('/')

# ELIMINAR REGISTRO
@app.route('/eliminar/<int:id>')
def eliminar(id):

    conn = mysql.connect()
    cursor = conn.cursor()

    # ELIMINAR IMAGEN DEL REGISTRO
    cursor.execute('SELECT foto FROM empleados WHERE id = %s', (id))
    imagen = cursor.fetchall()
    ruta = 'uploads/' + imagen[0][0]

    if exists(ruta):
        os.remove(ruta)
        
    # ELIMINAR REGISTRO
    cursor.execute('DELETE FROM empleados WHERE id = %s', (id))
    conn.commit()

    return redirect('/')

# SE INICIA LA APLICACION
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
