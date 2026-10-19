# Limitações — diagnóstico da aquaponia

O rastro abaixo é o das rotas fixas, gravado em `evals/parte9/rastro_rotas.json`. Ele não gasta token e não depende de modelo. Custo em dólar, acerto do texto gerado e comportamento do agente **ainda não foram medidos**: nesta máquina não há `GROQ_API_KEY`. Os números da tabela de medição ficam em branco de propósito. Previsão não entra no lugar de resultado.

| Caso | Forma | Causa | Consultas | Chamadas LLM | Entrada | Saída | Custo US$ | Abstenção correta |
|---|---|---|---|---|---|---|---|---|
| A-101 a A-105 | workflow | a medir | a medir | a medir | a medir | a medir | a medir | a medir |
| A-101 a A-105 | agente | a medir | a medir | a medir | a medir | a medir | a medir | a medir |

Para preencher a tabela: `python src/parte9_aquaponia.py --medir`, com `GROQ_API_KEY` no ambiente. A leitura numérica vai para `docs/parte9_medicao.md` e não apaga este texto. O preço usado no código é o do material da disciplina, conferido em 21/08/2026 (`openai/gpt-oss-20b`, US$ 0,075 / US$ 0,30 por milhão de tokens). Na execução final, reconferir o preço publicado e anotar a data.

## O que a rota já mostra

| Caso | Rota | Consulta decisiva na rota? |
|---|---|---|
| A-101 | telemetria, atuadores, referência | sim — eventos dos atuadores |
| A-102 | telemetria, tendência visual, referência | sim — telemetria e referência |
| A-103 | telemetria, atuadores, manejo | sim — manejo |
| A-104 | telemetria, tendência visual, referência | não — falta calibração |
| A-105 | telemetria, atuadores, referência | não — falta calibração |

O classificador é uma tabela escrita antes de rodar. No A-101 o alerta cita pH e crescimento; a regra olha pH primeiro. O rastro cai na rota `ph` e encontra a bomba.

## Limitação 1 — causa fora da rota

No A-104 a rota de crescimento devolve isto, e só isto:

- telemetria, origem `telemetria/esp32-l08`: pH 6,9; TDS 480 mg/L; luz 500 lux; vazão 6,2 L/min; validade válida
- visão, origem `visao/captura-01`: área dia 7 = 333,31 cm²; dia 8 = 262 cm²; enquadramento alterado
- referência: a área projetada não deve cair de forma abrupta sem outra evidência

Não há `consultar_calibracao` nessa lista. O texto colhido não contém “22%”, “deslocada” nem “fator de escala”. Essas palavras estão só na calibração: captura deslocada 4 cm, fator de escala −22%, verificação vencida. O juiz exige o termo da causa **e** essa consulta no rastro. Sem ela, o workflow não pode ser marcado como acerto, mesmo que o redator invente “câmera”. O rastro prova a ausência da consulta.

Se, na medição, o agente chamar `consultar_calibracao` e nomear a escala, o acerto é da seleção adaptativa. Se repetir consulta ou inventar doença, a falha fica no JSON da resposta, não numa frase genérica de que “o agente errou”.

## Limitação 2 — leitura suspeita pode parecer causa da água

No A-105 a rota de pH devolve:

- telemetria: pH 8,1; validade=suspeita; origem `telemetria/esp32-l08`
- atuadores: nenhum comando de dosagem
- referência: pH 6,5–7,2; leitura suspeita exige verificação antes de qualquer ação

O offset +0,8 e a palavra “sonda” não aparecem nesse rastro. Estão só em `consultar_calibracao`. O workflow pode, a partir da validade suspeita, recusar a dosagem — e isso conta como abstenção correta — sem ter apontado a causa. Pedir corretivo com pH 8,1 seria o erro que esta limitação vigia. As duas colunas, causa e abstenção, não se substituem.

## Limitação 3 — visão não é diagnóstico

A área do benchmark (260 cm², 333,31 cm², 351,68 cm²) é âncora de demonstração, não série longitudinal da planta. “Enquadramento alterado” é observação da captura. Não autoriza doença, praga nem produtividade. O A-104 é perda de escala da imagem, não perda de alface.

## Limitação 4 — mundo sintético

Cada caso tem verdade porque a causa foi escrita no código. Isso mede se a forma achou a evidência plantada. Não mede se a mesma causa ocorreria na planta piloto, nem se o sensor, o relé ou a câmera se comportam assim. Validade externa pede série real, calibração dos instrumentos e confirmação por procedimento de manejo.

## Limitação 5 — juiz por termos

O acerto automático exige um termo distintivo (`pH+`, `relé`, `TDS`, `filtro`, `escala`, `offset`, `sonda`, e os equivalentes da lista) e a consulta decisiva no rastro. Sintoma sozinho (“pH alto”, “crescimento baixo”, “vazão caiu”) não conta. Ainda assim o juiz erra se a resposta nega a causa com a própria palavra, ou se usa um sinônimo de fora da lista. A resposta integral e a lista ampla de termos ficam no JSON em `evals/parte9/`, para conferência manual.

## Limitação 6 — o dólar não é o custo do experimento

Quando a medição rodar, o custo soma só token de entrada e de saída do `openai/gpt-oss-20b`, no preço de 21/08/2026. Token de raciocínio desse modelo entra na saída e é cobrado. A espera entre casos, por causa do limite do plano, não é custo de inferência. Ficam de fora desenvolvimento, energia, hardware, armazenamento e o tempo do operador. Temperatura 0, teto de 2000 tokens e duas repetições não eliminam variação; o relatório deve trazer média, mediana e dispersão, não um número único tratado como exato.

## Limitação 7 — isto não valida controle físico

As seis consultas são leitura. Nada neste benchmark liga bomba, relé, ESP32 ou dosador, e nada mede ganho de biomassa. Diagnóstico supervisório e teste de infraestrutura da dissertação continuam separados.

## Como ler, quando houver número

1. Quantas causas cada forma sustentou em todas as repetições?
2. Qual o custo total e o custo médio por execução?
3. Quantas consultas de domínio e quantas chamadas ao modelo?
4. Nos casos em que as duas acertaram, qual foi mais barata?
5. O agente cobriu A-104 ou A-105, e esse ganho paga o custo a mais?

Se as duas acertam e o workflow é mais barato, o caso favorece o workflow. Se só o agente aponta a causa escondida, isso é ganho de cobertura, com o rastro e o dólar ao lado. Se o agente não cobre o que a rota já não cobre, o resultado válido é que o procedimento fixo basta para este benchmark.
