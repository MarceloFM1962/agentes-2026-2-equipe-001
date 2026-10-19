# Canvas — diagnóstico supervisório da aquaponia

**Pergunta.** Dado um alerta da planta, o que aponta a causa provável com melhor custo: um workflow de rota fixa ou um agente que escolhe as consultas?

O canvas da equipe (`docs/canvas.md`) descreve a planta inteira: sensores, visão, atuação e o operador. Esta página é só o recorte que dá para medir. O sistema não liga bomba. A saída é diagnóstico, com evidência, origem e próximo passo. A atuação continua no intertravamento e na confirmação humana.

| Campo | Definição |
|---|---|
| Problema | Um desvio de pH, vazão ou área projetada pode vir da água, do atuador, do manejo, da captura ou do sensor. A evidência está espalhada. Consultar tudo é caro; consultar pouco aponta a causa errada. |
| Usuário | Operador ou pesquisador da planta piloto (tilápia e alface, lote L-08). |
| Entrada | Alerta em texto, identificador do caso e lote. Ex.: “o pH está alto; devo dosar corretivo?” |
| Saída | Causa provável, evidência com origem, próximo passo seguro. Se a evidência não sustenta a causa, a resposta se abstém e não pede dosagem nem acionamento. |
| Workflow | Python escolhe a rota antes de executar: pH, crescimento ou vazão. O modelo só redige a resposta com o que a rota colheu. |
| Agente | Recebe as mesmas seis consultas como ferramentas e escolhe a próxima. Para com evidência suficiente ou em oito voltas. |
| O que fica igual | Mundo sintético, casos, texto das consultas, modelo, temperatura 0, teto de tokens, instrução de resposta, juiz e preço por token. |
| O que muda | Quem escolhe a próxima consulta: a tabela `ROTAS` ou o modelo. |
| Risco | Uma frase fluente pode trocar sintoma por causa, ou tratar erro de medição como problema da planta. |
| Hipótese | A rota fixa basta, e custa menos, quando a causa está na família do alerta. O agente só se justifica se apontar causa que a rota não consulta — em especial calibração nos casos A-104 e A-105 — e se esse ganho compensar consultas e tokens. |
| Critério | Se as duas acertam, vence a mais barata. Empate mais caro não escolhe o agente. Acerto só do agente é ganho de cobertura, contado junto do custo e das falhas. Não é licença para dizer que agente é sempre melhor. |

**Workflow ou agente?** As duas formas. A escolha do desenho fica para depois da medição, não para a preferência por uma arquitetura. O mundo sintético existe para essa comparação ser possível: a causa verdadeira é conhecida por construção.

O que já se sabe sem gastar token: a rota de crescimento não chama `consultar_calibracao`, e a rota de pH também não. Nos casos A-104 e A-105 a evidência decisiva está fora do procedimento fixo. Isso não é o resultado do modelo. É o buraco que o agente teria de cobrir para se justificar.
