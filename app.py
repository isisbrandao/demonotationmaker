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

        # Abordagem para a fonte Calibri (VAMOS MANTER Times por robustez)
        # Se quiser usar Calibri, você precisa de um arquivo .ttf no seu repositório GitHub
        # e usar: self.add_font('Calibri', '', 'Calibri.ttf')
        # Manteremos Times com os atributos visuais de Calibri (cor, tamanho).

    def header(self):
        """Define o cabeçalho do documento: Título Centralizado, Autor à Direita."""
        
        # 1. Título (Times New Roman, 18pt, Negrito, Itálico, AGORA CENTRALIZADO)
        self.set_font('Times', 'BI', 18) 
        self.set_text_color(0, 0, 0) # Preto
        
        # Centralização do Título (cálculo de largura do texto)
        title_width = self.get_string_width(self.doc_titulo)
        title_start_x = (210 - title_width) / 2 # Ponto de início para centralizar
        
        # Desenha o Título e o Autor na mesma linha
        # Título: Posição fixa no centro
        self.set_x(title_start_x)
        self.cell(title_width, 9, self.doc_titulo, 0, 0, 'C') # 0, 0 para NÃO pular linha
        
        # 2. Autor/Compositor (Times New Roman, 10pt, Itálico, Cinza, Alinhado à Direita)
        self.set_font('Times', 'I', 10)
        self.set_text_color(102, 102, 102) # Cinza
        
        # Posiciona o cursor para desenhar o autor alinhado à direita na mesma altura
        self.set_x(140) # Posição estratégica para garantir que o autor fique à direita da página
        self.cell(60, 9, self.doc_autor, 0, 1, 'R') # 0, 1 para pular linha após o autor

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
        
        # --- 2. Texto do Verso (POSICIONAMENTO CORRIGIDO) ---
        
        # Fonte: Times (em substituição a Calibri), Tamanho 10, Cor VERMELHA
        self.set_font('Times', '', 10) 
        self.set_text_color(255, 0, 0) 
        
        # Para que o texto fique ACIMA da linha vermelha e não seja cortado, 
        # movemos o cursor para CIMA ANTES de desenhar o texto.
        self.set_y(self.get_y() + 0.5) # Pequeno ajuste vertical para evitar corte
        
        # Converte o texto e desenha
        texto_seguro = verso.encode('latin-1', 'replace').decode('latin-1')
        text_height = 5
        self.multi_cell(0, text_height, texto_seguro, border=0, align='L', fill=False)
        
        # --- 3. Linha de Verso (Vermelha) ---
        
        # Move o cursor para a posição imediatamente abaixo do texto.
        # get_y() aponta para o final do multi_cell. Subimos um pouco para a linha encostar.
        self.set_y(self.get_y() - 4.5) 
        
        self.set_line_style((255, 0, 0), width=0.13)
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
