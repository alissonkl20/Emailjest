import pyautogui
import time
import webbrowser
import os
import requests
import subprocess

def open_vscode_and_run():
    # Abrir o VS Code
    os.system("code .")
    time.sleep(5)  # Aguarda o VS Code abrir

    # Abrir o terminal integrado no VS Code e executar o comando
    pyautogui.hotkey('ctrl', 'shift', '`')  # Abre o terminal integrado
    time.sleep(2)
    pyautogui.typewrite("cd C:\\Users\\Buffer\\Documents\\craping\\app")
    pyautogui.press("enter")
    pyautogui.typewrite("python app.py")
    pyautogui.press("enter")

def open_browser_and_access_url():
    # Inicia o servidor Flask em um processo separado
    server_process = subprocess.Popen(
        ["python", "app.py"],
        cwd="C:\\Users\\Buffer\\Documents\\craping\\app",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Aguarda o servidor iniciar
    for _ in range(10):  # Tenta por até 10 vezes (50 segundos no total)
        try:
            response = requests.get("http://127.0.0.1:5000/api/emails")
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(5)

    # Abrir o navegador padrão e acessar a URL
    webbrowser.open("http://127.0.0.1:5000/api/emails")

    # Opcional: Finaliza o processo do servidor após o uso (se necessário)
    # server_process.terminate()

if __name__ == "__main__":
    open_vscode_and_run()
    open_browser_and_access_url()