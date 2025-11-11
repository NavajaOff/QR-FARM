"""Migración inicial: todas las tablas y datos esenciales

Revision ID: 001
Revises: None
Create Date: 2025-11-05
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # -------------------
    # TABLAS
    # -------------------

    # Constantes para referencias de tabla
    PERSONAS_ID = PERSONAS_ID
    
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('rol', sa.String(50)),
        sa.Column('descripcion', sa.Text)
    )

    op.create_table(
        'tipo_pasto',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('tipo_pasto', sa.String(100))
    )

    op.create_table(
        'tipo_vacuna',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('nombre_vacuna', sa.String(255))
    )

    op.create_table(
        'personas',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_rol', sa.Integer, sa.ForeignKey('roles.id')),
        sa.Column('primer_nombre', sa.String(50)),
        sa.Column('segundo_nombre', sa.String(50)),
        sa.Column('primer_apellido', sa.String(50)),
        sa.Column('segundo_apellido', sa.String(50)),
        sa.Column('email', sa.String(100)),
        sa.Column('telefono', sa.String(10)),
        sa.Column('fecha_creacion', sa.DateTime, server_default=sa.func.current_timestamp())
    )

    op.create_table(
        'estado_ganado',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('tipo_estado', sa.String(50))
    )

    op.create_table(
        'revision',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('control', sa.DateTime),
        sa.Column('visita', sa.DateTime)
    )

    op.create_table(
        'potrero',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_tipo_pasto', sa.Integer, sa.ForeignKey('tipo_pasto.id')),
        sa.Column('nombre', sa.String(50)),
        sa.Column('capacidad', sa.Integer),
        sa.Column('hectareas', sa.Float),
        sa.Column('ocupacion', sa.Integer, server_default='0'),
        sa.Column('fecha_ultimo_uso', sa.DateTime),
        sa.Column('responsable_persona_id', sa.Integer, sa.ForeignKey(PERSONAS_ID)),
        sa.Column('proxima_limpieza', sa.DateTime),
        sa.Column('area', sa.Numeric(10,2)),
        sa.Column('ultima_limpieza', sa.DateTime),
        sa.Column('descripcion', sa.Text),
        sa.Column('estado', sa.Enum('disponible','ocupado','limpieza'), nullable=False, server_default='disponible')
    )

    op.create_table(
        'ganado',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_potrero', sa.Integer, sa.ForeignKey('potrero.id')),
        sa.Column('id_persona', sa.Integer, sa.ForeignKey(PERSONAS_ID)),
        sa.Column('id_revision', sa.Integer, sa.ForeignKey('revision.id')),
        sa.Column('nombre', sa.String(50)),
        sa.Column('peso', sa.Integer),
        sa.Column('raza', sa.String(50)),
        sa.Column('fecha_nacimiento', sa.DateTime),
        sa.Column('id_estado', sa.Integer, sa.ForeignKey('estado_ganado.id')),
        sa.Column('sexo', sa.Enum('macho','hembra'), nullable=False)
    )

    op.create_table(
        'qr',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_ganado', sa.Integer, sa.ForeignKey('ganado.id', ondelete='CASCADE')),
        sa.Column('id_persona_encargado', sa.Integer, sa.ForeignKey(PERSONAS_ID)),
        sa.Column('id_persona_dueno', sa.Integer, sa.ForeignKey(PERSONAS_ID)),
        sa.Column('codigo_qr', sa.String(255), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime, server_default=sa.func.current_timestamp()),
        sa.Column('fecha_actualizacion', sa.DateTime, server_default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp())
    )

    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_persona', sa.Integer, sa.ForeignKey(PERSONAS_ID)),
        sa.Column('id_rol', sa.Integer, sa.ForeignKey('roles.id')),
        sa.Column('contrasena', sa.String(255)),
        sa.Column('estado', sa.Enum('activo','inactivo'), server_default='activo')
    )

    op.create_table(
        'vacunacion',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_animal', sa.Integer, sa.ForeignKey('ganado.id')),
        sa.Column('nombre_animal', sa.String(50)),
        sa.Column('fecha_inicio', sa.DateTime),
        sa.Column('fecha_fin', sa.DateTime),
        sa.Column('fecha_aplicacion', sa.DateTime),
        sa.Column('proxima_dosis', sa.DateTime),
        sa.Column('responsable', sa.Integer, sa.ForeignKey(PERSONAS_ID)),
        sa.Column('estado', sa.Enum('aplicado','pendiente'), server_default='pendiente'),
        sa.Column('id_tipo_vacuna', sa.Integer, sa.ForeignKey('tipo_vacuna.id'))
    )

    # -------------------
    # DATOS INICIALES
    # -------------------

    # Roles
    op.bulk_insert(
        sa.table('roles',
            sa.column('id', sa.Integer),
            sa.column('rol', sa.String),
            sa.column('descripcion', sa.String)
        ),
        [
            {'id':1,'rol':'admin','descripcion':'Administrador del sistema'},
            {'id':2,'rol':'usuario','descripcion':'Usuario normal'}
        ]
    )

    # Tipo de pasto
    op.bulk_insert(
        sa.table('tipo_pasto',
            sa.column('id', sa.Integer),
            sa.column('tipo_pasto', sa.String)
        ),
        [
            {'id':1,'tipo_pasto':'Brachiaria humidicola'},
            {'id':2,'tipo_pasto':'Brachiaria decumbens'},
            {'id':3,'tipo_pasto':'Pasto mombazaa'}
        ]
    )

    # Tipo vacuna
    op.bulk_insert(
        sa.table('tipo_vacuna',
            sa.column('id', sa.Integer),
            sa.column('nombre_vacuna', sa.String)
        ),
        [
            {'id':1,'nombre_vacuna':'Brucella'},
            {'id':2,'nombre_vacuna':'Aftosa'},
            {'id':3,'nombre_vacuna':'Clostridiales'}
        ]
    )

    # Estado ganado
    op.bulk_insert(
        sa.table('estado_ganado',
            sa.column('id', sa.Integer),
            sa.column('tipo_estado', sa.String)
        ),
        [
            {'id':1,'tipo_estado':'saludable'},
            {'id':2,'tipo_estado':'revision'},
            {'id':3,'tipo_estado':'enfermo'}
        ]
    )

    # Personas, ganado, potrero, qr, usuarios, vacunacion...
    # Aquí se puede seguir agregando los datos iniciales de manera completa como en tu dump SQL

def downgrade():
    op.drop_table('vacunacion')
    op.drop_table('usuarios')
    op.drop_table('qr')
    op.drop_table('ganado')
    op.drop_table('potrero')
    op.drop_table('revision')
    op.drop_table('estado_ganado')
    op.drop_table('personas')
    op.drop_table('tipo_vacuna')
    op.drop_table('tipo_pasto')
    op.drop_table('roles')
