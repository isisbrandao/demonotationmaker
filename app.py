import streamlit as st
from fpdf import FPDF 
import io 
import sys
import os 

# --- 1. CONFIGURAÇÃO DA CLASSE PDF CUSTOMIZADA ---

class PDF(FPDF):
    """Classe customizada para gerar o PDF com seu layout específico."""
    
    def __init__(self, titulo, autor):
        super().__init__('P', 'mm', 'A4') 
        self.doc_titulo = titulo
        self.doc_autor = autor
        self.set_left_margin(10)
        self.set_right_margin(10)
        
        self.calibri_loaded = False 

        # Tenta carregar a fonte Calibri (necessário se os .ttf foram fornecidos)
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
        """Define o cabeçalho do documento e o espaçamento de 1cm (10mm)."""
        
        # 1. Título e Autor (mantido)
        self.set_font('Times', 'BI', 18) 
        self.set_text_color(0, 0, 0)
        title_width = self.get_string_width(self.doc_titulo)
        title_start_x = (210 - title_width) / 2
        
        self.set_x(title_start_x)
        self.cell(title_width, 9, self.doc_titulo, 0, 0, 'C') 
        
        self.set_font('Times', 'I', 10)
        self.set_text_color(102, 102, 102) 
        self.set_x(140) 
        self.cell(60, 9, self.doc_autor, 0, 1, 'R') 

        self.ln(5) 
        
        # 2. Linha Cinza (Divisória)
        self.set_draw_color(192, 192, 192) 
        self.set_line_width(0.1) 
        self.line(10, self.get_y(), 200, self.get_y())
        
        # 3. NOVO ESPAÇAMENTO: Adiciona 10mm (1cm) entre a linha cinza e o conteúdo
        self.ln(10) 

    def set_line_style(self, color_rgb, width=0.1):
        """Define a cor e espessura da linha."""
        self.set_draw_color(color_rgb[0], color_rgb[1], color_rgb[2])
        self.set_line_width(width)

    def criar_pauta(self, verso):
        """Adiciona a pauta (linha preta, linha vermelha e texto do verso ACIMA da linha)."""
        
        # 1. Linha de Notas (Preta) - Agora está 10mm abaixo da linha cinza
        self.set_line_style((0, 0, 0), width=0.13)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5) 
        
        # 2. Texto do Verso (Fonte e Posicionamento)
        if self.calibri_loaded:
            self.set_font('Calibri', '', 10) 
        else:
            self.set_font('Times', 'I', 10) 
            
        self.set_text_color(255, 0, 0) 
        
        # Ajuste vertical para mover o texto para cima (-5.5mm)
        self.set_y(self.get_y() - 5.5) 
        
        # Converte o texto e desenha
        texto_seguro = verso.encode('latin-1', 'replace').decode('latin-1')
        text_height = 5
        self.multi_cell(0, text_height, texto_seguro, border=0, align='L', fill=False)
        
        # 3. Linha de Verso (Vermelha)
        
        # Ajuste vertical para que a linha fique próxima do texto (-1.0mm)
        self.set_y(self.get_y() - 1.0) 
        
        self.set_line_style((255, 0, 0), width=0.13)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8) 


# --- 2. CONFIGURAÇÃO DA INTERFACE STREAMLIT (COM MÚLTIPLOS BLOCOS) ---

st.set_page_config(page_title="Music Notation Maker", layout="centered")

st.title("🎵 Music Notation Maker")
st.markdown("Crie seu modelo de partitura de violino com organização automática de versos.")

# Inicializa o estado da sessão para armazenar os blocos de verso
if 'blocos' not in st.session_state:
    st.session_state.blocos = [""] # Começa com um bloco vazio

def adicionar_bloco():
    """Função chamada pelo botão para adicionar um novo campo de texto."""
    st.session_state.blocos.append("")

def remover_bloco(index):
    """Função chamada para remover um campo de texto."""
    if len(st.session_state.blocos) > 1:
        st.session_state.blocos.pop(index)
    else:
        st.warning("Pelo menos um bloco de letra deve permanecer.")


# --- ÁREA DE INPUT ---

titulo = st.text_input("Escreva aqui o título da música", "Brilha, Brilha, Estrelinha")
autor = st.text_input("Escreva aqui o autor ou compositor da música", "Jane Taylor")

st.subheader("Blocos de Letra (Um verso por linha)")

# Cria os campos de texto dinamicamente
for i, verso_bloco in enumerate(st.session_state.blocos):
    col1, col2 = st.columns([10, 1])
    
    with col1:
        st.session_state.blocos[i] = st.text_area(
            f"Bloco {i+1}", 
            value=verso_bloco if verso_bloco else "Verso 1\nVerso 2",
            height=100,
            key=f"bloco_{i}"
        )
    with col2:
        # Botão de remoção
        st.markdown("<br>", unsafe_allow_html=True) # Espaçamento para alinhar
        st.button("❌", key=f"remover_{i}", on_click=remover_bloco, args=(i,))

# Botão para adicionar mais blocos
st.button("➕ Adicionar outro bloco de letra", on_click=adicionar_bloco)


# --- BOTÃO PRINCIPAL DE GERAÇÃO ---
st.markdown("---")

if st.button("🌟 Gerar e Baixar Partitura Completa"):
    
    # 3. GERAÇÃO DO PDF
    
    try:
        pdf = PDF(titulo, autor)
        pdf.add_page()
    except Exception as e:
        st.error(f"Erro ao inicializar o PDF: {e}")
        print(f"Erro na inicialização do PDF: {e}", file=sys.stderr)
        st.stop()

    # Processa todos os blocos de verso
    for bloco_texto in st.session_state.blocos:
        versos = [v.strip() for v in bloco_texto.split('\n') if v.strip()]
        
        for verso in versos:
            pdf.criar_pauta(verso)
            
        # Adiciona uma quebra de linha maior entre blocos, se houver mais blocos
        pdf.ln(10)
            
    # 4. Saída e Download 
    
    try:
        buffer = io.BytesIO()
        buffer.write(pdf.output(dest='S'))
        buffer.seek(0)
        
        st.download_button(
            label="Download do PDF Final",
            data=buffer, 
            file_name=f"{titulo.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
        st.success("✅ Partitura gerada com sucesso! Clique no botão de download acima.")

    except Exception as e:
        st.error(f"Erro ao gerar o download: {e}")
        print(f"Erro no processo de download: {e}", file=sys.stderr)
