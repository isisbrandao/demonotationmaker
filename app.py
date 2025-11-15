import streamlit as st
from fpdf import FPDF # fpdf2 é o nome do pacote, FPDF é o nome da classe

# --- 1. CONFIGURAÇÃO DA CLASSE PDF CUSTOMIZADA ---

class PDF(FPDF):
    """Classe customizada para gerar o PDF com seu layout específico."""
    
    def header(self, titulo, autor):
        """Define o cabeçalho do documento (Título, Autor e Linha Cinza)."""
        self.set_font('Times', 'BI', 18) # Times New Roman, 18pt, Negrito, Itálico
        w = self.get_string_width(titulo) + 6
        self.set_x((210 - w) / 2) # Centraliza o título
        self.cell(w, 9, titulo, 0, 1, 'C')
        
        # Autor (Times New Roman, 10pt, Itálico, Cinza #666666)
        self.set_font('Times', 'I', 10)
        self.set_text_color(102, 102, 102) # RGB (102, 102, 102) para #666666
        self.cell(0, 5, autor, 0, 1, 'C')
        self.ln(5) # Linha de espaço
        
        # Linha Cinza (Anotações Gerais - Divisória)
        self.set_draw_color(192, 192, 192) # Cinza Claro
        self.set_line_width(0.1) 
        # Desenha uma linha horizontal (x1, y1, x2, y2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5) # Espaço para anotações

    def set_line_style(self, color_rgb, width=0.1):
        """Define a cor e espessura da linha."""
        self.set_draw_color(color_rgb[0], color_rgb[1], color_rgb[2])
        self.set_line_width(width)

    def criar_pauta(self, verso):
        """Adiciona a pauta (linha preta, linha vermelha e texto do verso)."""
        
        # 1. Linha de Notas (Preta: #000000, 0.5px - 0.13mm)
        self.set_line_style((0, 0, 0), width=0.13)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5) # Espaço abaixo da linha preta
        
        # 2. Linha de Verso (Vermelha: #FF0000, 0.5px - 0.13mm)
        self.set_line_style((255, 0, 0), width=0.13)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2) # Espaço mínimo para o texto

        # 3. Texto do Verso
        self.set_font('Times', '', 10)
        self.set_text_color(0, 0, 0) # Volta ao preto para o texto
        self.multi_cell(0, 5, verso)
        self.ln(8) # Espaço maior antes do próximo bloco/pauta


# --- 2. CONFIGURAÇÃO DA INTERFACE STREAMLIT ---

st.set_page_config(page_title="Music Notation Maker", layout="centered")

st.title("🎵 Music Notation Maker")
st.markdown("Crie seu modelo de partitura de violino com organização automática de versos.")

# Campos de entrada
titulo = st.text_input("Escreva aqui o título da música", "Título da música")
autor = st.text_input("Escreva aqui o autor ou compositor da música", "Autor/Compositor")
letra = st.text_area("Cole aqui o trecho da música", height=200, 
                     value="Brilha, brilha, estrelinha\nQuero ver você brilhar\nLá no alto, lá no céu\nNum desenho de cordel")

# Botão para gerar
if st.button("Clique aqui para gerar o PDF"):
    
    # 3. GERAÇÃO DO PDF
    
    # Inicializa o PDF
    pdf = PDF()
    pdf.add_page()
    
    # O fpdf2 trata a função header() automaticamente na add_page, mas 
    # precisamos passar os parâmetros para que ele os utilize.
    pdf.header(titulo, autor)
    
    # Processa a letra
    versos = [v.strip() for v in letra.split('\n') if v.strip()]
    
    # Adiciona cada pauta
    for verso in versos:
        pdf.criar_pauta(verso)
        
    # Salva o arquivo em memória para download
    pdf_output = pdf.output(dest='S').encode('latin1')
    
    # 4. BOTÃO DE DOWNLOAD
    st.download_button(
        label="Download do PDF Final",
        data=pdf_output,
        file_name=f"{titulo.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
    st.success("✅ Partitura gerada com sucesso!")
