# Dados

## Regra

Nada de dado confidencial, pessoal ou proprietário neste repositório. Apenas dado **sintético, público ou anonimizado**.

Isso não é burocracia: o *tier* gratuito do Gemini usa o conteúdo enviado para melhorar produtos do Google (ver `pricing` na documentação oficial). O que você mandar para a API sai do seu controle.

## Organização

| Pasta | O que vai aqui | Vai para o GitHub? |
|---|---|---|
| `dados/exemplo/` | dado sintético ou público, pequeno, para os labs | **sim** |
| `dados/brutos/` | dado real que você usa localmente | **não** — está no `.gitignore` |

## Se o seu problema depende de dado sigiloso

Três saídas, em ordem de preferência:

1. **Gerar dado sintético representativo.** Você escreve um script que produz dados com a mesma estrutura e as mesmas armadilhas do real. Dá trabalho, mas costuma melhorar o projeto: força a equipe a entender o dado.
2. **Anonimizar.** Substituir identificadores, nomes de equipamento, códigos de cliente. Cuidado com reidentificação por combinação de campos.
3. **Rodar local com Ollama.** Nada sai da sua máquina. Configuração no `.env.example`, opção C. Modelos pequenos erram mais — o que é observável e discutível no Encontro 13, não um defeito.

Em dúvida, fale com o professor **antes** de subir o arquivo. Depois de enviado ao GitHub, apagar não basta: continua no histórico.
