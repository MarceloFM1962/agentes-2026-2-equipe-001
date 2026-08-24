# Canvas de Problema — Equipe 001

## 1. O problema em uma frase

> Hoje, o responsável por uma planta de aquaponia precisa monitorar continuamente as condições da água e o funcionamento do sistema, mas esse acompanhamento depende de medições e intervenções manuais e não consegue responder rapidamente a todas as alterações, o que pode causar estresse ou mortalidade dos peixes, deficiência no desenvolvimento das plantas, desperdício de recursos e redução da produtividade.

## 2. Quem sofre com isso

O problema afeta diretamente:

* responsáveis pela operação e manutenção de sistemas de aquaponia;
* pesquisadores e estudantes que utilizam plantas experimentais;
* produtores urbanos e rurais que adotam sistemas aquícolas integrados;
* peixes e plantas, cujo desenvolvimento depende da manutenção das condições adequadas;
* instituições que precisam manter sistemas experimentais operando de maneira contínua e segura.

No contexto deste projeto, o principal usuário será o operador de uma planta experimental de aquaponia, composta por criação de tilápias e cultivo de alface.

## 3. Como se resolve hoje

Atualmente, o acompanhamento é realizado principalmente por meio de medições manuais ou da consulta individual a sensores. O operador verifica parâmetros como pH, temperatura, oxigênio dissolvido, condutividade elétrica e nível da água, compara os valores com faixas recomendadas e decide se deve acionar bombas, aeradores, alimentadores ou outros equipamentos.

Alguns sistemas utilizam controladores com regras fixas, alarmes e temporizadores. Essas soluções, entretanto, geralmente analisam cada variável isoladamente, possuem pouca capacidade de interpretar o contexto, não aprendem com o histórico e apresentam dificuldade para lidar com situações não previstas nas regras iniciais.

## 4. PEAS

|                                                                | Preencha                                                                                                                                                                                                                                                                                                                                                                                                       |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **P**erformance — como se mede sucesso, de forma verificável   | Percentual de tempo em que pH, temperatura, oxigênio dissolvido, condutividade elétrica e nível da água permanecem dentro das faixas estabelecidas; redução da quantidade e da duração das anomalias; tempo entre a detecção e a resposta; precisão dos alertas; disponibilidade do sistema; redução de intervenções manuais; consumo de água e energia; crescimento e sobrevivência dos peixes e das plantas. |
| **E**nvironment — sobre que dados, sistemas e documentos opera | Planta experimental de aquaponia com tanque de tilápias, área de cultivo de alface, tubulações, bombas, aeradores, reservatórios, sensores, atuadores, ESP32, Raspberry Pi ou equipamento equivalente, banco de dados histórico, interface web e documentos técnicos contendo limites operacionais e recomendações de manejo.                                                                                  |
| **A**ctuators — que ações o agente pode executar               | Acionar ou desligar bombas de circulação, aeradores e dosadores; ajustar tempos ou níveis de atuação; emitir alertas; registrar ocorrências; solicitar confirmação do operador em situações críticas; recomendar inspeção, calibração ou manutenção. No protótipo inicial, ações de maior risco poderão exigir autorização humana.                                                                             |
| **S**ensors — o que ele recebe como entrada                    | Medições de pH, temperatura da água e do ambiente, oxigênio dissolvido, condutividade elétrica, nível e fluxo da água; estado e consumo dos equipamentos; imagens das plantas e, futuramente, dos peixes; histórico das medições e atuações; comandos, observações e respostas fornecidas pelo operador.                                                                                                       |

## 5. Dados — a seção decisiva

| Pergunta                                                         | Resposta                                                                                                                                                                                                                                                                                                                                                                                             |
| ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Que dados são necessários?                                       | Séries temporais dos sensores; estado dos atuadores; registros de alarmes, falhas, calibrações, manutenções e intervenções do operador; imagens periódicas das plantas; parâmetros de referência para tilápia, alface e qualidade da água; resultados observados após cada ação executada.                                                                                                           |
| Você **já tem acesso**, ou supõe que terá?                       | Há acesso à planta experimental, aos sensores, aos dispositivos embarcados e aos dados que serão coletados pelo próprio projeto. Parte dos dados históricos ainda precisará ser produzida durante a operação da planta. Também poderão ser utilizados conjuntos de dados públicos para apoiar o desenvolvimento inicial dos módulos de visão computacional.                                          |
| Formato e volume aproximado                                      | Dados tabulares e séries temporais em CSV, JSON ou banco SQLite; registros textuais de eventos e intervenções; imagens em JPEG ou PNG. Considerando de 5 a 10 variáveis coletadas a cada minuto, estima-se entre 2,6 e 5,3 milhões de registros por ano. As imagens poderão representar de dezenas a centenas de gigabytes, dependendo da frequência, resolução e tempo do experimento.              |
| Há informação confidencial, pessoal ou proprietária?             | Em princípio, os dados ambientais e operacionais não são pessoais. Entretanto, credenciais de acesso, configurações de rede, imagens que identifiquem pessoas e informações técnicas ainda não publicadas deverão ser protegidas. Os dados experimentais e os modelos desenvolvidos também poderão ser considerados proprietários da pesquisa ou da instituição.                                     |
| Se houver: anonimizar, gerar sintético ou rodar em Ollama local? | Remover pessoas e identificadores das imagens e dos registros; substituir credenciais por identificadores fictícios; utilizar dados sintéticos para testar falhas raras ou perigosas; manter dados e modelos sensíveis em infraestrutura local. Quando for necessário empregar um modelo de linguagem, priorizar a execução local por meio do Ollama, especialmente para dados ainda não publicados. |

## 6. Por que isso precisa de um agente

* [x] O número de caminhos possíveis é grande ou desconhecido de antemão
* [x] Exige decidir **quais** informações buscar, não só processar informação dada
* [x] Entrada é não estruturada (texto livre, documento, relato)
* [x] Requer combinar fontes ou ferramentas de formas que variam por caso

Um agente é necessário porque a mesma alteração pode possuir causas diferentes. Uma redução do oxigênio dissolvido, por exemplo, pode estar relacionada à temperatura elevada, excesso de biomassa, falha do aerador, interrupção da circulação ou problema no sensor. O sistema deverá consultar dados históricos, verificar outros sensores, analisar o estado dos equipamentos, selecionar ferramentas de diagnóstico e decidir entre observar, alertar, recomendar uma ação ou atuar automaticamente.

A entrada não estruturada estará presente nos relatos do operador, documentos técnicos, registros de manutenção e recomendações de manejo. Assim, o agente deverá combinar regras de segurança, modelos de detecção de anomalias, histórico operacional e conhecimento técnico.

## 7. Como saberemos que funcionou

Três casos de teste, com a resposta esperada:

1. **Queda do oxigênio dissolvido:** o sensor indica oxigênio dissolvido abaixo do limite seguro, enquanto o aerador está desligado.
   **Resposta esperada:** o agente valida a leitura usando medições recentes, identifica o risco, aciona o aerador, registra a decisão, acompanha a recuperação do parâmetro e alerta o operador caso o valor não retorne à faixa adequada dentro do tempo definido.

2. **Possível falha no sensor de pH:** o valor de pH muda abruptamente, sem alteração correspondente nos demais parâmetros.
   **Resposta esperada:** o agente identifica a leitura como potencialmente inconsistente, compara com o histórico, solicita uma nova medição e recomenda inspeção ou calibração. O sistema não deve acionar automaticamente a dosagem de corretivos com base em uma única leitura suspeita.

3. **Tendência de aumento da temperatura:** a temperatura da água cresce continuamente e se aproxima do limite operacional, embora ainda não o tenha ultrapassado.
   **Resposta esperada:** o agente detecta a tendência, estima o risco de ultrapassagem, verifica o estado da circulação e da aeração, recomenda ou executa ações preventivas permitidas e envia ao operador uma explicação baseada nos dados observados.

## 8. Escopo

|                                               |                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Dentro — o mínimo que precisa funcionar**   | Receber dados reais ou simulados de pH, temperatura, oxigênio dissolvido, condutividade elétrica e nível da água; armazenar o histórico; detectar valores anormais e tendências; verificar o estado dos atuadores; consultar regras e documentos técnicos; apresentar diagnóstico e recomendação explicável; emitir alertas; acionar, em ambiente controlado, pelo menos uma bomba ou um aerador; manter registro das decisões e ações.                                 |
| **Fora — tentação explicitamente descartada** | Controlar uma instalação comercial de grande escala; eliminar completamente a supervisão humana; realizar dosagem automática de substâncias potencialmente perigosas sem mecanismos adicionais de segurança; diagnosticar doenças de peixes ou plantas com finalidade veterinária ou agronômica definitiva; controlar simultaneamente todas as etapas de alimentação, produção e comercialização; garantir autonomia total diante de qualquer falha física ou elétrica. |

## 9. Riscos

| Risco                                                                                 | Como perceberemos cedo                                                                                                        | Plano B                                                                                                                                                                                             |
| ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quantidade insuficiente de dados reais, principalmente de falhas e situações anormais | Poucos eventos anormais registrados e modelos com desempenho instável ou incapazes de generalizar                             | Utilizar regras definidas por especialistas, simulação de cenários, injeção controlada de falhas e geração de dados sintéticos; manter o aprendizado de máquina como módulo complementar            |
| Sensor defeituoso, descalibrado ou sujeito a ruído                                    | Saltos abruptos, valores impossíveis, leituras constantes ou divergência em relação a sensores redundantes e medições manuais | Aplicar validação de faixa, filtros, redundância, confirmação temporal e calibração periódica; impedir ações críticas baseadas em uma única leitura                                                 |
| Ação incorreta do agente prejudicar peixes, plantas ou equipamentos                   | Recomendações incompatíveis com as regras de segurança, acionamentos frequentes ou ausência de recuperação do parâmetro       | Limitar a autonomia, definir regras invioláveis, utilizar confirmação humana para ações críticas, disponibilizar desligamento de emergência e retornar ao controle manual                           |
| Falha de comunicação, energia ou processamento                                        | Perda de pacotes, ausência prolongada de dados, dispositivos desconectados ou atraso nas respostas                            | Manter controle local básico independente do agente, armazenar dados temporariamente nos dispositivos, utilizar estado operacional seguro e emitir alerta quando a comunicação retornar             |
| Desempenho inadequado do agente ou do modelo de linguagem                             | Respostas contraditórias, diagnósticos sem evidência ou seleção incorreta de ferramentas                                      | Restringir as ações disponíveis, exigir justificativas baseadas nos sensores, usar respostas estruturadas, testar casos conhecidos e recorrer a regras determinísticas quando a confiança for baixa |
| Escopo excessivo para o prazo da disciplina                                           | Muitos módulos parcialmente desenvolvidos e nenhum fluxo completo funcionando                                                 | Priorizar um produto mínimo viável: monitoramento, detecção de três tipos de anomalia, recomendação explicável e acionamento controlado de um aerador ou uma bomba                                  |
