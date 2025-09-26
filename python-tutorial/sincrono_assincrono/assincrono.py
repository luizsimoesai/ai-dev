"""
asyncio é a biblioteca padrão do Python para lidar com tarefas assíncronas e concorrência sem usar threads.
Ela permite que seu código "espere" de forma inteligente por coisas demoradas (como chamadas de rede), 
sem bloquear o resto do programa.

async def
Declara uma função assíncrona (chamada de corrotina).

await
Chama e espera outra corrotina terminar — mas sem travar o programa.

asyncio.run()
Executa a corrotina principal.
"""


import asyncio

async def tarefa():
    print("Início")
    await asyncio.sleep(2)
    print("Fim")

async def main():
    await tarefa()
    print("Depois da tarefa")

asyncio.run(main())
