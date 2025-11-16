import streamlit as st
from fpdf import FPDF 
import io 
import sys
import os 

# --- 1. CONFIGURAÇÃO DA CLASSE PDF CUSTOMIZADA ---

class PDF(FPDF):
    """Classe customizada para gerar o PDF com seu layout específico."""
    
    def __init__(self):
        super().__init__('P', 'mm', 'A4') 
        self.set_left_margin(10)
        self.set_right_margin(10)
        
        self.calibri_loaded = False 
        
        # Tenta carregar a fonte Calibri (Se os arquivos .ttf estiverem no repositório)
        try:
            if os.path.exists('Calibri.ttf'):
                self.add_font('Calibri', '', 'Calibri.ttf')
                if os.path.exists('CalibriB.ttf'):
                    self.add_font('Calibri', 'B', 'CalibriB.ttf')
                if os.path.exists('CalibriI.ttf'):
                    self.add_font('Calibri', 'I', 'CalibriI.ttf')
                self.calibri_loaded = True
        except Exception as e:
            print(f"Erro ao carregar fonte Calibri: {e}. Usando Times como fallback.", file=sys.stderr)
            self.calibri_loaded = False

    def header(self):
        """O header padrão é sobrescrito, usamos 'add_music_header' manualmente."""
        pass

    def add_music_header(self, titulo, autor):
        """Adiciona o cabeçalho de uma música específica (chamado manualmente)."""
        
        # Começa uma nova página (importante para múltiplas músicas)
        self.add_page() 
        
        # 1. Título (Centralizado)
        self.set_font('Times', 'BI', 18) 
        self.set_text_color(0, 0, 0)
        
        title_width = self.get_string_width(titulo)
        title_start_x = (210 - title_width) / 2
        
        self.set_x(title_start_x)
        self.cell(title_width, 9, titulo, 0, 0, 'C') 
        
        # 2. Autor/Compositor (À Direita)
        self.set_font('Times', 'I', 10)
        self.set_text_color(102, 102, 102) 
        
        self.set_x(140) 
        self.cell(60, 9, autor, 0, 1, 'R') 

        self.ln(5) 
        
        # 3. Linha Cinza (Divisória)
        self.set_draw_color(192, 192, 192) 
        self.set_line_width(0.1) 
        self.line(10, self.get_y(), 200, self.get_y())
        
        # 4. ESPAÇAMENTO: 1cm (10mm) entre a linha cinza e o conteúdo
        self.ln(10) 

    # ESTA É A FUNÇÃO QUE ESTAVA FALTANDO OU INACESSÍVEL NO SEU ERRO
    def set_line_style(self, color_rgb, width=0.1):
        """Define a cor e espessura da linha."""
        self.set_draw_color(color_rgb[0], color_rgb[1], color_rgb[2])
        self.set_line_width(width)

    def criar_pauta(self, verso):
        """Adiciona a pauta (linha preta, linha vermelha e texto do verso ACIMA da linha)."""
        
        # 1. Linha de Notas (Preta)
        self.set_line_style((0, 0, 0), width=0.13) # Esta linha causava o erro
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5) 
        
        # 2. Texto do Verso 
        if self.calibri_loaded:
            self.set_font('Calibri', '', 10) 
        else:
            self.set_font('Times', 'I', 10) 
            
        self.set_text_color(255, 0, 0) 
        
        self.set_y(self.get_y() - 5.5) 
        
        texto_seguro = verso.encode('latin-1', 'replace').decode('latin-1')
        text_height = 5
        self.multi_cell(0, text_height, texto_seguro, border=0, align='L', fill=False)
        
        # 3. Linha de Verso (Vermelha)
        
        self.set_y(self.get_y() - 1.0) 
        
        self.set_line_style((255, 0, 0), width=0.13)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8) 


# --- 2. FUNÇÕES DE ESTADO DE SESSÃO PARA MÚLTIPLAS MÚSICAS ---

# Estrutura de dados inicial para uma música (com placeholders corrigidos)
MUSICA_TEMPLATE = {
    "titulo": "Título da música",
    "autor": "Autor/Compositor",
    "letra": "Cole aqui a letra da música (Um verso por linha)",
}

def inicializar_estado():
    """Inicializa o estado da sessão com uma música vazia."""
    if 'musicas' not in st.session_state:
        st.session_state.musicas = [MUSICA_TEMPLATE.copy()]

def adicionar_musica():
    """Adiciona um novo template de música à lista."""
    st.session_state.musicas.append(MUSICA_TEMPLATE.copy())

def remover_musica(index):
    """Remove uma música da lista."""
    if len(st.session_state.musicas) > 1:
        st.session_state.musicas.pop(index)
    else:
        st.warning("Pelo menos uma música deve permanecer.")


# --- 3. CONFIGURAÇÃO DA INTERFACE STREAMLIT ---

inicializar_estado()

st.set_page_config(page_title="Music Notation Maker", layout="centered")

st.title("🎵 Gerador de Partituras Múltiplas")
st.markdown("Adicione e personalize várias músicas. Um único download gerará todas as partituras em sequência.")

# Itera sobre a lista de músicas no estado
for i, musica in enumerate(st.session_state.musicas):
    
    st.subheader(f"🎼 Música {i+1}")
    
    col1, col2 = st.columns([10, 1])
    
    # Campo de Título
    st.session_state.musicas[i]["titulo"] = col1.text_input(
        f"Título da Música {i+1}", 
        value=musica["titulo"], 
        key=f"titulo_{i}"
    )

    # Campo de Autor
    st.session_state.musicas[i]["autor"] = col1.text_input(
        f"Autor/Compositor {i+1}", 
        value=musica["autor"], 
        key=f"autor_{i}"
    )

    # Campo de Letra (com o novo placeholder)
    st.session_state.musicas[i]["letra"] = col1.text_area(
        f"Letra da Música {i+1} (Um verso por linha)", 
        value=musica["letra"],
        height=150,
        key=f"letra_{i}"
    )
    
    # Botão de remoção
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("❌ Remover Música", key=f"remover_{i}", on_click=remover_musica, args=(i,))
    
    st.markdown("---") # Separador visual entre músicas

# Botão para adicionar mais músicas
st.button("➕ Adicionar Outra Música", on_click=adicionar_musica)


# --- BOTÃO PRINCIPAL DE GERAÇÃO ---

if st.button("🌟 Gerar e Baixar Partitura Completa (PDF ÚNICO)"):
    
    # 4. GERAÇÃO DO PDF
    
    try:
        pdf = PDF()
    except Exception as e:
        st.error(f"Erro ao inicializar o PDF: {e}")
        print(f"Erro na inicialização do PDF: {e}", file=sys.stderr)
        st.stop()

    # Processa CADA MÚSICA separadamente
    for musica in st.session_state.musicas:
        
        # 4a. Adiciona o Cabeçalho da MÚSICA
        pdf.add_music_header(musica["titulo"], musica["autor"])
        
        # 4b. Processa os Versos da MÚSICA
        versos = [v.strip() for v in musica["letra"].split('\n') if v.strip()]
        
        if not versos:
            pdf.ln(20) 
            pdf.set_font('Times', 'I', 12)
            pdf.cell(0, 10, "⚠️ Esta música não tem letra.", 0, 1, 'C')
        else:
            for verso in versos:
                pdf.criar_pauta(verso)
            
    # 5. Saída e Download 
    
    try:
        buffer = io.BytesIO()
        buffer.write(pdf.output(dest='S'))
        buffer.seek(0)
        
        st.download_button(
            label="Download do PDF Final",
            data=buffer, 
            file_name="Partituras_Multiplas.pdf",
            mime="application/pdf"
        )
        st.success("✅ Partituras geradas com sucesso! Clique no botão de download acima.")

    except Exception as e:
        st.error(f"Erro ao gerar o download: {e}")
        print(f"Erro no processo de download: {e}", file=sys.stderr)
