import json

# Função para carregar tarefas do arquivo JSON
def carregar_tarefas():
    try:
        with open('tarefas.json', 'r', encoding='utf-8') as arquivo:
            tarefas = json.load(arquivo)
            if not isinstance(tarefas, list):
                return []
            return [tarefa for tarefa in tarefas if isinstance(tarefa, dict) and 'texto' in tarefa]
    except FileNotFoundError:
        return []

# Função para salvar tarefas no arquivo JSON
def salvar_tarefas(tarefas):
    with open('tarefas.json', 'w', encoding='utf-8') as arquivo:
        json.dump(tarefas, arquivo, indent=4, ensure_ascii=False)

def salvar_tarefas_concluidas(tarefas_concluidas):
    with open('tarefas_concluidas.json', 'w', encoding='utf-8') as arquivo:
        json.dump(tarefas_concluidas, arquivo, indent=4, ensure_ascii=False)

def carregar_tarefas_concluidas():
    try:
        with open('tarefas_concluidas.json', 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        return []