"""
Neighborhood Action Dashboard
Painel comunitário de ocorrências da Comunidade Vale Verde (fictícia)

Global Solution 2026.2 - FIAP - Ciência da Computação - Grupo 34

Como executar (a partir da pasta GLOBAL-SOLUTION-1):
    python src/sistema.py

O sistema lê as ocorrências e o histórico dos arquivos da pasta data/,
valida cada registro, organiza os dados em estruturas (lista, fila, pilha,
dicionário, hierarquia e matriz) e oferece um menu no terminal para
consultar, cadastrar, atualizar e acompanhar indicadores.

Usa apenas Python básico (biblioteca padrão), sem pacotes externos.
"""
import os

# ======================================================================
# 1. CONFIGURAÇÃO E VALORES PADRONIZADOS
# ======================================================================

# Caminhos dos arquivos de dados (funciona de qualquer pasta)
PASTA_SRC = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(PASTA_SRC, "..", "data")
ARQ_OCORRENCIAS = os.path.join(PASTA_DADOS, "ocorrencias.csv")
ARQ_HISTORICO = os.path.join(PASTA_DADOS, "historico.csv")

DIA_INICIAL = 30  # "hoje" na simulação: dia 30 do período acompanhado

# Categorias padronizadas: código interno -> nome exibido
CATEGORIAS = {
    "ILUMINACAO": "Iluminação",
    "ACESSIBILIDADE": "Acessibilidade",
    "LIMPEZA": "Limpeza",
    "CONSERVACAO": "Conservação",
}

# Situações padronizadas: código interno -> (nome exibido, significado)
# Tuplas porque são informações fixas, que não mudam durante a execução.
STATUS = {
    "ABERTA": ("Aberta", "registrada e ainda não examinada pela equipe"),
    "EM_ANALISE": ("Em análise", "examinada, com atendimento em avaliação ou andamento"),
    "CONCLUIDA": ("Concluída", "problema resolvido e demanda encerrada"),
}

# Mudanças de situação permitidas (de -> para). Concluída não muda mais.
TRANSICOES = {
    "ABERTA": ("EM_ANALISE",),
    "EM_ANALISE": ("CONCLUIDA", "ABERTA"),
    "CONCLUIDA": (),
}

# Campos de uma ocorrência. Todos são obrigatórios.
CAMPOS_OBRIGATORIOS = ("codigo", "categoria", "descricao", "bairro",
                       "local", "dia_abertura", "status")

# Tabela para remover acentos (aceita "análise" ou "analise", por exemplo)
SEM_ACENTO = str.maketrans("áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ",
                           "aaaaeeiooouucAAAAEEIOOOUUC")


# ======================================================================
# 2. FUNÇÕES AUXILIARES DE TEXTO E ENTRADA
# ======================================================================

def normalizar(texto):
    """Padroniza um texto: sem acentos, maiúsculo, espaços viram '_'.
    Ex.: ' em análise ' -> 'EM_ANALISE'."""
    return texto.strip().translate(SEM_ACENTO).upper().replace(" ", "_")


def padronizar_codigo(texto):
    """Aceita '5', '05' ou '005' e devolve '005'."""
    texto = texto.strip()
    if texto.isdigit():
        return texto.zfill(3)
    return texto


def cortar(texto, tamanho):
    """Corta textos longos para caberem na tabela."""
    if len(texto) <= tamanho:
        return texto
    return texto[:tamanho - 1] + "…"


def ler_entrada(mensagem):
    """input() que encerra de forma amigável se a entrada acabar."""
    try:
        return input(mensagem)
    except EOFError:
        print("\nEntrada encerrada. Até logo!")
        raise SystemExit


def escolher_opcao(titulo, opcoes, permitir_vazio=False):
    """Mostra opções numeradas e devolve o código escolhido.
    Aceita o número ou o nome (com ou sem acento).
    Com permitir_vazio=True, Enter devolve None (= todas)."""
    chaves = list(opcoes)
    print(titulo)
    for i, chave in enumerate(chaves, start=1):
        nome = opcoes[chave][0] if isinstance(opcoes[chave], tuple) else opcoes[chave]
        print(f"  {i}) {nome}")
    if permitir_vazio:
        print("  Enter) todas")

    resposta = ler_entrada("Escolha: ").strip()
    if resposta == "" and permitir_vazio:
        return None
    if resposta.isdigit() and 1 <= int(resposta) <= len(chaves):
        return chaves[int(resposta) - 1]
    if normalizar(resposta) in opcoes:
        return normalizar(resposta)
    print("[ERRO] Opção inválida.")
    return "INVALIDA"


def contem_dado_pessoal(texto):
    """Regra de privacidade: recusa textos com e-mail ou com 8 ou mais
    dígitos seguidos (possível telefone ou documento)."""
    digitos_seguidos = 0
    maior_sequencia = 0
    for caractere in texto:
        if caractere.isdigit():
            digitos_seguidos += 1
            maior_sequencia = max(maior_sequencia, digitos_seguidos)
        else:
            digitos_seguidos = 0
    # Expressão booleana com OR: basta uma das condições para recusar
    return "@" in texto or maior_sequencia >= 8


# ======================================================================
# 3. VALIDAÇÃO
# ======================================================================

def validar_ocorrencia(campos, painel):
    """Confere uma ocorrência e devolve a lista de problemas encontrados.
    Lista vazia = registro válido."""
    erros = []

    # Campos obrigatórios: ausente ou só espaços é erro
    for campo in CAMPOS_OBRIGATORIOS:
        if not campos.get(campo, "").strip():
            erros.append(f"campo obrigatório '{campo}' ausente")

    categoria = campos.get("categoria", "")
    status = campos.get("status", "")
    dia = campos.get("dia_abertura", "")

    if categoria and categoria not in CATEGORIAS:
        erros.append(f"categoria desconhecida '{categoria}'")
    if status and status not in STATUS:
        erros.append(f"situação desconhecida '{status}'")

    # AND + NOT: o dia precisa ser número E estar entre 1 e o dia atual
    dia_valido = dia.isdigit() and 1 <= int(dia) <= painel["dia_atual"]
    if dia and not dia_valido:
        erros.append(f"dia de abertura inválido '{dia}'")

    if campos.get("codigo") in painel["indice"]:
        erros.append(f"código '{campos['codigo']}' já existe")

    for campo in ("descricao", "local"):
        if contem_dado_pessoal(campos.get(campo, "")):
            erros.append(f"'{campo}' parece conter dado pessoal (e-mail ou telefone)")

    return erros


# ======================================================================
# 4. CARREGAMENTO DOS DADOS
# ======================================================================

def ler_csv(caminho):
    """Lê um arquivo CSV separado por ';' e devolve uma lista de
    (número da linha, dicionário campo -> valor)."""
    registros = []
    with open(caminho, encoding="utf-8") as arquivo:
        linhas = arquivo.read().splitlines()
    cabecalho = linhas[0].split(";")
    for numero, linha in enumerate(linhas[1:], start=2):
        if not linha.strip():
            continue
        valores = linha.split(";")
        # Linha com colunas faltando: completa com vazio (vira campo ausente)
        while len(valores) < len(cabecalho):
            valores.append("")
        registros.append((numero, dict(zip(cabecalho, valores))))
    return registros


def adicionar_ocorrencia(painel, campos):
    """Guarda uma ocorrência já validada nas estruturas do painel."""
    ocorrencia = {
        "codigo": campos["codigo"],
        "categoria": campos["categoria"],
        "descricao": campos["descricao"].strip(),
        "bairro": campos["bairro"].strip(),
        "local": campos["local"].strip(),
        "dia_abertura": int(campos["dia_abertura"]),
        "status": campos["status"],
        "dia_conclusao": None,
    }
    painel["ocorrencias"].append(ocorrencia)              # lista
    painel["indice"][ocorrencia["codigo"]] = ocorrencia    # dicionário
    return ocorrencia


def registrar_evento(painel, codigo, dia, anterior, novo, observacao):
    """Registra uma mudança no histórico (lista) e na pilha de eventos."""
    evento = {"codigo": codigo, "dia": dia, "status_anterior": anterior,
              "status_novo": novo, "observacao": observacao}
    painel["historico"].append(evento)
    painel["pilha_eventos"].append(evento)   # empilhar: o mais recente fica no topo
    if novo == "CONCLUIDA":
        painel["indice"][codigo]["dia_conclusao"] = dia


def carregar_dados():
    """Lê os arquivos, valida os registros e monta todas as estruturas."""
    painel = {
        "ocorrencias": [],     # lista com todas as ocorrências válidas
        "indice": {},          # dicionário: código -> ocorrência
        "fila_triagem": [],    # fila (FIFO): códigos abertos ainda não examinados
        "pilha_eventos": [],   # pilha (LIFO): últimas atualizações
        "historico": [],       # lista completa de eventos
        "rejeitados": [],      # registros inconsistentes e o motivo
        "dia_atual": DIA_INICIAL,
    }

    # 4.1 Ocorrências
    for numero, campos in ler_csv(ARQ_OCORRENCIAS):
        campos["codigo"] = padronizar_codigo(campos.get("codigo", ""))
        campos["categoria"] = normalizar(campos.get("categoria", ""))
        campos["status"] = normalizar(campos.get("status", ""))
        erros = validar_ocorrencia(campos, painel)
        if erros:
            painel["rejeitados"].append({"linha": numero, "codigo": campos["codigo"],
                                         "descricao": campos.get("descricao", ""),
                                         "motivos": erros})
        else:
            adicionar_ocorrencia(painel, campos)

    # 4.2 Histórico (só eventos de ocorrências válidas e situações conhecidas)
    for numero, campos in ler_csv(ARQ_HISTORICO):
        codigo = padronizar_codigo(campos["codigo"])
        anterior = normalizar(campos["status_anterior"])
        novo = normalizar(campos["status_novo"])
        if codigo in painel["indice"] and anterior in STATUS and novo in STATUS:
            registrar_evento(painel, codigo, int(campos["dia"]), anterior, novo,
                             campos["observacao"])
        else:
            painel["rejeitados"].append({"linha": numero, "codigo": codigo,
                                         "descricao": "evento do histórico",
                                         "motivos": ["evento de ocorrência inexistente ou situação desconhecida"]})

    # 4.3 Fila de triagem: abertas, na ordem de registro (dia e código)
    abertas = [oc for oc in painel["ocorrencias"] if oc["status"] == "ABERTA"]
    abertas.sort(key=lambda oc: (oc["dia_abertura"], oc["codigo"]))
    for oc in abertas:
        painel["fila_triagem"].append(oc["codigo"])   # enfileirar no fim
    return painel


# ======================================================================
# 5. ESTRUTURAS DERIVADAS: HIERARQUIA E MATRIZ
# ======================================================================

def montar_hierarquia(ocorrencias):
    """Hierarquia bairro -> categoria -> lista de códigos."""
    hierarquia = {}
    for oc in ocorrencias:
        bairro = hierarquia.setdefault(oc["bairro"], {})
        bairro.setdefault(oc["categoria"], []).append(oc["codigo"])
    return hierarquia


def montar_matriz(ocorrencias):
    """Matriz (lista de listas): linhas = categorias, colunas = situações.
    matriz[i][j] = quantidade de ocorrências da categoria i na situação j."""
    categorias = list(CATEGORIAS)
    situacoes = list(STATUS)
    matriz = [[0 for _ in situacoes] for _ in categorias]
    for oc in ocorrencias:
        i = categorias.index(oc["categoria"])
        j = situacoes.index(oc["status"])
        matriz[i][j] += 1
    return matriz


# ======================================================================
# 6. CONSULTAS E ATUALIZAÇÃO
# ======================================================================

def imprimir_tabela(ocorrencias):
    """Listagem legível: código, categoria, bairro, local e situação."""
    if not ocorrencias:
        print("Nenhuma ocorrência para mostrar.")
        return
    print(f"{'Cód.':<5} {'Categoria':<15} {'Bairro':<20} {'Local':<28} {'Situação':<11}")
    print("-" * 82)
    for oc in ocorrencias:
        print(f"{oc['codigo']:<5} {CATEGORIAS[oc['categoria']]:<15} "
              f"{cortar(oc['bairro'], 20):<20} {cortar(oc['local'], 28):<28} "
              f"{STATUS[oc['status']][0]:<11}")
    print(f"Total: {len(ocorrencias)} ocorrência(s).")


def filtrar(ocorrencias, categoria=None, status=None):
    """Filtra por categoria e/ou situação. None = sem filtro naquele campo."""
    resultado = []
    for oc in ocorrencias:
        # Expressão booleana documentada no README:
        # (categoria vazia OU igual) E (situação vazia OU igual)
        if (categoria is None or oc["categoria"] == categoria) and \
           (status is None or oc["status"] == status):
            resultado.append(oc)
    return resultado


def atualizar_status(painel, codigo, novo, observacao):
    """Muda a situação de uma ocorrência, se a mudança for permitida.
    Devolve (sucesso, mensagem)."""
    if codigo not in painel["indice"]:
        return False, f"Ocorrência {codigo} não encontrada."
    oc = painel["indice"][codigo]
    atual = oc["status"]

    if novo not in STATUS:
        return False, f"Situação '{novo}' desconhecida."
    elif novo == atual:
        return False, f"A ocorrência {codigo} já está como '{STATUS[atual][0]}'."
    elif novo not in TRANSICOES[atual]:
        return False, (f"Mudança não permitida: '{STATUS[atual][0]}' -> "
                       f"'{STATUS[novo][0]}'.")
    else:
        oc["status"] = novo
        # Saiu de "aberta": deixa a fila de triagem
        if atual == "ABERTA" and codigo in painel["fila_triagem"]:
            painel["fila_triagem"].remove(codigo)
        # Voltou para "aberta": entra de novo no fim da fila
        if novo == "ABERTA":
            painel["fila_triagem"].append(codigo)
        registrar_evento(painel, codigo, painel["dia_atual"], atual, novo,
                         observacao or "sem observação")
        return True, (f"Ocorrência {codigo}: '{STATUS[atual][0]}' -> "
                      f"'{STATUS[novo][0]}' (dia {painel['dia_atual']}).")


def proximo_codigo(painel):
    """Gera um código único: maior código já usado + 1 (inclui rejeitados)."""
    usados = list(painel["indice"]) + [r["codigo"] for r in painel["rejeitados"]]
    numeros = [int(c) for c in usados if c.isdigit()]
    return str(max(numeros, default=0) + 1).zfill(3)


# ======================================================================
# 7. INDICADORES
# ======================================================================

def calcular_indicadores(painel):
    """Calcula totais, proporções, pendências e tempos médios."""
    ocorrencias = painel["ocorrencias"]
    total = len(ocorrencias)

    por_categoria = {chave: 0 for chave in CATEGORIAS}
    por_status = {chave: 0 for chave in STATUS}
    pendentes_por_categoria = {chave: 0 for chave in CATEGORIAS}
    tempos_conclusao = []
    tempos_pendentes = []

    for oc in ocorrencias:
        por_categoria[oc["categoria"]] += 1
        por_status[oc["status"]] += 1
        pendente = oc["status"] == "ABERTA" or oc["status"] == "EM_ANALISE"
        if pendente:
            pendentes_por_categoria[oc["categoria"]] += 1
            tempos_pendentes.append(painel["dia_atual"] - oc["dia_abertura"])
        elif oc["dia_conclusao"] is not None:
            tempos_conclusao.append(oc["dia_conclusao"] - oc["dia_abertura"])

    def media(valores):
        return sum(valores) / len(valores) if valores else 0

    return {
        "total": total,
        "por_categoria": por_categoria,
        "por_status": por_status,
        "pendentes": por_status["ABERTA"] + por_status["EM_ANALISE"],
        "pendentes_por_categoria": pendentes_por_categoria,
        "tempos_conclusao": tempos_conclusao,
        "media_conclusao": media(tempos_conclusao),
        "media_pendentes": media(tempos_pendentes),
    }


def percentual(parte, total):
    return parte / total * 100 if total else 0


def maiores(contagem):
    """Devolve (nomes das categorias com o maior valor, maior valor).
    Considera empates: todas as que tiverem o maior valor entram."""
    maior = max(contagem.values())
    nomes = [CATEGORIAS[chave] for chave, valor in contagem.items() if valor == maior]
    return " e ".join(nomes), maior


def interpretar(ind):
    """Gera uma conclusão curta a partir dos números."""
    if ind["total"] == 0:
        return ["Não há ocorrências cadastradas."]
    mais_frequente, qtd_frequente = maiores(ind["por_categoria"])
    mais_pendente, qtd_pendente = maiores(ind["pendentes_por_categoria"])
    concluidas = percentual(ind["por_status"]["CONCLUIDA"], ind["total"])
    frases = [
        f"Mais ocorrências: {mais_frequente} ({qtd_frequente} de {ind['total']}).",
        f"Mais pendências: {mais_pendente} "
        f"({qtd_pendente} em aberto ou em análise{' cada' if ' e ' in mais_pendente else ''}).",
        f"Só {concluidas:.0f}% das demandas foram concluídas; "
        f"{ind['pendentes']} seguem pendentes.",
    ]
    if ind["media_pendentes"] > ind["media_conclusao"] > 0:
        frases.append("As pendências já esperam, em média, mais do que o tempo "
                      "que as concluídas levaram: é sinal de fila acumulando.")
    return frases


# ======================================================================
# 8. TELAS DO MENU
# ======================================================================

def tela_listar(painel):
    print("\n=== TODAS AS OCORRÊNCIAS ===")
    imprimir_tabela(painel["ocorrencias"])


def mostrar_detalhes(painel, oc):
    print(f"\nOcorrência {oc['codigo']}")
    print(f"  Categoria : {CATEGORIAS[oc['categoria']]}")
    print(f"  Descrição : {oc['descricao']}")
    print(f"  Bairro    : {oc['bairro']}")
    print(f"  Local     : {oc['local']}")
    print(f"  Abertura  : dia {oc['dia_abertura']}")
    print(f"  Situação  : {STATUS[oc['status']][0]} ({STATUS[oc['status']][1]})")
    eventos = [e for e in painel["historico"] if e["codigo"] == oc["codigo"]]
    if eventos:
        print("  Histórico :")
        for e in eventos:
            de = STATUS[e["status_anterior"]][0] if e["status_anterior"] else "—"
            print(f"    dia {e['dia']:>2}: {de} -> {STATUS[e['status_novo']][0]}"
                  f" ({e['observacao']})")


def tela_buscar(painel):
    print("\n=== BUSCAR POR CÓDIGO ===")
    codigo = padronizar_codigo(ler_entrada("Código da ocorrência (ex.: 5 ou 005): "))
    if codigo in painel["indice"]:        # acesso direto pelo dicionário
        mostrar_detalhes(painel, painel["indice"][codigo])
    else:
        print(f"[AVISO] Ocorrência '{codigo}' não encontrada.")


def tela_filtrar(painel):
    print("\n=== FILTRAR OCORRÊNCIAS ===")
    categoria = escolher_opcao("Categoria:", CATEGORIAS, permitir_vazio=True)
    if categoria == "INVALIDA":
        return
    status = escolher_opcao("Situação:", STATUS, permitir_vazio=True)
    if status == "INVALIDA":
        return
    nome_cat = CATEGORIAS[categoria] if categoria else "todas"
    nome_sit = STATUS[status][0] if status else "todas"
    print(f"\nFiltro: categoria = {nome_cat} | situação = {nome_sit}")
    imprimir_tabela(filtrar(painel["ocorrencias"], categoria, status))


def tela_cadastrar(painel):
    print("\n=== CADASTRAR NOVA OCORRÊNCIA ===")
    print("Não informe nomes, telefones ou e-mails: use apenas locais genéricos.")
    categoria = escolher_opcao("Categoria:", CATEGORIAS)
    bairros = sorted({oc["bairro"] for oc in painel["ocorrencias"]})
    print("Bairros já cadastrados: " + ", ".join(bairros))
    campos = {
        "codigo": proximo_codigo(painel),
        "categoria": "" if categoria == "INVALIDA" else categoria,
        "descricao": ler_entrada("Descrição breve: "),
        "bairro": ler_entrada("Bairro: "),
        "local": ler_entrada("Local genérico (ex.: Praça Central): "),
        "dia_abertura": str(painel["dia_atual"]),
        "status": "ABERTA",      # toda demanda nova começa como aberta
    }
    erros = validar_ocorrencia(campos, painel)
    if erros:
        print("[ERRO] Cadastro não realizado:")
        for erro in erros:
            print(f"  - {erro}")
        return
    adicionar_ocorrencia(painel, campos)
    painel["fila_triagem"].append(campos["codigo"])   # entra no fim da fila
    registrar_evento(painel, campos["codigo"], painel["dia_atual"], "", "ABERTA",
                     "registro criado")
    print(f"[OK] Ocorrência {campos['codigo']} cadastrada como 'Aberta' "
          f"no dia {painel['dia_atual']} e colocada na fila de triagem.")


def tela_triagem(painel):
    print("\n=== FILA DE TRIAGEM (ordem de registro) ===")
    fila = painel["fila_triagem"]
    if not fila:
        print("A fila está vazia: não há demandas abertas aguardando exame.")
        return
    print("Na fila: " + " -> ".join(fila))
    codigo = fila[0]                       # o primeiro a entrar é o primeiro a sair
    mostrar_detalhes(painel, painel["indice"][codigo])
    resposta = normalizar(ler_entrada("\nExaminar esta ocorrência agora? (s/n): "))
    if resposta in ("S", "SIM"):
        observacao = ler_entrada("Observação (opcional): ").strip()
        ok, mensagem = atualizar_status(painel, codigo, "EM_ANALISE",
                                        observacao or "examinada na triagem")
        print(("[OK] " if ok else "[ERRO] ") + mensagem)
    else:
        print("Nada foi alterado.")


def tela_atualizar(painel):
    print("\n=== ATUALIZAR SITUAÇÃO ===")
    codigo = padronizar_codigo(ler_entrada("Código da ocorrência: "))
    if codigo not in painel["indice"]:
        print(f"[AVISO] Ocorrência '{codigo}' não encontrada.")
        return
    oc = painel["indice"][codigo]
    atual = oc["status"]
    permitidas = TRANSICOES[atual]
    print(f"Situação atual: {STATUS[atual][0]}")
    if not permitidas:
        print("[AVISO] Ocorrência concluída: a situação não pode mais ser alterada.")
        return
    opcoes = {chave: STATUS[chave] for chave in permitidas}
    novo = escolher_opcao("Mudar para:", opcoes)
    if novo == "INVALIDA":
        return
    observacao = ler_entrada("Observação (opcional): ").strip()
    ok, mensagem = atualizar_status(painel, codigo, novo, observacao)
    print(("[OK] " if ok else "[ERRO] ") + mensagem)


def tela_ultimas(painel, quantidade=5):
    print(f"\n=== ÚLTIMAS {quantidade} ATUALIZAÇÕES (pilha: mais recente primeiro) ===")
    pilha = painel["pilha_eventos"]
    if not pilha:
        print("Nenhuma atualização registrada.")
        return
    # Lê do topo para baixo sem remover nada da pilha
    for evento in reversed(pilha[-quantidade:]):
        de = STATUS[evento["status_anterior"]][0] if evento["status_anterior"] else "—"
        print(f"  dia {evento['dia']:>2} | {evento['codigo']} | {de} -> "
              f"{STATUS[evento['status_novo']][0]} | {evento['observacao']}")


def tela_hierarquia(painel):
    print("\n=== HIERARQUIA: BAIRRO -> CATEGORIA -> OCORRÊNCIAS ===")
    print("Comunidade Vale Verde")
    for bairro, categorias in sorted(montar_hierarquia(painel["ocorrencias"]).items()):
        total_bairro = sum(len(codigos) for codigos in categorias.values())
        print(f"  {bairro} ({total_bairro})")
        for categoria, codigos in categorias.items():
            print(f"      {CATEGORIAS[categoria]:<15} {', '.join(codigos)}")


def tela_indicadores(painel):
    ind = calcular_indicadores(painel)
    total = ind["total"]
    print("\n=== PAINEL DE INDICADORES ===")
    print(f"Dados de origem: {total} ocorrências válidas, dia atual = {painel['dia_atual']}")
    print("Regra: proporção (%) = quantidade / total x 100\n")

    print("Por categoria:")
    for chave, qtd in ind["por_categoria"].items():
        print(f"  {CATEGORIAS[chave]:<15} {qtd:>3}  ({percentual(qtd, total):5.1f}%)")
    print("\nPor situação:")
    for chave, qtd in ind["por_status"].items():
        print(f"  {STATUS[chave][0]:<15} {qtd:>3}  ({percentual(qtd, total):5.1f}%)")

    print("\nMatriz categoria x situação:")
    situacoes = list(STATUS)
    print(f"  {'':<15}" + "".join(f"{STATUS[s][0]:>12}" for s in situacoes) + f"{'Total':>8}")
    for i, linha in enumerate(montar_matriz(painel["ocorrencias"])):
        nome = CATEGORIAS[list(CATEGORIAS)[i]]
        print(f"  {nome:<15}" + "".join(f"{v:>12}" for v in linha) + f"{sum(linha):>8}")

    print(f"\nPendências (abertas + em análise): {ind['pendentes']}")
    tempos = ", ".join(str(t) for t in ind["tempos_conclusao"]) or "nenhum"
    print("Tempo médio até a conclusão = soma (dia de conclusão - dia de abertura) / concluídas")
    print(f"  tempos: {tempos} -> média = {ind['media_conclusao']:.1f} dias")
    print("Espera média das pendentes = soma (dia atual - dia de abertura) / pendentes")
    print(f"  média = {ind['media_pendentes']:.1f} dias")

    print("\nInterpretação:")
    for frase in interpretar(ind):
        print(f"  - {frase}")


def tela_inconsistentes(painel):
    print("\n=== REGISTROS INCONSISTENTES (não carregados) ===")
    if not painel["rejeitados"]:
        print("Nenhum registro inconsistente.")
        return
    for r in painel["rejeitados"]:
        print(f"  Linha {r['linha']} | código {r['codigo'] or '—'} | {r['descricao']}")
        for motivo in r["motivos"]:
            print(f"      motivo: {motivo}")
    print("Tratamento: o registro fica fora das contagens até ser corrigido no arquivo.")


def tela_ajuda():
    print("\n=== AJUDA: SITUAÇÕES E REGRAS ===")
    for chave, (nome, significado) in STATUS.items():
        destinos = ", ".join(STATUS[d][0] for d in TRANSICOES[chave]) or "nenhuma"
        print(f"  {nome:<11} = {significado}. Pode mudar para: {destinos}.")
    print("  Categorias: " + ", ".join(CATEGORIAS.values()) + ".")
    print("  Digite o número da opção ou o nome, com ou sem acento.")


def tela_avancar_dia(painel):
    texto = ler_entrada(f"Dia atual = {painel['dia_atual']}. Avançar quantos dias? ").strip()
    if texto.isdigit() and 1 <= int(texto) <= 30:
        painel["dia_atual"] += int(texto)
        print(f"[OK] Agora é o dia {painel['dia_atual']} da simulação.")
    else:
        print("[ERRO] Informe um número de 1 a 30.")


# ======================================================================
# 9. PROGRAMA PRINCIPAL
# ======================================================================

MENU = (
    ("1", "Listar todas as ocorrências", tela_listar),
    ("2", "Buscar ocorrência por código", tela_buscar),
    ("3", "Filtrar por categoria e/ou situação", tela_filtrar),
    ("4", "Cadastrar nova ocorrência", tela_cadastrar),
    ("5", "Triagem: examinar a próxima da fila", tela_triagem),
    ("6", "Atualizar a situação de uma ocorrência", tela_atualizar),
    ("7", "Ver últimas atualizações", tela_ultimas),
    ("8", "Ver hierarquia bairro -> categoria", tela_hierarquia),
    ("9", "Painel de indicadores", tela_indicadores),
    ("10", "Ver registros inconsistentes", tela_inconsistentes),
    ("11", "Avançar o dia da simulação", tela_avancar_dia),
    ("12", "Ajuda: situações e regras", None),
)


def main():
    painel = carregar_dados()
    print("=" * 60)
    print("  NEIGHBORHOOD ACTION DASHBOARD - Comunidade Vale Verde")
    print("=" * 60)
    print(f"{len(painel['ocorrencias'])} ocorrências carregadas, "
          f"{len(painel['historico'])} eventos no histórico, "
          f"{len(painel['rejeitados'])} registro(s) inconsistente(s) separado(s).")

    while True:
        print(f"\n--- MENU (dia {painel['dia_atual']}) ---")
        for numero, texto, _ in MENU:
            print(f"{numero:>3}) {texto}")
        print("  0) Sair")
        opcao = ler_entrada("Opção: ").strip()

        if opcao == "0":
            print("Até logo! Obrigado por acompanhar as demandas da comunidade.")
            break
        elif opcao == "12":
            tela_ajuda()
        else:
            funcao = None
            for numero, _, acao in MENU:
                if numero == opcao:
                    funcao = acao
            if funcao is None:
                print("[ERRO] Opção inválida. Digite um número do menu.")
            else:
                funcao(painel)


if __name__ == "__main__":
    main()
