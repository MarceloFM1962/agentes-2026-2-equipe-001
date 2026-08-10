# Projeto de Agente — Equipe Professor

Repositório da equipe para a disciplina **Tópicos Especiais em Inteligência Artificial — Agentes Inteligentes e suas Aplicações** (IFES Serra, 2026/2).

> **Primeira coisa a fazer:** preencha a tabela abaixo e a seção "Nosso problema". Depois siga `PRIMEIROS_PASSOS.md`.

## Equipe

| Nome | Usuário no GitHub | Pasta de trabalho |
|---|---|---|
| | | `src/membros/Daniel/` |
| | | `src/membros/Claude/` |
| | | `src/membros/Gemini/` |

## Nosso problema

*Agente Tutor*

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env        # depois edite o .env com sua chave
python src/exemplo_chamada.py
```

## Estrutura

```
.env.example          modelo de configuração — copie para .env e preencha
.env                  suas chaves. NUNCA vai para o GitHub (está no .gitignore)
requirements.txt      bibliotecas do projeto
src/llm.py            cliente único de LLM, usado por todo o projeto
src/exemplo_chamada.py  primeira chamada, do Encontro 2
src/membros/<nome>/   sua pasta pessoal — só você edita arquivos aqui
src/agente/           código compartilhado do agente (a partir do Encontro 5)
dados/                dados sintéticos ou anonimizados. Nada confidencial.
docs/canvas.md        canvas de problema da equipe
docs/atas/            ata de cada reunião de equipe
evals/                casos de teste do agente (a partir do Encontro 13)
```

## Regra de convivência no repositório

Até o Encontro 7, **cada integrante edita apenas arquivos dentro da própria pasta** em `src/membros/`. Isso evita conflito de edição simultânea, que é o único jeito de git dar dor de cabeça de verdade. A partir do Encontro 7 passamos a usar *branch* e *pull request*, e a regra relaxa.

## Regra de dados — não negociável

Nenhum dado confidencial, pessoal ou proprietário entra neste repositório nem é enviado a API de modelo gratuito. Use dado sintético, público ou anonimizado. Se o seu problema depende de dado sigiloso, fale com o professor: a saída é rodar local com Ollama.

## Entregas

| Marco | Encontro | Como entregar |
|---|---|---|
| Marco 1 | 7 | *tag* `marco-1` no repositório |
| Marco 2 | 12 | *tag* `marco-2` |
| Marco 3 | 18 | *tag* `marco-3` + `docs/relatorio.md` |
