# Folha de git — uma página, quatro botões

Você não precisa entender git para usar git nesta disciplina. Precisa de quatro passos, sempre na mesma ordem, no painel **Source Control** do VS Code (o ícone com três bolinhas ligadas, na barra da esquerda, ou `Ctrl+Shift+G`).

---

## O caminho de todo dia

**Antes de começar a trabalhar:**

**1. Baixar o que os colegas fizeram** — no menu `...` do painel Source Control → **Pull**.

**Depois de trabalhar:**

**2. Escolher o que enviar** — passe o mouse sobre cada arquivo modificado e clique no **`+`** (chama-se *stage*: separar para envio).

**3. Escrever o que você fez** — na caixa de texto acima, uma frase curta no presente: `adiciona ferramenta de consulta ao histórico`. Depois clique em **Commit**.

**4. Enviar** — clique em **Sync Changes** (ou `...` → **Push**).

> **A ordem importa.** Sempre **Pull** antes de começar. É o que evita 90% dos problemas.

---

## O que cada palavra significa

| Palavra | Em português claro |
|---|---|
| *Repository* (repo) | a pasta do projeto, com todo o histórico |
| *Clone* | baixar o projeto para o seu computador, pela primeira vez |
| *Pull* | trazer o que os colegas enviaram |
| *Stage* (`+`) | marcar um arquivo para entrar no próximo envio |
| *Commit* | registrar uma versão, com uma descrição |
| *Push* / *Sync* | mandar seus commits para o GitHub |

Um *commit* é uma **fotografia** do projeto com uma legenda. O histórico é o álbum. Nada se perde.

---

## Regras da disciplina

- **Edite só arquivos da sua pasta** `src/membros/<seu-nome>/` até o Encontro 7. Se duas pessoas editam o mesmo arquivo ao mesmo tempo, aparece um conflito — e conflito não é assunto desta disciplina.
- **Faça commits pequenos e frequentes.** Um por tarefa concluída, não um gigante no fim da semana. Além de ser mais fácil de desfazer, o histórico é uma das evidências da sua nota de participação.
- **Nunca envie o arquivo `.env`.** Ele tem sua chave de API. O `.gitignore` já protege — não altere a primeira linha dele.

---

## Quando algo dá errado

| O que aparece | O que fazer |
|---|---|
| Pede usuário e senha, e a senha não funciona | Senha do site não serve mais para o git. No VS Code: `Ctrl+Shift+P` → `Git: Clone` faz o login correto pelo navegador. Se persistir, veja "Accounts" (ícone de pessoa, canto inferior esquerdo) → entre na conta do GitHub. |
| *"Your branch is behind"* | Faça **Pull** antes de tentar enviar. |
| *"Merge conflict"* em um arquivo | **Não tente resolver sozinho.** Avise a equipe, não edite mais aquele arquivo e traga para o atendimento. |
| Enviou a chave de API por acidente | Avise o professor **imediatamente** e apague a chave em https://aistudio.google.com/apikey (ou no console do Groq) e gere outra. Apagar o arquivo depois não basta: ela continua no histórico. |
| Não sei o que fiz e quero voltar | Não apague nada. Chame o professor. Em git, quase nada se perde de verdade. |
| Tudo travou e a entrega é hoje | Compacte a pasta do projeto em `.zip` e envie ao professor. **A entrega nunca depende do git funcionar.** |

---

## Uma coisa que vale saber

O professor está aprendendo git junto com a turma nesta edição. Se você já sabe, avise — vai ser designado como referência da sua equipe. Se não sabe, está em boa companhia: estes quatro passos dão conta do semestre inteiro.
