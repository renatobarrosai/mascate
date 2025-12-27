"""Templates de resposta por voz para o Mascate.

Define as frases padrão para sucessos, erros e pedidos de confirmação.
"""

from __future__ import annotations

import random

TEMPLATES = {
    "success": [
        "Pronto, painho. Já fiz isso.",
        "Feito! O que mais você precisa?",
        "Certo, processado com sucesso.",
        "Tudo resolvido por aqui.",
    ],
    "confirm": [
        "Você tem certeza que quer {action}?",
        "Isso parece perigoso: {action}. Confirma?",
        "Posso prosseguir com {action}?",
    ],
    "error": [
        "Vixe, deu erro aqui. Não consegui {action}.",
        "Desculpe, houve um problema técnico.",
        "Não foi possível completar essa tarefa agora.",
    ],
    "not_found": [
        "Não encontrei {target}.",
        "Procurei, mas {target} não está por aqui.",
    ],
    "greeting": [
        "Oi! Como posso te ajudar hoje?",
        "Mascate às ordens. O que vamos fazer?",
    ],
}


def get_response(category: str, **kwargs: str) -> str:
    """Obtém uma resposta aleatória de uma categoria formatada.

    Args:
        category: Chave do template.
        kwargs: Variáveis para formatação (ex: action, target).

    Returns:
        Frase formatada.
    """
    options = TEMPLATES.get(category, ["Processado."])
    phrase = random.choice(options)
    return phrase.format(**kwargs)
