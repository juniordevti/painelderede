#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Painel de Rede
Software desktop para visualizar informações básicas de rede.
Autor: Junior Silva
Versão: 1.0
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import socket
import platform

try:
    import requests  # type: ignore
except ImportError:
    requests = None  # type: ignore


class PainelRede:
    def __init__(self, root):
        self.root = root
        self.root.title("Painel de Informações de Rede")
        # altura aumentada para acomodar todos os botões
        self.root.geometry("420x480")
        # permitir redimensionar verticalmente caso novo botão seja adicionado
        self.root.resizable(False, True)

        # define tema hacker: fundo preto com texto verde
        self.root.configure(bg="black")
        self.fonte = ("Consolas", 12)  # fonte monoespaçada
        self.cor_texto = "#00FF00"  # verde brilhante
        self.cor_botao_bg = "#000000"
        self.cor_botao_fg = "#00FF00"
        self.criar_interface()

    # ==============================
    # FUNÇÕES DE REDE
    # ==============================
    def obter_ip_local(self):
        try:
            hostname = socket.gethostname()
            ip_local = socket.gethostbyname(hostname)
            messagebox.showinfo("IP Local", f"Seu IP Local é:\n{ip_local}")
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível obter o IP local.\n\n{erro}")

    def obter_ip_publico(self):
        try:
            resposta = requests.get("https://api.ipify.org", timeout=5)
            ip_publico = resposta.text
            messagebox.showinfo("IP Público", f"Seu IP Público é:\n{ip_publico}")
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível obter o IP público.\n\n{erro}")

    def obter_nome_maquina(self):
        try:
            nome = socket.gethostname()
            messagebox.showinfo("Nome da Máquina", f"Nome do computador:\n{nome}")
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))

    def obter_info_sistema(self):
        try:
            sistema = platform.system()
            versao = platform.version()
            arquitetura = platform.machine()
            processador = platform.processor()
            info = (
                f"Sistema Operacional: {sistema}\n"
                f"Versão: {versao}\n"
                f"Arquitetura: {arquitetura}\n"
                f"Processador: {processador}"
            )
            messagebox.showinfo("Informações do Sistema", info)
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))

    def obter_redes_wifi(self):
        """Abre janela que lista redes Wi‑Fi detectadas e permite atualizar.

        A identificação de IP não é possível sem conexão, por isso não aparece
        na lista."""
        try:
            redes = self._scan_wifi()
        except Exception as erro:
            messagebox.showerror(
                "Erro", f"Não foi possível listar redes Wi-Fi.\n\n{erro}"
            )
            return

        # criar janela de resultado
        janela = tk.Toplevel(self.root)
        janela.title("Redes Wi-Fi disponíveis")
        janela.configure(bg="black")
        janela.geometry("400x300")
        lista = tk.Listbox(
            janela,
            font=self.fonte,
            fg=self.cor_texto,
            bg="black",
            selectbackground="#333333",
            activestyle="none",
        )
        lista.pack(fill="both", expand=True, padx=10, pady=10)
        for item in redes:
            lista.insert("end", item)

        def atualizar():
            lista.delete(0, "end")
            try:
                novas = self._scan_wifi()
                if novas:
                    for it in novas:
                        lista.insert("end", it)
                else:
                    lista.insert("end", "Nenhuma rede encontrada")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        botao = tk.Button(
            janela,
            text="🔄 Atualizar",
            command=atualizar,
            font=self.fonte,
            fg=self.cor_botao_fg,
            bg=self.cor_botao_bg,
            activebackground="#333333",
            activeforeground=self.cor_botao_fg,
            relief="flat",
        )
        botao.pack(pady=5)

    def _scan_wifi(self):
        """Retorna lista de strings SSID - BSSID usando netsh."""
        import subprocess, re

        output = subprocess.check_output(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        )
        redes = []
        current_ssid = None
        for line in output.splitlines():
            ssid_match = re.match(r"^\s*SSID\s+\d+\s+:\s+(.*)$", line)
            if ssid_match:
                current_ssid = ssid_match.group(1)
            bssid_match = re.match(r"^\s*BSSID\s+\d+\s+:\s+(.*)$", line)
            if bssid_match and current_ssid:
                redes.append(f"{current_ssid} - {bssid_match.group(1)}")
        if not redes:
            redes = ["Nenhuma rede encontrada"]
        redes.append("(IP não disponível sem conexão)")
        return redes

    def obter_senha_wifi(self):
        """Pede SSID e mostra a senha salva (se houver) usando netsh."""
        try:
            ssid = simpledialog.askstring(
                "Senha Wi-Fi", "Digite o SSID da rede:", parent=self.root
            )
            if not ssid:
                return
            self._mostrar_senha_para_ssid(ssid)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _mostrar_senha_para_ssid(self, ssid: str):
        import subprocess, re

        output = subprocess.check_output(
            ["netsh", "wlan", "show", "profile", f"name={ssid}", "key=clear"],
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        )
        match = re.search(r"Key Content\s+:\s+(.*)", output)
        if match:
            senha = match.group(1)
        else:
            senha = "(não encontrada)"
        messagebox.showinfo("Senha Wi-Fi", f"Rede: {ssid}\nSenha: {senha}")

    def obter_senha_wifi_conectada(self):
        """Identifica SSID atual e mostra sua senha salva se houver."""
        try:
            import subprocess, re

            output = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
            )
            match = re.search(r"^\s*SSID\s*:\s*(.+)$", output, re.MULTILINE)
            if not match:
                messagebox.showinfo(
                    "Senha Wi-Fi", "Não conectado a nenhuma rede Wi-Fi."
                )
                return
            ssid = match.group(1).strip()
            self._mostrar_senha_para_ssid(ssid)
        except subprocess.CalledProcessError:
            messagebox.showerror(
                "Erro",
                "Falha ao obter informações da interface Wi-Fi.",
            )
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # ==============================
    # INTERFACE
    # ==============================
    def criar_interface(self):
        titulo = tk.Label(
            self.root,
            text="Painel de Informações de Rede",
            font=("Consolas", 16, "bold"),
            fg=self.cor_texto,
            bg="black",
        )
        titulo.pack(pady=20)

        botoes = [
            ("📡 Mostrar IP Local", self.obter_ip_local),
            ("🌍 Mostrar IP Público", self.obter_ip_publico),
            ("🖥 Nome da Máquina", self.obter_nome_maquina),
            ("🔎 Informações do Sistema", self.obter_info_sistema),
            ("📶 Escanear redes Wi‑Fi", self.obter_redes_wifi),
            ("🔑 Mostrar senha Wi‑Fi", self.obter_senha_wifi),
            ("🔒 Senha da rede atual", self.obter_senha_wifi_conectada),
            ("❌ Sair", self.root.quit),
        ]

        for texto, comando in botoes:
            botao = tk.Button(
                self.root,
                text=texto,
                width=35,
                height=2,
                command=comando,
                font=self.fonte,
                fg=self.cor_botao_fg,
                bg=self.cor_botao_bg,
                activebackground="#333333",
                activeforeground=self.cor_botao_fg,
                relief="flat",
            )
            botao.pack(pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = PainelRede(root)
    root.mainloop()
