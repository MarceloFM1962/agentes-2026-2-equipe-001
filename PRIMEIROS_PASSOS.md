# Primeiros passos — faça isto antes do Encontro 2

Cerca de 50 minutos. Se travar em algum item, **não pule**: escreva no canal da turma. Os dez primeiros minutos do Encontro 2 são plantão, mas o resto da aula depende disto pronto.

---

## Parte 1 — O repositório da equipe (~20 min)

Só **uma pessoa da equipe** faz os passos 1 a 3. Os demais começam no passo 4.

1. Crie uma conta em https://github.com (se ainda não tem).
2. Abra o repositório-modelo da disciplina e clique no botão verde **Use this template** → **Create a new repository**.
   - **Repository name:** `agentes-2026-2-equipe-<numero>`
   - Marque **Private**.
   - Clique em **Create repository**.
3. No repositório novo: **Settings** → **Collaborators** → **Add people** → digite o usuário GitHub de cada colega → **Add**. Avise que eles precisam aceitar o convite por e-mail.
4. Instale o **Visual Studio Code**: https://code.visualstudio.com
5. No VS Code, aperte `Ctrl+Shift+P`, digite `Git: Clone`, pressione Enter, cole a URL do repositório da equipe e escolha uma pasta no seu computador.
   - Na primeira vez o VS Code vai pedir para você entrar na sua conta do GitHub. Aceite e faça o login pelo navegador. **É isso que resolve a autenticação** — o passo que mais costuma travar.
6. Abra o `README.md`, preencha a tabela da equipe, salve com `Ctrl+S`.
7. Faça seu primeiro envio: veja `FOLHA_GIT.md`, os quatro passos do "caminho de todo dia".

Deu certo se, ao abrir o repositório no navegador, o `README.md` aparece com o nome da sua equipe.

---

## Parte 2 — As chaves de API (~20 min)

Cada pessoa cria as **suas próprias** chaves. Não compartilhe: os limites de uso são por projeto, e chave compartilhada faz a aula prática travar para todos.

### Gemini (provedor principal)

1. Acesse https://aistudio.google.com/apikey e entre com sua conta Google.
2. Clique em **Create API key**. Se pedir para escolher ou criar um projeto, **crie um novo** — não use um projeto compartilhado.
3. Copie a chave. Não fecha a página antes de colar em algum lugar seguro.

### Groq (provedor secundário)

1. Acesse https://console.groq.com e crie a conta.
2. Vá em **API Keys** → **Create API Key** e copie.

### Colocar as chaves no lugar certo

1. Na pasta do projeto, faça uma **cópia** do arquivo `.env.example` e chame a cópia de `.env` (só isso, com o ponto na frente e sem extensão).
2. Abra o `.env` e cole sua chave do Gemini na linha `LLM_API_KEY=`.
3. Salve.

> **Nunca** coloque a chave dentro de um arquivo `.py`, e nunca envie o `.env` ao GitHub. O `.gitignore` do repositório já impede isso — e é por isso que aquela primeira linha dele não deve ser removida.

---

## Parte 3 — Testar (~10 min)

No VS Code, abra o terminal (`Ctrl+'`) e rode:

```bash
pip install -r requirements.txt
python src/exemplo_chamada.py
```

Se aparecer a resposta do modelo, está pronto.

### Se der erro

| Mensagem | O que fazer |
|---|---|
| `Configuração incompleta` | O arquivo `.env` não existe ou está com nome errado. Confira que é `.env`, não `env` nem `.env.txt`. |
| `A chave no .env ainda é o texto de exemplo` | Você copiou o `.env.example` mas não colou sua chave. |
| `401` ou `invalid api key` | Chave copiada pela metade. Gere outra e cole de novo. |
| `429` | Você estourou o limite do tier gratuito. Espere alguns minutos. A partir do Encontro 3 o código passa a tratar isso sozinho. |
| `ModuleNotFoundError` | O `pip install -r requirements.txt` não rodou. Rode de novo e leia o que ele diz. |
| `python: command not found` | Instale o Python 3.11 ou superior: https://www.python.org/downloads/ e marque "Add Python to PATH". |

### Plano B

Não conseguiu instalar nada na sua máquina? Use o **Google Colab** (https://colab.research.google.com), que não exige instalação. Avise o professor: você trabalhará por lá, e a entrega dos arquivos será por *upload* no GitHub pelo navegador.

---

## Parte 4 — Canvas de problema (~10 min)

Preencha o rascunho individual do canvas em `docs/canvas.md`. Não precisa estar bom — precisa estar escrito, para haver o que discutir em equipe no Encontro 2.
