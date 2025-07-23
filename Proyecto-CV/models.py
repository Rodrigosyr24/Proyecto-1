from extensions import db
from flask_login import UserMixin # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore

# --- Tablas de Asociación (Tablas "puente") ---
oferta_habilidades = db.Table('oferta_habilidades',
    db.Column('oferta_id', db.Integer, db.ForeignKey('ofertas_empleo.id'), primary_key=True),
    db.Column('habilidad_id', db.Integer, db.ForeignKey('habilidades.id'), primary_key=True)
)

oferta_idiomas = db.Table('oferta_idiomas',
    db.Column('oferta_id', db.Integer, db.ForeignKey('ofertas_empleo.id'), primary_key=True),
    db.Column('idioma_id', db.Integer, db.ForeignKey('idiomas.id'), primary_key=True)
)

# ======================================================
#  1. MODELO DE USUARIO (La cuenta de acceso)
# ======================================================
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    tipo_usuario = db.Column(db.String(50), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
    perfil = db.relationship('Perfil', back_populates='usuario', uselist=False, cascade="all, delete-orphan")
    empresa = db.relationship('Empresa', back_populates='usuario', uselist=False, cascade="all, delete-orphan")
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

# ======================================================
#  2. MODELO DE PERFIL (Para Candidatos)
# ======================================================
class Perfil(db.Model):
    __tablename__ = 'perfiles'
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(255))
    titular = db.Column(db.String(255))
    resumen = db.Column(db.Text)
    telefono = db.Column(db.String(50))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    usuario = db.relationship('Usuario', back_populates='perfil')
    experiencias = db.relationship('Experiencia', backref='perfil', lazy=True, cascade="all, delete-orphan")
    educacion = db.relationship('Educacion', backref='perfil', lazy=True, cascade="all, delete-orphan")
    proyectos = db.relationship('Proyecto', backref='perfil', lazy=True, cascade="all, delete-orphan")
    enlaces = db.relationship('Enlace', backref='perfil', lazy=True, cascade="all, delete-orphan")
    habilidades = db.relationship('HabilidadesPerfil', backref='perfil', lazy=True, cascade="all, delete-orphan")
    idiomas = db.relationship('IdiomasPerfil', backref='perfil', lazy=True, cascade="all, delete-orphan")
    postulaciones = db.relationship('Postulacion', backref='perfil', lazy=True, cascade="all, delete-orphan")
    propuestas_recibidas = db.relationship('Propuesta', backref='perfil', lazy=True, cascade="all, delete-orphan")

# ======================================================
#  3. MODELO DE EMPRESA
# ======================================================
class Empresa(db.Model):
    __tablename__ = 'empresas'
    id = db.Column(db.Integer, primary_key=True)
    nombre_empresa = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    sitio_web = db.Column(db.String(255))
    sector = db.Column(db.String(100))
    tamaño = db.Column(db.String(100))
    logo_url = db.Column(db.String(255))
    portada_url = db.Column(db.String(255))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    usuario = db.relationship('Usuario', back_populates='empresa')
    ofertas = db.relationship('OfertaEmpleo', backref='empresa', lazy=True, cascade="all, delete-orphan")
    propuestas_enviadas = db.relationship('Propuesta', backref='empresa', lazy=True, cascade="all, delete-orphan")

# ======================================================
#  4. MODELOS MODULARES (Las secciones del perfil)
# ======================================================
class Experiencia(db.Model):
    __tablename__ = 'experiencias'
    id = db.Column(db.Integer, primary_key=True)
    cargo = db.Column(db.String(255), nullable=False)
    empresa = db.Column(db.String(255), nullable=False)
    id_perfil = db.Column(db.Integer, db.ForeignKey('perfiles.id'), nullable=False)

class Educacion(db.Model):
    __tablename__ = 'educacion'
    id = db.Column(db.Integer, primary_key=True)
    institucion = db.Column(db.String(255), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    id_perfil = db.Column(db.Integer, db.ForeignKey('perfiles.id'), nullable=False)

class Proyecto(db.Model):
    __tablename__ = 'proyectos'
    id = db.Column(db.Integer, primary_key=True)
    nombre_proyecto = db.Column(db.String(255), nullable=False)
    id_perfil = db.Column(db.Integer, db.ForeignKey('perfiles.id'), nullable=False)

class Enlace(db.Model):
    __tablename__ = 'enlaces'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    id_perfil = db.Column(db.Integer, db.ForeignKey('perfiles.id'), nullable=False)

# --- Modelos para Habilidades e Idiomas ---
class Habilidad(db.Model):
    __tablename__ = 'habilidades'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)

class HabilidadesPerfil(db.Model):
    __tablename__ = 'habilidades_perfil'
    id = db.Column(db.Integer, primary_key=True)
    id_perfil = db.Column(db.Integer, db.ForeignKey('perfiles.id'), nullable=False)
    id_habilidad = db.Column(db.Integer, db.ForeignKey('habilidades.id'), nullable=False)

class Idioma(db.Model):
    __tablename__ = 'idiomas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)

class IdiomasPerfil(db.Model):
    __tablename__ = 'idiomas_perfil'
    id = db.Column(db.Integer, primary_key=True)
    id_perfil = db.Column(db.Integer, db.ForeignKey('perfiles.id'), nullable=False)
    id_idioma = db.Column(db.Integer, db.ForeignKey('idiomas.id'), nullable=False)
    nivel = db.Column(db.String(50))

# --- Modelo de Oferta de Empleo (VERSIÓN FINAL Y COMPLETA) ---
class OfertaEmpleo(db.Model):
    __tablename__ = 'ofertas_empleo'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    responsabilidades = db.Column(db.Text)
    ubicacion = db.Column(db.String(255))
    tipo_contrato = db.Column(db.String(100))
    salario_min = db.Column(db.Integer)
    salario_max = db.Column(db.Integer)
    experiencia_total_min = db.Column(db.Integer)
    
    # Columnas que faltaban en tu versión
    fecha_publicacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    activa = db.Column(db.Boolean, default=True)
    
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    
    # Relaciones
    postulaciones = db.relationship('Postulacion', backref='oferta_empleo', lazy=True, cascade="all, delete-orphan")
    habilidades_requeridas = db.relationship('Habilidad', secondary=oferta_habilidades, backref='ofertas')
    idiomas_requeridos = db.relationship('Idioma', secondary=oferta_idiomas, backref='ofertas')


class Postulacion(db.Model):
    __tablename__ = 'postulaciones'
    id = db.Column(db.Integer, primary_key=True)
    fecha_postulacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    estado = db.Column(db.String(50), default='Enviada') # Ej: 'Enviada', 'CV Visto', 'En Proceso'
    id_perfil = db.Column(db.Integer, db.ForeignKey('perfiles.id'), nullable=False)
    id_oferta = db.Column(db.Integer, db.ForeignKey('ofertas_empleo.id'), nullable=False)

# ======================================================
#  NUEVO: MODELO PARA PROPUESTAS DIRECTAS
# ======================================================
class Propuesta(db.Model):
    __tablename__ = 'propuestas'
    id = db.Column(db.Integer, primary_key=True)
    mensaje = db.Column(db.Text, nullable=False)
    fecha_envio = db.Column(db.DateTime, default=db.func.current_timestamp())
    estado = db.Column(db.String(50), default='Enviada') # Ej: 'Enviada', 'Vista', 'Aceptada', 'Rechazada'
    
    # Relaciones
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    id_perfil = db.Column(db.Integer, db.ForeignKey('perfiles.id'), nullable=False)

# ======================================================
#  NUEVO: MODELO PARA NOTIFICACIONES
# ======================================================
class Notificacion(db.Model):
    __tablename__ = 'notificaciones'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(255), nullable=False)
    enlace_url = db.Column(db.String(255))
    leida = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relación: A qué usuario pertenece esta notificación
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

