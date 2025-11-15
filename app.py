import streamlit as st
from fpdf import FPDF 
import io # Importamos a biblioteca io para o buffer de bytes

# --- 1. CONFIGURAÇÃO DA CLASSE PDF CUSTOMIZADA (mantida) ---

class PDF(FPDF):
    """Classe customizada para gerar o PDF com seu layout específico."""
    
    def __init__(self, titulo, autor):
        super().__init__('P', 'mm', 'A4') 
        self.doc_titulo = titulo
        self.doc_autor = autor
        self.set_left_margin(10)
        self.set_right_margin(10)

    def header(self):
        """Define o cabeçalho do documento."""
        self.set_font('Times', 'BI', 18) 
        w = self.get_string_width(self.doc_titulo) + 6
        self.set_x((210 - w) / 2) 
        self.set_text_color(0, 0, 0) 
        self.cell(w, 9, self.doc_titulo, 0, 1, 'C')
        
        self.set_font('Times', 'I', 10)
        self.set_text_color(102, 102, 102) 
        self.cell(0, 5, self.doc_autor, 0, 1, 'C')
        self.ln(5) 
        
        self.set_draw_color(192, 192, 192) 
        self.set_line_width(0.1) 
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5) 

    def set_line_style(self, color_rgb, width=0.1):
        """Define a cor e espessura da linha."""
        self.set_draw_color(color_rgb[0], color_rgb[1], color_rgb[2])
        self.set_line_width(width)

    def criar_pauta(self, verso):
        """Adiciona a pauta (linha preta, linha vermelha e texto do verso)."""
        
        # 1. Linha de Notas (Preta)
        self.set_line_style((0, 0, 0), width=0.13)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5) 
        
        # 2. Linha de Verso (Vermelha)
        self.set_line_style((255, 0, 0), width=0.13)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2) 

        # 3. Texto do Verso
        self.set_font('Times', '', 10)
        self.set_text_color(0, 0, 0) 
        # Garante que o texto seja compatível com a codificação Latin-1
        texto_seguro = verso.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 5, texto_seguro)
        self.ln(8) 


# --- 2. CONFIGURAÇÃO DA INTERFACE STREAMLIT (mantida) ---

st.set_page_config(page_title="Music Notation Maker", layout="centered")

st.title("🎵 Music Notation Maker")
st.markdown("Crie seu modelo de partitura de violino com organização automática de versos.")

# Campos de entrada
titulo = st.text_input("Escreva aqui o título da música", "Título da música")
autor = st.text_input("Escreva aqui o autor ou compositor da música", "Autor/Compositor")
letra = st.text_area("Cole aqui o trecho da música (Um verso por linha)", height=200, 
                     value="Brilha, brilha, estrelinha\nQuero ver você brilhar\nLá no alto, lá no céu")

# Botão para gerar
if st.button("Clique aqui para gerar o PDF"):
    
    # 3. GERAÇÃO DO PDF
    
    pdf = PDF(titulo, autor)
    pdf.add_page()
    
    versos = [v.strip() for v in letra.split('\n') if v.strip()]
    
    if not versos:
        st.warning("Por favor, cole a letra da música na caixa de texto acima.")
    else:
        for verso in versos:
            pdf.criar_pauta(verso)
            
        # 4. Saída e Download (CORREÇÃO CRÍTICA AQUI)
        
        # Cria um buffer de bytes na memória
        buffer = io.BytesIO()
        # Salva o PDF no buffer
        buffer.write(pdf.output(dest='S'))
        # Retorna ao início do buffer
