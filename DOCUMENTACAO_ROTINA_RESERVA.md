# Documentação Técnica: Módulo de Reserva de Pedidos (Tray Commerce × ERP)

> **Registro Histórico de Engenharia:** Desenvolvimento inicial no Claude Code e evolução/deploy executivo no Antigravity.

---

## 1. Visão Geral e Contexto da Solução

O **Módulo de Reserva de Pedidos** foi desenvolvido para solucionar um desafio crítico na integração entre o **ERP Retaguarda** (gestão física/lojas) e a plataforma de e-commerce **Tray Commerce**:

* **Problema:** Entre o momento em que um cliente compra na Tray e a emissão formal da Nota Fiscal (NF-e) no ERP (faturamento), o estoque físico ainda não foi baixado no banco de dados. Sem um mecanismo de proteção, outro cliente poderia comprar a mesma peça na Tray ou no PDV físico, gerando **furo de estoque / venda duplicada**.
* **Solução:** Aplicação de **Reserva Virtual Automática** na importação do pedido como Orçamento (`STATUS_RESERVA=1`, `STATUS=2`).
* **Regra Fundamental de Sincronia com a Tray:**
  $$\text{Estoque Enviado à Tray} = \text{Estoque Físico Real (ERP)} - \text{Soma das Reservas de Pedidos Não Faturados}$$

---

## 2. Fase 1: Desenvolvimento e Homologação Inicial no Claude Code

Nesta etapa, todo o core da integração, os testes automatizados com mock e a primeira versão de evidências foram construídos:

### 2.1. Ambiente de Teste e Mock
* **`mock_tray.py`**: Servidor local simulando a API REST da Tray Commerce para receber as chamadas do integrador sem depender de uma loja de produção.
* **`clona_pedido.py` / `demo_guiado.py`**: Scripts para clonar e injetar o **Pedido Modelo #4141** no fluxo do integrador.
* **Itens utilizados no Pedido Modelo #4141 (1 un cada):**
  1. `27176` – *BALAO LISO CHAMPAGNE 5* (Estoque Real inicial: 43 un)
  2. `27218` – *BALAO LISO ROSE QUARTZ 5* (Estoque Real inicial: 31 un)
  3. `27424` – *BALAO CROMADO ROSE GOLD 5* (Estoque Real inicial: 59 un)

### 2.2. Execução dos 4 Momentos do Ciclo de Reserva
1. **Passo 1 (Antes da importação):** Consulta de estoque no ERP comprovando que não havia reservas e a Tray exibia o estoque pleno (43, 31, 59).
2. **Passo 2 (Importação do Pedido #4141):** O integrador grava o orçamento `42146` com `STATUS_RESERVA=1`. A rotina abate 1 unidade de cada produto e reenvia à Tray (42, 30, 58).
3. **Passo 2.1 (Conferência no ERP):** Consulta na tela de produtos exibindo a reserva de 1 unidade visível na barra inferior.
4. **Passo 3 (Faturamento NF-e):** Emissão simulada da NF-e. Ocorre a baixa real do estoque físico (42, 30, 58) e a reserva zera. O saldo enviado à Tray **não sofre alteração**, comprovando que não há duplo desconto.
5. **Passo 4 (Cancelamento da NF-e):** Estorno fiscal devolve o estoque físico para 43, 31 e 59. A Tray é atualizada imediatamente.

### 2.3. Coleta de Evidências e Apresentação V1
* **`evidencias_demo.json`**: Arquivo estruturado armazenando o log de eventos e os estados de saldo em cada etapa.
* **`prints/`**: Capturas da barra inferior do ERP Retaguarda (`passo1_itemX.png`, `passo2-1_itemX.png`, etc.) e imagens do painel Tray geradas via script (`gera_pedido_tray_img.py` e `gera_estoque_tray_img.py`).
* **`gera_apresentacao.py` (V1)**: Script gerador do arquivo `apresentacao_demo_reserva_4141.html`.
* **Gargalos identificados na V1:**
  - Prints empilhados verticalmente geravam **scroll excessivo**, perdendo o formato de apresentação/slides.
  - Dificuldade de comparar produtos lado a lado sem rolar a página.
  - Navegação que avançava ao clicar em qualquer ponto do texto.
  - Imagens com textos miúdos do ERP sem mecanismo de zoom.

---

## 3. Fase 2: Evolução, Refatoração Executiva e Deploy no Antigravity

Nesta fase, a apresentação foi transformada em um **Dashboard Interativo Split-Screen de nível executivo** e publicada globalmente na nuvem:

### 3.1. Backup Preventivo de Segurança
Antes de qualquer alteração, foi realizado o backup recursivo integral da pasta de trabalho:
* **Diretório:** `../backup_teste_mock_tray_20261124_145311`

### 3.2. Reformulação do `gera_apresentacao.py` (Versão 2.0)
O script gerador foi completamente reescrito para eliminar o scroll e oferecer usabilidade profissional:
1. **Layout Split-Screen Fixo:** 
   - Coluna esquerda: Título, badges, tabela de saldos colorida, logs de terminal e alertas explicativos.
   - Coluna direita: Visualizador de evidências em tamanho otimizado para o monitor.
2. **Sistema de Abas (Tabs) para Evidências:**
   - Cada produto do pedido e os painéis da Tray possuem abas individuais (`[Cód 27176]`, `[Cód 27218]`, `[Cód 27424]`, `[🛒 Painel Tray]`). A troca é instantânea sem rolagem de tela.
3. **Zoom / Lightbox Modal:**
   - Clique em qualquer print abre a imagem ampliada em tela cheia com alta definição para leitura detalhada da barra inferior do ERP (fechamento via `ESC` ou clique fora).
4. **Stepper Superior Clicável:**
   - Barra superior com navegação de etapas: `0. Visão Geral` → `1. Antes` → `2. Reserva` → `2.1 Estoque Reservado` → `3. Faturamento NF-e` → `4. Cancelamento NF-e` → `Resumo Comparativo`.
5. **Ergonomia e Atalhos de Teclado:**
   - Navegação por botões dedicados (*Anterior* / *Próximo*).
   - Setas `←` e `→` para navegar etapas.
   - Teclas numéricas `1`, `2`, `3`, `4`, `5` para alternar as abas das imagens.
6. **Matriz de Resumo Comparativo:**
   - Tabela consolidada comparando os 4 momentos do item principal e detalhando os 3 pilares técnicos (Sem furo de estoque, Sem duplo desconto, Independência do PDV físico).

### 3.3. Padronização para Hospedagem Web
* **`index.html`**: Gerado a partir do layout v2 para carregar como página raiz em servidores web.
* **`.nojekyll`**: Adicionado à raiz para desativar o processamento do Jekyll no GitHub e carregar arquivos estáticos/HTML puros instantaneamente.
* **`README.md`**: Criado com formatação GitHub Flavored Markdown contendo a explicação da regra e o link oficial da demo.
* **`.gitignore`**: Configurado para omitir logs pesados (`requests.log.jsonl`), arquivos `.out` e mocks descartáveis.

### 3.4. Versionamento Git e Deploy no GitHub Pages
1. **Inicialização do Repositório Git:**
   - Branch padrão definida como `main`.
   - Commit inicial estruturado com 29 arquivos rastreados (código, templates, dados e pasta `prints/`).
2. **Push Remoto:**
   - Repositório: `https://github.com/andersonlogicbox/MODULO_RESERV_PED_TRAY.git`
   - O token de acesso pessoal fornecido foi utilizado na autenticação segura via API/SSH e imediatamente removido da URL remota local (`.git/config`) para proteção de credenciais.
3. **Adequação de Visibilidade e Ativação do GitHub Pages:**
   - O repositório estava originalmente como *privado*. Como o GitHub Pages em contas gratuitas requer repositório público, a visibilidade foi alterada para *público* via API do GitHub.
   - Ativação do endpoint do Pages apontando para `branch: main`, `path: /`.
   - Build concluído e validado com status HTTP 200.

---

## 4. Tabela de Consolidação dos Estados de Estoque

| Momento | Real ERP | Reserva Virtual | Disponível Tray | Comportamento do Sistema |
| :--- | :---: | :---: | :---: | :--- |
| **1. Antes da Importação** | 43 | 0 | **43** | Estado livre. Nenhuma venda em andamento. |
| **2. Importação do Pedido #4141** | 43 | **1** | **42** | `STATUS_RESERVA=1`. A Tray tem o saldo abatido para evitar venda concorrente. |
| **3. Faturamento (NF-e Emitida)** | 42 | 0 | **42** | Baixa real no estoque físico. A reserva é desativada. Saldo na Tray permanece estável. |
| **4. Cancelamento da NF-e** | 43 | 0 | **43** | Estorno fiscal devolve a mercadoria ao estoque e reenvia 43 à Tray. |

---

## 5. Links e Referências

* 🌐 **Apresentação Online (GitHub Pages):**  
  [https://andersonlogicbox.github.io/MODULO_RESERV_PED_TRAY/](https://andersonlogicbox.github.io/MODULO_RESERV_PED_TRAY/)
* 📦 **Repositório do Projeto:**  
  [https://github.com/andersonlogicbox/MODULO_RESERV_PED_TRAY](https://github.com/andersonlogicbox/MODULO_RESERV_PED_TRAY)
* 🗄️ **Backup Local Pré-Refatoração:**  
  `../backup_teste_mock_tray_20261124_145311`

---

## 6. Procedimento para Aplicação em Novos Clientes

Quando for apresentar ou implantar a solução para um novo cliente:
1. Envie o link do **GitHub Pages** para o cliente ou diretoria avaliar o fluxo visual.
2. Na implantação técnica, garanta que o integrador esteja configurado com:
   - Gravação de pedidos com flag de reserva habilitada (`STATUS_RESERVA=1`).
   - Gatilho no faturamento para liberação da reserva na emissão da NF-e.
   - Rotina de cálculo de sincronia: `Disponível = Estoque_Filial - Soma_Reservas`.
