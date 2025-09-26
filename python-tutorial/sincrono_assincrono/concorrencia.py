"""
asyncio.gather()
Executa várias corrotinas ao mesmo tempo (concorrência).
"""


import asyncio

async def tarefa1():
    await asyncio.sleep(1)
    print("Tarefa 1")

async def tarefa2():
    await asyncio.sleep(1)
    print("Tarefa 2")

async def main():
    await asyncio.gather(tarefa1(), tarefa2())

asyncio.run(main())
