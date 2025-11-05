


"""datos reales actuales

Revision ID: 75b46c2713f7
Revises: 002
Create Date: 2025-11-05 16:39:32.681619

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75b46c2713f7'
down_revision: str = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Insertar datos reales de personas (excluyendo el admin que ya existe)
    op.bulk_insert(
        sa.table('personas',
            sa.column('id', sa.Integer),
            sa.column('id_rol', sa.Integer),
            sa.column('primer_nombre', sa.String),
            sa.column('segundo_nombre', sa.String),
            sa.column('primer_apellido', sa.String),
            sa.column('segundo_apellido', sa.String),
            sa.column('email', sa.String),
            sa.column('telefono', sa.String),
            sa.column('fecha_creacion', sa.DateTime)
        ),
        [
            {'id': 2, 'id_rol': 2, 'primer_nombre': 'Ronald', 'segundo_nombre': None, 'primer_apellido': 'bejarano', 'segundo_apellido': 'barbosa', 'email': 'ronald@example.com', 'telefono': '1234567890', 'fecha_creacion': '2025-11-05'},
            {'id': 3, 'id_rol': 2, 'primer_nombre': 'Maria', 'segundo_nombre': None, 'primer_apellido': 'Gonzalez', 'segundo_apellido': 'Perez', 'email': 'maria@example.com', 'telefono': '0987654321', 'fecha_creacion': '2025-11-05'},
            {'id': 4, 'id_rol': 2, 'primer_nombre': 'Carlos', 'segundo_nombre': None, 'primer_apellido': 'Rodriguez', 'segundo_apellido': 'Lopez', 'email': 'carlos@example.com', 'telefono': '1122334455', 'fecha_creacion': '2025-11-05'},
        ]
    )

    # Insertar datos reales de usuarios
    op.bulk_insert(
        sa.table('usuarios',
            sa.column('id', sa.Integer),
            sa.column('id_persona', sa.Integer),
            sa.column('id_rol', sa.Integer),
            sa.column('contrasena', sa.String),
            sa.column('estado', sa.Enum('activo', 'inactivo'))
        ),
        [
            {'id': 2, 'id_persona': 2, 'id_rol': 2, 'contrasena': '123456', 'estado': 'activo'},
            {'id': 3, 'id_persona': 3, 'id_rol': 2, 'contrasena': '123456', 'estado': 'activo'},
            {'id': 4, 'id_persona': 4, 'id_rol': 2, 'contrasena': '123456', 'estado': 'activo'},
        ]
    )

    # Insertar datos reales de potreros
    op.bulk_insert(
        sa.table('potrero',
            sa.column('id', sa.Integer),
            sa.column('id_tipo_pasto', sa.Integer),
            sa.column('nombre', sa.String),
            sa.column('capacidad', sa.Integer),
            sa.column('hectareas', sa.Float),
            sa.column('ocupacion', sa.Integer),
            sa.column('fecha_ultimo_uso', sa.DateTime),
            sa.column('responsable_persona_id', sa.Integer),
            sa.column('proxima_limpieza', sa.DateTime),
            sa.column('area', sa.DECIMAL),
            sa.column('ultima_limpieza', sa.DateTime),
            sa.column('descripcion', sa.Text),
            sa.column('estado', sa.String)
        ),
        [
            {'id': 1, 'id_tipo_pasto': 1, 'nombre': 'Potrero 1', 'capacidad': 10, 'hectareas': 5.0, 'ocupacion': 2, 'fecha_ultimo_uso': '2025-09-26', 'responsable_persona_id': 2, 'proxima_limpieza': '2025-11-08', 'area': '500.00', 'ultima_limpieza': '2025-09-26', 'descripcion': '', 'estado': 'ocupado'},
            {'id': 2, 'id_tipo_pasto': 2, 'nombre': 'Potrero 2', 'capacidad': 8, 'hectareas': 4.0, 'ocupacion': 1, 'fecha_ultimo_uso': '2025-09-25', 'responsable_persona_id': 3, 'proxima_limpieza': '2025-11-07', 'area': '400.00', 'ultima_limpieza': '2025-09-25', 'descripcion': '', 'estado': 'ocupado'},
            {'id': 3, 'id_tipo_pasto': 3, 'nombre': 'Potrero 3', 'capacidad': 12, 'hectareas': 6.0, 'ocupacion': 3, 'fecha_ultimo_uso': '2025-09-24', 'responsable_persona_id': 4, 'proxima_limpieza': '2025-11-06', 'area': '600.00', 'ultima_limpieza': '2025-09-24', 'descripcion': '', 'estado': 'ocupado'},
            {'id': 4, 'id_tipo_pasto': 1, 'nombre': 'Potrero 4', 'capacidad': 6, 'hectareas': 3.0, 'ocupacion': 1, 'fecha_ultimo_uso': '2025-09-23', 'responsable_persona_id': 2, 'proxima_limpieza': '2025-11-05', 'area': '300.00', 'ultima_limpieza': '2025-09-23', 'descripcion': '', 'estado': 'libre'},
            {'id': 5, 'id_tipo_pasto': 2, 'nombre': 'Potrero 5', 'capacidad': 15, 'hectareas': 7.5, 'ocupacion': 2, 'fecha_ultimo_uso': '2025-09-22', 'responsable_persona_id': 3, 'proxima_limpieza': '2025-11-04', 'area': '750.00', 'ultima_limpieza': '2025-09-22', 'descripcion': '', 'estado': 'ocupado'},
            {'id': 6, 'id_tipo_pasto': 3, 'nombre': 'Potrero 6', 'capacidad': 9, 'hectareas': 4.5, 'ocupacion': 0, 'fecha_ultimo_uso': '2025-09-21', 'responsable_persona_id': 4, 'proxima_limpieza': '2025-11-03', 'area': '450.00', 'ultima_limpieza': '2025-09-21', 'descripcion': '', 'estado': 'libre'},
            {'id': 7, 'id_tipo_pasto': 1, 'nombre': 'Potrero 7', 'capacidad': 11, 'hectareas': 5.5, 'ocupacion': 1, 'fecha_ultimo_uso': '2025-09-20', 'responsable_persona_id': 2, 'proxima_limpieza': '2025-11-02', 'area': '550.00', 'ultima_limpieza': '2025-09-20', 'descripcion': '', 'estado': 'ocupado'},
            {'id': 8, 'id_tipo_pasto': 2, 'nombre': 'Potrero 8', 'capacidad': 7, 'hectareas': 3.5, 'ocupacion': 0, 'fecha_ultimo_uso': '2025-09-19', 'responsable_persona_id': 3, 'proxima_limpieza': '2025-11-01', 'area': '350.00', 'ultima_limpieza': '2025-09-19', 'descripcion': '', 'estado': 'libre'},
            {'id': 9, 'id_tipo_pasto': 3, 'nombre': 'Potrero 9', 'capacidad': 13, 'hectareas': 6.5, 'ocupacion': 2, 'fecha_ultimo_uso': '2025-09-18', 'responsable_persona_id': 4, 'proxima_limpieza': '2025-10-31', 'area': '650.00', 'ultima_limpieza': '2025-09-18', 'descripcion': '', 'estado': 'ocupado'},
            {'id': 10, 'id_tipo_pasto': 1, 'nombre': 'Potrero 10', 'capacidad': 8, 'hectareas': 4.0, 'ocupacion': 1, 'fecha_ultimo_uso': '2025-09-17', 'responsable_persona_id': 2, 'proxima_limpieza': '2025-10-30', 'area': '400.00', 'ultima_limpieza': '2025-09-17', 'descripcion': '', 'estado': 'ocupado'},
            {'id': 11, 'id_tipo_pasto': 2, 'nombre': 'Potrero 11', 'capacidad': 10, 'hectareas': 5.0, 'ocupacion': 0, 'fecha_ultimo_uso': '2025-09-16', 'responsable_persona_id': 3, 'proxima_limpieza': '2025-10-29', 'area': '500.00', 'ultima_limpieza': '2025-09-16', 'descripcion': '', 'estado': 'libre'},
            {'id': 12, 'id_tipo_pasto': 3, 'nombre': 'Potrero 12', 'capacidad': 14, 'hectareas': 7.0, 'ocupacion': 3, 'fecha_ultimo_uso': '2025-09-15', 'responsable_persona_id': 4, 'proxima_limpieza': '2025-10-28', 'area': '700.00', 'ultima_limpieza': '2025-09-15', 'descripcion': '', 'estado': 'ocupado'},
            {'id': 13, 'id_tipo_pasto': 1, 'nombre': 'Potrero 13', 'capacidad': 9, 'hectareas': 4.5, 'ocupacion': 1, 'fecha_ultimo_uso': '2025-09-14', 'responsable_persona_id': 2, 'proxima_limpieza': '2025-10-27', 'area': '450.00', 'ultima_limpieza': '2025-09-14', 'descripcion': '', 'estado': 'ocupado'},
            {'id': 14, 'id_tipo_pasto': 2, 'nombre': 'Potrero 14', 'capacidad': 12, 'hectareas': 6.0, 'ocupacion': 2, 'fecha_ultimo_uso': '2025-09-13', 'responsable_persona_id': 3, 'proxima_limpieza': '2025-10-26', 'area': '600.00', 'ultima_limpieza': '2025-09-13', 'descripcion': '', 'estado': 'ocupado'},
            {'id': 15, 'id_tipo_pasto': 2, 'nombre': 'Potrero 4', 'capacidad': 5, 'hectareas': 2.0, 'ocupacion': 3, 'fecha_ultimo_uso': '2025-09-24', 'responsable_persona_id': 5, 'proxima_limpieza': '2025-11-08', 'area': '223.00', 'ultima_limpieza': '2025-09-24', 'descripcion': '', 'estado': 'ocupado'},
        ]
    )

    # Insertar datos reales de ganado
    op.bulk_insert(
        sa.table('ganado',
            sa.column('id', sa.Integer),
            sa.column('codigo_qr', sa.String),
            sa.column('id_potrero', sa.Integer),
            sa.column('id_persona', sa.Integer),
            sa.column('nombre', sa.String),
            sa.column('raza', sa.String),
            sa.column('fecha_nacimiento', sa.Date),
            sa.column('edad', sa.Integer),
            sa.column('sexo', sa.Enum('macho', 'hembra')),
            sa.column('peso', sa.Float),
            sa.column('estado', sa.String),
            sa.column('estado_salud', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ),
        [
            {'id': 1, 'codigo_qr': 'QR_1_mago.png', 'id_potrero': 1, 'id_persona': 2, 'nombre': 'mago', 'raza': 'Holstein', 'fecha_nacimiento': '2023-01-15', 'edad': 2, 'sexo': 'macho', 'peso': 450.5, 'estado': 'saludable', 'estado_salud': 'saludable', 'created_at': '2025-11-05', 'updated_at': '2025-11-05'},
            {'id': 2, 'codigo_qr': 'QR_2_luna.png', 'id_potrero': 2, 'id_persona': 3, 'nombre': 'luna', 'raza': 'Jersey', 'fecha_nacimiento': '2022-06-20', 'edad': 3, 'sexo': 'hembra', 'peso': 380.2, 'estado': 'saludable', 'estado_salud': 'saludable', 'created_at': '2025-11-05', 'updated_at': '2025-11-05'},
            {'id': 3, 'codigo_qr': 'QR_3_rayo.png', 'id_potrero': 3, 'id_persona': 4, 'nombre': 'rayo', 'raza': 'Holstein', 'fecha_nacimiento': '2023-03-10', 'edad': 2, 'sexo': 'macho', 'peso': 420.8, 'estado': 'revision', 'estado_salud': 'revision', 'created_at': '2025-11-05', 'updated_at': '2025-11-05'},
            {'id': 4, 'codigo_qr': 'QR_4_estrella.png', 'id_potrero': 5, 'id_persona': 2, 'nombre': 'estrella', 'raza': 'Jersey', 'fecha_nacimiento': '2021-11-05', 'edad': 4, 'sexo': 'hembra', 'peso': 395.3, 'estado': 'saludable', 'estado_salud': 'saludable', 'created_at': '2025-11-05', 'updated_at': '2025-11-05'},
            {'id': 5, 'codigo_qr': 'QR_5_titan.png', 'id_potrero': 7, 'id_persona': 3, 'nombre': 'titan', 'raza': 'Holstein', 'fecha_nacimiento': '2022-08-12', 'edad': 3, 'sexo': 'macho', 'peso': 480.1, 'estado': 'saludable', 'estado_salud': 'saludable', 'created_at': '2025-11-05', 'updated_at': '2025-11-05'},
            {'id': 6, 'codigo_qr': 'QR_6_bella.png', 'id_potrero': 9, 'id_persona': 4, 'nombre': 'bella', 'raza': 'Jersey', 'fecha_nacimiento': '2023-05-18', 'edad': 2, 'sexo': 'hembra', 'peso': 365.7, 'estado': 'saludable', 'estado_salud': 'saludable', 'created_at': '2025-11-05', 'updated_at': '2025-11-05'},
            {'id': 7, 'codigo_qr': 'QR_7_fuego.png', 'id_potrero': 10, 'id_persona': 2, 'nombre': 'fuego', 'raza': 'Holstein', 'fecha_nacimiento': '2022-12-03', 'edad': 3, 'sexo': 'macho', 'peso': 435.9, 'estado': 'enfermo', 'estado_salud': 'enfermo', 'created_at': '2025-11-05', 'updated_at': '2025-11-05'},
            {'id': 8, 'codigo_qr': 'QR_8_linda.png', 'id_potrero': 12, 'id_persona': 3, 'nombre': 'linda', 'raza': 'Jersey', 'fecha_nacimiento': '2021-09-25', 'edad': 4, 'sexo': 'hembra', 'peso': 410.4, 'estado': 'saludable', 'estado_salud': 'saludable', 'created_at': '2025-11-05', 'updated_at': '2025-11-05'},
            {'id': 9, 'codigo_qr': 'QR_9_mago.png', 'id_potrero': 13, 'id_persona': 4, 'nombre': 'mago', 'raza': 'Holstein', 'fecha_nacimiento': '2023-07-08', 'edad': 2, 'sexo': 'macho', 'peso': 398.6, 'estado': 'saludable', 'estado_salud': 'saludable', 'created_at': '2025-11-05', 'updated_at': '2025-11-05'},
        ]
    )


def downgrade() -> None:
    # Eliminar datos reales (en orden inverso para respetar foreign keys)
    op.execute("DELETE FROM vacunacion WHERE id > 0")
    op.execute("DELETE FROM ganado WHERE id > 0")
    op.execute("DELETE FROM potrero WHERE id > 0")
    op.execute("DELETE FROM usuarios WHERE id_persona > 1")  # Excluir admin
    op.execute("DELETE FROM personas WHERE id > 1")  # Excluir admin
