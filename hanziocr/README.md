# HanziOCR

Reconheça, traduza e ouça texto chinês (hanzi) direto da tela com um clique.  
Leve, modular e totalmente integrado ao desktop Linux.

---

## 🧩 Visão geral

- Projeto: **HanziOCR**  
- Comando principal: `hanziocr`  
- Local de instalação: `~/.local/share/hanziocr`  
- Pasta temporária: `/tmp/hanzi_ocr/`  
- Histórico: `~/.cache/hanziocr/history.log`  
- Idioma configurável: `/tmp/hanzi_ocr/lang.conf` (contém `pt` ou `en`)

---

## ⚙️ Fluxo de funcionamento

1. O usuário executa `hanziocr start`, que garante que o servidor e o tray estejam ativos.  
2. Uma área da tela é capturada usando **Spectacle** (outros como *grim* ou *maim* não foram testados).  
3. O arquivo `request.json` é criado com o caminho da imagem.  
4. O servidor (`hanzi_ocr_server.py`) realiza OCR via **PaddleOCR**, converte para **pinyin** e traduz.  
5. O resultado é salvo em `response.json`, copiado para o clipboard, exibido por notificação e salvo no histórico.

---

## 📜 Scripts incluídos

1. `hanzi_capture.sh`  
   Captura a tela, envia a imagem ao servidor e exibe o resultado traduzido.  
   Copia o texto final para o clipboard e o adiciona ao histórico.

2. `hanzi_ocr_server.py`  
   Processa imagens enviadas, realiza OCR (PaddleOCR), gera pinyin e traduz.  
   Retorna o resultado em `response.json`.

3. `hanzi_ocr_tray.py`  
   Cria o ícone na bandeja do sistema com menu interativo:
   - Alternar servidor (iniciar/parar)
   - Alternar idioma (pt/en)
   - Ver histórico
   - Capturar, falar ou repetir resultado
   - Encerrar tudo (tray + servidor)

4. `hanzi_capture_speak.sh`  
   Versão que, além de capturar e traduzir, lê o texto em voz alta via **gTTS + mpv**.

5. `hanzi_replay.sh`  
   Reexibe o último resultado salvo em `response.json`.

6. `hanzi_kill.sh`  
   Encerra completamente o servidor e o tray, limpando processos do HanziOCR.

7. `install.sh`  
   Script de instalação automática; copia scripts, instala dependências e cria o comando `hanziocr`.

8. `uninstall.sh` *(gerado automaticamente pelo instalador)*  
   Remove completamente a instalação.

---

## 🧰 Instalação automática

Coloque todos os arquivos na mesma pasta (por exemplo: `~/Downloads/hanziocr`) e execute o instalador com:

Executar `./install.sh` na pasta onde os arquivos foram extraídos.

O instalador:

- detecta automaticamente o gerenciador de pacotes (`dnf`, `apt`, `pacman`, `zypper`)  
- instala dependências do sistema e do Python  
- copia os scripts para `~/.local/share/hanziocr/`  
- cria o comando executável `hanziocr` em `~/.local/bin/`  
- gera o desinstalador `uninstall.sh`

Após a instalação, execute `hanziocr start` para iniciar.

---

## ⚙️ Comandos disponíveis

- `hanziocr start` → captura texto e traduz  
- `hanziocr speak` → captura, traduz e lê em voz alta  
- `hanziocr replay` → mostra o último resultado  
- `hanziocr tray` → abre o ícone da bandeja manualmente  
- `hanziocr server` → inicia o servidor OCR diretamente  
- `hanziocr kill` → encerra todos os processos do HanziOCR  

---

## 🖥️ Tray do sistema

O ícone na bandeja (pystray) oferece:

- 🟩 Iniciar / 🟥 Parar servidor  
- 🌐 Alternar idioma (pt / en)  
- 📜 Ver histórico (abre `~/.cache/hanziocr/history.log`)  
- 📂 Abrir pasta temporária (`/tmp/hanzi_ocr/`)  
- 🎥 Captura  
- 🔊 Speak  
- ♻️ Replay  
- 🧹 Kill All  
- 🚪 Sair (encerra tudo)

O histórico é mantido com as entradas mais recentes no topo.

---

## 🧩 Dependências

**Testado apenas em:** Nobara Linux (base Fedora).  
Outras distribuições podem funcionar, mas **não foram testadas**.

**Dependências Python (instaladas automaticamente pelo script):**  
- paddleocr  
- paddlepaddle (escolher versão compatível com sua CPU/GPU)  
- jieba  
- pypinyin  
- pystray  
- Pillow  
- deep-translator  

**Dependências de sistema (exemplo Fedora):**  
- spectacle (ou outro utilitário de captura)  
- jq  
- libnotify / notify-send  
- zenity  
- translate-shell (`trans`)  
- xclip ou wl-clipboard  
- mpv  
- ferramentas de compilação (gcc, g++, cmake, etc.)  
- python3-devel  

Observação:  
O pacote `paddlepaddle` tem variantes (CPU, CUDA, ROCm). Consulte sua GPU e a documentação do Paddle antes de instalar a versão GPU.

---

## 📁 Estrutura de pastas

- `~/.local/share/hanziocr/` → scripts e arquivos instalados  
- `/tmp/hanzi_ocr/` → comunicação interna (request/response) e arquivos temporários  
- `~/.cache/hanziocr/` → histórico persistente (history.log)  
- `~/.local/bin/hanziocr` → comando executável  

---

## 💬 Mensagens esperadas

- 🈶 Servidor OCR pronto — servidor iniciado corretamente  
- 🚫 Nenhum OCR disponível — falha ao inicializar OCR  
- ✅ OCR completo — processamento concluído com sucesso  

---

## 📦 Observações importantes

- Suporte offline (ArgosTranslate) **não está implementado** por padrão  
- O projeto foi desenvolvido e **testado apenas em Nobara/Fedora**  
- Uso de ferramentas alternativas de captura (*grim*, *maim*) **não foi testado**  
- Mantenha as dependências instaladas para evitar falhas em runtime  

---

## ✨ Resumo

**HanziOCR** combina OCR, pinyin e tradução online para ler texto chinês diretamente da tela com um atalho.  
Ideal para estudos, legendas e leitura em tempo real.

Execute: `hanziocr start`

Developed by: Tito Duque.✨
