
from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'qr_farm_super_secret_key_2025'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/inventario')
def inventario():
    return render_template('inventario.html')

from flask import request, redirect, url_for, flash, session

@app.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    if request.method == 'POST':
        return redirect(url_for('menu'))
    return render_template('iniciar_sesion.html', error=None)

@app.route('/gestionar_animales')
def gestionar_animales():
    return render_template('gestionar_animales.html')

@app.route('/gestionar_potreros')
def gestionar_potreros():
    return render_template('gestionar_potreros.html')

@app.route('/escanear_qr')
def escanear_qr():
    return render_template('escanear_qr.html')

@app.route('/crear_cuenta')
def crear_cuenta():
    return render_template('crear_cuenta.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/registro_vacunacion')
def registro_vacunacion():
    return render_template('registro_vacunacion.html')

if __name__ == '__main__':
    app.run(debug=True)
