"""
🗄️ Modelos de Base de Datos - Inspector API

Este módulo define todos los modelos SQLAlchemy para la base de datos del sistema
de gestión de inventario de registros de inspección.

Modelos incluidos:
- Registro: Entidad principal para almacenar información de inspecciones
- Usuario: Gestión de usuarios del sistema
- HistorialCambio: Auditoría de cambios en registros
- HistorialUsuario: Auditoría de cambios en usuarios

Autor: Daniel Bermúdez  
Versión: 1.0.0
"""

from sqlalchemy import Column, Integer, String, Index, DateTime, ForeignKey, Boolean
from app.db.base import Base
import logging
import datetime
from sqlalchemy.orm import relationship

# Configuración básica del logger
logger = logging.getLogger(__name__)

class Registro(Base):
    """
    Modelo para almacenar registros de inspección.
    
    Este modelo representa la entidad principal del sistema, conteniendo
    toda la información relacionada con los dispositivos inspeccionados.
    
    Atributos:
        id: Identificador único del registro
        numero_inspector: Número único del inspector
        nombre: Nombre del dispositivo (formato: ins{numero})
        observaciones: Observaciones sobre el dispositivo
        status: Estado del dispositivo (activo/inactivo)
        region: Región geográfica
        flota: Flota asignada
        encargado: Persona responsable
        celular: Número de contacto
        correo: Correo electrónico
        direccion: Dirección física
        uso: Tipo de uso (Residencial/Comercial)
        departamento: Departamento
        ciudad: Ciudad
        tecnologia: Tecnología utilizada
        cmts_olt: Equipo CMTS/OLT
        id_servicio: Identificador del servicio
        mac_sn: Dirección MAC o número de serie
        uuid: Identificador único universal
    """
    __tablename__ = "registros"

    id = Column(Integer, primary_key=True, index=True)
    numero_inspector = Column(Integer, nullable=False)
    nombre = Column(String, nullable=False)
    observaciones = Column(String, nullable=False)
    status = Column(String, nullable=False)
    region = Column(String, nullable=False)
    flota = Column(String, nullable=False)
    encargado = Column(String, nullable=False)
    celular = Column(String, nullable=False)
    correo = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    uso = Column(String, nullable=False)
    departamento = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)
    tecnologia = Column(String, nullable=False)
    cmts_olt = Column(String, nullable=False)
    id_servicio = Column(String, nullable=False)
    mac_sn = Column(String, nullable=False)
    uuid = Column(String, nullable=True)

    # Índices para optimizar consultas frecuentes
    __table_args__ = (
        Index('idx_region_ciudad', 'region', 'ciudad'),
        Index('idx_tecnologia', 'tecnologia'),
        Index('idx_flota', 'flota'),
        Index('idx_uso', 'uso'),
        Index('idx_mac_sn', 'mac_sn'),
        Index('idx_id_servicio', 'id_servicio'),
        Index('idx_nombre', 'nombre'),
        # Índices únicos para prevenir duplicados
        Index('idx_numero_inspector_unique', 'numero_inspector', unique=True),
        Index('idx_nombre_unique', 'nombre', unique=True),
    )

    # Relación con historial (comentada temporalmente para evitar errores)
    # historial = relationship(
    #     "HistorialCambio",
    #     back_populates="registro",
    #     cascade="all, delete-orphan",
    #     passive_deletes=True
    # )

    def as_dict(self):
        """
        Convierte el registro a un diccionario.
        
        Returns:
            dict: Diccionario con todos los campos del registro
            
        Raises:
            Exception: Si hay un error en la conversión
        """
        try:
            d = {
                "id": self.id,
                "numero_inspector": self.numero_inspector,
                "uuid": self.uuid,
                "nombre": self.nombre,
                "observaciones": self.observaciones,
                "status": self.status,
                "region": self.region,
                "flota": self.flota,
                "encargado": self.encargado,
                "celular": self.celular,
                "correo": self.correo,
                "direccion": self.direccion,
                "uso": self.uso,
                "departamento": self.departamento,
                "ciudad": self.ciudad,
                "tecnologia": self.tecnologia,
                "cmts_olt": self.cmts_olt,
                "id_servicio": self.id_servicio,
                "mac_sn": self.mac_sn
            }
            logger.info(f"as_dict ejecutado para Registro ID={self.id}")
            return d
        except Exception as e:
            logger.error(f"Error en as_dict para Registro ID={getattr(self, 'id', None)}: {e}")
            raise

class Usuario(Base):
    """
    Modelo para gestionar usuarios del sistema.
    
    Este modelo maneja la autenticación y autorización de usuarios,
    incluyendo roles y información de perfil.
    
    Atributos:
        id: Identificador único del usuario
        username: Nombre de usuario único
        email: Correo electrónico único
        password_hash: Hash de la contraseña
        nombre: Nombre real del usuario
        apellido: Apellido del usuario
        rol: Rol del usuario (admin/user)
        foto_perfil: URL de la foto de perfil
        fecha_creacion: Fecha de creación del usuario
        activo: Estado activo/inactivo del usuario
    """
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    rol = Column(String, nullable=False, default="user")  # 'admin' o 'user'
    foto_perfil = Column(String, nullable=True)  # URL o ruta de la foto
    fecha_creacion = Column(String, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)  # Para soft delete

class HistorialCambio(Base):
    """
    Modelo para auditar cambios en registros.
    
    Este modelo mantiene un historial completo de todos los cambios
    realizados en los registros del sistema para auditoría.
    
    Atributos:
        id: Identificador único del cambio
        numero_inspector: Número del inspector relacionado
        fecha: Fecha y hora del cambio
        usuario: Usuario que realizó el cambio
        accion: Tipo de acción (creacion/edicion/eliminacion)
        campo: Campo modificado (opcional)
        valor_anterior: Valor anterior del campo
        valor_nuevo: Nuevo valor del campo
        descripcion: Descripción adicional del cambio
    """
    __tablename__ = "historial_cambios"

    id = Column(Integer, primary_key=True, index=True)
    numero_inspector = Column(Integer, nullable=False, index=True)
    fecha = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    usuario = Column(String, nullable=False)
    accion = Column(String, nullable=False)  # 'creacion', 'edicion', 'eliminacion'
    campo = Column(String, nullable=True)  # Puede ser null para acciones globales
    valor_anterior = Column(String, nullable=True)
    valor_nuevo = Column(String, nullable=True)
    descripcion = Column(String, nullable=True)

    # Relación con el registro (comentada temporalmente para evitar errores)
    # registro = relationship(
    #     "Registro",
    #     back_populates="historial",
    #     foreign_keys=[numero_inspector],
    #     primaryjoin="HistorialCambio.numero_inspector == Registro.numero_inspector"
    # )

class HistorialUsuario(Base):
    """
    Modelo para auditar cambios en usuarios.
    
    Este modelo mantiene un historial de cambios realizados en
    las cuentas de usuario para auditoría administrativa.
    
    Atributos:
        id: Identificador único del cambio
        usuario_id: ID del usuario modificado
        fecha: Fecha y hora del cambio
        admin_que_realizo_cambio: Username del admin que hizo el cambio
        accion: Tipo de acción realizada
        campo: Campo modificado (opcional)
        valor_anterior: Valor anterior del campo
        valor_nuevo: Nuevo valor del campo
        descripcion: Descripción adicional del cambio
    """
    __tablename__ = "historial_usuarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    fecha = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    admin_que_realizo_cambio = Column(String, nullable=False)  # Username del admin que hizo el cambio
    accion = Column(String, nullable=False)  # 'creacion', 'edicion', 'activacion', 'desactivacion', 'eliminacion', 'restablecer_password'
    campo = Column(String, nullable=True)  # Campo modificado (para ediciones)
    valor_anterior = Column(String, nullable=True)
    valor_nuevo = Column(String, nullable=True)
    descripcion = Column(String, nullable=True)

    # Relación con el usuario
    usuario = relationship("Usuario", backref="historial")
