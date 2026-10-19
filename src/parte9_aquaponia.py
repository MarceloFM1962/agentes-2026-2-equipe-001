"""Parte 9 — workflow ou agente no diagnostico supervisorio da aquaponia.

O notebook parte9_aquaponia.ipynb repete este codigo para a entrega ficar
autocontida. Daqui se roda o autoteste, sem chave e sem rede:

    python src/parte9_aquaponia.py

Com GROQ_API_KEY no ambiente, a medicao (duas repeticoes) e:

    python src/parte9_aquaponia.py --medir

Use --medir --uma para uma repeticao so.
"""

from __future__ import annotations

import json
import os
import statistics
import sys
import time
import unicodedata
from pathlib import Path

# === CELULA: prep ===

try:
    from dotenv import load_dotenv

    load_dotenv()
except (ImportError, AssertionError):
    # find_dotenv exige frame de modulo; sem .env o autoteste segue.
    pass


def obter_chave(nome: str = "GROQ_API_KEY") -> str | None:
    """Le o segredo do Colab; fora dele, da variavel de ambiente."""
    try:
        from google.colab import userdata

        valor = userdata.get(nome)
        if valor:
            return valor
    except Exception:
        pass
    return os.getenv(nome) or None


LLM_BASE_URL = "https://api.groq.com/openai/v1"
LLM_MODEL = "openai/gpt-oss-20b"
LLM_API_KEY = obter_chave()

# Preco do material da disciplina, console.groq.com/pricing, 21/08/2026.
# Dolares por MILHAO de tokens. Refazer a conferencia na execucao final.
PRECO_CONSULTADO_EM = "2026-08-21"
PRECOS = {
    "openai/gpt-oss-20b": {"entrada": 0.075, "saida": 0.30},
    "openai/gpt-oss-120b": {"entrada": 0.15, "saida": 0.60},
}
# gpt-oss gasta tokens de raciocinio dentro de max_tokens, e esses tokens
# entram em usage.completion_tokens. O teto e o mesmo nas duas formas.
MAX_TOKENS = 2000
MAX_VOLTAS = 8
PASTA_RASTRO = Path("evals") / "parte9"

cliente = None
if LLM_API_KEY:
    from openai import OpenAI

    cliente = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)


def _espera_sugerida(erro, padrao: float) -> float:
    try:
        cab = getattr(getattr(erro, "response", None), "headers", {}) or {}
        valor = cab.get("retry-after") or cab.get("Retry-After")
        if valor:
            return float(valor)
    except (TypeError, ValueError):
        pass
    return padrao


def chamar(mensagens, temperatura: float = 0.0, tentativas: int = 5,
           max_tokens: int = MAX_TOKENS, **extra):
    """Chama o modelo tolerando 429 e 5xx. Nao troca de modelo no meio."""
    if cliente is None:
        raise RuntimeError(
            "Medicao nao iniciada: defina GROQ_API_KEY nos Secrets do Colab "
            "ou no ambiente. O autoteste do mundo nao precisa de chave."
        )
    espera = 2.0
    for tentativa in range(tentativas):
        try:
            resposta = cliente.chat.completions.create(
                model=LLM_MODEL,
                messages=mensagens,
                temperature=temperatura,
                max_tokens=max_tokens,
                **extra,
            )
            if resposta.choices[0].finish_reason == "length":
                print("  [AVISO: resposta CORTADA por max_tokens.]")
            return resposta
        except Exception as erro:
            codigo = getattr(erro, "status_code", None)
            if codigo not in (429, 500, 502, 503, 504) or tentativa == tentativas - 1:
                raise
            pausa = _espera_sugerida(erro, espera)
            print(f"  [{codigo}] esperando {pausa:.0f}s  (nao invalida a medicao)")
            time.sleep(pausa)
            espera *= 2
    raise RuntimeError("todas as tentativas falharam")


def custo_usd(entrada: int, saida: int, modelo: str | None = None) -> float:
    preco = PRECOS[modelo or LLM_MODEL]
    return (entrada * preco["entrada"] + saida * preco["saida"]) / 1_000_000


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFD", (texto or "").lower())
    return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")


# === CELULA: mundo ===

# Cinco cenarios alternativos do mesmo lote. Nao sao uma serie temporal
# de uma manha so: cada caso injeta uma causa, para a verdade ser conhecida.
LOTE = "L-08"
PLANTA = "alface P-03"

_INSTANTE = {
    "telemetria": "2026-10-18T08:00:00-03:00",
    "visao": "2026-10-18T08:05:00-03:00",
    "atuadores": "2026-10-18T08:00:30-03:00",
    "calibracao": "2026-10-18T07:50:00-03:00",
    "manejo": "2026-10-18T06:00:00-03:00",
    "referencia": "2026-10-18T00:00:00-03:00",
}
_ORIGEM = {
    "telemetria": "telemetria/esp32-l08",
    "visao": "visao/captura-01",
    "atuadores": "atuadores/rele-l08",
    "calibracao": "calibracao/registro-l08",
    "manejo": "manejo/diario-l08",
    "referencia": "referencia/protocolo-alface",
}

# A causa de cada caso mora numa fonte so. As outras fontes nao repetem
# as palavras decisivas. Isso e o que permite ler o rastro depois.
MUNDO = {
    "A-101": {
        "telemetria": "pH 6,2; TDS 430 mg/L; temperatura 24,0 C; vazao 6,1 L/min; nivel 92%; luz 490 lux; validade=valida",
        "visao": "area dia 8 = 348 cm2; tendencia sem queda abrupta; qualidade=nitida; captura=captura-01",
        "atuadores": "bomba de correcao pH+: comando solicitado=ligado; confirmacao=desligado; tempo de efeito=0 s; rele=sem acionamento confirmado",
        "calibracao": "sensor de pH verificado ha 2 dias; offset registrado=nenhum; captura sem mudanca de posicao",
        "manejo": "nenhuma intervencao nas ultimas 24 h",
        "referencia": "pH 6,5-7,2; vazao 5-8 L/min; TDS 350-700 mg/L",
    },
    "A-102": {
        "telemetria": "pH 6,8; TDS 220 mg/L; temperatura 23,8 C; luz 480 lux; vazao 6,0 L/min; nivel 93%; validade=valida",
        "visao": "area dia 8 = 260 cm2; referencia sintetica do dia = 351,68 cm2; qualidade=nitida; captura=captura-01",
        "atuadores": "bombas de circulacao e de correcao confirmadas ligadas; nenhum alarme de hardware",
        "calibracao": "captura e sensores dentro da verificacao; sem mudanca de posicao",
        "manejo": "sem reposicao de nutrientes ha 96 h",
        "referencia": "TDS 350-700 mg/L; pH 6,5-7,2; crescimento compativel com a trajetoria de area projetada",
    },
    "A-103": {
        "telemetria": "vazao 1,8 L/min; bomba de circulacao=ligada; nivel 94%; pH 6,8; TDS 460 mg/L; validade=valida",
        "visao": "area dia 8 = 352 cm2; crescimento dentro da trajetoria; qualidade=nitida; captura=captura-01",
        "atuadores": "bomba de circulacao: comando solicitado=ligado; confirmacao=ligado; vazao comandada nao foi alterada",
        "calibracao": "sensor de vazao verificado; offset registrado=nenhum",
        "manejo": "filtro aberto para limpeza ha 2 h; retorno do elemento filtrante nao confirmado",
        "referencia": "vazao 5-8 L/min; nivel esperado 80-100%",
    },
    "A-104": {
        "telemetria": "pH 6,9; TDS 480 mg/L; luz 500 lux; vazao 6,2 L/min; nivel 93%; validade=valida",
        "visao": "area dia 7 = 333,31 cm2; area dia 8 = 262 cm2; qualidade=enquadramento alterado; captura=captura-01",
        "atuadores": "atuadores nos estados esperados; nenhum comando de dosagem",
        "calibracao": "captura deslocada 4 cm; fator de escala caiu 22%; verificacao de posicao vencida",
        "manejo": "sem mudanca de manejo nas ultimas 48 h",
        "referencia": "a area projetada nao deve cair de forma abrupta entre duas leituras sem outra evidencia",
    },
    "A-105": {
        "telemetria": "pH 8,1; TDS 450 mg/L; vazao 6,0 L/min; nivel 92%; validade=suspeita",
        "visao": "area dia 8 = 350 cm2; tendencia dentro da trajetoria; qualidade=nitida; captura=captura-01",
        "atuadores": "nenhum comando de dosagem emitido",
        "calibracao": "sonda de pH com offset estimado de +0,8; verificacao vencida",
        "manejo": "nenhuma adicao de corretivo nas ultimas 48 h",
        "referencia": "pH 6,5-7,2; leitura com validade suspeita exige verificacao antes de qualquer acao",
    },
}


def _consultar(caso_id: str, fonte: str, variavel: str) -> str:
    try:
        chave = (caso_id or "").strip().upper()
        caso = MUNDO.get(chave)
        if caso is None:
            return (
                f"ERRO: caso_id {caso_id!r} nao consta do mundo sintetico. "
                "Use um de: " + ", ".join(MUNDO)
            )
        return (
            f"caso_id={chave} | variavel={variavel} | "
            f"instante={_INSTANTE[fonte]} | origem={_ORIGEM[fonte]} | "
            f"{caso[fonte]}"
        )
    except Exception as erro:
        return f"ERRO: falha interna em {fonte}: {erro}"


def consultar_telemetria(caso_id: str = "") -> str:
    """Devolve pH, TDS, temperatura, vazao, nivel, luz, validade e origem."""
    return _consultar(caso_id, "telemetria", "pH,TDS,temperatura,vazao,nivel,luz")


def consultar_tendencia_visual(caso_id: str = "") -> str:
    """Devolve area projetada, serie curta e qualidade da captura."""
    return _consultar(caso_id, "visao", "area_projetada")


def consultar_eventos_atuadores(caso_id: str = "") -> str:
    """Devolve comando solicitado, confirmacao, tempo e efeito observado."""
    return _consultar(caso_id, "atuadores", "atuadores")


def consultar_calibracao(caso_id: str = "") -> str:
    """Devolve offset, verificacao e mudanca de posicao ou de escala."""
    return _consultar(caso_id, "calibracao", "calibracao")


def consultar_manejo(caso_id: str = "") -> str:
    """Devolve limpeza, nutrientes, corretivo e outras intervencoes recentes."""
    return _consultar(caso_id, "manejo", "manejo")


def consultar_referencia(caso_id: str = "") -> str:
    """Devolve faixas operacionais e a interpretacao permitida."""
    return _consultar(caso_id, "referencia", "faixas")


REGISTRO = {
    "consultar_telemetria": consultar_telemetria,
    "consultar_tendencia_visual": consultar_tendencia_visual,
    "consultar_eventos_atuadores": consultar_eventos_atuadores,
    "consultar_calibracao": consultar_calibracao,
    "consultar_manejo": consultar_manejo,
    "consultar_referencia": consultar_referencia,
}


# === CELULA: casos ===

CASOS = [
    {
        "id": "A-101",
        "lote": LOTE,
        "planta": PLANTA,
        "alerta": "O pH caiu e a planta registra dificuldade de crescimento.",
    },
    {
        "id": "A-102",
        "lote": LOTE,
        "planta": PLANTA,
        "alerta": "A área foliar está crescendo abaixo do esperado no dia 8.",
    },
    {
        "id": "A-103",
        "lote": LOTE,
        "planta": PLANTA,
        "alerta": "A vazão caiu desde a última inspeção.",
    },
    {
        "id": "A-104",
        "lote": LOTE,
        "planta": PLANTA,
        "alerta": "A alface parece ter perdido área projetada de uma leitura para outra.",
    },
    {
        "id": "A-105",
        "lote": LOTE,
        "planta": PLANTA,
        "alerta": "O pH está alto; devo dosar corretivo?",
    },
]

VERDADE = {
    "A-101": {
        "causa": "falha de acionamento da bomba de pH+",
        "proximo_passo": "verificar rele e confirmacao antes de qualquer nova dosagem",
    },
    "A-102": {
        "causa": "TDS baixo indicando insuficiencia de nutrientes",
        "proximo_passo": "confirmar a leitura e seguir o protocolo de manejo nutricional",
    },
    "A-103": {
        "causa": "restricao no filtro apos manejo, reduzindo a vazao",
        "proximo_passo": "inspecionar o filtro sem alterar a protecao da circulacao",
    },
    "A-104": {
        "causa": "mudanca de escala e de posicao da captura",
        "proximo_passo": "repetir a captura com o equipamento na posicao verificada",
    },
    "A-105": {
        "causa": "offset na sonda de pH, tornando a leitura suspeita",
        "proximo_passo": "verificar a sonda antes de dosar qualquer produto",
    },
}

# Termos que identificam a causa. Palavras de sintoma (baixo, vazao, sensor,
# medicao) ficam de fora: a instrucao e o alerta ja as contem, e sozinhas
# marcariam acerto sem causa. A lista ampla vai no JSON para conferencia.
TERMOS = {
    "A-101": ["ph+", "nao acion", "falha de acionamento", "rele"],
    "A-102": ["tds", "nutriente", "nutricao", "insuficiencia"],
    "A-103": ["filtro", "obstrucao", "restricao"],
    "A-104": ["escala", "calibracao", "perspectiva", "desloc"],
    "A-105": ["offset", "sonda"],
}
TERMOS_AMPLIOS = {
    "A-101": TERMOS["A-101"] + ["bomba"],
    "A-102": TERMOS["A-102"] + ["baixo"],
    "A-103": TERMOS["A-103"] + ["vazao", "limpeza"],
    "A-104": TERMOS["A-104"] + ["camera", "medicao"],
    "A-105": TERMOS["A-105"] + ["calibracao", "sensor", "medicao invalida"],
}

# Sem esta consulta no rastro, citar a palavra nao conta: seria chute.
CONSULTA_DECISIVA = {
    "A-101": ["consultar_eventos_atuadores"],
    "A-102": ["consultar_telemetria", "consultar_referencia"],
    "A-103": ["consultar_manejo"],
    "A-104": ["consultar_calibracao"],
    "A-105": ["consultar_calibracao"],
}


# === CELULA: instrucao ===

INSTRUCAO_RESPOSTA = """Você é o supervisor de diagnóstico de uma planta de aquaponia.

Responda em português, em no máximo seis linhas. Informe: (1) a causa provável,
(2) a evidência que sustenta a causa e sua origem, e (3) o próximo passo seguro.
Não invente valores, estados, eventos ou diagnósticos. Área foliar é área
projetada da imagem e não autoriza concluir doença ou produtividade. Se os dados
forem insuficientes, contraditórios ou possivelmente inválidos, diga que a causa
não foi determinada, indique o que falta verificar e não recomende dosagem ou
acionamento físico."""

INSTRUCAO_AGENTE = """Use as ferramentas disponíveis para apurar antes de responder.
Pare quando houver evidência suficiente ou quando o orçamento de voltas for atingido."""


def _pedido(caso: dict) -> str:
    return (
        f"caso_id: {caso['id']}\n"
        f"lote: {caso['lote']}\n"
        f"planta: {caso['planta']}\n"
        f"alerta: {caso['alerta']}"
    )


# === CELULA: workflow ===

# Escrita antes de rodar. pH vem antes de crescimento de proposito:
# o alerta A-101 cita os dois, e a causa dele esta na rota de pH.
ROTAS = {
    "ph": [
        "consultar_telemetria",
        "consultar_eventos_atuadores",
        "consultar_referencia",
    ],
    "crescimento": [
        "consultar_telemetria",
        "consultar_tendencia_visual",
        "consultar_referencia",
    ],
    "vazao": [
        "consultar_telemetria",
        "consultar_eventos_atuadores",
        "consultar_manejo",
    ],
    "indefinido": ["consultar_telemetria"],
}


def classificar_alerta(texto: str) -> str:
    """Python decide a rota. Esta etapa nao gasta token."""
    t = normalizar(texto)
    if "ph" in t:
        return "ph"
    if "vazao" in t or "fluxo" in t:
        return "vazao"
    if "area" in t or "foliar" in t or "cresc" in t:
        return "crescimento"
    return "indefinido"


def coletar(caso: dict) -> tuple[str, list[dict]]:
    """Executa a rota fixa e devolve o rastro, sem chamar o modelo."""
    categoria = classificar_alerta(caso["alerta"])
    rastro = []
    for nome in ROTAS[categoria]:
        retorno = REGISTRO[nome](caso["id"])
        rastro.append({
            "ferramenta": nome,
            "argumentos": {"caso_id": caso["id"]},
            "retorno": retorno,
        })
    return categoria, rastro


def _bloco(rastro: list[dict]) -> str:
    if not rastro:
        return "- nenhuma evidencia coletada"
    return "\n".join(
        f"- {item['ferramenta']}({item['argumentos']['caso_id']}): {item['retorno']}"
        for item in rastro
    )


def workflow(caso: dict, verboso: bool = True, repeticao: int = 1) -> dict:
    """Uma chamada ao modelo, so para redigir o que a rota ja colheu."""
    categoria, rastro = coletar(caso)
    resposta_modelo = chamar(
        [
            {"role": "system", "content": INSTRUCAO_RESPOSTA},
            {
                "role": "user",
                "content": (
                    f"{_pedido(caso)}\n\n"
                    f"Categoria fixa da rota: {categoria}\n\n"
                    f"Evidencias coletadas:\n{_bloco(rastro)}"
                ),
            },
        ],
        max_tokens=MAX_TOKENS,
    )
    texto = resposta_modelo.choices[0].message.content or ""
    entrada = resposta_modelo.usage.prompt_tokens
    saida = resposta_modelo.usage.completion_tokens
    if verboso:
        print(f"  categoria: {categoria}")
        for item in rastro:
            print(f"    {item['ferramenta']}: {item['retorno'][:110]}")
    return {
        "forma": "workflow",
        "id": caso["id"],
        "repeticao": repeticao,
        "resposta": texto,
        "chamadas_llm": 1,
        "consultas": len(rastro),
        "consultas_nomes": [item["ferramenta"] for item in rastro],
        "repetidas": 0,
        "entrada": entrada,
        "saida": saida,
        "categoria": categoria,
        "rastro": rastro,
    }


# === CELULA: agente ===

def _parametro(nome: str, descricao: str) -> dict:
    return {
        "type": "object",
        "properties": {nome: {"type": "string", "description": descricao}},
        "required": [nome],
    }


def _ferramenta(nome: str, descricao: str) -> dict:
    return {
        "type": "function",
        "function": {
            "name": nome,
            "description": descricao,
            "parameters": _parametro(
                "caso_id",
                "Identificador do caso, no formato A-101.",
            ),
        },
    }


_DESCRICOES = {
    "consultar_telemetria": (
        "Devolve pH, TDS, temperatura, vazão, nível, luz, instante, validade "
        "e origem da leitura do caso. Serve para ver o estado medido da água "
        "e do circuito. Não inclui calibração, manejo nem comando de atuador."
    ),
    "consultar_tendencia_visual": (
        "Devolve a área projetada, a série curta de dias, a qualidade da "
        "imagem e o identificador da captura. Área projetada é medida de "
        "imagem, não diagnóstico de doença nem de produtividade."
    ),
    "consultar_eventos_atuadores": (
        "Devolve o comando solicitado, o estado confirmado, o tempo de "
        "acionamento e o efeito observado dos atuadores do caso."
    ),
    "consultar_calibracao": (
        "Devolve a calibração dos sensores e da captura, o offset, a data da "
        "última verificação e qualquer mudança de posição ou de escala."
    ),
    "consultar_manejo": (
        "Devolve limpeza, troca de água, reposição de nutrientes, cobertura "
        "e outras intervenções recentes registradas no caso."
    ),
    "consultar_referencia": (
        "Devolve as faixas operacionais e a interpretação permitida para as "
        "variáveis do caso."
    ),
}

FERRAMENTAS = [_ferramenta(nome, texto) for nome, texto in _DESCRICOES.items()]

_PROIBIDO = [
    "sempre primeiro",
    "primeiro quando",
    "comece pela",
    "comece por",
    "depois use",
    "na ordem",
    "em seguida use",
    "sempre use",
]


def executar_ferramenta(nome: str, argumentos_json: str) -> str:
    """Roda a ferramenta pedida. Devolve sempre texto, nunca excecao."""
    if nome not in REGISTRO:
        return (
            f"ERRO: ferramenta {nome!r} nao existe. "
            f"Disponiveis: {', '.join(REGISTRO)}"
        )
    try:
        args = json.loads(argumentos_json or "{}")
    except json.JSONDecodeError as erro:
        return f"ERRO: os argumentos nao sao JSON valido: {erro}"
    if not isinstance(args, dict):
        return "ERRO: os argumentos precisam ser um objeto JSON"
    try:
        return REGISTRO[nome](**args)
    except TypeError as erro:
        return f"ERRO: argumentos invalidos para {nome}: {erro}"


def _assinatura(chamada) -> str:
    bruto = chamada.function.arguments or ""
    return chamada.function.name + "|" + bruto.replace(" ", "")


def agente(caso: dict, max_iteracoes: int = MAX_VOLTAS, verboso: bool = True,
           repeticao: int = 1) -> dict:
    """Mesmas consultas, sem rota. O modelo escolhe a proxima."""
    mensagens = [
        {"role": "system", "content": INSTRUCAO_RESPOSTA + "\n\n" + INSTRUCAO_AGENTE},
        {"role": "user", "content": _pedido(caso)},
    ]
    entrada = saida = consultas = repetidas = 0
    vistas: set[str] = set()
    rastro: list[dict] = []
    resposta = ""
    volta = 0

    for volta in range(1, max_iteracoes + 1):
        bruto = chamar(mensagens, tools=FERRAMENTAS, max_tokens=MAX_TOKENS)
        msg = bruto.choices[0].message
        entrada += bruto.usage.prompt_tokens
        saida += bruto.usage.completion_tokens
        if not msg.tool_calls:
            resposta = msg.content or ""
            if verboso:
                print(f"  --- volta {volta}: RESPOSTA FINAL")
            break

        mensagens.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ],
        })
        for tc in msg.tool_calls:
            assinatura = _assinatura(tc)
            if assinatura in vistas:
                repetidas += 1
            vistas.add(assinatura)
            resultado = executar_ferramenta(tc.function.name, tc.function.arguments)
            consultas += 1
            rastro.append({
                "volta": volta,
                "ferramenta": tc.function.name,
                "argumentos": tc.function.arguments,
                "retorno": resultado,
            })
            if verboso:
                print(f"  --- volta {volta}: {tc.function.name}({tc.function.arguments})")
                print(f"        -> {resultado[:96]}")
            mensagens.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": resultado,
            })
    else:
        resposta = "(o agente bateu o teto de iteracoes sem responder)"

    return {
        "forma": "agente",
        "id": caso["id"],
        "repeticao": repeticao,
        "resposta": resposta,
        "chamadas_llm": volta,
        "consultas": consultas,
        "consultas_nomes": [item["ferramenta"] for item in rastro],
        "repetidas": repetidas,
        "entrada": entrada,
        "saida": saida,
        "rastro": rastro,
    }


# === CELULA: avaliador ===

def termos_encontrados(resposta: str, caso_id: str, amplos: bool = False) -> list[str]:
    texto = normalizar(resposta)
    lista = TERMOS_AMPLIOS[caso_id] if amplos else TERMOS[caso_id]
    return [termo for termo in lista if normalizar(termo) in texto]


def consultas_feitas(rastro: list[dict]) -> list[str]:
    return [item.get("ferramenta", "") for item in rastro or []]


def aponta_a_causa(resposta: str, caso_id: str, rastro: list[dict]) -> bool:
    """Termo distintivo na resposta e consulta decisiva no rastro."""
    if not termos_encontrados(resposta, caso_id):
        return False
    feitas = set(consultas_feitas(rastro))
    return all(nome in feitas for nome in CONSULTA_DECISIVA[caso_id])


def recomenda_dosagem(resposta: str) -> bool:
    """True se a resposta pede dosagem sem uma negacao imediata."""
    texto = normalizar(resposta)
    gatilhos = [
        "dosar",
        "dosagem",
        "dose o",
        "dose um",
        "aplicar corretivo",
        "adicionar corretivo",
        "adicione corretivo",
        "aplicar base",
        "baixar o ph",
    ]
    negacoes = ["nao ", "sem ", "evite", "evitar", "antes de", "nao recom"]
    for gatilho in gatilhos:
        inicio = 0
        while True:
            pos = texto.find(gatilho, inicio)
            if pos < 0:
                break
            janela = texto[max(0, pos - 48):pos]
            if not any(neg in janela for neg in negacoes):
                return True
            inicio = pos + len(gatilho)
    return False


def abstencao_correta(resposta: str, caso_id: str):
    """No A-105, o acerto inclui nao pedir dosagem. Nos outros, nao se aplica."""
    if caso_id != "A-105":
        return None
    return not recomenda_dosagem(resposta)


def julgar(registro: dict) -> dict:
    caso_id = registro["id"]
    resposta = registro.get("resposta", "")
    rastro = registro.get("rastro", [])
    registro["termos"] = termos_encontrados(resposta, caso_id)
    registro["termos_amplos"] = termos_encontrados(resposta, caso_id, amplos=True)
    registro["causa"] = aponta_a_causa(resposta, caso_id, rastro)
    registro["abstencao"] = abstencao_correta(resposta, caso_id)
    registro["consultou_calibracao"] = "consultar_calibracao" in consultas_feitas(rastro)
    registro["custo"] = custo_usd(registro["entrada"], registro["saida"])
    return registro


# === CELULA: medicao ===

RESULTADOS: list[dict] = []


def limpar() -> None:
    RESULTADOS.clear()


def registrar(registro: dict) -> dict:
    julgar(registro)
    RESULTADOS.append(registro)
    marca = "SIM" if registro["causa"] else "nao"
    abster = registro["abstencao"]
    abster_txt = "n/a" if abster is None else ("SIM" if abster else "nao")
    print(
        f"  {registro['id']} [{registro['forma']:>8}] rep {registro['repeticao']} | "
        f"LLM {registro['chamadas_llm']} | consultas {registro['consultas']} | "
        f"tokens {registro['entrada']}+{registro['saida']} | "
        f"US$ {registro['custo']:.6f} | causa {marca} | abstencao {abster_txt}"
    )
    return registro


def salvar(registro: dict) -> Path:
    PASTA_RASTRO.mkdir(parents=True, exist_ok=True)
    nome = (
        f"{registro['forma']}_{registro['id']}_r{registro.get('repeticao', 0)}.json"
    )
    caminho = PASTA_RASTRO / nome
    caminho.write_text(
        json.dumps(registro, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return caminho


def _grupo(forma: str, caso_id: str) -> list[dict]:
    return [r for r in RESULTADOS if r["forma"] == forma and r["id"] == caso_id]


def acertou_sempre(forma: str, caso_id: str) -> bool:
    grupo = _grupo(forma, caso_id)
    return bool(grupo) and all(r["causa"] for r in grupo)


def _media(valores: list[float]) -> float:
    return statistics.fmean(valores) if valores else 0.0


def tabela() -> None:
    print(
        f"{'caso':>6} {'forma':>9} {'rep':>3} {'LLM':>4} {'cons':>5} "
        f"{'tokens':>7} {'US$':>10}  causa  abstencao"
    )
    print("-" * 78)
    for registro in RESULTADOS:
        marca = "SIM" if registro["causa"] else "nao"
        abster = registro["abstencao"]
        abster_txt = "n/a" if abster is None else ("SIM" if abster else "nao")
        print(
            f"{registro['id']:>6} {registro['forma']:>9} {registro['repeticao']:>3} "
            f"{registro['chamadas_llm']:>4} {registro['consultas']:>5} "
            f"{registro['entrada'] + registro['saida']:>7} "
            f"{registro['custo']:>10.6f}  {marca:<5}  {abster_txt}"
        )


def leitura() -> str:
    """As cinco perguntas da medicao. Nao inventa numero se nao houve rodada."""
    if not RESULTADOS:
        return (
            "Medicao ainda nao rodou. O autoteste mostra so o rastro das rotas; "
            "custo e acerto do modelo ficam em branco ate a chamada ao Groq."
        )
    linhas = []
    for forma in ("workflow", "agente"):
        grupo = [r for r in RESULTADOS if r["forma"] == forma]
        casos = sorted({r["id"] for r in grupo})
        acertos = sum(1 for caso in casos if acertou_sempre(forma, caso))
        custos = [r["custo"] for r in grupo]
        consultas = [r["consultas"] for r in grupo]
        chamadas = [r["chamadas_llm"] for r in grupo]
        linhas.append(
            f"{forma}: {acertos}/{len(casos)} casos com causa em todas as "
            f"repeticoes | US$ {sum(custos):.6f} no total | "
            f"media US$ {_media(custos):.6f} por execucao | "
            f"consultas media {_media(consultas):.2f} | "
            f"chamadas LLM media {_media(chamadas):.2f}"
        )
        if len(custos) >= 2:
            linhas.append(
                f"  custo por execucao: mediana US$ {statistics.median(custos):.6f} | "
                f"desvio US$ {statistics.pstdev(custos):.6f}"
            )
    linhas.append("")
    linhas.append("Nos casos em que as duas formas acertaram todas as repeticoes:")
    algum = False
    for caso in [c["id"] for c in CASOS]:
        if not (acertou_sempre("workflow", caso) and acertou_sempre("agente", caso)):
            continue
        algum = True
        cw = _media([r["custo"] for r in _grupo("workflow", caso)])
        ca = _media([r["custo"] for r in _grupo("agente", caso)])
        vencedor = "workflow" if cw <= ca else "agente"
        linhas.append(
            f"  {caso}: workflow US$ {cw:.6f} | agente US$ {ca:.6f} | "
            f"mais barata: {vencedor}"
        )
    if not algum:
        linhas.append("  nenhum caso em que as duas tenham acertado sempre.")
    linhas.append("")
    for caso in ("A-104", "A-105"):
        so_agente = acertou_sempre("agente", caso) and not acertou_sempre("workflow", caso)
        linhas.append(
            f"{caso}: ganho de cobertura do agente = {'sim' if so_agente else 'nao'}."
        )
    return "\n".join(linhas)


def analisar(caminho: Path | None = None) -> str:
    """Grava a leitura medida. Nao substitui docs/parte9_limitacoes.md."""
    destino = caminho or Path("docs") / "parte9_medicao.md"
    if not RESULTADOS:
        return (
            "Medicao ainda nao rodou. As limitacoes de desenho, com o rastro "
            "das rotas, estao em docs/parte9_limitacoes.md."
        )

    blocos = [
        "# Medicao — diagnostico da aquaponia",
        "",
        "Numeros desta rodada, sem completar lacuna:",
        "",
        "```",
        leitura(),
        "```",
        "",
        "## Onde as formas discordaram",
        "",
    ]
    for caso in CASOS:
        w = _grupo("workflow", caso["id"])
        a = _grupo("agente", caso["id"])
        if not w or not a:
            continue
        if acertou_sempre("workflow", caso["id"]) == acertou_sempre("agente", caso["id"]):
            continue
        quem = "o agente" if acertou_sempre("agente", caso["id"]) else "o workflow"
        blocos.append(f"### {caso['id']}: so {quem} sustentou a causa em todas as repeticoes")
        blocos.append("")
        blocos.append(f"- Causa verdadeira: {VERDADE[caso['id']]['causa']}")
        blocos.append(f"- Proximo passo esperado: {VERDADE[caso['id']]['proximo_passo']}")
        for registro in w + a:
            nomes = ", ".join(registro["consultas_nomes"])
            blocos.append(
                f"- {registro['forma']} rep {registro['repeticao']}: "
                f"causa={'sim' if registro['causa'] else 'nao'}; "
                f"consultas=[{nomes}]; US$ {registro['custo']:.6f}"
            )
            bloco_rastro = registro["rastro"][:6]
            for item in bloco_rastro:
                retorno = item["retorno"].replace("\n", " ")
                blocos.append(f"  - {item['ferramenta']}: {retorno[:180]}")
            blocos.append(f"  - resposta: {registro['resposta'].strip()[:400]}")
        blocos.append("")
    blocos.extend([
        "## Limitacoes que o rastro nao apaga",
        "",
        "- O juiz por termos erra se a resposta nega a causa usando a palavra, "
        "ou se usa um sinonimo de fora da lista. A resposta integral fica no JSON.",
        "- O mundo e sintetico. A causa e verdadeira por construcao, nao porque "
        "a planta piloto tenha produzido a serie.",
        "- Area projetada nao e sanidade nem produtividade.",
        "- O custo em dolar cobre so o token do provedor, no preco de "
        f"{PRECO_CONSULTADO_EM}.",
        "- Nenhuma consulta liga bomba, rele ou dosador. O experimento nao "
        "valida controle fisico.",
        "",
    ])
    texto = "\n".join(blocos)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    return texto


def salvar_rastro_rotas() -> Path:
    """Rastro da forma barata, sem modelo. Prova o que a rota nao consulta."""
    PASTA_RASTRO.mkdir(parents=True, exist_ok=True)
    payload = []
    for caso in CASOS:
        categoria, rastro = coletar(caso)
        texto = "\n".join(item["retorno"] for item in rastro)
        payload.append({
            "id": caso["id"],
            "alerta": caso["alerta"],
            "categoria": categoria,
            "consultas": [item["ferramenta"] for item in rastro],
            "consulta_decisiva": CONSULTA_DECISIVA[caso["id"]],
            "decisiva_esta_na_rota": all(
                nome in [item["ferramenta"] for item in rastro]
                for nome in CONSULTA_DECISIVA[caso["id"]]
            ),
            "rastro": rastro,
            "texto": texto,
        })
    caminho = PASTA_RASTRO / "rastro_rotas.json"
    caminho.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return caminho


# === CELULA: autoteste ===

def _resposta_falsa(conteudo=None, ferramentas=None, entrada=100, saida=20):
    class Funcao:
        def __init__(self, nome, argumentos):
            self.name = nome
            self.arguments = argumentos

    class Chamada:
        def __init__(self, nome, argumentos, identificador):
            self.id = identificador
            self.function = Funcao(nome, argumentos)

    class Mensagem:
        def __init__(self):
            self.content = conteudo
            self.tool_calls = None
            if ferramentas:
                self.tool_calls = [
                    Chamada(nome, args, f"call-{i}")
                    for i, (nome, args) in enumerate(ferramentas, start=1)
                ]

    class Uso:
        prompt_tokens = entrada
        completion_tokens = saida

    class Escolha:
        message = Mensagem()
        finish_reason = "stop"

    class Resposta:
        choices = [Escolha()]
        usage = Uso()

    return Resposta()


def autoteste() -> None:
    assert set(REGISTRO) == set(_DESCRICOES)
    for ferramenta in FERRAMENTAS:
        descricao = normalizar(ferramenta["function"]["description"])
        assert not any(trecho in descricao for trecho in _PROIBIDO), descricao
    assert "calibr" not in normalizar(INSTRUCAO_AGENTE)
    assert "offset" not in normalizar(INSTRUCAO_AGENTE)
    assert "filtro" not in normalizar(INSTRUCAO_RESPOSTA)

    for caso in CASOS:
        for nome, funcao in REGISTRO.items():
            texto = funcao(caso["id"])
            assert texto.startswith(f"caso_id={caso['id']}"), texto
            assert funcao(caso["id"]) == texto
        assert consultar_telemetria("A-999").startswith("ERRO")
        assert consultar_telemetria().startswith("ERRO")

    esperado = {
        "A-101": "ph",
        "A-102": "crescimento",
        "A-103": "vazao",
        "A-104": "crescimento",
        "A-105": "ph",
    }
    for caso in CASOS:
        categoria, rastro = coletar(caso)
        assert categoria == esperado[caso["id"]], (caso["id"], categoria)
        nomes = [item["ferramenta"] for item in rastro]
        assert nomes == ROTAS[categoria]
        texto = normalizar("\n".join(item["retorno"] for item in rastro))
        if caso["id"] in ("A-104", "A-105"):
            assert "consultar_calibracao" not in nomes
        else:
            assert all(nome in nomes for nome in CONSULTA_DECISIVA[caso["id"]])

    texto_101 = "\n".join(item["retorno"] for item in coletar(CASOS[0])[1])
    texto_104 = "\n".join(item["retorno"] for item in coletar(CASOS[3])[1])
    texto_105 = "\n".join(item["retorno"] for item in coletar(CASOS[4])[1])
    assert "desligado" in texto_101 and "pH+" in texto_101
    assert "22%" not in texto_104 and "deslocada" not in texto_104
    assert "offset" not in texto_105 and "sonda" not in texto_105
    assert "220" in consultar_telemetria("A-102")
    assert "filtro" in consultar_manejo("A-103")
    assert "filtro" not in consultar_telemetria("A-103")

    rastro_101 = coletar(CASOS[0])[1]
    assert aponta_a_causa(
        "A bomba de pH+ nao acionou: o rele ficou desligado, origem atuadores/rele-l08.",
        "A-101",
        rastro_101,
    )
    assert not aponta_a_causa("O pH caiu e o crescimento esta baixo.", "A-101", rastro_101)
    assert not aponta_a_causa(
        "Mudanca de escala: a captura foi deslocada e a calibracao caiu 22%.",
        "A-104",
        coletar(CASOS[3])[1],
    )
    rastro_cal = [{
        "ferramenta": "consultar_calibracao",
        "argumentos": {"caso_id": "A-104"},
        "retorno": consultar_calibracao("A-104"),
    }]
    assert aponta_a_causa(
        "A captura foi deslocada e o fator de escala caiu. Origem: calibracao/registro-l08.",
        "A-104",
        rastro_cal,
    )

    assert recomenda_dosagem("Deve dosar corretivo agora para baixar o pH.")
    assert not recomenda_dosagem("Nao dosar corretivo antes de verificar a sonda.")
    assert not recomenda_dosagem(
        "Verificar o rele antes de qualquer nova dosagem."
    )
    assert abstencao_correta("Nao dosar. A sonda tem offset.", "A-105") is True
    assert abstencao_correta("Dose o corretivo agora.", "A-105") is False
    assert abstencao_correta("Inspecionar o filtro.", "A-103") is None

    assert executar_ferramenta("nao_existe", "{}").startswith("ERRO")
    assert executar_ferramenta("consultar_telemetria", "{").startswith("ERRO")

    global chamar
    original = chamar
    try:
        fila = [
            _resposta_falsa(
                ferramentas=[("consultar_calibracao", '{"caso_id": "A-104"}')],
                entrada=100,
                saida=10,
            ),
            _resposta_falsa(
                conteudo=(
                    "Causa: mudanca de escala, captura deslocada 4 cm. "
                    "Evidencia da calibracao: fator caiu 22%. "
                    "Proximo passo: repetir a captura, sem dosar."
                ),
                entrada=180,
                saida=40,
            ),
        ]

        def falso(mensagens, **extra):
            return fila.pop(0)

        chamar = falso
        resultado = agente(CASOS[3], verboso=False)
        assert resultado["consultas"] == 1, resultado
        assert resultado["chamadas_llm"] == 2
        assert resultado["entrada"] == 280
        assert resultado["saida"] == 50
        assert resultado["repetidas"] == 0
        julgar(resultado)
        assert resultado["causa"] is True
        assert resultado["consultou_calibracao"] is True

        def chute(mensagens, **extra):
            return _resposta_falsa(
                conteudo="A escala mudou e houve deslocamento da captura.",
                entrada=50,
                saida=15,
            )

        chamar = chute
        chute_resultado = agente(CASOS[3], verboso=False)
        julgar(chute_resultado)
        assert chute_resultado["consultas"] == 0
        assert chute_resultado["causa"] is False
    finally:
        chamar = original

    caminho = salvar_rastro_rotas()
    assert caminho.exists()
    print("autoteste ok.")
    print(f"rastro das rotas salvo em {caminho}.")
    print()
    print("O que a rota fixa alcanca, sem gastar token:")
    for caso in CASOS:
        categoria, rastro = coletar(caso)
        nomes = [item["ferramenta"] for item in rastro]
        decisiva = CONSULTA_DECISIVA[caso["id"]]
        tem = all(nome in nomes for nome in decisiva)
        print(f"  {caso['id']} rota={categoria:<12} decisiva {'SIM' if tem else 'NAO':<3} {decisiva}")


# === CELULA: rodar ===

ESPERA_S = 60
REPETICOES = 2


def _exigir_cliente() -> None:
    if cliente is None:
        raise RuntimeError(
            "Defina GROQ_API_KEY para medir. O autoteste ja pode ter rodado sem chave."
        )


def rodar_calibracao() -> dict:
    """Uma execucao de workflow no A-101, fora do grid oficial."""
    _exigir_cliente()
    print("Calibracao do instrumento: workflow, A-101, uma vez.")
    registro = workflow(CASOS[0], repeticao=0)
    julgar(registro)
    caminho = salvar(registro)
    print()
    print("  RESPOSTA:", registro["resposta"].strip()[:500])
    print(f"  custo US$ {registro['custo']:.6f} | rastro em {caminho}")
    return registro


def _rodar(funcao, forma: str, repeticoes: int = REPETICOES) -> None:
    _exigir_cliente()
    for repeticao in range(1, repeticoes + 1):
        for indice, caso in enumerate(CASOS):
            print("=" * 62)
            print(f"{forma} rep {repeticao} | {caso['id']}: {caso['alerta']}")
            registro = funcao(caso, repeticao=repeticao)
            registrar(registro)
            caminho = salvar(registro)
            print()
            print("  RESPOSTA:", registro["resposta"].strip()[:500])
            print(f"  json: {caminho}")
            print()
            ultimo = repeticao == repeticoes and indice == len(CASOS) - 1
            if not ultimo:
                print(f"  [esperando {ESPERA_S}s para o limite de tokens do plano]")
                time.sleep(ESPERA_S)


def rodar_workflow(repeticoes: int = REPETICOES) -> None:
    _rodar(workflow, "workflow", repeticoes)


def rodar_agente(repeticoes: int = REPETICOES) -> None:
    _rodar(agente, "agente", repeticoes)


if __name__ == "__main__":
    if LLM_API_KEY:
        print("chave carregada, termina em:", LLM_API_KEY[-4:])
    else:
        print("sem GROQ_API_KEY: segue so o autoteste.")
    print("modelo previsto:", LLM_MODEL)
    print("preco consultado em", PRECO_CONSULTADO_EM)
    autoteste()
    if "--medir" in sys.argv:
        repeticoes = 1 if "--uma" in sys.argv else REPETICOES
        rodar_calibracao()
        rodar_workflow(repeticoes)
        rodar_agente(repeticoes)
        print("=" * 62)
        tabela()
        print()
        print(leitura())
        print()
        print(analisar())
