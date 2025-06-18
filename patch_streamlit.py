# patch_streamlit.py - Run this to patch the streamlit method for Docker
import sys
import os

def patch_streamlit_method():
    """Patch the _mostrar_interface_grafica method to work in Docker"""
    
    # Find the main module file
    main_file = None
    for root, dirs, files in os.walk('.'):
        if 'fut.py' in files:
            main_file = os.path.join(root, 'fut.py')
            break
    
    if not main_file:
        print("Could not find fut.py")
        return
    
    # Read the file
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the problematic method
    old_method = '''def _mostrar_interface_grafica(self):
        """Inicia a execução do streamlit."""
        # Criar o comando do ambiente virtual
        caminho_venv = self.fachada.obter_caminho('venv')
        if not caminho_venv.exists():
            caminho_venv = ''
        else:
            caminho_venv = str(caminho_venv) + " && "
        if sys.platform == 'win32':
            comando = [
            str(caminho_venv)
            , "streamlit", "run", str(self.fachada.obter_caminho('script_frontend'))
        ]
        else:
            ativar_ambiente = ''
            if caminho_venv:
                ativar_ambiente = f"source {str(caminho_venv)} && "
            comando = [
                "bash", "-i", "-c", f"{ativar_ambiente} streamlit run {str(self.fachada.obter_caminho('script_frontend'))}"
            ]
        comando += [
            "&&", "streamlit", "run", self.fachada.obter_caminho('script_frontend')
        ]
        resultado = subprocess.run(comando)'''
    
    new_method = '''def _mostrar_interface_grafica(self):
        """Inicia a execução do streamlit."""
        script_frontend = str(self.fachada.obter_caminho('script_frontend'))
        
        # Simple command for Docker environment
        comando = [
            "streamlit", "run", script_frontend,
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true"
        ]
        
        print(f"Starting Streamlit with: {' '.join(comando)}")
        resultado = subprocess.run(comando)'''
    
    # Replace the method
    if old_method in content:
        content = content.replace(old_method, new_method)
        
        # Write back to file
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Successfully patched the Streamlit method for Docker!")
    else:
        print("Could not find the exact method to patch. The code might have changed.")
        print("You may need to manually edit the _mostrar_interface_grafica method.")

if __name__ == "__main__":
    patch_streamlit_method()