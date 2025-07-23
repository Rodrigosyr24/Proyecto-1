# 1. Importar las herramientas necesarias
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify # type: ignore
from flask_login import LoginManager, login_user, logout_user, login_required, current_user  # type: ignore
from extensions import db
from models import Usuario, Perfil, Empresa, Experiencia, Educacion, Proyecto, Enlace, Habilidad, HabilidadesPerfil, Idioma, IdiomasPerfil, OfertaEmpleo,  Postulacion, Propuesta, Notificacion # type: ignore
from werkzeug.utils import secure_filename # type: ignore
from sqlalchemy import or_

# 2. Crear la instancia de la aplicación Flask
app = Flask(__name__)

# 3. Configuración de la Base de Datos y la Aplicación
# (He dejado tu contraseña como la pusiste)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Rodrigosyr24082004#@localhost:5432/auracv_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mi_llave_secreta_super_aleatoria'

# --- NUEVO: CONFIGURACIÓN PARA LA SUBIDA DE ARCHIVOS ---
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 4. Conectar nuestra instancia 'db' con la aplicación Flask
db.init_app(app)

# 5. Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'portal_candidatos' 

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# 6. Crear TODAS las tablas en la base de datos si no existen
with app.app_context():
    db.create_all()
    

# --- NUEVA FUNCIÓN AUXILIAR PARA VALIDAR ARCHIVOS ---
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ======================================================
#  RUTAS DE LA APLICACIÓN
# ======================================================

# Ruta para la búsqueda global
@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('pagina_de_inicio'))
    if current_user.is_authenticated and current_user.tipo_usuario == 'empresa':
        return redirect(url_for('dashboard_empresa', q=query))
    else:
        return redirect(url_for('busqueda_empleos', q=query))

# --- Rutas de Autenticación ---

@app.route('/portal-candidatos', methods=['GET', 'POST'])
def portal_candidatos():
    if request.method == 'POST':
        if 'login-email' in request.form:
            email = request.form.get('login-email')
            password = request.form.get('login-password')
            usuario = Usuario.query.filter_by(email=email, tipo_usuario='candidato').first()
            if usuario and usuario.check_password(password):
                login_user(usuario)
                return redirect(url_for('mi_perfil'))
            else:
                flash('Correo electrónico o contraseña incorrectos.', 'error')
                return redirect(url_for('portal_candidatos'))
        elif 'signup-email' in request.form:
            email = request.form.get('signup-email')
            password = request.form.get('signup-password')
            
            # --- LÓGICA DE REGISTRO MEJORADA ---
            nuevo_usuario = Usuario(email=email, tipo_usuario='candidato')
            nuevo_usuario.set_password(password)
            
            # Creamos un perfil vacío y lo asociamos al nuevo usuario
            nuevo_perfil = Perfil(usuario=nuevo_usuario)
            
            db.session.add(nuevo_usuario)
            db.session.add(nuevo_perfil)
            db.session.commit()
            
            flash('¡Cuenta creada con éxito! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('portal_candidatos'))
    return render_template('portal_empleados.html', body_class='auth-page-dark')

@app.route('/portal-empresas', methods=['GET', 'POST'])
def portal_empresas():
    if request.method == 'POST':
        if 'login-email' in request.form:
            email = request.form.get('login-email')
            password = request.form.get('login-password')
            usuario = Usuario.query.filter_by(email=email, tipo_usuario='empresa').first()
            
            if usuario and usuario.check_password(password):
                login_user(usuario)
                return redirect(url_for('dashboard_empresa'))
            else:
                flash('Correo electrónico o contraseña incorrectos.', 'error')
                return redirect(url_for('portal_empresas'))
        elif 'signup-email' in request.form:
            email = request.form.get('signup-email')
            password = request.form.get('signup-password')
            nombre_empresa = request.form.get('signup-name') # Obtenemos el nombre de la empresa
            
            # --- LÓGICA DE REGISTRO MEJORADA ---
            nuevo_usuario = Usuario(email=email, tipo_usuario='empresa')
            nuevo_usuario.set_password(password)
            
            # Creamos un perfil de empresa vacío y lo asociamos
            nueva_empresa = Empresa(usuario=nuevo_usuario, nombre_empresa=nombre_empresa)
            
            db.session.add(nuevo_usuario)
            db.session.add(nueva_empresa)
            db.session.commit()

            flash('¡Cuenta de empresa creada con éxito! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('portal_empresas'))
    return render_template('portal_empresas.html', body_class='auth-page-dark')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('pagina_de_inicio'))

# --- Rutas Públicas y Protegidas ---

@app.route('/')
def pagina_de_inicio():
    return render_template('index.html')

# --- RUTA DE BÚSQUEDA DE EMPLEOS (VERSIÓN FINAL CON FILTROS) ---
@app.route('/ofertas')
def busqueda_empleos():
    # 1. Empezamos con una consulta base que obtiene todas las ofertas activas
    query = OfertaEmpleo.query.filter_by(activa=True)

    # 2. Obtenemos los parámetros de los filtros desde la URL
    keywords = request.args.get('keywords')
    location = request.args.get('location')
    experience = request.args.get('exp')
    # ... (y así con los demás filtros)

    # 3. Aplicamos los filtros a la consulta si existen
    if keywords:
        # Buscamos las palabras clave en el título, descripción o nombre de la empresa
        query = query.filter(or_(
            OfertaEmpleo.titulo.ilike(f'%{keywords}%'),
            OfertaEmpleo.descripcion.ilike(f'%{keywords}%'),
            Empresa.nombre_empresa.ilike(f'%{keywords}%')
        )).join(Empresa)

    if location:
        query = query.filter(OfertaEmpleo.ubicacion.ilike(f'%{location}%'))

    if experience:
        if experience == '0-2':
            query = query.filter(OfertaEmpleo.experiencia_total_min <= 2)
        elif experience == '3-5':
            query = query.filter(OfertaEmpleo.experiencia_total_min.between(3, 5))
        elif experience == '6-10':
            query = query.filter(OfertaEmpleo.experiencia_total_min.between(6, 10))
        elif experience == '10-plus':
            query = query.filter(OfertaEmpleo.experiencia_total_min > 10)

    # 4. Ejecutamos la consulta final y la pasamos a la plantilla
    lista_de_ofertas = query.order_by(OfertaEmpleo.fecha_publicacion.desc()).all()
    
    return render_template('busqueda_empleos.html', ofertas=lista_de_ofertas)


@app.route('/mi-perfil')
@login_required
def mi_perfil():
    # 'current_user' ya tiene acceso al perfil gracias a nuestras relaciones en models.py
    # Simplemente pasamos el objeto 'perfil' a la plantilla.
    perfil = current_user.perfil
    return render_template('mi_perfil.html', perfil=perfil)

# --- RUTA DE EDICIÓN DE PERFIL MEJORADA ---
@app.route('/mi-perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    if current_user.tipo_usuario != 'candidato':
        return redirect(url_for('pagina_de_inicio'))

    perfil = current_user.perfil

    if request.method == 'POST':
        # Lógica para guardar la información personal (Pestaña 1)
        perfil.nombre_completo = request.form.get('nombre_completo')
        perfil.titular = request.form.get('titular')
        perfil.resumen = request.form.get('resumen')
        perfil.telefono = request.form.get('telefono')
        
        db.session.commit()
        flash('¡Tu información personal ha sido actualizada!', 'success')
        return redirect(url_for('mi_perfil'))

    # Si es GET, cargamos la página con toda la información del perfil
    return render_template('editar_perfil.html', 
                            experiencias=current_user.perfil.experiencias,
                            educacion=current_user.perfil.educacion,
                            proyectos=current_user.perfil.proyectos,
                            enlaces=current_user.perfil.enlaces)

# --- NUEVAS RUTAS PARA AÑADIR ITEMS ---

@app.route('/experiencia/agregar', methods=['POST'])
@login_required
def agregar_experiencia():
    if current_user.tipo_usuario == 'candidato':
        cargo = request.form.get('exp-title')
        empresa = request.form.get('exp-company')
        nueva_experiencia = Experiencia(cargo=cargo, empresa=empresa, perfil=current_user.perfil)
        db.session.add(nueva_experiencia)
        db.session.commit()
        flash('¡Experiencia añadida con éxito!', 'success')
    return redirect(url_for('editar_perfil'))

@app.route('/educacion/agregar', methods=['POST'])
@login_required
def agregar_educacion():
    if current_user.tipo_usuario == 'candidato':
        institucion = request.form.get('edu-institution')
        titulo = request.form.get('edu-degree')
        nueva_educacion = Educacion(institucion=institucion, titulo=titulo, perfil=current_user.perfil)
        db.session.add(nueva_educacion)
        db.session.commit()
        flash('Formación académica añadida con éxito!', 'success')
    return redirect(url_for('editar_perfil'))

@app.route('/proyecto/agregar', methods=['POST'])
@login_required
def agregar_proyecto():
    if current_user.tipo_usuario == 'candidato':
        nombre = request.form.get('project-title')
        tecnologias = request.form.get('project-tech')
        nuevo_proyecto = Proyecto(nombre_proyecto=nombre, tecnologias=tecnologias, perfil=current_user.perfil)
        db.session.add(nuevo_proyecto)
        db.session.commit()
        flash('¡Proyecto añadido con éxito!', 'success')
    return redirect(url_for('editar_perfil'))

# --- RUTA MEJORADA PARA GUARDAR HABILIDADES ---
@app.route('/habilidades/guardar', methods=['POST'])
@login_required
def guardar_habilidades():
    if current_user.tipo_usuario == 'candidato':
        perfil = current_user.perfil
        
        # --- Procesar Habilidades Técnicas ---
        HabilidadesPerfil.query.filter_by(id_perfil=perfil.id).delete()
        nombres_habilidades = request.form.getlist('habilidades')
        
        for nombre in nombres_habilidades:
            habilidad = Habilidad.query.filter_by(nombre=nombre).first()
            if not habilidad:
                habilidad = Habilidad(nombre=nombre)
                db.session.add(habilidad)
            nueva_habilidad_perfil = HabilidadesPerfil(perfil=perfil, habilidad=habilidad)
            db.session.add(nueva_habilidad_perfil)

        # --- Procesar Idiomas ---
        IdiomasPerfil.query.filter_by(id_perfil=perfil.id).delete()
        nombres_idiomas = request.form.getlist('idiomas')
        
        for nombre in nombres_idiomas:
            nivel = request.form.get(f'idioma_nivel_{nombre}')
            idioma = Idioma.query.filter_by(nombre=nombre).first()
            if not idioma:
                idioma = Idioma(nombre=nombre)
                db.session.add(idioma)
            nuevo_idioma_perfil = IdiomasPerfil(perfil=perfil, idioma=idioma, nivel=nivel)
            db.session.add(nuevo_idioma_perfil)

        db.session.commit()
        flash('¡Habilidades e idiomas guardados con éxito!', 'success')
        
    return redirect(url_for('editar_perfil'))

@app.route('/enlace/agregar', methods=['POST'])
@login_required
def agregar_enlace():
    if current_user.tipo_usuario == 'candidato':
        nombre = request.form.get('nombre')
        url = request.form.get('url')
        nuevo_enlace = Enlace(nombre=nombre, url=url, perfil=current_user.perfil)
        db.session.add(nuevo_enlace)
        db.session.commit()
        flash('¡Enlace añadido con éxito!', 'success')
    return redirect(url_for('editar_perfil'))

@app.route('/enlace/eliminar/<int:enlace_id>', methods=['POST'])
@login_required
def eliminar_enlace(enlace_id):
    enlace_a_eliminar = Enlace.query.get_or_404(enlace_id)
    if enlace_a_eliminar.perfil.id == current_user.perfil.id:
        db.session.delete(enlace_a_eliminar)
        db.session.commit()
        flash('Enlace eliminado.', 'success')
    return redirect(url_for('editar_perfil'))

# --- RUTA DE MIS POSTULACIONES (MEJORADA) ---
@app.route('/mis-postulaciones')
@login_required
def mis_postulaciones():
    # Nos aseguramos de que solo los candidatos puedan ver esta página
    if current_user.tipo_usuario != 'candidato':
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('pagina_de_inicio'))

    # Buscamos todas las postulaciones del perfil del usuario actual, ordenadas por fecha
    postulaciones_del_usuario = Postulacion.query.filter_by(id_perfil=current_user.perfil.id).order_by(Postulacion.fecha_postulacion.desc()).all()
    
    # Pasamos la lista de postulaciones a la plantilla
    return render_template('mis_postulaciones.html', postulaciones=postulaciones_del_usuario)


# --- RUTA DE PROPUESTAS (MEJORADA) ---
@app.route('/propuestas')
@login_required
def propuestas():
    # Nos aseguramos de que solo los candidatos puedan ver esta página
    if current_user.tipo_usuario != 'candidato':
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('pagina_de_inicio'))

    # Buscamos todas las propuestas recibidas por el perfil del usuario actual
    propuestas_recibidas = current_user.perfil.propuestas_recibidas
    
    # Pasamos la lista de propuestas a la plantilla
    return render_template('propuestas.html', propuestas=propuestas_recibidas)

# --- NUEVA RUTA PARA ENVIAR UNA PROPUESTA ---
@app.route('/propuesta/enviar/<int:perfil_id>', methods=['POST'])
@login_required
def enviar_propuesta(perfil_id):
    # Nos aseguramos de que solo las empresas puedan enviar propuestas
    if current_user.tipo_usuario != 'empresa':
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('pagina_de_inicio'))

    # Buscamos el perfil del candidato al que se le enviará la propuesta
    perfil_destino = Perfil.query.get_or_404(perfil_id)
    
    # Obtenemos el mensaje del formulario del modal
    mensaje = request.form.get('mensaje')

    if mensaje:
        # Creamos la nueva propuesta
        nueva_propuesta = Propuesta(
            mensaje=mensaje,
            empresa=current_user.empresa, # La empresa que envía
            perfil=perfil_destino        # El perfil que recibe
        )
        db.session.add(nueva_propuesta)
        
        # 2. (NUEVO) Creamos la notificación para el candidato
        texto_notificacion = f"¡Has recibido una nueva propuesta de <strong>{current_user.empresa.nombre_empresa}</strong>!"
        
        nueva_notificacion = Notificacion(
            texto=texto_notificacion,
            id_usuario=perfil_destino.id_usuario,
            # El enlace llevará al candidato a su página de propuestas
            enlace_url=url_for('propuestas') 
        )
        db.session.add(nueva_notificacion)
        
        db.session.commit()
        flash('¡Propuesta enviada con éxito!', 'success')
    else:
        flash('El mensaje no puede estar vacío.', 'error')

    # Redirigimos de vuelta al panel de la empresa
    return redirect(url_for('dashboard_empresa'))

# --- RUTA DEL PANEL DE EMPRESA (CON FILTROS) ---
@app.route('/dashboard-empresa')
@login_required
def dashboard_empresa():
    if current_user.tipo_usuario != 'empresa':
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('pagina_de_inicio'))

    # 1. Empezamos con una consulta base que obtiene todos los perfiles
    query = Perfil.query

    # 2. Obtenemos los parámetros de los filtros
    keywords = request.args.get('keywords')
    location = request.args.get('location')
    # (Aquí añadiríamos la lógica para los demás filtros como años de experiencia)

    # 3. Aplicamos los filtros a la consulta si existen
    if keywords:
        query = query.filter(or_(
            Perfil.nombre_completo.ilike(f'%{keywords}%'),
            Perfil.titular.ilike(f'%{keywords}%')
            # (Aquí podríamos añadir la búsqueda por habilidades)
        ))
    
    if location:
        query = query.filter(Perfil.ubicacion.ilike(f'%{location}%'))

    # 4. Ejecutamos la consulta final
    lista_de_perfiles = query.all()
    
    # Obtenemos las ofertas de la empresa actual para el panel derecho
    ofertas_de_la_empresa = current_user.empresa.ofertas

    # 5. Pasamos las listas a la plantilla.
    return render_template('dashboard_empresa.html', 
                            perfiles=lista_de_perfiles, 
                            ofertas=ofertas_de_la_empresa)

# --- RUTA PARA PUBLICAR OFERTA (VERSIÓN FINAL) ---
@app.route('/publicar-oferta', methods=['GET', 'POST'])
@login_required
def publicar_oferta():
    if current_user.tipo_usuario != 'empresa':
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('pagina_de_inicio'))

    if request.method == 'POST':
        # --- Obtener datos de texto y numéricos ---
        titulo = request.form.get('job-title')
        ubicacion = request.form.get('location')
        tipo_contrato = request.form.get('contract-type')
        descripcion = request.form.get('job-description')
        responsabilidades = request.form.get('responsibilities')
        experiencia_total_min = request.form.get('total-experience')
        salario_min = request.form.get('salary-min')
        salario_max = request.form.get('salary-max')

        # --- Crear la instancia de la oferta ---
        nueva_oferta = OfertaEmpleo(
            titulo=titulo,
            ubicacion=ubicacion,
            tipo_contrato=tipo_contrato,
            descripcion=descripcion,
            responsabilidades=responsabilidades,
            experiencia_total_min=int(experiencia_total_min) if experiencia_total_min else None,
            salario_min=int(salario_min) if salario_min else None,
            salario_max=int(salario_max) if salario_max else None,
            empresa=current_user.empresa
        )

        # --- Procesar y asociar Habilidades ---
        nombres_habilidades = request.form.getlist('habilidades')
        for nombre in nombres_habilidades:
            habilidad = Habilidad.query.filter_by(nombre=nombre).first()
            if not habilidad:
                habilidad = Habilidad(nombre=nombre)
                db.session.add(habilidad)
            nueva_oferta.habilidades_requeridas.append(habilidad)

        # --- Procesar y asociar Idiomas ---
        nombres_idiomas = request.form.getlist('idiomas')
        for nombre in nombres_idiomas:
            idioma = Idioma.query.filter_by(nombre=nombre).first()
            if not idioma:
                idioma = Idioma(nombre=nombre)
                db.session.add(idioma)
            nueva_oferta.idiomas_requeridos.append(idioma)

        # Guardar todo en la base de datos
        db.session.add(nueva_oferta)
        db.session.commit()

        flash('¡Tu oferta de empleo ha sido publicada con éxito!', 'success')
        return redirect(url_for('perfil_empresa'))

    return render_template('publicar_oferta.html')

@app.route('/api/perfil/<int:perfil_id>')
@login_required
def get_perfil_data(perfil_id):
    # Buscamos el perfil en la base de datos
    perfil = Perfil.query.get_or_404(perfil_id)
    
    # --- LÓGICA PARA CREAR LA NOTIFICACIÓN ---
    # Creamos una notificación para el dueño del perfil que está siendo visto.
    texto_notificacion = f"La empresa {current_user.empresa.nombre_empresa} ha visto tu perfil."
    
    # (En una app real, verificaríamos que no se creen notificaciones duplicadas muy seguido)
    
    nueva_notificacion = Notificacion(
        texto=texto_notificacion,
        id_usuario=perfil.id_usuario,
        # El enlace podría llevar al perfil de la empresa que lo vio
        enlace_url=url_for('perfil_empresa_publico', empresa_id=current_user.empresa.id) 
    )
    db.session.add(nueva_notificacion)
    db.session.commit()
    # --- FIN DE LA LÓGICA DE NOTIFICACIÓN ---
    
    # --- CONSTRUIMOS EL PERFIL COMPLETO ---
    experiencias_data = []
    for exp in perfil.experiencias:
        experiencias_data.append({
            'cargo': exp.cargo,
            'empresa': exp.empresa
            # (podríamos añadir fechas aquí también)
        })
    
    # Creamos un "diccionario" con la información que queremos mostrar
    perfil_data = {
        'nombre_completo': perfil.nombre_completo,
        'titular': perfil.titular,
        'foto_url': perfil.foto_perfil_url or '/static/img/perfil_placeholder.png',
        'email': perfil.usuario.email,
        'resumen': perfil.resumen,
        # (Aquí añadiríamos la experiencia, educación, etc.)
    }
    # Convertimos el diccionario a formato JSON y se lo enviamos al navegador
    return jsonify(perfil_data)

# --- NUEVA RUTA PÚBLICA PARA EL PERFIL DE EMPRESA ---
# (Necesaria para que los enlaces de las notificaciones funcionen)
@app.route('/empresa/<int:empresa_id>')
def perfil_empresa_publico(empresa_id):
    empresa = Empresa.query.get_or_404(empresa_id)
    return render_template('perfil_empresa.html', empresa=empresa)

# --- RUTA PARA VER EL PERFIL PÚBLICO DE LA EMPRESA (MEJORADA) ---
@app.route('/empresa/perfil')
@login_required
def perfil_empresa():
    # En una app real, esta ruta podría ser pública y recibir un ID de la empresa.
    # Por ahora, para simplificar, muestra el perfil de la empresa del usuario logueado.
    if current_user.tipo_usuario != 'empresa':
        # Si un candidato intenta ver esta página, lo redirigimos
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('pagina_de_inicio'))

    # Gracias a las relaciones de SQLAlchemy, al obtener la empresa,
    # también tenemos acceso a sus ofertas (empresa.ofertas).
    empresa = current_user.empresa
    return render_template('perfil_empresa.html', empresa=empresa)

# --- RUTA PARA EDITAR EL PERFIL DE LA EMPRESA (MEJORADA) ---
@app.route('/empresa/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil_empresa():
    if current_user.tipo_usuario != 'empresa':
        return redirect(url_for('pagina_de_inicio'))

    empresa = current_user.empresa

    if request.method == 'POST':
        # Guardar datos de texto
        empresa.nombre_empresa = request.form.get('nombre_empresa')
        empresa.sector = request.form.get('sector')
        empresa.tamaño = request.form.get('tamaño')
        empresa.sitio_web = request.form.get('sitio_web')
        empresa.descripcion = request.form.get('descripcion')
        
        # --- LÓGICA PARA MANEJAR LA SUBIDA DEL LOGO ---
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Guardamos el archivo en nuestra carpeta 'static/uploads'
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # Guardamos la ruta en la base de datos
                empresa.logo_url = f'/{UPLOAD_FOLDER}/{filename}'

        # --- LÓGICA PARA MANEJAR LA SUBIDA DE LA PORTADA ---
        if 'portada' in request.files:
            file = request.files['portada']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                empresa.portada_url = f'/{UPLOAD_FOLDER}/{filename}'

        db.session.commit()
        flash('¡El perfil de tu empresa ha sido actualizado!', 'success')
        return redirect(url_for('perfil_empresa'))

    return render_template('editar_perfil_empresa.html')

# --- RUTA DE DETALLE DE OFERTA (MEJORADA) ---
@app.route('/oferta/<int:oferta_id>')
def oferta_detalle(oferta_id):
    oferta = OfertaEmpleo.query.get_or_404(oferta_id)
    return render_template('oferta_detalle.html', oferta=oferta)

# --- NUEVA RUTA PARA MANEJAR LA POSTULACIÓN ---
@app.route('/oferta/<int:oferta_id>/postular', methods=['POST'])
@login_required
def postular_oferta(oferta_id):
    # Nos aseguramos de que solo los candidatos puedan postular
    if current_user.tipo_usuario != 'candidato':
        flash('Solo los candidatos pueden postular a las ofertas.', 'error')
        return redirect(url_for('oferta_detalle', oferta_id=oferta_id))

    oferta = OfertaEmpleo.query.get_or_404(oferta_id)
    
    # Verificamos si el candidato ya postuló a esta oferta para evitar duplicados
    postulacion_existente = Postulacion.query.filter_by(
        id_perfil=current_user.perfil.id,
        id_oferta=oferta.id
    ).first()

    if postulacion_existente:
        flash('Ya has postulado a esta oferta.', 'info')
        return redirect(url_for('oferta_detalle', oferta_id=oferta_id))

    # Creamos la nueva postulación
    nueva_postulacion = Postulacion(perfil=current_user.perfil, oferta_empleo=oferta)
    db.session.add(nueva_postulacion)
    db.session.commit()

    flash('¡Has postulado con éxito!', 'success')
    # Redirigimos al candidato a su página de seguimiento
    return redirect(url_for('mis_postulaciones'))

# --- RUTA PARA GESTIONAR APLICANTES DE UNA OFERTA (MEJORADA) ---
@app.route('/oferta/<int:oferta_id>/aplicantes')
@login_required
def gestion_aplicantes(oferta_id):
    if current_user.tipo_usuario != 'empresa':
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('pagina_de_inicio'))

    oferta = OfertaEmpleo.query.get_or_404(oferta_id)

    if oferta.empresa.id != current_user.empresa.id:
        flash('No tienes permiso para ver los aplicantes de esta oferta.', 'error')
        return redirect(url_for('dashboard_empresa'))

    # Clasificamos las postulaciones por su estado
    postulaciones = oferta.postulaciones
    nuevos_aplicantes = [p for p in postulaciones if p.estado == 'Enviada']
    en_revision = [p for p in postulaciones if p.estado == 'En Revisión']
    entrevista = [p for p in postulaciones if p.estado == 'Entrevista']
    contratado = [p for p in postulaciones if p.estado == 'Contratado']

    return render_template('gestion_aplicantes.html', 
                            oferta=oferta, 
                            nuevos=nuevos_aplicantes,
                            revision=en_revision,
                            entrevistas=entrevista,
                            contratados=contratado)

# --- NUEVA RUTA PARA ACTUALIZAR EL ESTADO CON DRAG & DROP ---
@app.route('/postulacion/actualizar-estado/<int:postulacion_id>', methods=['POST'])
@login_required
def actualizar_estado_drag_drop(postulacion_id):
    if current_user.tipo_usuario != 'empresa':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    postulacion = Postulacion.query.get_or_404(postulacion_id)
    
    # Verificación de seguridad
    if postulacion.oferta_empleo.empresa.id != current_user.empresa.id:
        return jsonify({'error': 'Acción no autorizada'}), 403

    # Obtenemos el nuevo estado enviado por el JavaScript
    data = request.get_json()
    nuevo_estado = data.get('nuevo_estado')

    if nuevo_estado:
        postulacion.estado = nuevo_estado
        
        # 2. (NUEVO) Creamos la notificación para el candidato
        texto_notificacion = f"El estado de tu postulación para <strong>{postulacion.oferta_empleo.titulo}</strong> ha cambiado a <strong>'{nuevo_estado}'</strong>."
        
        nueva_notificacion = Notificacion(
            texto=texto_notificacion,
            id_usuario=postulacion.perfil.id_usuario,
            # El enlace llevará al candidato a su página de seguimiento
            enlace_url=url_for('mis_postulaciones') 
        )
        db.session.add(nueva_notificacion)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Estado actualizado'})
    
    return jsonify({'error': 'No se proporcionó un nuevo estado'}), 400

# --- RUTA DE NOTIFICACIONES (VERSIÓN FINAL) ---
@app.route('/notificaciones')
@login_required
def notificaciones():
    # 1. Buscamos todas las notificaciones del usuario actual, ordenadas por fecha
    lista_notificaciones = Notificacion.query.filter_by(id_usuario=current_user.id).order_by(Notificacion.fecha_creacion.desc()).all()
    
    # 2. (NUEVO) Marcamos todas las notificaciones no leídas como leídas
    notificaciones_no_leidas = Notificacion.query.filter_by(id_usuario=current_user.id, leida=False).all()
    for notificacion in notificaciones_no_leidas:
        notificacion.leida = True
    
    # 3. Guardamos el cambio en la base de datos
    db.session.commit()

    # 4. Pasamos la lista completa a la plantilla
    return render_template('notificaciones.html', notificaciones=lista_notificaciones)

# Iniciar el servidor
if __name__ == '__main__':
    app.run(debug=True)
