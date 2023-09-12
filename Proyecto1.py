from graphviz import Digraph

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

def create_ast(postfix):
    stack = []
    operators = ['|','*','.']

    for char in postfix:
        if char not in operators:  # si es un operador, se crea un nuevo nodo y se empuja en la pila
            new_node = Node(char)
            stack.append(new_node)
        else:  # si es un operador, se crea un nuevo nodo y se conecta con dos nodos anteriores
            new_node = Node(char)
            new_node.right = stack.pop()  # el segundo nodo se convierte en el hijo derecho
            if char != '*':  # '*' es un operador unario
                new_node.left = stack.pop()  # el primer nodo se convierte en el hijo izquierdo
            stack.append(new_node)
            
    return stack[0] if stack else None  # el último nodo en la pila es la raíz del AST

def plot_tree(root, graph=None):
    if graph is None:
        graph = Digraph()
        graph.node(name=str(id(root)), label=root.value)
    if root.left:  # si el nodo izquierdo existe, se agrega al gráfico y se conecta con la raíz
        graph.node(name=str(id(root.left)), label=root.left.value)
        graph.edge(str(id(root)), str(id(root.left)))
        plot_tree(root.left, graph)
    if root.right:  # si el nodo derecho existe, se agrega al gráfico y se conecta con la raíz
        graph.node(name=str(id(root.right)), label=root.right.value)
        graph.edge(str(id(root)), str(id(root.right)))
        plot_tree(root.right, graph)
    return graph

def shunting_yard(regex):
    postfix = ''
    operators = ['|','?','+','*','.']
    stack = []
    formattedRegEx = formatRegEx(regex)
    
    i=0
    print("\n----Linea-----")
    while i<len(formattedRegEx):
        c = formattedRegEx[i]
        print('Caracter:'+c)
        
        if c=='(':
            stack.append(c)
        elif c==')':
            while stack[-1]!='(':
                postfix+=stack.pop()
            
            stack.pop()
        elif c in operators:
            while len(stack)>0:
                peekedChar = stack[-1]
                peekedCharPrecedence = getPrecedence(peekedChar)
                currentCharPrecedence = getPrecedence(c)
                
                if peekedCharPrecedence>=currentCharPrecedence:
                    postfix+=stack.pop()
                else:
                    break
            
            stack.append(c)
        elif c=='\\':
            if i+1<len(formattedRegEx):
                print('Caracter escapado:'+formattedRegEx[i+1])
                postfix+=formattedRegEx[i+1]
                i+=1
        else:
            postfix+=c
        
        i+=1
        
        print('Pila:'+str(stack))
        print('Cola:'+postfix+'\n')
    
    while len(stack)>0:
        postfix+=stack.pop()
    
    return postfix

def getPrecedence(c):
    if c=='(':
        return 1
    elif c=='|':
        return 2
    elif c=='.':
        return 3
    elif c=='?':
        return 4
    elif c=='*':
        return 4
    elif c=='+':
        return 4

def formatRegEx(regex):
    allOperators = ['|','?','+','*']
    binaryOperators = ['|']
    res = ''
    
    while '+' in regex:
        i=regex.index('+')
        if regex[i-1]!=')':
            regex=regex.replace(regex[i-1]+"+",regex[i-1]+regex[i-1]+"*")
        elif regex[i-1]==')':
            j=i-2
            count = 0
            
            while (regex[j]!='(' or count!=0) and j>=0:
                if regex[j]==')':
                    count+=1
                elif regex[j]=='(':
                    count-=1
                j-=1
            if regex[j]=='(' and count==0:
                sub=regex[j:i]
                regex=regex.replace(sub+"+",sub+sub+"*")
                
    while '?' in regex:
        i=regex.index('?')
        if regex[i-1]!=')':
            regex=regex.replace(regex[i-1]+"?","("+regex[i-1]+"|ε)")
        elif regex[i-1]==')':
            j=i-2
            count = 0
            
            while (regex[j]!='(' or count!=0) and j>=0:
                if regex[j]==')':
                    count+=1
                elif regex[j]=='(':
                    count-=1
                j-=1
            if regex[j]=='(' and count==0:
                sub=regex[j:i]
                regex=regex.replace(sub+"?","("+sub+"|ε)")
                
    i=0
    while i<len(regex):
        c1 = regex[i]
        
        if i+1<len(regex):
            c2 = regex[i+1]
            
            if c1=='\\':
                c1+=c2
                if i+2<len(regex):
                    c2 = regex[i+2]
                else:
                    c2 = ''
                i+=1
            elif c1=='[':
                j=i+1
                while j<len(regex) and regex[j]!=']':
                    c1+=regex[j]
                    j+=1
                c1+=regex[j]
                i=j
                if i+1<len(regex):
                    c2 = regex[i+1]
                else:
                    c2 = ''
            res+=c1
            
            if c2!='' and c1!='(' and c2!=')' and c2 not in allOperators and c1 not in binaryOperators:
                res+='.'
        else:
            res+=c1
        i+=1
    
    return res


#Lab4

class AFNState:
    state_counter = 0
    states = []

    def __init__(self):
        self.name = str(AFNState.state_counter)
        AFNState.state_counter += 1
        AFNState.states.append(self)

        self.transitions = {}
        self.is_accept = False

class AFN:
    def __init__(self):
        self.start = None
        self.accept = None
        
def ast_to_afn(node,left_start=None,start_node=True):
    if not node:
        return None
    
    afn = AFN()
    
    # Un nodo básico con un carácter
    if node.value not in ['|', '.', '*']:
        if left_start:
            start = left_start
        else:
            start = AFNState()
            
        accept = AFNState()
        if start_node:
            accept.is_accept = True
            
        start.transitions[node.value] = [accept]
        afn.start = start
        afn.accept = accept
    elif node.value == '|':
        if left_start:
            start = left_start
        else:
            start = AFNState()
            
        afn_left = ast_to_afn(node=node.left,start_node=False)
        afn_right = ast_to_afn(node=node.right,start_node=False)
            
        accept = AFNState()
        if start_node:
            accept.is_accept = True
        
        start.transitions['ε'] = [afn_left.start, afn_right.start]
        afn_left.accept.transitions['ε'] = [accept]
        afn_right.accept.transitions['ε'] = [accept]
        
        afn.start = start
        afn.accept = accept
    elif node.value == '*':
        if left_start:
            start = left_start
        else:
            start = AFNState()
            
        afn_inner = ast_to_afn(node=node.right,start_node=False)
        
        accept = AFNState()
        if start_node:
            accept.is_accept = True
        
        start.transitions['ε'] = [afn_inner.start, accept]
        afn_inner.accept.transitions['ε'] = [afn_inner.start, accept]
        
        afn.start = start
        afn.accept = accept
    elif node.value == '.':
        afn_left = ast_to_afn(node=node.left,start_node=False)
        afn_right = ast_to_afn(node=node.right,left_start=afn_left.accept,start_node=False)
        
        afn.start = afn_left.start
        afn.accept = afn_right.accept
        if start_node:
            afn.accept.is_accept = True

    return afn

def plot_af(state, graph=None, visited=None):
    if visited is None:
        visited = set()

    if state in visited:
        return graph

    if graph is None:
        graph = Digraph(engine='dot', graph_attr={'rankdir': 'LR'})
    
    if state.is_accept:
        graph.node(name=str(id(state)), label=state.name, shape='doublecircle')
    else:
        graph.node(name=str(id(state)), label=state.name, shape='circle')
        
    visited.add(state)

    for symbol, next_states in state.transitions.items():
        for next_state in next_states:
            graph.edge(str(id(state)), str(id(next_state)), label=symbol)
            plot_af(next_state, graph, visited)

    return graph

def e_closure_state(state, visited=None):
    if visited is None:
        visited = set()

    if state in visited:
        return
        
    visited.add(state)

    for symbol, next_states in state.transitions.items():
        for next_state in next_states:
            if symbol == 'ε':
                e_closure_state(next_state,visited)

    return visited

def e_closure(S):
    res = set()
    for state in S:
        res = res.union(e_closure_state(state))
        
    return res

def move(S,c):
    res = set()
    
    for state in S:
        for symbol,next_states in state.transitions.items():
            for next_state in next_states:
                if symbol == c:
                    res.add(next_state)
    
    return res
    
def AFN_simulation(afn,w):
    F = set()
    F.add(afn.accept)
    So = set()
    So.add(afn.start)
    
    S = e_closure(So)

    for c in w:
        S = e_closure(move(S,c))
        
    if F.intersection(S):
        return "sí"
    else:
        return "no"
    

#Proyecto 1

class AFDState:
    state_counter = 'A'
    states = []

    def __init__(self,subset=set()):
        self.name = str(AFDState.state_counter)
        AFDState.state_counter = chr(ord(AFDState.state_counter) + 1)
        AFDState.states.append(self)
        self.subset = subset

        self.transitions = {}
        self.is_accept = False

class AFD:
    def __init__(self):
        self.start = None
        self.accept = []
        
def regexAlphabet(postfix):
    alphabet = set()
    reserved = ['|','*','.','ε']
    
    for char in postfix:
        if char not in reserved:
            alphabet.add(char)
            
    return alphabet

def afn_to_afd(alphabet,afn):
    F = set()
    F.add(afn.accept)
    states = []
    
    So = set()
    So.add(afn.start)
    
    afd = AFD()
    
    states.append(AFDState(subset=e_closure(So)))
    afd.start = states[0]
    
    if afn.accept in states[0].subset:
        afd.accept.append(states[0])
        states[0].is_accept = True
    
    contador=0
    nuevosEstados=0
    
    while contador!=nuevosEstados or (contador==0 and nuevosEstados==0):
        if nuevosEstados!=0:
            contador+=1
        
        for symbol in alphabet:
            cambio=False
            subset=e_closure(move(states[contador].subset,symbol))
            
            for state in states:
                if state.subset==subset:
                    states[contador].transitions[symbol] = [state]
                    cambio=True
                    break
            
            if cambio!=True:
                newState = AFDState(subset)
                
                if afn.accept in subset:
                    afd.accept.append(newState)
                    newState.is_accept = True
                
                states[contador].transitions[symbol] = [newState]
                states.append(newState)
                nuevosEstados+=1
        
    return afd

with open("texto.txt", 'r') as f:
    i=1
    for linea in f:
        linea = linea.strip()
        postfix = shunting_yard(linea)
        print(f"Expresion regular: {linea}")
        print(f"Postfijo: {postfix}")
        ast_root = create_ast(postfix)
        tree_graph = plot_tree(ast_root)
        nombre_archivo_pdf = 'AST no '+ str(i)
        tree_graph.view(filename=nombre_archivo_pdf,cleanup=True)
        
        #Lab4
        afn = ast_to_afn(ast_root)
        afn_graph = plot_af(afn.start)
        nombre_archivo_pdf = 'AFN no ' + str(i)
        afn_graph.view(filename=nombre_archivo_pdf,cleanup=True)
        
        #Esperar ingreso de cadena
        #respuesta = ""
        #while respuesta!="y" and respuesta!="n":
            #respuesta = input("\n¿Desea ingresar una cadena para simular el AFN? y/n\n")
            #if respuesta=="y":
                #w = input("Ingrese la cadena w.\n")
                #print(AFN_simulation(afn,w))
                #input("Presione [Enter] para continuar.")
            #elif respuesta=="n":
                #pass
            #else:
                #print("Respuesta incorrecta. Intente de nuevo.")
        
        #Proyecto 1
        afd = afn_to_afd(regexAlphabet(postfix),afn)
        afd_graph = plot_af(afd.start)
        nombre_archivo_pdf = 'AFD no ' + str(i)
        afd_graph.view(filename=nombre_archivo_pdf,cleanup=True)    
        
        AFNState.state_counter = 0
        AFNState.states = []
        AFDState.state_counter = 'A'
        AFDState.states = []
        i+=1