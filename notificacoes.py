from plyer import notification

# Função para enviar notificações ao usuário
def enviar_notificacao(texto_tarefa, tipo="pendente"):
    if tipo == "pendente":
        notification.notify(
            title="Tarefa Pendente",
            message=f"A tarefa '{texto_tarefa}' vai vencer em menos de 1 hora!",
            timeout=10
        )
    elif tipo == "concluida":
        notification.notify(
            title="Tarefa Concluída",
            message=f"A tarefa '{texto_tarefa}' foi movida para as concluídas, pois o prazo foi atingido.",
            timeout=10
        )
