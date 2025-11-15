import streamlit as st
from fpdf import FPDF # Linha ESSENCIAL para definir a classe FPDF

# --- 1. CONFIGURAÇÃO DA CLASSE PDF CUSTOMIZADA ---

class PDF(FPDF):
    """Classe customizada para gerar o PDF com seu layout específico."""
    
    def __init__(self, titulo, autor):
        # Inicializa a classe base FPDF
        super().__init__('P', 'mm', 'A4') 
        self.doc_titulo = titulo
        self.doc_autor = autor
        # Adiciona a fonte Times New Roman (fontes padrão)
        # Nota: fpdf2 usa fontes embutidas que simulam Times, I é itálico, B é negrito, etc.
        # Não precisamos de arquivos .ttf, pois o fpdf2 já tem as métricas
        

    def header(self):
        """Define o cabeçalho do documento (Título, Autor e Linha Cinza)."""
        
        # Título: Times New Roman, 18pt, Negrito, Itálico
        self.set_font('Times', 'BI', 18) 
        w = self.get_string_width(self.doc_titulo) + 6
        self.set_x((210 - w) / 2) # Centraliza o título
        self.set_text_color(0, 0, 0) # Preto para o título
        self.cell(w, 9, self.doc_titulo, 0, 1, 'C')
        
        # Autor: Times New Roman, 10pt, Itálico, Cinza #666666
        self.set_font('Times', 'I', 10)
        self.set_text_color(102, 102, 102) # RGB (102, 102, 102) para #666666
        self.cell(0, 5, self.doc_autor, 0, 1, 'C')
        self.ln(5) 
        
        # Linha Cinza (Anotações Gerais - Divisória)
        self.set_draw_color(192, 192, 192) # Cinza Claro
        self.set_line_width(0.1) 
        self.line(10, self.get_x(), 200, self.get_x())
        self.ln(5) # Espaço para anotações

    def set_line_style(self, color_rgb, width=0.1):
        """Define a cor e espessura da linha."""
        self.set_draw_color(color_rgb[0], color_rgb[1], color_rgb[2])
        self.set_line_width(width)

    def criar_pauta(self, verso):
        """Adiciona a pauta (linha preta, linha vermelha e texto do verso)."""
        
        # 1. Linha de Notas (Preta: #000000, 0.5px -> aprox. 0.13mm)
        self.set_line_style((0, 0, 0), width=0.13)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5) # Espaço abaixo da linha preta
        
        # 2. Linha de Verso (Vermelha: #FF0000, 0.5px -> aprox. 0.13mm)
        self.set_line_style((255, 0, 0), width=0.13)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2) # Espaço mínimo para o texto

        # 3. Texto do Verso
        self.set_font('Times', '', 10)
        self.set_text_color(0, 0, 0) # Volta ao preto para o texto do verso
        self.multi_cell(0, 5, verso)
        self.ln(8) # Espaço maior antes do próximo bloco/pauta


# --- 2. CONFIGURAÇÃO DA INTERFACE STREAMLIT ---

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
    
    # Inicializa o PDF, passando o título e o autor para a classe
    pdf = PDF(titulo, autor)
    
    # Adiciona a primeira página (isso chama o método header() automaticamente)
    pdf.add_page()
    
    # Processa a letra
    versos = [v.strip() for v in letra.split('\n') if v.strip()]
    
    if not versos:
        st.warning("Por favor, cole a letra da música na caixa de texto acima.")
    else:
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
        st.success("✅ Partitura gerada com sucesso! Clique no botão de download acima.")
