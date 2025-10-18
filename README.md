# HanziOcr

Reconheça, traduza e ouça texto chinês (hanzi) direto da tela com um clique.  
Leve, modular e totalmente integrado ao desktop Linux.  

---

## 🧩 Visão geral

- Projeto: **HanziOcr**  
- Script principal do usuário: `hanzi_capture.sh` (inicia servidor e tray automaticamente)  
- Servidor OCR: `hanzi_ocr_server.py` (processa imagens e gera resultados)  
- Tray do sistema: `hanzi_ocr_tray.py` (ícone com menu e controles)  
- Pasta temporária: `/tmp/hanzi_ocr/`  
- Comunicação: `request.json` (entrada) → `response.json` (saída)  
- Idioma configurável: `/tmp/hanzi_ocr/lang.conf` (pode conter "pt" ou "en")

---

## ⚙️ Fluxo de funcionamento

1. O usuário executa `hanzi_capture.sh`, que garante que o servidor e o tray estejam ativos.  
2. Uma área da tela é capturada usando **Spectacle** (Tenta utilizar outros como grim caso não possua o spectacle, mas nenhum outro foi testado).  
3. O arquivo `request.json` é criado com o caminho da imagem.  
4. O servidor (`hanzi_ocr_server.py`) detecta o pedido, faz OCR com **PaddleOCR**, gera **pinyin** e tenta traduzir.  
5. O resultado é salvo em `response.json`, copiado para o clipboard e exibido por notificação.  

---

## 📜 Scripts incluídos

### 1. hanzi_capture.sh
Captura uma área da tela (via Spectacle) e garante que o servidor e o tray estejam em execução.  
Envia o pedido ao servidor e mostra o resultado por notificação.  
Também copia o texto traduzido para o clipboard.  

### 2. hanzi_ocr_server.py
Processa as imagens enviadas.  
Monitora `/tmp/hanzi_ocr/`, realiza OCR (PaddleOCR), converte para pinyin e traduz.  
Gera `response.json` com texto, pinyin e tradução.  

### 3. hanzi_ocr_tray.py
Cria o ícone na bandeja do sistema, oferecendo menu com:
- Alternar servidor (iniciar/parar)  
- Alternar idioma (português/inglês)  
- Abrir `/tmp/hanzi_ocr/`  
- Executar captura, fala e repetição  
- Encerrar tudo (encerra servidor e tray)

### 4. hanzi_capture_speak.sh
Versão do `hanzi_capture.sh` que, além de capturar e traduzir,  
lê o texto em voz alta e faz busca no dicionário MDBG.  
Também copia o texto para o clipboard.  

### 5. hanzi_replay.sh
Reexibe o último resultado (texto, pinyin e tradução)  
a partir de `response.json` e copia o texto novamente para o clipboard.  

### 6. hanzi_kill.sh
Encerra completamente o servidor e o tray, limpando processos do HanziOcr.  

---

## 🛠️ Instalação

### 1. Colocar os scripts no PATH
Crie uma pasta e copie os arquivos para lá:  
`mkdir -p ~/.local/bin`  
`cp hanzi_capture.sh hanzi_ocr_server.py hanzi_ocr_tray.py hanzi_capture_speak.sh hanzi_replay.sh hanzi_kill.sh ~/.local/bin/`  
`chmod +x ~/.local/bin/hanzi_*`

### 2. Instalar dependências

**Dependências Python (instalar com pip):**  
`python3 -m pip install --user paddleocr paddlepaddle jieba pypinyin argostranslate`

**Dependências de sistema (exemplo Fedora/DNF):**  
`sudo dnf install spectacle jq notify-send zenity gcc g++ cmake python3-devel translate-shell`

**Outras distros:**  
- Debian/Ubuntu → usar `apt install`  
- Arch/Manjaro → usar `pacman -S`  
- openSUSE → usar `zypper install`

**Importante:**  
O pacote `paddlepaddle` deve corresponder à sua GPU/CPU (ROCm, CUDA ou CPU).  
Consulte a documentação oficial para escolher a versão correta.  

---

## ⚙️ Configuração e uso

- Idioma de tradução: gravar `pt` ou `en` em `/tmp/hanzi_ocr/lang.conf`.  
- O tray permite alternar o idioma facilmente.  
- Logs do servidor aparecem no terminal do `hanzi_ocr_server.py`.  
- Use `hanzi_capture.sh` como ponto de entrada principal.  

---

## 💬 Mensagens esperadas

- 🈶 **Servidor OCR pronto** — servidor iniciado corretamente.  
- 🚫 **Nenhum OCR disponível** — falha ao inicializar OCR.  
- ✅ **OCR completo** — processamento concluído com sucesso.  

---

## 📦 Observações finais

- Nome oficial do projeto: **HanziOcr**  
- Script principal: **hanzi_capture.sh**  
- Todos os scripts devem manter seus nomes originais.  
- O **ArgosTranslate** é opcional, mas permite tradução offline (Configuração desativada por enquanto).  
- Mantenha todas as dependências instaladas para evitar falhas em runtime.  

---

## ✨ Resumo rápido

**HanziOcr** combina OCR, pinyin e tradução (online/offline)  
para ler texto chinês diretamente da tela com apenas um atalho.  
Ideal para estudos, legendas, leitura e tradução de interfaces em tempo real.
