"""
Primeira chamada de API — Encontro 2.

Rode com:
    python src/exemplo_chamada.py

Se aparecer a resposta do modelo e o consumo de tokens, seu ambiente está
pronto. Se der erro, leia a mensagem: ela diz o que falta.
"""

from llm import conversar, descrever_configuracao


def main() -> None:
    print("Configuração:", descrever_configuracao())
    print()

    pergunta = "Em uma frase, qual a diferença entre um chatbot e um agente?"
    print("Pergunta:", pergunta)
    print()

    resposta = conversar(
        pergunta,
        instrucao_de_sistema=(
            "Você responde a estudantes de mestrado em engenharia. "
            "Seja preciso e conciso. Responda em português do Brasil."
        ),
    )
    print("Resposta:", resposta)

    print()
    print("Funcionou. Agora troque LLM_BASE_URL e LLM_MODEL no .env para o")
    print("outro provedor e rode de novo. O código não muda — só a configuração.")


if __name__ == "__main__":
    main()
