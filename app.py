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

        # Adicionar a fonte Calibri se necessário (o fpdf2 usa fontes básicas por padrão)
        # Para usar Calibri, você teria que carregar o arquivo .ttf e usar o comando:
        # self.add_font('Calibri', '', 'Calibri.ttf')
        # Por simplicidade e robustez no Streamlit Cloud, vamos usar Times para Título/Autor
        # e usar a cor e tamanho especificados.

    def header(self):
        """Define o cabeçalho do documento (Título Centralizado e Autor à Direita)."""
        
        # 1. Título (Times New Roman, 18pt, Negrito, Itálico, Centralizado)
        self.set_font('Times', 'BI', 18) 
        self.set_text_color(0, 0, 0) 
        
        # Define a posição do Título
        title_width = self.get_string_width(self.doc_titulo)
        title_x = 10 # Começa na margem esquerda
        
        # Cria a célula do Título (largura arbitrária de 100mm, sem borda)
        self.set_x(title_x)
        self.cell(100, 9, self.doc_titulo, 0, 0, 'L') # 'L' para alinhar à esquerda
        
        # 2. Autor/Compositor (Times New Roman, 10pt, Itálico, Cinza, Alinhado à Direita)
        self.set_font('Times', 'I', 10)
        self.set_text_color(102, 102, 102) 
        
        # Calcula a posição para alinhar à direita (Margem Direita está em 200 - 10 = 190)
        autor_x = 110 # Define o início da célula do autor (pode precisar de ajuste fino)
        
        # Move o cursor para o X do autor
        self.set_x(autor_x)
        # Cria a célula do Autor (largura de 90mm, sem borda, 'R' para alinhar à direita)
        self.cell(90, 9, self.doc_autor, 0, 1, 'R') # '1' para quebrar a linha após o autor
        
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
        """Adiciona a pauta (linha preta, linha vermelha e texto do verso em cima da linha)."""
        
        # --- 1. Linha de Notas (Preta) ---
        self.set_line_style((0, 0, 0), width=0.13)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5) # Espaço abaixo da linha preta
        
        # --- 2. Texto do Verso (NOVO POSICIONAMENTO) ---
        
        # Define a fonte, tamanho 10, e cor VERMELHA (#FF0000)
        # Usaremos Times, pois Calibri exige carregamento extra de arquivo .ttf
        self.set_font('Times', '', 10) 
        self.set_text_color(255, 0, 0) # Cor Vermelha
        
        # Converte e posiciona o texto (precisamos do MultiCell para quebra de linha)
        texto_seguro = verso.encode('latin-1', 'replace').decode('latin-1')
        
        # Altura da linha de texto (ex: 5mm)
        text_height = 5
        
        # Move o cursor para CIMA, onde a linha vermelha será desenhada
        self.set_y(self.get_y() + 1) # Pequeno ajuste para garantir que fique "em cima"
        
        # Adiciona o texto (MultiCell usa a cor vermelha e define a posição)
        self.multi_cell(0, text_height, texto_seguro, border=0, align='L', fill=False)
        
        # --- 3. Linha de Verso (Vermelha) ---
        
        # Agora desenhamos a linha vermelha ABAIXO do texto
        self.set_line_style((255, 0, 0), width=0.13)
        
        # Move o cursor para a posição imediatamente abaixo do texto que acabou de ser desenhado
        self.set_y(self.get_y() - 2) # Subir um pouco para a linha encostar no texto
        
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8) # Espaço maior antes do próximo bloco/pauta


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
    
    try:
        pdf = PDF(titulo, autor)
        pdf.add_page()
    except Exception as e:
        st.error(f"Erro ao inicializar o PDF: {e}")
        print(f"Erro na inicialização do PDF: {e}", file=sys.stderr)
        st.stop()

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
