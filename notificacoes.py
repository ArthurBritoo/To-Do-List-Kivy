from plyer import notification

# Função para enviar notificações ao usuário
def enviar_notificacao(texto_tarefa):
    notification.notify(
        title="Tarefa Pendente",
        message=f"A tarefa '{texto_tarefa}' está prestes a vencer!",
        timeout=10
    )
