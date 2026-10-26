import ast

codigo = """
def suma(a, b):
    total = a + b
    return total
"""

arbol = ast.parse(codigo)

print("=== ast.dump ===")
print(ast.dump(arbol, indent=2))

print("\n=== ast.walk (recorrido por niveles) ===")
for nodo in ast.walk(arbol):
    print(type(nodo).__name__)

print("\n=== ast.unparse (AST -> código) ===")
print(ast.unparse(arbol))