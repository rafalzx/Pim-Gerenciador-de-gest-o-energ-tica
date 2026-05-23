"""
╔══════════════════════════════════════════════════════════╗
║         ECOTECH MONITOR — SOFTWARE HOUSE VERDE           ║
║     Sistema de Gestão de Consumo Energético de TI        ║
╠══════════════════════════════════════════════════════════╣
║  PIM — 1º Semestre de Análise e Desenvolvimento          ║
║                                                          ║
║  PROBLEMA IDENTIFICADO:                                  ║
║  A empresa não possui controle do consumo de energia     ║
║  dos seus servidores e estações de trabalho, gerando     ║
║  custos elevados, emissão desnecessária de CO₂ e         ║
║  ausência de dados para decisões sustentáveis.           ║
║                                                          ║
║  SOLUÇÃO:                                                ║
║  Sistema que monitora, registra e analisa o consumo,     ║
║  gera alertas éticos e sugere ações de melhoria.         ║
╚══════════════════════════════════════════════════════════╝
"""

import json        # Leitura e gravação de dados em formato JSON
import os          # Operações com arquivos e sistema operacional
import datetime    # Manipulação de datas e horários
import random      # Simulação de leituras de sensores (ambiente demo)
import statistics  # Funções estatísticas nativas do Python

# ============================================================
# CONSTANTES — valores fixos que definem as regras do sistema
# ============================================================

ARQUIVO_SERVIDORES  = "servidores.json"   # Cadastro dos servidores
ARQUIVO_LEITURAS    = "leituras.json"     # Histórico de leituras de consumo
ARQUIVO_ALERTAS     = "alertas.json"      # Histórico de alertas emitidos

TARIFA_KWH          = 0.75    # Tarifa de energia em R$/kWh (média Brasil 2024)
META_MENSAL_KWH     = 2000.0  # Meta de consumo mensal da empresa em kWh
LIMITE_ALERTA_W     = 400.0   # Acima deste consumo (Watts), emite alerta por servidor
CO2_POR_KWH         = 0.0817  # kg de CO₂ emitido por kWh (fator MCTIC Brasil)
NOME_EMPRESA        = "EcoTech Software House"
VERSAO              = "2.1.0"


# ============================================================
# FUNÇÕES DE ARQUIVO — gravação e leitura de dados
# ============================================================

def carregar_dados(caminho):
    """
    Lê um arquivo JSON do disco e retorna os dados.
    Caso o arquivo não exista ou esteja corrompido,
    retorna uma lista vazia para não travar o sistema.
    """
    # Verifica se o arquivo existe antes de tentar abrir
    if not os.path.exists(caminho):
        return []  # Primeira execução: retorna lista vazia

    with open(caminho, "r", encoding="utf-8") as f:
        try:
            return json.load(f)       # Converte JSON → objeto Python
        except json.JSONDecodeError:
            # Arquivo corrompido: avisa e retorna lista vazia
            print(f"  [AVISO] Arquivo '{caminho}' corrompido. Iniciando zerado.")
            return []


def salvar_dados(caminho, dados):
    """
    Grava qualquer lista ou dicionário Python em um arquivo JSON.
    indent=4 formata o arquivo de forma legível para humanos.
    ensure_ascii=False preserva acentos e caracteres especiais.
    """
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


# ============================================================
# FUNÇÕES UTILITÁRIAS — ferramentas usadas em todo o sistema
# ============================================================

def limpar_tela():
    """Limpa o terminal: 'cls' no Windows, 'clear' no Linux/Mac."""
    os.system("cls" if os.name == "nt" else "clear")


def linha(char="═", tam=58):
    """Imprime uma linha decorativa de separação."""
    print("  " + char * tam)


def pausar():
    """Aguarda ENTER do usuário antes de continuar."""
    input("\n  Pressione ENTER para continuar...")


def agora():
    """Retorna data e hora atual formatada como string."""
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M")


def so_data():
    """Retorna apenas a data de hoje no formato DD/MM/AAAA."""
    return datetime.date.today().strftime("%d/%m/%Y")


def mes_atual():
    """Retorna o mês e ano atuais no formato MM/AAAA."""
    return datetime.date.today().strftime("%m/%Y")


def gerar_id(lista):
    """
    Gera um ID inteiro único e sequencial.
    Percorre a lista e retorna o maior ID encontrado + 1.
    Se a lista estiver vazia, começa do 1.
    """
    if not lista:
        return 1                           # Lista vazia: começa do 1

    maior = 0
    for item in lista:                     # Estrutura de repetição
        if item["id"] > maior:
            maior = item["id"]

    return maior + 1                       # Próximo ID disponível


def watts_para_kwh(watts, horas):
    """
    Converte Watts consumidos em um período para kWh.
    Fórmula: kWh = (W × h) ÷ 1000
    """
    return (watts * horas) / 1000.0


def calcular_co2(kwh):
    """
    Calcula a emissão de CO₂ (em kg) equivalente
    a um consumo em kWh, usando o fator de emissão
    da matriz elétrica brasileira (MCTIC).
    """
    return kwh * CO2_POR_KWH


def calcular_custo(kwh):
    """Calcula o custo em reais dado um consumo em kWh."""
    return kwh * TARIFA_KWH


def classificar_consumo(watts):
    """
    Classifica o nível de consumo de um servidor
    com base nos Watts medidos. Retorna uma string
    com a classificação e um ícone visual.

    Estrutura condicional em cascata (if/elif/else).
    """
    if watts <= 150:
        return "🟢 ÓTIMO"       # Consumo muito baixo
    elif watts <= 250:
        return "🟡 NORMAL"      # Consumo dentro do esperado
    elif watts <= LIMITE_ALERTA_W:
        return "🟠 ELEVADO"     # Atenção necessária
    else:
        return "🔴 CRÍTICO"     # Requer ação imediata


# ============================================================
# FUNÇÕES DE SERVIDORES — cadastro e gerenciamento
# ============================================================

def listar_servidores(servidores):
    """
    Exibe todos os servidores cadastrados em formato tabular.
    Para cada servidor mostra: ID, nome, tipo, localização e status.
    """
    limpar_tela()
    linha()
    print(f"  {NOME_EMPRESA} — Servidores Cadastrados")
    linha()

    # Verifica se há servidores antes de tentar listar
    if not servidores:
        print("  Nenhum servidor cadastrado ainda.")
        print("  Use a opção [2] para cadastrar.")
        pausar()
        return

    # Cabeçalho da tabela
    print(f"  {'ID':<4} {'Nome':<20} {'Tipo':<16} {'Local':<14} {'Status'}")
    linha("─")

    # Estrutura de repetição: percorre todos os servidores
    for srv in servidores:
        status = "✔ Ativo" if srv["ativo"] else "✖ Inativo"
        print(
            f"  {srv['id']:<4} "
            f"{srv['nome']:<20} "
            f"{srv['tipo']:<16} "
            f"{srv['local']:<14} "
            f"{status}"
        )

    linha()
    print(f"  Total: {len(servidores)} servidor(es) | "
          f"Ativos: {sum(1 for s in servidores if s['ativo'])}")
    pausar()


def cadastrar_servidor(servidores):
    """
    Coleta dados de um novo servidor via terminal e
    cria um dicionário com todas as informações.
    Persiste os dados no arquivo JSON ao final.
    """
    limpar_tela()
    linha()
    print("  Cadastrar Novo Servidor")
    linha()

    # Coleta os dados do servidor
    nome       = input("  Nome do servidor (ex: SRV-PROD-01) : ").strip()
    tipo       = input("  Tipo (Web / Banco / Aplicação / CI) : ").strip()
    local      = input("  Localização (ex: Rack A / Nuvem)    : ").strip()
    consumo_s  = input("  Consumo base estimado (Watts)        : ").strip()

    # Validação: campos obrigatórios não podem estar vazios
    if not nome or not tipo:
        print("\n  [ERRO] Nome e Tipo são obrigatórios.")
        pausar()
        return servidores

    # Validação: consumo deve ser numérico
    if not consumo_s.replace(".", "").isdigit():
        print("\n  [ERRO] Consumo deve ser um número. Ex: 250 ou 350.5")
        pausar()
        return servidores

    # Criação do dicionário do servidor
    # Cada servidor é representado por um dicionário Python
    novo = {
        "id"             : gerar_id(servidores),
        "nome"           : nome,
        "tipo"           : tipo if tipo else "Não informado",
        "local"          : local if local else "Não informado",
        "consumo_base_w" : float(consumo_s),   # Consumo padrão em Watts
        "ativo"          : True,               # Começa ativo ao ser cadastrado
        "data_cadastro"  : agora()
    }

    servidores.append(novo)                        # Adiciona à lista
    salvar_dados(ARQUIVO_SERVIDORES, servidores)   # Grava no arquivo

    print(f"\n  ✔ Servidor '{nome}' cadastrado! (ID: {novo['id']})")
    pausar()
    return servidores


def alternar_status(servidores):
    """
    Ativa ou desativa um servidor pelo ID.
    Servidores inativos não são incluídos nas leituras de consumo.
    Isso permite simular desligamento planejado (manutenção, fim de projeto).
    """
    limpar_tela()
    linha()
    print("  Ativar / Desativar Servidor")
    linha()

    entrada = input("  ID do servidor: ").strip()

    # Valida se a entrada é um número inteiro
    if not entrada.isdigit():
        print("\n  [ERRO] ID deve ser um número inteiro.")
        pausar()
        return servidores

    id_alvo = int(entrada)
    alvo    = None

    # Busca o servidor pelo ID na lista
    for srv in servidores:               # Estrutura de repetição
        if srv["id"] == id_alvo:
            alvo = srv
            break

    if alvo is None:
        print(f"\n  [ERRO] Servidor ID {id_alvo} não encontrado.")
        pausar()
        return servidores

    # Inverte o status: True → False ou False → True
    alvo["ativo"] = not alvo["ativo"]
    novo_status   = "ATIVADO" if alvo["ativo"] else "DESATIVADO"

    salvar_dados(ARQUIVO_SERVIDORES, servidores)

    print(f"\n  ✔ Servidor '{alvo['nome']}' foi {novo_status}.")
    pausar()
    return servidores


# ============================================================
# FUNÇÕES DE LEITURAS — registro e simulação de consumo
# ============================================================

def registrar_leitura_manual(servidores, leituras, alertas):
    """
    Permite registrar manualmente o consumo medido
    de um servidor em um determinado momento.
    Após registrar, verifica automaticamente se
    o consumo ultrapassa o limite de alerta.
    """
    limpar_tela()
    linha()
    print("  Registrar Leitura de Consumo")
    linha()

    # Lista apenas servidores ativos para seleção
    ativos = [s for s in servidores if s["ativo"]]  # List comprehension

    if not ativos:
        print("  Nenhum servidor ativo para registrar leitura.")
        pausar()
        return leituras, alertas

    # Exibe servidores ativos disponíveis
    print("  Servidores ativos:\n")
    for srv in ativos:
        print(f"    [{srv['id']}] {srv['nome']} — base: {srv['consumo_base_w']}W")

    print()
    entrada_id = input("  ID do servidor: ").strip()
    entrada_w  = input("  Consumo medido (Watts): ").strip()
    entrada_h  = input("  Horas no período (ex: 1, 8, 24): ").strip()

    # Validações de entrada
    if not entrada_id.isdigit():
        print("\n  [ERRO] ID inválido.")
        pausar()
        return leituras, alertas

    if not entrada_w.replace(".", "").isdigit():
        print("\n  [ERRO] Watts deve ser um número.")
        pausar()
        return leituras, alertas

    if not entrada_h.replace(".", "").isdigit():
        print("\n  [ERRO] Horas deve ser um número.")
        pausar()
        return leituras, alertas

    id_srv = int(entrada_id)
    watts  = float(entrada_w)
    horas  = float(entrada_h)

    # Busca o servidor pelo ID
    servidor_alvo = None
    for srv in ativos:
        if srv["id"] == id_srv:
            servidor_alvo = srv
            break

    if servidor_alvo is None:
        print(f"\n  [ERRO] Servidor ID {id_srv} não encontrado.")
        pausar()
        return leituras, alertas

    # Calcula métricas derivadas
    kwh    = watts_para_kwh(watts, horas)
    co2    = calcular_co2(kwh)
    custo  = calcular_custo(kwh)
    nivel  = classificar_consumo(watts)

    # Cria o dicionário da leitura
    nova_leitura = {
        "id"            : gerar_id(leituras),
        "id_servidor"   : id_srv,
        "nome_servidor" : servidor_alvo["nome"],
        "watts"         : watts,
        "horas"         : horas,
        "kwh"           : round(kwh, 4),
        "co2_kg"        : round(co2, 4),
        "custo_reais"   : round(custo, 4),
        "nivel"         : nivel,
        "data"          : agora(),
        "mes"           : mes_atual()
    }

    leituras.append(nova_leitura)
    salvar_dados(ARQUIVO_LEITURAS, leituras)

    # Exibe o resumo da leitura registrada
    print(f"\n  ✔ Leitura registrada com sucesso!")
    print(f"  Servidor : {servidor_alvo['nome']}")
    print(f"  Consumo  : {watts}W por {horas}h = {kwh:.3f} kWh")
    print(f"  CO₂      : {co2:.4f} kg")
    print(f"  Custo    : R$ {custo:.4f}")
    print(f"  Nível    : {nivel}")

    # Verifica se deve emitir alerta de consumo elevado
    if watts > LIMITE_ALERTA_W:
        alertas = emitir_alerta(
            alertas,
            servidor_alvo["nome"],
            watts,
            f"Consumo de {watts}W supera o limite de {LIMITE_ALERTA_W}W"
        )

    pausar()
    return leituras, alertas


def simular_leituras_automaticas(servidores, leituras, alertas):
    """
    Simula uma rodada de leituras automáticas para todos
    os servidores ativos, como se fossem sensores reais.

    Em um ambiente real, este código seria substituído por
    chamadas a APIs de monitoramento (Zabbix, Prometheus, etc.).

    Usa random para variar o consumo em ±30% do valor base,
    simulando picos e quedas normais de uso.
    """
    limpar_tela()
    linha()
    print("  Simulação de Leituras Automáticas")
    linha()

    ativos = [s for s in servidores if s["ativo"]]

    if not ativos:
        print("  Nenhum servidor ativo para simular.")
        pausar()
        return leituras, alertas

    print(f"  Simulando leituras para {len(ativos)} servidor(es)...\n")

    # Período simulado: 1 hora de operação por leitura
    horas_simuladas = 1.0

    # Estrutura de repetição: gera uma leitura por servidor ativo
    for srv in ativos:
        base  = srv["consumo_base_w"]

        # Variação aleatória de ±30% do consumo base
        # Simula cargas variáveis (deploy, compilação, inatividade)
        variacao = random.uniform(0.70, 1.30)
        watts    = round(base * variacao, 1)

        kwh   = watts_para_kwh(watts, horas_simuladas)
        co2   = calcular_co2(kwh)
        custo = calcular_custo(kwh)
        nivel = classificar_consumo(watts)

        # Cria e salva a leitura simulada
        leitura = {
            "id"            : gerar_id(leituras),
            "id_servidor"   : srv["id"],
            "nome_servidor" : srv["nome"],
            "watts"         : watts,
            "horas"         : horas_simuladas,
            "kwh"           : round(kwh, 4),
            "co2_kg"        : round(co2, 4),
            "custo_reais"   : round(custo, 4),
            "nivel"         : nivel,
            "data"          : agora(),
            "mes"           : mes_atual()
        }

        leituras.append(leitura)

        # Feedback visual imediato durante a simulação
        print(f"  {srv['nome']:<22} → {watts:>6.1f}W  {nivel}")

        # Alerta automático se consumo for crítico
        if watts > LIMITE_ALERTA_W:
            alertas = emitir_alerta(
                alertas,
                srv["nome"],
                watts,
                f"Pico de consumo detectado: {watts}W"
            )

    # Salva todas as leituras de uma só vez (mais eficiente)
    salvar_dados(ARQUIVO_LEITURAS, leituras)

    print(f"\n  ✔ {len(ativos)} leitura(s) registrada(s) em {agora()}")
    pausar()
    return leituras, alertas


# ============================================================
# FUNÇÕES DE ALERTAS — ética e responsabilidade ambiental
# ============================================================

def emitir_alerta(alertas, nome_servidor, watts, motivo):
    """
    Registra um alerta de consumo elevado no sistema.
    Os alertas são a camada ética do sistema: informam
    os gestores sobre comportamentos que violam as metas
    ambientais da empresa, permitindo ação corretiva.
    """
    novo_alerta = {
        "id"           : gerar_id(alertas),
        "servidor"     : nome_servidor,
        "watts"        : watts,
        "motivo"       : motivo,
        "data"         : agora(),
        "resolvido"    : False   # Alerta aberto até ser tratado
    }

    alertas.append(novo_alerta)
    salvar_dados(ARQUIVO_ALERTAS, alertas)

    # Exibe o alerta em destaque no terminal
    print(f"\n  ⚠  ALERTA #{novo_alerta['id']} — {nome_servidor}")
    print(f"     {motivo}")

    return alertas


def listar_alertas(alertas):
    """
    Exibe todos os alertas registrados, mostrando
    quais ainda estão em aberto e quais foram resolvidos.
    Alertas em aberto representam riscos ambientais ativos.
    """
    limpar_tela()
    linha()
    print(f"  {NOME_EMPRESA} — Central de Alertas")
    linha()

    if not alertas:
        print("  Nenhum alerta registrado. Sistema operando normalmente.")
        pausar()
        return alertas

    # Separa alertas abertos e resolvidos usando list comprehension
    abertos    = [a for a in alertas if not a["resolvido"]]
    resolvidos = [a for a in alertas if a["resolvido"]]

    print(f"  Abertos: {len(abertos)}  |  Resolvidos: {len(resolvidos)}\n")

    print(f"  {'ID':<4} {'Servidor':<22} {'Watts':<8} {'Status':<12} {'Data'}")
    linha("─")

    for alerta in alertas:    # Estrutura de repetição
        status = "✔ Resolvido" if alerta["resolvido"] else "⚠ Em aberto"
        print(
            f"  {alerta['id']:<4} "
            f"{alerta['servidor']:<22} "
            f"{alerta['watts']:<8} "
            f"{status:<12} "
            f"{alerta['data']}"
        )
        print(f"       → {alerta['motivo']}")

    linha()

    # Opção de marcar alerta como resolvido
    if abertos:
        opcao = input("\n  Marcar alerta como resolvido? (ID ou ENTER para pular): ").strip()
        if opcao.isdigit():
            id_alvo = int(opcao)
            for alerta in alertas:
                if alerta["id"] == id_alvo:
                    alerta["resolvido"] = True
                    salvar_dados(ARQUIVO_ALERTAS, alertas)
                    print(f"\n  ✔ Alerta #{id_alvo} marcado como resolvido.")
                    break

    pausar()
    return alertas


# ============================================================
# FUNÇÕES ESTATÍSTICAS — análise de dados de consumo
# ============================================================

def relatorio_estatistico(servidores, leituras):
    """
    Gera um relatório completo com estatísticas de consumo.
    Usa o módulo 'statistics' para cálculos de média,
    mediana e desvio padrão — demonstrando uso de biblioteca
    nativa do Python para análise de dados reais.

    O relatório aborda:
    - Visão geral do consumo total
    - Métricas por servidor (ranking)
    - Comparação com a meta mensal
    - Impacto ambiental (CO₂) e financeiro
    - Distribuição por nível de consumo
    """
    limpar_tela()
    linha()
    print(f"  {NOME_EMPRESA}")
    print(f"  Relatório Estatístico de Consumo Energético")
    print(f"  Gerado em: {agora()}")
    linha()

    # Filtra apenas leituras do mês atual para análise
    leituras_mes = [l for l in leituras if l["mes"] == mes_atual()]

    if not leituras_mes:
        print("  Sem leituras registradas neste mês.")
        print("  Use 'Simular leituras' para gerar dados de exemplo.")
        pausar()
        return

    # ── BLOCO 1: Visão Geral ──────────────────────────────────
    total_kwh    = sum(l["kwh"]         for l in leituras_mes)
    total_co2    = sum(l["co2_kg"]      for l in leituras_mes)
    total_custo  = sum(l["custo_reais"] for l in leituras_mes)
    total_leit   = len(leituras_mes)

    # Extrai lista de valores de Watts para cálculos estatísticos
    lista_watts = [l["watts"] for l in leituras_mes]

    # Cálculos estatísticos usando o módulo statistics
    media_w   = statistics.mean(lista_watts)      # Média aritmética
    mediana_w = statistics.median(lista_watts)    # Mediana (valor central)
    # Desvio padrão: só calculável com 2+ valores
    desvio_w  = statistics.stdev(lista_watts) if len(lista_watts) >= 2 else 0

    print(f"\n  ┌─ RESUMO DO MÊS ({mes_atual()}) ─────────────────────┐")
    print(f"  │  Leituras registradas : {total_leit:<6}               │")
    print(f"  │  Consumo total        : {total_kwh:<8.2f} kWh         │")
    print(f"  │  Emissão de CO₂       : {total_co2:<8.4f} kg          │")
    print(f"  │  Custo estimado       : R$ {total_custo:<8.2f}         │")
    print(f"  └────────────────────────────────────────────────┘")

    # ── BLOCO 2: Estatísticas de Watts ────────────────────────
    print(f"\n  ESTATÍSTICAS DE CONSUMO (Watts)")
    linha("─")
    print(f"  Média       : {media_w:>8.1f} W")
    print(f"  Mediana     : {mediana_w:>8.1f} W")
    print(f"  Desvio pad. : {desvio_w:>8.1f} W  (variação do consumo)")
    print(f"  Mínimo      : {min(lista_watts):>8.1f} W")
    print(f"  Máximo      : {max(lista_watts):>8.1f} W")

    # ── BLOCO 3: Comparação com a meta mensal ─────────────────
    print(f"\n  COMPARAÇÃO COM A META MENSAL")
    linha("─")
    percentual = (total_kwh / META_MENSAL_KWH) * 100

    # Barra de progresso visual
    barras_cheias = int(percentual / 5)          # Cada bloco = 5%
    barras_cheias = min(barras_cheias, 20)        # Limita a 20 blocos
    barra = "█" * barras_cheias + "░" * (20 - barras_cheias)

    print(f"  Meta       : {META_MENSAL_KWH:.0f} kWh/mês")
    print(f"  Consumido  : {total_kwh:.2f} kWh ({percentual:.1f}%)")
    print(f"  [{barra}] {percentual:.0f}%")

    # Estrutura condicional: avalia situação em relação à meta
    if percentual <= 70:
        print(f"\n  ✔ META CONFORTÁVEL — consumo excelente!")
    elif percentual <= 100:
        print(f"\n  ⚠ ATENÇÃO — dentro da meta, mas monitorar.")
    elif percentual <= 130:
        print(f"\n  ✖ META SUPERADA em {percentual - 100:.1f}% — redução necessária.")
    else:
        print(f"\n  🔴 CRÍTICO — consumo {percentual - 100:.1f}% acima da meta!")

    # ── BLOCO 4: Ranking por servidor ─────────────────────────
    print(f"\n  RANKING DE CONSUMO POR SERVIDOR")
    linha("─")

    # Dicionário para acumular kWh por servidor
    consumo_por_srv = {}    # Chave: nome do servidor, Valor: kWh acumulado

    for leitura in leituras_mes:                    # Estrutura de repetição
        nome = leitura["nome_servidor"]
        if nome in consumo_por_srv:
            consumo_por_srv[nome] += leitura["kwh"]  # Acumula se já existe
        else:
            consumo_por_srv[nome]  = leitura["kwh"]  # Cria nova entrada

    # Ordena o dicionário por valor (kWh) em ordem decrescente
    ranking = sorted(consumo_por_srv.items(), key=lambda x: x[1], reverse=True)

    print(f"  {'#':<3} {'Servidor':<22} {'kWh':>8}  {'Custo':>10}  {'CO₂ (kg)'}")
    linha("─")

    posicao = 1
    for nome, kwh in ranking:          # Percorre o ranking ordenado
        custo_srv = calcular_custo(kwh)
        co2_srv   = calcular_co2(kwh)
        medalha   = ["🥇", "🥈", "🥉"].pop(0) if posicao <= 3 else f" {posicao}."

        print(
            f"  {medalha:<3} {nome:<22} "
            f"{kwh:>8.3f}  "
            f"R$ {custo_srv:>7.2f}  "
            f"{co2_srv:.4f} kg"
        )
        posicao += 1

    # ── BLOCO 5: Distribuição por nível de consumo ────────────
    print(f"\n  DISTRIBUIÇÃO POR NÍVEL DE CONSUMO")
    linha("─")

    # Dicionário de contagem por nível
    niveis = {
        "🟢 ÓTIMO"   : 0,
        "🟡 NORMAL"  : 0,
        "🟠 ELEVADO" : 0,
        "🔴 CRÍTICO" : 0
    }

    for leitura in leituras_mes:          # Conta ocorrências por nível
        nivel = leitura["nivel"]
        for chave in niveis:              # Verifica a chave correta
            if chave in nivel:
                niveis[chave] += 1
                break

    for nivel, qtd in niveis.items():    # Exibe resultado
        if total_leit > 0:
            pct = (qtd / total_leit) * 100
        else:
            pct = 0
        barra_nivel = "█" * int(pct / 5)
        print(f"  {nivel:<14}: {qtd:>3} ({pct:5.1f}%)  {barra_nivel}")

    # ── BLOCO 6: Impacto ambiental equivalente ─────────────────
    print(f"\n  IMPACTO AMBIENTAL — EQUIVALÊNCIAS")
    linha("─")
    # Dados de referência para comunicar o impacto de forma humana
    arvores_eq  = total_co2 / 21.77    # 1 árvore absorve ~21,77 kg CO₂/ano
    km_carro_eq = total_co2 / 0.21     # Carro médio emite ~0,21 kg CO₂/km

    print(f"  {total_co2:.4f} kg de CO₂ emitidos equivalem a:")
    print(f"  • {arvores_eq:.3f} árvores necessárias para compensar (1 ano)")
    print(f"  • {km_carro_eq:.1f} km percorridos por um carro a gasolina")

    linha()
    pausar()


# ============================================================
# FUNÇÕES DE SUGESTÕES — recomendações de sustentabilidade
# ============================================================

def sugestoes_melhoria(servidores, leituras, alertas):
    """
    Analisa os dados coletados e apresenta sugestões
    concretas de melhoria, baseadas em boas práticas de
    green computing e infraestrutura sustentável.

    Esta seção representa a dimensão ÉTICA do sistema:
    a empresa não apenas monitora, mas age com responsabilidade
    ambiental baseada em dados reais.
    """
    limpar_tela()
    linha()
    print(f"  {NOME_EMPRESA}")
    print(f"  Recomendações de Sustentabilidade")
    linha()

    leituras_mes  = [l for l in leituras if l["mes"] == mes_atual()]
    alertas_abertos = [a for a in alertas if not a["resolvido"]]

    if not leituras_mes:
        print("  Sem dados suficientes para gerar recomendações.")
        print("  Registre leituras de consumo primeiro.")
        pausar()
        return

    lista_watts   = [l["watts"]    for l in leituras_mes]
    media_w       = statistics.mean(lista_watts)
    total_kwh     = sum(l["kwh"]   for l in leituras_mes)
    percentual    = (total_kwh / META_MENSAL_KWH) * 100

    # Lista de recomendações — estrutura de dados do tipo lista de dicionários
    recomendacoes = []

    # Regra 1: média de consumo acima de 300W
    if media_w > 300:
        recomendacoes.append({
            "prioridade" : "ALTA",
            "area"       : "Infraestrutura",
            "titulo"     : "Revisar configuração de hardware",
            "descricao"  : (
                f"Média de {media_w:.0f}W está acima do ideal. "
                "Verifique servidores ociosos e considere virtualização "
                "para consolidar cargas de trabalho em menos máquinas."
            ),
            "impacto"    : "Redução de até 40% no consumo"
        })

    # Regra 2: meta mensal ultrapassada
    if percentual > 100:
        recomendacoes.append({
            "prioridade" : "ALTA",
            "area"       : "Gestão",
            "titulo"     : "Implementar política de desligamento agendado",
            "descricao"  : (
                "Meta mensal superada. Servidores de desenvolvimento podem "
                "ser desligados fora do horário comercial (18h–8h) e "
                "nos finais de semana, reduzindo horas ativas."
            ),
            "impacto"    : f"Economia de até R$ {calcular_custo(total_kwh * 0.30):.2f}/mês"
        })

    # Regra 3: há alertas em aberto
    if alertas_abertos:
        recomendacoes.append({
            "prioridade" : "MÉDIA",
            "area"       : "Monitoramento",
            "titulo"     : f"Tratar {len(alertas_abertos)} alerta(s) em aberto",
            "descricao"  : (
                "Alertas de consumo elevado indicam picos não gerenciados. "
                "Investigue se há processos travados, vazamentos de memória "
                "ou cargas mal distribuídas nesses servidores."
            ),
            "impacto"    : "Redução de picos e maior estabilidade"
        })

    # Regra 4: sugestão sempre presente (boas práticas gerais)
    recomendacoes.append({
        "prioridade" : "BAIXA",
        "area"       : "Sustentabilidade",
        "titulo"     : "Migrar para energia renovável",
        "descricao"  : (
            "Contratar fornecimento de energia certificada (Selo I-REC) "
            "ou instalar painéis solares no datacenter reduz a pegada "
            "de carbono sem alterar o consumo em kWh."
        ),
        "impacto"    : "Emissão de CO₂ próxima de zero"
    })

    recomendacoes.append({
        "prioridade" : "BAIXA",
        "area"       : "Ética Corporativa",
        "titulo"     : "Publicar relatório ambiental anual",
        "descricao"  : (
            "Divulgar os dados de consumo e as metas cumpridas reforça "
            "o compromisso ESG da empresa, agrega valor à marca e "
            "atende exigências de grandes clientes corporativos."
        ),
        "impacto"    : "Diferencial competitivo e reputacional"
    })

    # Exibe as recomendações em ordem de prioridade
    icones = {"ALTA": "🔴", "MÉDIA": "🟡", "BAIXA": "🟢"}
    contador = 1

    for rec in recomendacoes:          # Estrutura de repetição
        icone = icones.get(rec["prioridade"], "•")
        print(f"\n  {icone} [{rec['prioridade']}] #{contador} — {rec['titulo']}")
        print(f"     Área    : {rec['area']}")
        print(f"     Ação    : {rec['descricao']}")
        print(f"     Impacto : {rec['impacto']}")
        contador += 1

    linha()
    print(f"  {len(recomendacoes)} recomendação(ões) gerada(s) com base nos dados atuais.")
    pausar()


# ============================================================
# POPULAR DADOS — ambiente de demonstração para apresentação
# ============================================================

def popular_demonstracao(servidores, leituras, alertas):
    """
    Popula o sistema com dados realistas para demonstração.
    Simula uma software house com 5 servidores típicos
    e um histórico de leituras variadas, incluindo
    situações normais, alertas e consumo crítico.

    Só executa se o sistema estiver vazio (primeira carga).
    """
    if servidores:
        print("\n  [AVISO] Sistema já possui dados. Operação ignorada.")
        pausar()
        return servidores, leituras, alertas

    # Lista de servidores de uma software house típica
    servidores = [
        {"id": 1, "nome": "SRV-WEB-01",   "tipo": "Web / Frontend",   "local": "Rack A",  "consumo_base_w": 220.0, "ativo": True,  "data_cadastro": agora()},
        {"id": 2, "nome": "SRV-API-02",   "tipo": "Backend / API",    "local": "Rack A",  "consumo_base_w": 310.0, "ativo": True,  "data_cadastro": agora()},
        {"id": 3, "nome": "SRV-DB-01",    "tipo": "Banco de Dados",   "local": "Rack B",  "consumo_base_w": 380.0, "ativo": True,  "data_cadastro": agora()},
        {"id": 4, "nome": "SRV-CI-CD",    "tipo": "CI/CD / Build",    "local": "Rack B",  "consumo_base_w": 450.0, "ativo": True,  "data_cadastro": agora()},
        {"id": 5, "nome": "SRV-HOMOLOG",  "tipo": "Homologação",      "local": "Rack C",  "consumo_base_w": 190.0, "ativo": False, "data_cadastro": agora()},
    ]

    # Gera leituras históricas variadas para cada servidor ativo
    id_leitura = 1
    for srv in servidores:
        if not srv["ativo"]:
            continue                  # Pula servidores inativos

        # Gera entre 4 e 7 leituras por servidor
        qtd_leituras = random.randint(4, 7)

        for _ in range(qtd_leituras):    # Estrutura de repetição
            variacao = random.uniform(0.65, 1.40)
            watts    = round(srv["consumo_base_w"] * variacao, 1)
            horas    = random.choice([1.0, 4.0, 8.0, 12.0])
            kwh      = watts_para_kwh(watts, horas)

            leituras.append({
                "id"            : id_leitura,
                "id_servidor"   : srv["id"],
                "nome_servidor" : srv["nome"],
                "watts"         : watts,
                "horas"         : horas,
                "kwh"           : round(kwh, 4),
                "co2_kg"        : round(calcular_co2(kwh), 4),
                "custo_reais"   : round(calcular_custo(kwh), 4),
                "nivel"         : classificar_consumo(watts),
                "data"          : agora(),
                "mes"           : mes_atual()
            })
            id_leitura += 1

            # Alerta para leituras críticas
            if watts > LIMITE_ALERTA_W:
                alertas.append({
                    "id"        : gerar_id(alertas),
                    "servidor"  : srv["nome"],
                    "watts"     : watts,
                    "motivo"    : f"Pico detectado na simulação histórica: {watts}W",
                    "data"      : agora(),
                    "resolvido" : random.choice([True, False])  # Alguns já resolvidos
                })

    # Grava todos os dados nos arquivos JSON
    salvar_dados(ARQUIVO_SERVIDORES, servidores)
    salvar_dados(ARQUIVO_LEITURAS,   leituras)
    salvar_dados(ARQUIVO_ALERTAS,    alertas)

    print(f"\n  ✔ Ambiente de demonstração carregado!")
    print(f"  Servidores: {len(servidores)} | Leituras: {len(leituras)} | Alertas: {len(alertas)}")
    pausar()
    return servidores, leituras, alertas


# ============================================================
# MENUS DE NAVEGAÇÃO
# ============================================================

def menu_servidores(servidores, leituras, alertas):
    """Submenu de gerenciamento de servidores."""
    while True:
        limpar_tela()
        linha()
        print(f"  Gerenciar Servidores")
        linha()
        print("  [1] Listar servidores")
        print("  [2] Cadastrar servidor")
        print("  [3] Ativar / Desativar servidor")
        print("  [0] Voltar")
        linha()

        op = input("  Opção: ").strip()

        if op == "1":
            listar_servidores(servidores)
        elif op == "2":
            servidores = cadastrar_servidor(servidores)
        elif op == "3":
            servidores = alternar_status(servidores)
        elif op == "0":
            break
        else:
            print("\n  [ERRO] Opção inválida.")
            pausar()

    return servidores


def menu_leituras(servidores, leituras, alertas):
    """Submenu de registro de leituras de consumo."""
    while True:
        limpar_tela()
        linha()
        print(f"  Registrar Consumo")
        linha()
        print("  [1] Registrar leitura manual")
        print("  [2] Simular leituras automáticas (demo)")
        print("  [0] Voltar")
        linha()

        op = input("  Opção: ").strip()

        if op == "1":
            leituras, alertas = registrar_leitura_manual(servidores, leituras, alertas)
        elif op == "2":
            leituras, alertas = simular_leituras_automaticas(servidores, leituras, alertas)
        elif op == "0":
            break
        else:
            print("\n  [ERRO] Opção inválida.")
            pausar()

    return leituras, alertas


def menu_principal():
    """
    Ponto central do sistema.
    Carrega os dados persistidos e mantém o loop
    principal do programa ativo até o usuário sair.
    """
    # Carrega dados dos arquivos JSON (ou listas vazias)
    servidores  = carregar_dados(ARQUIVO_SERVIDORES)
    leituras    = carregar_dados(ARQUIVO_LEITURAS)
    alertas     = carregar_dados(ARQUIVO_ALERTAS)

    while True:    # Loop principal — mantém o programa rodando
        limpar_tela()
        linha("═")
        print(f"  ⚡ {NOME_EMPRESA}")
        print(f"     EcoTech Monitor  v{VERSAO}")
        linha("═")
        print("  [1] Gerenciar Servidores")
        print("  [2] Registrar Consumo")
        print("  [3] Central de Alertas")
        print("  [4] Relatório Estatístico")
        print("  [5] Sugestões de Melhoria")
        print("  [6] Carregar dados de demonstração")
        print("  [0] Sair")
        linha()

        # Painel de status rápido no menu principal
        ativos      = sum(1 for s in servidores if s["ativo"])
        leit_mes    = sum(1 for l in leituras   if l["mes"] == mes_atual())
        alert_aberto= sum(1 for a in alertas    if not a["resolvido"])

        print(
            f"  Servidores ativos: {ativos}  │  "
            f"Leituras este mês: {leit_mes}  │  "
            f"Alertas abertos: {alert_aberto}"
        )
        linha()

        op = input("  Opção: ").strip()

        # Estrutura condicional: direciona para o módulo correto
        if op == "1":
            servidores = menu_servidores(servidores, leituras, alertas)

        elif op == "2":
            leituras, alertas = menu_leituras(servidores, leituras, alertas)

        elif op == "3":
            alertas = listar_alertas(alertas)

        elif op == "4":
            relatorio_estatistico(servidores, leituras)

        elif op == "5":
            sugestoes_melhoria(servidores, leituras, alertas)

        elif op == "6":
            servidores, leituras, alertas = popular_demonstracao(
                servidores, leituras, alertas
            )

        elif op == "0":
            limpar_tela()
            linha()
            print("  Sistema encerrado.")
            print(f"  Dados salvos em: {ARQUIVO_SERVIDORES}, {ARQUIVO_LEITURAS}")
            linha()
            break    # Encerra o loop principal

        else:
            print("\n  [ERRO] Opção inválida. Use os números do menu.")
            pausar()


# ============================================================
# PONTO DE ENTRADA — executa apenas quando rodado diretamente
# ============================================================
if __name__ == "__main__":
    menu_principal()