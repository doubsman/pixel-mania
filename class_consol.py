import subprocess
import tempfile
import os
import time

class CmdTerminal:
    def __init__(self, largeur, hauteur, commande=None, texte=None):
        # Limiter les dimensions à des valeurs raisonnables
        self.largeur = min(max(largeur, 20), 150)  # Min 20, Max 150
        self.hauteur = min(max(hauteur, 10), 50)   # Min 10, Max 50
        self.commande = commande
        self.texte = texte

    def run(self):
        if self.texte:
            # Créer un fichier temporaire pour le texte
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as text_file:
                text_file.write(self.texte)
                text_file_name = text_file.name

            # Créer un fichier temporaire pour le script PowerShell
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8') as ps_file:
                ps_file.write(f'$Host.UI.RawUI.WindowTitle = "ASCII Display"\n')
                ps_file.write('try {\n')
                # Obtenir les limites du système
                ps_file.write('    $maxWindowSize = $Host.UI.RawUI.MaxWindowSize\n')
                ps_file.write('    $maxBufferSize = $Host.UI.RawUI.MaxPhysicalWindowSize\n')
                # Calculer les dimensions finales
                ps_file.write(f'    $desiredWidth = [Math]::Min({self.largeur}, $maxWindowSize.Width)\n')
                ps_file.write(f'    $desiredHeight = [Math]::Min({self.hauteur}, $maxWindowSize.Height)\n')
                # Définir d'abord la taille de la fenêtre
                ps_file.write('    $windowSize = New-Object Management.Automation.Host.Size($desiredWidth, $desiredHeight)\n')
                ps_file.write('    $Host.UI.RawUI.WindowSize = $windowSize\n')
                # Puis définir le buffer légèrement plus grand
                ps_file.write('    $bufferSize = New-Object Management.Automation.Host.Size($desiredWidth, [Math]::Max($desiredHeight, 300))\n')
                ps_file.write('    $Host.UI.RawUI.BufferSize = $bufferSize\n')
                ps_file.write('} catch {\n')
                ps_file.write('    Write-Host "Adjusting window size..."\n')
                ps_file.write('    try {\n')
                ps_file.write('        $defaultWidth = 80\n')
                ps_file.write('        $defaultHeight = 25\n')
                ps_file.write('        $Host.UI.RawUI.WindowSize = New-Object Management.Automation.Host.Size($defaultWidth, $defaultHeight)\n')
                ps_file.write('        $Host.UI.RawUI.BufferSize = New-Object Management.Automation.Host.Size($defaultWidth, 300)\n')
                ps_file.write('    } catch {\n')
                ps_file.write('        Write-Host "Using system default size"\n')
                ps_file.write('    }\n')
                ps_file.write('}\n')
                ps_file.write('$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8\n')
                ps_file.write(f'Get-Content -Encoding UTF8 "{text_file_name}"\n')
                ps_file.write('Write-Host ""\n')
                ps_file.write('Write-Host "Press any key to continue..."\n')
                ps_file.write('$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")\n')
                ps_script = ps_file.name

            # Lancer PowerShell dans une nouvelle fenêtre sans attendre
            cmd = f'start powershell -NoProfile -ExecutionPolicy Bypass -File "{ps_script}"'
            process = subprocess.Popen(cmd, shell=True)
            
            # Démarrer un thread pour nettoyer les fichiers temporaires après un délai
            def cleanup():
                time.sleep(2)  # Attendre que la fenêtre soit bien ouverte
                try:
                    os.unlink(text_file_name)
                    os.unlink(ps_script)
                except:
                    pass

            import threading
            cleanup_thread = threading.Thread(target=cleanup)
            cleanup_thread.daemon = True
            cleanup_thread.start()

        elif self.commande:
            # Créer un fichier temporaire pour le script PowerShell
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8') as ps_file:
                ps_file.write(f'$Host.UI.RawUI.WindowTitle = "Command Execution"\n')
                ps_file.write('try {\n')
                # Obtenir les limites du système
                ps_file.write('    $maxWindowSize = $Host.UI.RawUI.MaxWindowSize\n')
                ps_file.write('    $maxBufferSize = $Host.UI.RawUI.MaxPhysicalWindowSize\n')
                # Calculer les dimensions finales
                ps_file.write(f'    $desiredWidth = [Math]::Min({self.largeur}, $maxWindowSize.Width)\n')
                ps_file.write(f'    $desiredHeight = [Math]::Min({self.hauteur}, $maxWindowSize.Height)\n')
                # Définir d'abord la taille de la fenêtre
                ps_file.write('    $windowSize = New-Object Management.Automation.Host.Size($desiredWidth, $desiredHeight)\n')
                ps_file.write('    $Host.UI.RawUI.WindowSize = $windowSize\n')
                # Puis définir le buffer légèrement plus grand
                ps_file.write('    $bufferSize = New-Object Management.Automation.Host.Size($desiredWidth, [Math]::Max($desiredHeight, 300))\n')
                ps_file.write('    $Host.UI.RawUI.BufferSize = $bufferSize\n')
                ps_file.write('} catch {\n')
                ps_file.write('    Write-Host "Adjusting window size..."\n')
                ps_file.write('    try {\n')
                ps_file.write('        $defaultWidth = 80\n')
                ps_file.write('        $defaultHeight = 25\n')
                ps_file.write('        $Host.UI.RawUI.WindowSize = New-Object Management.Automation.Host.Size($defaultWidth, $defaultHeight)\n')
                ps_file.write('        $Host.UI.RawUI.BufferSize = New-Object Management.Automation.Host.Size($defaultWidth, 300)\n')
                ps_file.write('    } catch {\n')
                ps_file.write('        Write-Host "Using system default size"\n')
                ps_file.write('    }\n')
                ps_file.write('}\n')
                ps_file.write(f'{self.commande}\n')
                ps_file.write('Write-Host ""\n')
                ps_file.write('Write-Host "Press any key to continue..."\n')
                ps_file.write('$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")\n')
                ps_script = ps_file.name

            # Lancer PowerShell dans une nouvelle fenêtre sans attendre
            cmd = f'start powershell -NoProfile -ExecutionPolicy Bypass -File "{ps_script}"'
            process = subprocess.Popen(cmd, shell=True)
            
            # Démarrer un thread pour nettoyer les fichiers temporaires après un délai
            def cleanup():
                time.sleep(2)  # Attendre que la fenêtre soit bien ouverte
                try:
                    os.unlink(ps_script)
                except:
                    pass

            import threading
            cleanup_thread = threading.Thread(target=cleanup)
            cleanup_thread.daemon = True
            cleanup_thread.start()

        else:
            print(" Vous devez spécifier soit une commande, soit un texte à afficher ")

# Exemple d'utilisation
if __name__ == "__main__":
    long_texte = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
    Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
    """
    terminal = CmdTerminal(80, 25, texte=long_texte)
    terminal.run()