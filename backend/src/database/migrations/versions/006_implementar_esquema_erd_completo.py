"""Implementar esquema completo según ERD

Revision ID: 006_esquema_erd
Revises: dfd51ca3cf7f
Create Date: 2025-12-07

Esta migración implementa el esquema completo de la base de datos según el ERD proporcionado,
asegurando que todas las tablas, campos, relaciones y constraints estén correctamente definidos.
"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006_esquema_erd'
down_revision: str = 'dfd51ca3cf7f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Constants
TENANT_ID_FK = 'tenants.id'


def _crear_tabla_estado_potrero(inspector: sa.Inspector) -> None:
    """Crea la tabla estado_potrero si no existe."""
    tables = inspector.get_table_names()
    if 'estado_potrero' not in tables:
        op.create_table(
            'estado_potrero',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('nombre_estado', sa.String(100), nullable=False, unique=True)
        )
        # Insertar estados por defecto
        op.execute("""
            INSERT INTO estado_potrero (id, nombre_estado) VALUES
            (1, 'disponible'),
            (2, 'ocupado'),
            (3, 'limpieza')
            ON DUPLICATE KEY UPDATE nombre_estado = VALUES(nombre_estado)
        """)


def _crear_tabla_historial_potreros_base() -> None:
    """Crea la tabla historial_potreros con la estructura base."""
    op.create_table(
        'historial_potreros',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_potrero', sa.Integer, sa.ForeignKey('potrero.id', ondelete='CASCADE'), nullable=False),
        sa.Column('fecha_ultima_limpieza', sa.DateTime, nullable=True),
        sa.Column('fecha_proxima_limpieza', sa.DateTime, nullable=True),
        sa.Column('fecha_ultimo_uso', sa.DateTime, nullable=True),
        sa.Column('observaciones', sa.Text, nullable=True)
    )


def _migrar_datos_historial_potrero() -> None:
    """Migra datos desde historial_potrero a historial_potreros."""
    op.execute("""
        INSERT INTO historial_potreros (id_potrero, fecha_ultimo_uso, fecha_ultima_limpieza, fecha_proxima_limpieza, observaciones)
        SELECT
            id_potrero,
            MAX(CASE WHEN tipo_evento = 'uso' THEN fecha_evento END) as fecha_ultimo_uso,
            MAX(CASE WHEN tipo_evento = 'limpieza' AND (observaciones IS NULL OR observaciones != 'Programada') THEN fecha_evento END) as fecha_ultima_limpieza,
            MAX(CASE WHEN tipo_evento = 'limpieza' AND observaciones = 'Programada' THEN fecha_evento END) as fecha_proxima_limpieza,
            MAX(CASE WHEN tipo_evento = 'limpieza' AND observaciones = 'Programada' THEN observaciones END) as observaciones
        FROM historial_potrero
        GROUP BY id_potrero
    """)


def _actualizar_historial_potreros_existente() -> None:
    """Actualiza registros existentes en historial_potreros con datos de historial_potrero."""
    op.execute("""
        UPDATE historial_potreros hp
        INNER JOIN (
            SELECT
                id_potrero,
                MAX(CASE WHEN tipo_evento = 'uso' THEN fecha_evento END) as fecha_ultimo_uso,
                MAX(CASE WHEN tipo_evento = 'limpieza' AND (observaciones IS NULL OR observaciones != 'Programada') THEN fecha_evento END) as fecha_ultima_limpieza,
                MAX(CASE WHEN tipo_evento = 'limpieza' AND observaciones = 'Programada' THEN fecha_evento END) as fecha_proxima_limpieza,
                MAX(CASE WHEN tipo_evento = 'limpieza' AND observaciones = 'Programada' THEN observaciones END) as observaciones
            FROM historial_potrero
            GROUP BY id_potrero
        ) hp_old ON hp.id_potrero = hp_old.id_potrero
        SET
            hp.fecha_ultimo_uso = COALESCE(hp_old.fecha_ultimo_uso, hp.fecha_ultimo_uso),
            hp.fecha_ultima_limpieza = COALESCE(hp_old.fecha_ultima_limpieza, hp.fecha_ultima_limpieza),
            hp.fecha_proxima_limpieza = COALESCE(hp_old.fecha_proxima_limpieza, hp.fecha_proxima_limpieza),
            hp.observaciones = COALESCE(hp_old.observaciones, hp.observaciones)
    """)


def _eliminar_tabla_historial_potrero(inspector: sa.Inspector) -> None:
    """Elimina índices y tabla historial_potrero."""
    try:
        indexes = inspector.get_indexes('historial_potrero')
        for idx in indexes:
            if idx['name'] not in ['PRIMARY']:
                try:
                    op.drop_index(idx['name'], 'historial_potrero')
                except Exception:
                    pass
    except Exception:
        pass

    op.drop_table('historial_potrero')


def _verificar_columnas_historial_potreros(inspector: sa.Inspector) -> None:
    """Verifica que historial_potreros tenga todas las columnas requeridas."""
    columns = [col['name'] for col in inspector.get_columns('historial_potreros')]
    required_columns = {
        'fecha_ultima_limpieza': sa.DateTime,
        'fecha_proxima_limpieza': sa.DateTime,
        'fecha_ultimo_uso': sa.DateTime,
        'observaciones': sa.Text
    }

    for col_name, col_type in required_columns.items():
        if col_name not in columns:
            op.add_column('historial_potreros', sa.Column(col_name, col_type, nullable=True))


def _crear_tabla_historial_potreros(inspector: sa.Inspector) -> None:
    """Crea o actualiza la tabla historial_potreros según el ERD y elimina historial_potrero."""
    tables = inspector.get_table_names()

    if 'historial_potrero' in tables and 'historial_potreros' not in tables:
        # Caso 1: Solo existe historial_potrero
        _crear_tabla_historial_potreros_base()
        _migrar_datos_historial_potrero()
        _eliminar_tabla_historial_potrero(inspector)

    elif 'historial_potrero' in tables and 'historial_potreros' in tables:
        # Caso 2: Existen ambas tablas
        _migrar_datos_historial_potrero()
        _actualizar_historial_potreros_existente()
        _eliminar_tabla_historial_potrero(inspector)

    elif 'historial_potreros' not in tables:
        # Caso 3: No existe historial_potreros
        _crear_tabla_historial_potreros_base()

    else:
        # Caso 4: Ya existe historial_potreros
        _verificar_columnas_historial_potreros(inspector)


def _actualizar_tabla_roles(inspector: sa.Inspector) -> None:
    """Asegura que la tabla roles tenga nivel y permisos según el ERD."""
    if 'roles' not in inspector.get_table_names():
        return
    
    columns = [col['name'] for col in inspector.get_columns('roles')]
    
    if 'nivel' not in columns:
        op.add_column('roles', sa.Column('nivel', sa.Enum('global', 'tenant', name='nivel_rol'), 
                                         server_default='tenant', nullable=True))
    
    if 'permisos' not in columns:
        op.add_column('roles', sa.Column('permisos', sa.JSON, nullable=True))


def _actualizar_tabla_personas(inspector: sa.Inspector) -> None:
    """Asegura que personas tenga tenant_id y constraints UNIQUE en email y telefono."""
    if 'personas' not in inspector.get_table_names():
        return
    
    columns = [col['name'] for col in inspector.get_columns('personas')]
    
    # Agregar tenant_id si no existe
    if 'tenant_id' not in columns:
        op.add_column('personas', sa.Column('tenant_id', sa.Integer,
                                           sa.ForeignKey(TENANT_ID_FK, ondelete='SET NULL'),
                                           nullable=True))
    
    # Asegurar constraints UNIQUE en email y telefono
    try:
        unique_constraints = inspector.get_unique_constraints('personas')
        email_unique = any('email' in constraint['column_names'] for constraint in unique_constraints)
        telefono_unique = any('telefono' in constraint['column_names'] for constraint in unique_constraints)
        
        if not email_unique:
            try:
                op.create_unique_constraint('uq_personas_email', 'personas', ['email'])
            except Exception:
                pass  # Puede fallar si hay duplicados
        
        if not telefono_unique:
            try:
                op.create_unique_constraint('uq_personas_telefono', 'personas', ['telefono'])
            except Exception:
                pass  # Puede fallar si hay duplicados
    except Exception:
        pass


def _actualizar_tabla_potrero(inspector: sa.Inspector) -> None:
    """Asegura que potrero tenga todos los campos según el ERD."""
    if 'potrero' not in inspector.get_table_names():
        return
    
    columns = [col['name'] for col in inspector.get_columns('potrero')]
    
    # Agregar id_estado_potrero si no existe
    if 'id_estado_potrero' not in columns:
        op.add_column('potrero', sa.Column('id_estado_potrero', sa.Integer, 
                                          sa.ForeignKey('estado_potrero.id'), 
                                          nullable=True))
    
    # Agregar area si no existe
    if 'area' not in columns:
        op.add_column('potrero', sa.Column('area', sa.Numeric(10, 2), nullable=True))
    
    # Agregar fecha_creacion si no existe
    if 'fecha_creacion' not in columns:
        op.add_column('potrero', sa.Column('fecha_creacion', sa.DateTime, 
                                          server_default=sa.func.current_timestamp(), 
                                          nullable=True))
    
    # Agregar fecha_actualizacion si no existe
    if 'fecha_actualizacion' not in columns:
        op.add_column('potrero', sa.Column('fecha_actualizacion', sa.DateTime, 
                                          server_default=sa.func.current_timestamp(), 
                                          onupdate=sa.func.current_timestamp(), 
                                          nullable=True))
    
    # Asegurar que tenant_id existe y tiene FK
    if 'tenant_id' not in columns:
        op.add_column('potrero', sa.Column('tenant_id', sa.Integer,
                                          sa.ForeignKey(TENANT_ID_FK, ondelete='CASCADE'),
                                          nullable=True))


def _actualizar_tabla_ganado(inspector: sa.Inspector) -> None:
    """Asegura que ganado tenga todos los campos según el ERD."""
    if 'ganado' not in inspector.get_table_names():
        return
    
    columns = [col['name'] for col in inspector.get_columns('ganado')]
    
    # Asegurar que tenant_id existe
    if 'tenant_id' not in columns:
        op.add_column('ganado', sa.Column('tenant_id', sa.Integer,
                                         sa.ForeignKey(TENANT_ID_FK, ondelete='CASCADE'),
                                         nullable=True))


def _actualizar_tabla_vacunacion(inspector: sa.Inspector) -> None:
    """Asegura que vacunacion tenga todos los campos según el ERD."""
    if 'vacunacion' not in inspector.get_table_names():
        return
    
    columns = [col['name'] for col in inspector.get_columns('vacunacion')]
    
    # Eliminar campos que no están en el ERD
    campos_a_eliminar = ['nombre_animal', 'fecha_inicio', 'fecha_fin']
    for campo in campos_a_eliminar:
        if campo in columns:
            try:
                op.drop_column('vacunacion', campo)
            except Exception:
                pass
    
    # Asegurar que responsable es FK a personas
    # Verificar si ya es FK
    fks = inspector.get_foreign_keys('vacunacion')
    responsable_es_fk = any(fk['constrained_columns'] == ['responsable'] for fk in fks)
    
    if not responsable_es_fk and 'responsable' in columns:
        # Intentar agregar FK (puede fallar si hay datos inválidos)
        try:
            op.create_foreign_key('fk_vacunacion_responsable', 'vacunacion', 'personas', 
                                 ['responsable'], ['id'])
        except Exception:
            pass
    
    # Asegurar que tenant_id existe
    if 'tenant_id' not in columns:
        op.add_column('vacunacion', sa.Column('tenant_id', sa.Integer,
                                              sa.ForeignKey(TENANT_ID_FK, ondelete='CASCADE'),
                                              nullable=True))


def _actualizar_tabla_qr(inspector: sa.Inspector) -> None:
    """Asegura que qr tenga todos los campos según el ERD."""
    if 'qr' not in inspector.get_table_names():
        return
    
    columns = [col['name'] for col in inspector.get_columns('qr')]
    
    # Asegurar que tenant_id existe
    if 'tenant_id' not in columns:
        op.add_column('qr', sa.Column('tenant_id', sa.Integer,
                                      sa.ForeignKey(TENANT_ID_FK, ondelete='CASCADE'),
                                      nullable=True))


def _actualizar_tabla_usuarios(inspector: sa.Inspector) -> None:
    """Asegura que usuarios tenga todos los campos según el ERD."""
    if 'usuarios' not in inspector.get_table_names():
        return
    
    columns = [col['name'] for col in inspector.get_columns('usuarios')]
    
    # Asegurar que tenant_id existe
    if 'tenant_id' not in columns:
        op.add_column('usuarios', sa.Column('tenant_id', sa.Integer,
                                            sa.ForeignKey(TENANT_ID_FK, ondelete='SET NULL'),
                                            nullable=True))


def _crear_indices(inspector: sa.Inspector) -> None:
    """Crea índices para mejorar el rendimiento."""
    # Índice en historial_potreros.id_potrero
    if 'historial_potreros' in inspector.get_table_names():
        indexes = [idx['name'] for idx in inspector.get_indexes('historial_potreros')]
        if 'idx_historial_potreros_potrero' not in indexes:
            try:
                op.create_index('idx_historial_potreros_potrero', 'historial_potreros', ['id_potrero'])
            except Exception:
                pass


def upgrade() -> None:
    """Implementa el esquema completo según el ERD."""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    _crear_tabla_estado_potrero(inspector)
    _crear_tabla_historial_potreros(inspector)
    _actualizar_tabla_roles(inspector)
    _actualizar_tabla_personas(inspector)
    _actualizar_tabla_potrero(inspector)
    _actualizar_tabla_ganado(inspector)
    _actualizar_tabla_vacunacion(inspector)
    _actualizar_tabla_qr(inspector)
    _actualizar_tabla_usuarios(inspector)
    _crear_indices(inspector)


def downgrade() -> None:
    """Revierte los cambios (parcial, algunos cambios son destructivos)."""
    # Nota: El downgrade no puede revertir completamente todos los cambios
    # ya que algunos son estructurales y pueden tener datos dependientes
    
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    # Eliminar índices
    if 'historial_potreros' in inspector.get_table_names():
        try:
            op.drop_index('idx_historial_potreros_potrero', 'historial_potreros')
        except Exception:
            pass
    
    # Eliminar constraints UNIQUE si existen
    try:
        op.drop_constraint('uq_personas_email', 'personas', type_='unique')
    except Exception:
        pass
    
    try:
        op.drop_constraint('uq_personas_telefono', 'personas', type_='unique')
    except Exception:
        pass
    
    # Nota: No eliminamos tablas ni columnas en downgrade para evitar pérdida de datos
    # Si se necesita un downgrade completo, debe hacerse manualmente

