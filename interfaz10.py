import re
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tabulate import tabulate


# Define los colores y la fuente que deseas utilizar
COLOR_PRINCIPAL = 'blue'
COLOR_SECUNDARIO = 'white'
COLOR_FONDO = 'gray'
FUENTE = ('Helvetica', 12)  

class InstruccionIntermedia:
    def _init_(self, operacion, operando1, operando2, resultado):
        self.operacion = operacion
        self.operando1 = operando1
        self.operando2 = operando2
        self.resultado = resultado

instrucciones_intermedias = []

funciones_codigo_intermedio = [
    ("asignacion", "Genera el código intermedio para una operación de asignación"),
    ("operacion_aritmetica", "Genera el código intermedio para operaciones aritméticas"),
    ("condicion_if", "Genera el código intermedio para una estructura de control 'if'"),
    ("bucle_while", "Genera el código intermedio para un bucle 'while'")
    ]

def miventana(input_string):
    # Patrones para cada tipo de token
    patrones = [
        ('PALABRA_RESERVADA', r'(IF|ELSE|WHILE|FOR|FUNCTION|VARIABLE)'),  # Palabras reservadas
        ('ENTERO', r'\d+'),  # Enteros
        ('TEXTO', r'"[^"]*"'),  # Texto entre comillas
        ('BOOLEANO', r'(Verdadero|Falso)'),  # Booleanos Verdadero o Falso
        ('DECIMAL', r'\d+\.\d+|\.\d+|\d+\.'),  # Decimales
        ('SUMA', r'\+'),  # Suma
        ('RESTA', r'-'),  # Resta
        ('MULTIPLICACION', r'\*'),  # Multiplicación
        ('DIVISION', r'/'),  # División
        ('IDENTIFICADOR', r'[a-zA-Z_]\w*'),  # Identificadores
        ('SIMBOLO', r'[,;=.¿?]'),  # Símbolos como coma y punto y coma
        ('PARENTESIS', r'[()]')  # Paréntesis
    ]

    token_regex = re.compile('|'.join('(?P<%s>%s)' % patron for patron in patrones))
    tokens = []

    # Coincidencias en el input_string y crear los tokens correspondientes
    for num_linea, linea in enumerate(input_string.split('\n'), start=1):
        for match in token_regex.finditer(linea):
            token_type = match.lastgroup
            token_value = match.group(token_type)
            tokens.append((num_linea, token_type, token_value))

    return tokens

def verificar_tokens(tokens):
    errores_lexicos = []
    errores_sintacticos = []
    variables_esperadas = False
    tipo_variable_esperado = False
    valor_esperado = False

    for num_linea, token_type, token_value in tokens:
        if token_type is None:
            errores_lexicos.append((num_linea, f"Token no reconocido: '{token_value}'"))
            continue

        if variables_esperadas:
            if token_type == 'IDENTIFICADOR':
                variables_esperadas = False
                tipo_variable_esperado = True
            else:
                errores_sintacticos.append((num_linea, "Se esperaba un nombre de variable"))

        elif tipo_variable_esperado:
            if token_type == 'PALABRA_RESERVADA' and token_value.lower() == 'es':
                tipo_variable_esperado = False
                valor_esperado = True
            else:
                errores_sintacticos.append((num_linea, "Se esperaba la palabra reservada 'es'"))

        elif valor_esperado:
            if token_type in ('ENTERO', 'TEXTO', 'DECIMAL', 'BOOLEANO'):
                valor_esperado = False
                variables_esperadas = True
            else:
                errores_sintacticos.append((num_linea, "Se esperaba un valor (ENTERO, TEXTO, DECIMAL, BOOLEANO)"))

        # Verificar si hay un punto y coma al final de la línea
        if token_value.strip() == ';':
            errores_sintacticos.append((num_linea, "No se espera ';' al final de la línea"))

    return errores_lexicos, errores_sintacticos


def verificar_palabras(input_string):
    errores = []
    # Separar el input_string en palabras individuales
    palabras = re.findall(r'\w+', input_string)

    for palabra in palabras:
        if not re.match(r'[a-zA-Z_]\w*', palabra):
            errores.append((f"Palabra no reconocida: '{palabra}'"))
    return errores

def analizador_semantico(tokens):
    tabla_simbolos = {}
    errores_semanticos = []

    for num_linea, token_type, token_value in tokens:
        if token_type == 'PALABRA_RESERVADA' and token_value.lower() == 'variable':
            # Declaración de variable
            _, _, nombre_variable = tokens.pop(0)  # Obtenemos el siguiente token que debe ser el nombre de la variable
            _, _, tipo_variable = tokens.pop(0)  # Obtenemos el siguiente token que debe ser el tipo de variable

            if nombre_variable in tabla_simbolos:
                errores_semanticos.append((num_linea, f"La variable '{nombre_variable}' ya ha sido declarada"))
            else:
                tabla_simbolos[nombre_variable] = tipo_variable

        elif token_type == 'IDENTIFICADOR':
            if token_value not in tabla_simbolos:
                errores_semanticos.append((num_linea, f"La variable '{token_value}' no ha sido declarada"))

        elif token_type in ('SUMA', 'RESTA', 'MULTIPLICACION', 'DIVISION'):
            # Operaciones aritméticas
            # Obtener los tipos de las variables involucradas en la operación
            tipo_operando1 = tabla_simbolos.get(tokens[num_linea - 2][2])
            tipo_operando2 = tabla_simbolos.get(tokens[num_linea][2])

            if tipo_operando1 not in ('ENTERO', 'DECIMAL') or tipo_operando2 not in ('ENTERO', 'DECIMAL'):
                errores_semanticos.append((num_linea, "Operación inválida. Solo se pueden realizar operaciones con variables numéricas"))

    return errores_semanticos

def generar_codigo_intermedio(tokens):
    global instrucciones_intermedias
    instrucciones_intermedias.clear()

def abrir_archivo():
    # Abrir el cuadro de diálogo para seleccionar el archivo
    archivo_path = filedialog.askopenfilename(filetypes=[('Archivos de texto', '*.txt')])

    # Verificar si se seleccionó un archivo
    if archivo_path:
        # Abrir el archivo
        try:
            with open(archivo_path, 'r') as archivo:
                contenido = archivo.read()
                lineas = contenido.split("\n")  # Separar el contenido por saltos de línea

                tabla_tokens = []
                errores_lexicos = []
                errores_sintacticos = []
                for num_linea, linea in enumerate(lineas, start=1):
                    errores_palabras = verificar_palabras(linea)  # Verificar palabras no reconocidas
                    errores_lexicos.extend([(num_linea, error) for error in errores_palabras])
                    tokens = miventana(linea)  # Obtener los tokens de cada línea
                    errores_lex, errores_sin = verificar_tokens(tokens)
                    errores_lexicos.extend(errores_lex)
                    errores_sintacticos.extend(errores_sin)
                    for num_token, token_type, token_value in tokens:
                        tabla_tokens.append([num_linea, num_token, token_type, token_value])


                   # Generar código intermedio
                    generar_codigo_intermedio(tokens)

                   # Ventana para mostrar el contenido y el análisis léxico y sintáctico
                    ventana = tk.Toplevel()
                    ventana.title('Analizador Léxico y Sintáctico Las J\'S')
                    ventana.geometry("1000x500")

                    # Cambiar el estilo del tema de la interfaz a 'clam'
                    estilo_clam = ttk.Style(ventana)
                    estilo_clam.theme_use('clam')

                    # Configurar los colores y fuentes para los widgets
                    estilo_clam.configure("Treeview", background=COLOR_SECUNDARIO, foreground=COLOR_PRINCIPAL, font=FUENTE)
                    estilo_clam.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_PRINCIPAL, font=FUENTE)

                    # Crear un widget de etiqueta para mostrar el contenido del archivo
                    etiqueta_contenido = tk.Label(ventana, text=contenido, wraplength=500, justify='left', font=('Arial', 12))
                    etiqueta_contenido.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

                    # Etiqueta para la tabla de tokens
                    etiqueta_tokens = tk.Label(ventana, text="Tabla de Tokens", font=('Arial', 12, 'bold'))
                    etiqueta_tokens.grid(row=1, column=0, padx=10, pady=5, sticky='w')

                  # Crear un widget de tabla utilizando el módulo ttk.Treeview para los tokens
                    tabla_tokens_widget = ttk.Treeview(ventana, columns=("Num. Línea", "Token", "Tipo", "Valor"), show="headings")
                    tabla_tokens_widget.heading("Num. Línea", text="Num. Línea")
                    tabla_tokens_widget.heading("Token", text="Token")
                    tabla_tokens_widget.heading("Tipo", text="Tipo")
                    tabla_tokens_widget.heading("Valor", text="Valor")

                    for item in tabla_tokens:
                     tabla_tokens_widget.insert("", "end", values=item)

                    tabla_tokens_widget.grid(row=2, column=0, padx=10, pady=5, sticky='nsew')
                    tabla_tokens_widget.column("Num. Línea", width=80, anchor="center")
                    tabla_tokens_widget.column("Token", width=100, anchor="center")
                    tabla_tokens_widget.column("Tipo", width=150, anchor="center")
                    tabla_tokens_widget.column("Valor", width=150, anchor="center")
                 
                    # Etiqueta para la tabla de errores léxicos
                    etiqueta_errores_lexicos = tk.Label(ventana, text="Errores Léxicos", font=('Arial', 12, 'bold'))
                    etiqueta_errores_lexicos.grid(row=3, column=0, padx=10, pady=5, sticky='w')

                    # Crear un widget de tabla para los errores léxicos
                    errores_lexicos_widget = ttk.Treeview(ventana, columns=("Num. Línea", "Error"), show="headings")
                    errores_lexicos_widget.heading("Num. Línea", text="Num. Línea")
                    errores_lexicos_widget.heading("Error", text="Error")

                    for item in errores_lexicos:
                         errores_lexicos_widget.insert("", "end", values=item)

                    errores_lexicos_widget.grid(row=4, column=0, padx=10, pady=5, sticky='nsew')
                    errores_lexicos_widget.column("Num. Línea", width=80, anchor="center")
                    errores_lexicos_widget.column("Error", width=400, anchor="w")
                    
                    # Centrar datos de la tabla
                    for col in ("Num. Línea", "Error"):
                        errores_lexicos_widget.column(col, anchor="center")

                    # Etiqueta para la tabla de errores sintácticos
                    etiqueta_errores_sintacticos = tk.Label(ventana, text="Errores Sintácticos", font=('Arial', 12, 'bold'))
                    etiqueta_errores_sintacticos.grid(row=1, column=1, padx=10, pady=5, sticky='w')

                  # Crear un widget de tabla para los errores sintácticos
                    errores_sintacticos_widget = ttk.Treeview(ventana, columns=("Num. Línea", "Error"), show="headings")
                    errores_sintacticos_widget.heading("Num. Línea", text="Num. Línea")
                    errores_sintacticos_widget.heading("Error", text="Error")

                    for item in errores_sintacticos:
                     errores_sintacticos_widget.insert("", "end", values=item)

                    errores_sintacticos_widget.grid(row=2, column=1, padx=10, pady=5, sticky='nsew')
                    errores_sintacticos_widget.column("Num. Línea", width=80, anchor="center")
                    errores_sintacticos_widget.column("Error", width=400, anchor="w")
                   
                   
                    # Centrar datos de la tabla
                    for col in ("Num. Línea", "Error"):
                     errores_sintacticos_widget.column(col, anchor="center")

                    ventana.grid_rowconfigure(0, weight=1)
                    ventana.grid_columnconfigure(0, weight=1)
                    ventana.grid_columnconfigure(1, weight=1)

                    errores_semanticos = analizador_semantico(tokens)

                    # Crear un widget de tabla para los errores semánticos
                    etiqueta_errores_semanticos = tk.Label(ventana, text="Errores Semánticos", font=('Arial', 12, 'bold'))
                    etiqueta_errores_semanticos.grid(row=3, column=1, padx=10, pady=5, sticky='w')

                    errores_semanticos_widget = ttk.Treeview(ventana, columns=("Num. Línea", "Error"), show="headings")
                    errores_semanticos_widget.heading("Num. Línea", text="Num. Línea")
                    errores_semanticos_widget.heading("Error", text="Error")

                    for num_linea, mensaje in errores_semanticos:
                        errores_semanticos_widget.insert("", "end", values=(num_linea, mensaje))

                        errores_semanticos_widget.grid(row=4, column=1, padx=10, pady=5, sticky='nsew')
                        # Centrar datos de la tabla
                        for col in ("Num. Línea", "Error"):
                         errores_semanticos_widget.column(col, anchor="center")

                    # Crear un widget de tabla para mostrar las funciones de código intermedio
                        tabla_funciones_ci_widget = ttk.Treeview(ventana, columns=("Nombre de la función", "Descripción"), show="headings")
                        tabla_funciones_ci_widget.heading("Nombre de la función", text="Nombre de la función")
                        tabla_funciones_ci_widget.heading("Descripción", text="Descripción")

                        for nombre_funcion, descripcion in funciones_codigo_intermedio:
                         tabla_funciones_ci_widget.insert("", "end", values=(nombre_funcion, descripcion))

                        tabla_funciones_ci_widget.grid(row=2, column=2, padx=10, pady=5, sticky='nsew')
                        tabla_funciones_ci_widget.column("Nombre de la función", width=200, anchor="center")
                        tabla_funciones_ci_widget.column("Descripción", width=300, anchor="w")
                  
                  # Mostrar el código intermedio en una tabla en la ventana
                    etiqueta_codigo_intermedio = tk.Label(ventana, text="Código Intermedio", font=('Arial', 12, 'bold'))
                    etiqueta_codigo_intermedio.grid(row=1, column=2, padx=10, pady=5, sticky='w')

                tabla_codigo_intermedio_widget = ttk.Treeview(ventana, columns=("Operación", "Operando 1", "Operando 2", "Resultado"), show="headings")
                tabla_codigo_intermedio_widget.heading("Operación", text="Operación")
                tabla_codigo_intermedio_widget.heading("Operando 1", text="Operando 1")
                tabla_codigo_intermedio_widget.heading("Operando 2", text="Operando 2")
                tabla_codigo_intermedio_widget.heading("Resultado", text="Resultado")

                for instruccion in instrucciones_intermedias:
                    tabla_codigo_intermedio_widget.insert("", "end", values=(instruccion.operacion, instruccion.operando1, instruccion.operando2, instruccion.resultado))

                tabla_codigo_intermedio_widget.grid(row=2, column=2, padx=10, pady=5, sticky='nsew')
                tabla_codigo_intermedio_widget.column("Operación", width=120, anchor="center")
                tabla_codigo_intermedio_widget.column("Operando 1", width=120, anchor="center")
                tabla_codigo_intermedio_widget.column("Operando 2", width=120, anchor="center")
                tabla_codigo_intermedio_widget.column("Resultado", width=120, anchor="center")

                ventana.grid_rowconfigure(0, weight=1)
                ventana.grid_columnconfigure(0, weight=1)
                ventana.grid_columnconfigure(1, weight=1)
                ventana.grid_columnconfigure(2, weight=1)
                ventana.mainloop()

        except FileNotFoundError:
            print(f"No se pudo encontrar el archivo: {archivo_path}")
        except IOError:
            print(f"No se pudo abrir el archivo: {archivo_path}")

# Crear la ventana principal
ventana_principal = tk.Tk()
ventana_principal.title("Analizador Léxico y Sintáctico Las J'S")
ventana_principal.geometry("600x400")

# Estilo para los widgets
style = ttk.Style()
style.configure("Treeview", font=('Arial', 12), rowheight=25)

# Botón para abrir el archivo
boton_abrir = tk.Button(ventana_principal, text="Seleccionar un archivo", command=abrir_archivo, bg="blue", fg="white")
boton_abrir.pack(pady=20)

ventana_principal.mainloop()