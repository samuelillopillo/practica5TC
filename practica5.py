def extraer_tokens(expresion):
    tokens = [] # Lista vacia donde guardaremos cada pieza encontrada
    i = 0 # indice
    n = len(expresion) # el tamaño de la cadena

    while i < n:
        if expresion[i].isspace():
            i += 1 # si hay un espacio en blanco avanza en 1
            continue

        c = expresion[i] # Guardamos en c el caracter exacto que estamos viendo

        # 1 El caracter acuatl es un parentesis?
        if c in '([{)]}':
            tokens.append((c, i)) # Guardamos el simbolo y su posicion i
            i += 1 # avanza el siguiente caracter
            continue

        # 2. Truco para saber si '+' o '-' es signo de un numero negativo/positivo
        es_signo_numero = False
        if c in '+-':
            # Es signo de un numero SOLO SI esta el principio de todo
            # o si justo antes hubo un parentesis que abre o un operador
            if len(tokens) == 0 or tokens[-1][0] in '([{+-*/':
                if i + 1 < n and expresion[i + 1].isdigit(): # y lo que sigue es un digito
                    es_signo_numero = True

        # 3. Si es un digito o descubrimos que empieza con signo negativo/positivo
        if c.isdigit() or es_signo_numero:
            inicio = i
            if c in '+-':
                i += 1 # avanza al signo
            while i < n and expresion[i].isdigit():
                i += 1 # avanza mientras sea un numero entero
            if i + 1 < n and expresion[i] == '.' and expresion[i + 1].isdigit():
                i += 1 # si hay un . lo saltamos
                while i < n and expresion[i].isdigit():
                    i += 1 # Sigue avanzando por los decimales

            # cortamos el pedazo completo (ej. "-65.4") y lo guardamos en la posicion inicial
            tokens.append((expresion[inicio:i], inicio))
            continue

        # 4. Si no fue numero, pero es +, -, *, / entonces es un operador aritmetico
        if c in '+-*/':
            tokens.append((c, i))
            i += 1
            continue

        # 5. Si escribio algun otro caracter los guardamos pra marcar error
        tokens.append((c, i))
        i += 1
        continue

    return tokens # Devolvemos la lista

def clasificar_numero(token):
    signo = "Negativo" if token.startswith('-') else "Positivo"
    tipo = "Real" if '.' in token else "Entero"
    return f"{tipo} {signo}"

def ver_pila(pila):
    # Muestra solo los simbolos
    return [s for s, _, _ in pila]

def validar_expresion(expresion):
    print(f"Expresion: {expresion}")

    tokens = extraer_tokens(expresion)
    pila = [] # pila vacia
    pares = {')': '(', ']': '[', '}': '{'} #diccionario para saber quien cierra a quien
    errores = [] # Lista para anotar los errores

    salida = [] # Guardamos los textos para marcar posibles errores previos
    historial_cierres = {')': [], ']': [], '}': []} # Guarda en que linea de 'salida' se cerro cada simbolo

    for token, pos in tokens:
        pos += 1
        # Caso a: si es un parentesis que abre, simepre se mete a la pila
        if token in '([{':
            idx_actual = len(salida)
            pila.append((token, pos, idx_actual)) # Metemos el simbolo y su posicion en la pila
            salida.append(f"{token} Parentesis que abre: {token} [se apila '{token}'] Pila: {ver_pila(pila)}")

        # Caso b si es un parentesis que cierra revisamos el tope de la pila
        elif token in ')]}':
            abierto_esperado = pares[token] # Ej, si llego ']' esperamos que haya un '['

            #Error 1. La pila esta vacia? (Cerro algo que nunca abrio)
            if len(pila) == 0:
                # Si ya habia cerrado este mismop simbolo tambienm lo marcamos como posible error
                for idx_linea in historial_cierres[token]:
                    if "(posible error)" not in salida[idx_linea]:
                        salida[idx_linea] = salida[idx_linea].replace(
                            f"Parentesis que cierra {token}",
                            f"Parentesis que cierra {token} (posible error)"
                        )
                salida.append(f"{token} Parentesis que cierra {token} (posible error). Pila: {ver_pila(pila)}")
                errores.append(f"Error en posicion {pos}: '{token}' no tiene parentesis que lo abra")

            # Si si hay cosas en la pila, sacamos el ultimo que entro
            else:
                tope_simbolo, tope_pos, _ = pila.pop()

                # El que sacamos de la pila coincide con el que cierra?
                if tope_simbolo == abierto_esperado:
                    idx_linea = len(salida)
                    historial_cierres[token].append(idx_linea) # Recorremos esta linea por si mas adelante sobra otro igual
                    salida.append(f"{token} Parentesis que cierra {token} [se desapila '{tope_simbolo}'] Pila: {ver_pila(pila)}")
                else:
                    #Error 2 se cruzaron Ej. habia '(' en la pila pero llego ']'
                    salida.append(f"{token} Parentesis que cierra {tope_simbolo} (Posible error) [se desapila '{tope_simbolo}'] Pila: {ver_pila(pila)}")
                    errores.append(f"Error en posicion {pos}: llego '{token}' pero se esperaba cerrar '{tope_simbolo}' (abierto en pos {tope_pos}).")

        # Caso c: si es un operador (+,-,*,/)
        elif token in '+-/*':
            salida.append(f"{token} Simbolo")

        # Caso d: si es un numero
        elif token[0].isdigit() or (token[0] in '+-' and len(token) > 1):
            salida.append(f"{token} {clasificar_numero(token)}")

        # Caso e: Cualkquier otro caracter invlido
        else:
            salida.append(f"{token} Caracter Invalido (error)")
            errores.append(f"Error en posicion {pos}: '{token}' es un caracter invalido.")

    # Error 3: Terminamos de leer toda la expresion y quedaron parentesis abiertos en la pila?
    while len(pila) > 0:
        simbolo_sin_cerrar, pos_sin_cerrar, idx_abierto = pila.pop()
        salida[idx_abierto] = salida[idx_abierto].replace(
            f"Parentesis que abre: {simbolo_sin_cerrar}",
            f"Parentesis que abre: {simbolo_sin_cerrar} (posible error)"
        )
        errores.append(f"Error en posicion {pos_sin_cerrar}: '{simbolo_sin_cerrar}' se quedo abierto en la pila.")

    for linea in salida:
        print(linea)
    # veredicto final
    if len(errores) == 0:
        print("El uso de parentesis es correcto")
    else:
        print("Error en la expresion")
        for e in errores:
            print("->", e)

validar_expresion("(534+65)")
validar_expresion("(-65.4+34)+53)")
validar_expresion("{6+[4*(5-3])}")

# Permitir ingresar una expresión manual al profesor
while True:
    nueva = input("\nIngresa una expresion para validar (o presiona Enter para salir): ")
    if nueva.strip() == "":
        break
    validar_expresion(nueva)
