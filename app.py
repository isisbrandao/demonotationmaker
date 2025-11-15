import streamlit as st
from fpdf import FPDF 
import io 
import sys

# --- 1. CONFIGURAÇÃO DA CLASSE PDF CUSTOMIZADA ---

class PDF(FPDF):
    """Classe customizada para gerar o PDF com seu layout específico."""
    
    def __init__(self, titulo, autor):
        super().__init__('P', 'mm', 'A4') 
        self.doc_titulo = titulo
        self.doc_autor = autor
        self.set_left_margin(10)
        self.set_right_margin(10)

    def header(self):
        """Define o cabeçalho do documento: Título Centralizado, Autor à Direita."""
        
        # 1. Título (Times New Roman, 18pt, Negrito, Itálico, Centralizado)
        self.set_font('Times', 'BI', 18) 
        self.set_text_color(0, 0, 0) # Preto
        
        title_width = self.get_string_width(self.doc_titulo)
        title_start_x = (210 - title_width) / 2
        
        # Título Centralizado
        self.set_x(title_start_x)
        self.cell(title_width, 9, self.doc_titulo, 0, 0, 'C') 
        
        # 2. Autor/Compositor (Times New Roman, 10pt, Itálico, Cinza, Alinhado à Direita)
        self.set_font('Times', 'I', 10)
        self.set_text_color(102, 102, 102) # Cinza
        
        # Posiciona o cursor para desenhar o autor alinhado à direita
        self.set_x(140) 
        self.cell(60, 9, self.doc_autor, 0, 1, 'R') # Pula linha após o autor

        self.ln(5) # Espaço abaixo do cabeçalho
        
        # 3. Linha Cinza (Divisória)
        self.set_draw_color(192, 192, 192) 
        self.set_line_width(0.1) 
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5) 

    def set_line_style(self, color_rgb, width=0.1):
        """Define a cor e espessura da linha."""
        self.set_draw_color(color_rgb[0], color_rgb[1], color_rgb[2])
        self.set_line_width(width)

    def criar_pauta(self, verso):
        """Adiciona a pauta (linha preta, linha vermelha e texto do verso ACIMA da linha)."""
        
        # 1. Linha de Notas (Preta)
        self.set_line_style((0, 0, 0), width=0.13)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5) # Espaço abaixo da linha preta
        
        # 2. Texto do Verso (POSICIONAMENTO CORRIGIDO PARA FICAR ACIMA)
        
        # Fonte: Times (Substituindo Calibri), Tamanho 10, Cor VERMELHA
        # Usamos 'I' (Itálico) para dar uma aparência mais leve.
        self.set_font('Times', 'I', 10) 
        self.set_text_color(255, 0, 0) 
        
        # Move o cursor para CIMA ANTES de desenhar o texto.
        # Ajuste de -4.5mm move o cursor para a posição ACIMA da linha vermelha.
        # A altura da célula (5mm) será desenhada de cima para baixo.
        self.set_y(self.get_y() - 4.5) 
        
        # Converte o texto e desenha
        texto_seguro = verso.encode('latin-1', 'replace').decode('latin-1')
        text_height = 5
        self.multi_cell(0, text_height, texto_seguro, border=0, align='L', fill=False)
        
        # 3. Linha de Verso (Vermelha)
        
        # Move o cursor para a posição imediatamente abaixo do texto.
        # O get_y() está no final do MultiCell. Subimos 1.5mm para a linha ficar colada.
        self.set_y(self.get_y() - 1.5) 
        
        self.set_line_style((255, 0, 0), width=0.13)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8) # Espaço maior antes do próximo bloco/pauta


# --- 2. CONFIGURAÇÃO DA INTERFACE STREAMLIT (mantida) ---

st.set_page_config(page_title="Music Notation Maker", layout="centered")

st.title("🎵 Music Notation Maker")
st.markdown("Crie seu modelo de partitura de violino com organização automática de versos.")

# Campos de entrada
titulo = st.text_input("Escreva aqui o título da música", "Brilha, Brilha, Estrelinha")
autor = st.text_input("Escreva aqui o autor ou compositor da música", "Jane Taylor")
letra = st.text_area("Cole aqui o trecho da música (Um verso por linha)", height=200, 
                     value="Brilha, brilha, estrelinha\nQuero ver você brilhar\nLá no alto, lá no céu\nNum desenho de cordel")

# Botão para gerar
if st.button("Clique aqui para gerar o PDF"):
    
    # 3. GERAÇÃO DO PDF
    
    try:
        pdf = PDF(titulo, autor)
        pdf.add_page()
    except Exception as e:
        st.error(f"Erro ao inicializar o PDF: {e}")
        print(f"Erro na inicialização do PDF: {e}", file=sys.stderr)
        st.stop()

    # O Streamlit já forneceu os versos
    # [cite_start]Brilha, brilha, estrelinha [cite: 3]
    # [cite_start]Quero ver você brilhar [cite: 4]
    # [cite_start]Lá no alto, lá no céu [cite: 5]
    # [cite_start]Num desenho de cordel [cite: 6]
    
    versos = [v.strip() for v in letra.split('\n') if v.strip()]
    
    if not versos:
        st.warning("Por favor, cole a letra da música na caixa de texto acima.")
    else:
        for verso in versos:
            pdf.criar_pauta(verso)
            
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
