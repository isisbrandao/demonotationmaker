# ... (Imports e funções add_border e criar_pauta permanecem as mesmas) ...

# --- 1. CONFIGURAÇÃO DA CLASSE PDF CUSTOMIZADA (CORRIGIDA) ---

class PDF(FPDF):
    """Classe customizada para gerar o PDF com seu layout específico."""
    
    # Novo método __init__ para receber e armazenar título e autor
    def __init__(self, titulo, autor):
        super().__init__()
        self.doc_titulo = titulo
        self.doc_autor = autor

    def header(self):
        """Define o cabeçalho do documento (agora usa os atributos da classe)."""
        
        # Título (Times New Roman, 18pt, Negrito, Itálico)
        self.set_font('Times', 'BI', 18) 
        w = self.get_string_width(self.doc_titulo) + 6
        self.set_x((210 - w) / 2) 
        self.cell(w, 9, self.doc_titulo, 0, 1, 'C')
        
        # Autor (Times New Roman, 10pt, Itálico, Cinza #666666)
        self.set_font('Times', 'I', 10)
        self.set_text_color(102, 102, 102) # RGB (102, 102, 102) para #666666
        self.cell(0, 5, self.doc_autor, 0, 1, 'C')
        self.ln(5) 
        
        # Linha Cinza (Anotações Gerais - Divisória)
        self.set_draw_color(192, 192, 192) # Cinza Claro
        self.set_line_width(0.1) 
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5) # Espaço para anotações

    # ... (O método criar_pauta e set_line_style permanecem os mesmos) ...

# --- 2. CONFIGURAÇÃO DA INTERFACE STREAMLIT ---

# ... (st.set_page_config, st.title, st.markdown, st.text_input, st.text_area permanecem os mesmos) ...

# Botão para gerar
if st.button("Clique aqui para gerar o PDF"):
    
    # 3. GERAÇÃO DO PDF (CORRIGIDA)
    
    # Inicializa o PDF, AGORA PASSANDO O TÍTULO E O AUTOR
    pdf = PDF(titulo, autor)
    
    # Adiciona a página. O FPDF agora chama pdf.header() sem argumentos,
    # mas o header() usa os atributos self.doc_titulo e self.doc_autor.
    pdf.add_page()
    
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
