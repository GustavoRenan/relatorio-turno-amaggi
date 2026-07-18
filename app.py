import streamlit as st

# Configuração da página móvel
st.set_page_config(page_title="Gerador de Relatório AMAGGI", page_icon="🦅", layout="centered")

def br_str_to_float(s: str) -> float:
    s = s.strip().replace(' ', '')
    if not s: return 0.0
    if ',' in s:
        s = s.replace('.', '').replace(',', '.')
    else:
        if s.count('.') > 1:
            partes = s.split('.')
            s = "".join(partes[:-1]) + "." + partes[-1]
    try: return float(s)
    except ValueError: return 0.0

def formatar_numero(valor: float) -> str:
    if valor == 0: return "000,000"
    partes = f"{valor:,.3f}".split('.')
    milhares = partes[0].replace(',', '.')
    decimais = partes[1]
    return f"{milhares},{decimais}"

def formatar_horario(h: str) -> str:
    digitos = "".join([c for c in h if c.isdigit()])
    if len(digitos) == 8:
        return f"{digitos[:2]}:{digitos[2:4]} às {digitos[4:6]}:{digitos[6:]}"
    return h

st.title("🦅 Otimizador de Turno - Equipe A")
st.write("Preencha os dados abaixo para gerar o relatório formatado.")

# --- DADOS GERAIS ---
st.subheader("📝 Dados Gerais")
equipe = st.text_input("Equipe:", value="A").upper()
data_raw = st.text_input("Data (apenas números):", value="18072026")
data = f"{data_raw[:2]}/{data_raw[2:4]}/{data_raw[4:]}" if (len(data_raw) == 8 and data_raw.isdigit()) else data_raw

horario_raw = st.text_input("Horário do Turno (apenas números):", value="23320700")
horario = formatar_horario(horario_raw)

# Configuração dos pontos
pontos_config = {
    "TERMINAL FLUTUANTE": {"navio": "MV UNION EXPLORER", "produto": "SOJA RR"},
    "TERMINAL MAQUIRA - BERÇO II": {"navio": "MV KAPTA DIMITROS", "produto": "MILHO"},
    "TERMINAL MAQUIRA - BERÇO III": {"navio": "MV MDS ARTEMIS", "produto": "MILHO"},
    "FUNDEIO GRÃOS": {"navio": "MV AGROPROSPERIS I", "produto": "MILHO"},
    "FUNDEIO FERTILIZANTE": {"navio": "MV BULK PRUDENCE", "produto": "FERTILIZANTE"}
}

produtos_lista = ["SOJA RR", "SOJA CONVENCIONAL", "MILHO", "FERTILIZANTE", "ÓLEO DEGOMADO"]
terminais_dados = []
balsas_limpas_total = 0

# --- PONTOS OPERACIONAIS ---
st.subheader("🚢 Pontos Operacionais")

for ponto, config in pontos_config.items():
    with st.expander(f"📍 {ponto}", expanded=False):
        operando = st.checkbox("Está operando?", value=True, key=f"op_{ponto}")
        
        navio = st.text_input("Nome do Navio:", value=config["navio"], key=f"navio_{ponto}").upper()
        
        idx_prod = produtos_lista.index(config["produto"]) if config["produto"] in produtos_lista else 0
        produto = st.selectbox("Produto:", produtos_lista, index=idx_prod, key=f"prod_{ponto}")
        
        if operando:
            status = "OPERANDO"
            cdo_input = st.text_input("Valores do CDO (separe por espaço):", key=f"cdo_{ponto}")
            tokens = cdo_input.split()
            carregado = sum([br_str_to_float(t) for t in tokens])
            prancha = carregado / 8.0
            st.caption(f"Soma CDO: {formatar_numero(carregado)} MT | Prancha: {formatar_numero(prancha)} t/h")
            impactos = st.text_input("Impactos Gerais do Ponto:", value="NIL", key=f"imp_{ponto}").upper()
            
            # Balsas
            balsas = []
            num_balsas = st.number_input("Quantidade de Balsas no turno:", min_value=0, max_value=5, value=1, key=f"nb_{ponto}")
            
            for i in range(int(num_balsas)):
                st.markdown(f"**Balsa {i+1}**")
                nome_b = st.text_input("Nome da Balsa:", key=f"nome_b_{ponto}_{i}").upper()
                if nome_b:
                    status_b = st.selectbox("Status:", ["LIMPA", "IN PROGRESS"], key=f"stat_b_{ponto}_{i}")
                    balsa_dict = {"nome": nome_b, "status": status_b}
                    
                    if status_b == "LIMPA":
                        balsas_limpas_total += 1
                        tempo = st.text_input("Tempo de descarga (apenas números):", key=f"tempo_b_{ponto}_{i}")
                        if len(tempo) == 4 and tempo.isdigit():
                            tempo = f"{tempo[:2]}:{tempo[2:]}"
                        balsa_dict["tempo_descarga"] = tempo
                        balsa_dict["impactos"] = st.text_input("Impactos da balsa:", key=f"imp_b_{ponto}_{i}").upper()
                    balsas.append(balsa_dict)
        else:
            status = "PARALISADO"
            carregado = 0.0
            prancha = 0.0
            impactos = st.text_input("Motivo da Paralisação:", value="PARADO OPERACIONAL", key=f"imp_par_{ponto}").upper()
            balsas = []
            
        terminais_dados.append({
            "nome": ponto, "navio": navio, "produto": produto, "status": status,
            "carregado": carregado, "prancha": prancha, "impactos": impactos, "balsas": balsas
        })

# --- BOIA 11 ---
st.subheader("⛴️ Quadro da Boia 11 (Comboio)")
empurrador = st.text_input("Empurrador:", value="ITIQUIRA").upper()
composicao = st.text_input("Composição:", value="13 BGS + 02 FERT").upper()
vazias = st.number_input("Balsas Vazias:", min_value=0, value=3)
em_descarga = st.number_input("Balsas em Descarga:", min_value=0, value=2)
carregadas = st.number_input("Balsas Carregadas:", min_value=0, value=2)
status_comboio = st.text_input("Status do Comboio:", value="FORMAÇÃO").upper()

# --- APOIO ---
st.subheader("🚢 Embarcações de Apoio")
apoio_lista = ["V. MASUTTI", "J. TRICHES", "TANGARÁ", "JACOB BORGES", "S.PISSOLO", "AMAZON I"]

# Campo dinâmico para adicionar mais embarcações
novas_embarcacoes = st.text_input("Adicionar outras embarcações (separe por vírgula se for mais de uma):")
if novas_embarcacoes:
    extras = [e.strip().upper() for e in novas_embarcacoes.split(",") if e.strip()]
    for extra in extras:
        if extra not in apoio_lista:
            apoio_lista.append(extra)

status_apoio = {}
cols = st.columns(2)
for idx, emp in enumerate(apoio_lista):
    with cols[idx % 2]:
        status_apoio[emp] = st.checkbox(f"{emp} Operante", value=True, key=f"chk_{emp}")

assinatura = st.text_input("Sua Assinatura:", value="GUSTAVO RENAN").upper()

# --- GERAR RELATÓRIO ---
st.markdown("---")
if st.button("🚀 GERAR RELATÓRIO FINAL", type="primary"):
    check_icons_total = "✅" * balsas_limpas_total
    linhas = [
        f"*RELATÓRIO EQUIPE {equipe}🦅*",
        f"*{data} - {horario}*",
        "",
        f"*DESCARREGADAS NO TURNO* - `{balsas_limpas_total:02d} BG'S` {check_icons_total}",
        "------------------------------------------"
    ]

    for t in terminais_dados:
        linhas.append(f"*{t['nome']}*")
        linhas.append(f"*🚢 - {t['navio']}*")
        linhas.append(f"*Produto:* `{t['produto']}`")
        linhas.append(f"*Status:* `{t['status']}`")
        label_carga = "Descarregado:" if "FERTILIZANTE" in t['produto'] else "Carregado:"
        linhas.append(f"*{label_carga}* `{formatar_numero(t['carregado'])} MT`")
        linhas.append(f"*Prancha:* `{formatar_numero(t['prancha'])} t/h`")
        linhas.append(f"*Impactos:* `{t['impactos']}`")
        linhas.append("")
        
        if t["nome"] == "FUNDEIO FERTILIZANTE" and t["status"] == "PARALISADO":
            linhas.append("*CARREGAMENTO DE BALSA:* `00 BG` \n\n*AGUARDANDO BALSA*")
            linhas.append("")
        elif t["balsas"] or t["status"] == "OPERANDO":
            limpas_aqui = sum(1 for b in t["balsas"] if b["status"] == "LIMPA")
            linhas.append(f"*DESCARGA:* `{limpas_aqui:02d} BG` {'✅' * limpas_aqui}")
            linhas.append("")

        for b in t["balsas"]:
            emoji = "✅" if b["status"] == "LIMPA" else "⌛"
            linhas.append(f"*{b['nome']}* - `{b['status']}` {emoji}")
            if b.get("tempo_descarga"):
                linhas.append(f"*Tempo de descarga:* `{b['tempo_descarga']}⏱️`")
            if b.get("impactos"):
                linhas.append(f"*IMPACTOS:* `{b['impactos']}`")
            linhas.append("")
        linhas.append("-----------------------------------------")

    linhas.append("*⛴️ SAÍDAS DE COMBOIO*")
    linhas.append("")
    linhas.append(f"*➡️ ⛵ {empurrador}* - `{composicao}`")
    linhas.append("")
    linhas.append(f" 🟢 *BALSAS VAZIAS:* `{vazias:02d} BGS`")
    linhas.append(f" 🟡 *BALSAS EM DESCARGA:* `{em_descarga:02d}` BG")
    linhas.append(f" ⚪*BG CARREGADA:* `{carregadas:02d} BG`")
    linhas.append(f" ⚪*STATUS:* `{status_comboio}`")
    linhas.append("")
    linhas.append("-------------------------------------------")
    linhas.append("*🚢 EMBARCAÇÕES DE APOIO*")
    
    for emp, operante in status_apoio.items():
        status_txt = "Operante`✅" if operante else "Inoperante`❌"
        linhas.append(f"*⛴️ {emp}* - `{status_txt}")

    linhas.append("")
    linhas.append(f"*Att.* `{assinatura}`")

    relatorio_pronto = "\n".join(linhas)
    
    st.subheader("📋 Copie o texto abaixo:")
    st.code(relatorio_pronto, language="markdown")
