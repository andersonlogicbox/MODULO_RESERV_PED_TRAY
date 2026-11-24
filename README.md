# Módulo de Reserva de Pedidos — Tray Commerce × ERP

> **Demonstração Interativa:** [Acessar Apresentação no GitHub Pages](https://andersonlogicbox.github.io/MODULO_RESERV_PED_TRAY/)

Este repositório contém a documentação técnica, evidências e a demonstração guiada do **Módulo de Reserva de Estoque por Pedido** desenvolvido para a integração entre o ERP Retaguarda e a plataforma de e-commerce **Tray Commerce**.

Embora o fluxo de validação tenha sido homologado com base no **Pedido Modelo #4141**, esta arquitetura e documentação servem como padrão oficial de implantação para **novos clientes** que necessitam de sincronização segura de estoque entre ERP físico e loja virtual.

---

## 🎯 Objetivo da Solução

Eliminar o **furo de estoque** e a **venda duplicada** de produtos entre o momento em que a venda ocorre na Tray e a emissão da Nota Fiscal (NF-e) no ERP, garantindo:
1. **Proteção Imediata:** Reserva virtual aplicada instantaneamente na importação do pedido.
2. **Sem Duplo Desconto:** Transição perfeita de "Reserva Virtual" para "Baixa Real" no faturamento da NF-e.
3. **Independência Operacional:** O PDV físico e o retaguarda continuam operando normalmente sem bloqueio de telas ou dados.

---

## 📐 Regra de Negócio

A fórmula aplicada pelo integrador e transmitida em tempo real à Tray é:

$$\text{Estoque Enviado à Tray} = \text{Estoque Físico Real (ERP)} - \text{Soma das Reservas de Pedidos Não Faturados}$$

---

## 🔄 Fluxo de Homologação (Passo a Passo)

| Etapa | Estoque Real (ERP) | Reserva Virtual | Saldo na Tray | Descrição |
| :--- | :---: | :---: | :---: | :--- |
| **1. Inicial** | 43 un | 0 un | **43 un** | Nenhum pedido pendente. Tray reflete o saldo real. |
| **2. Pedido Importado** | 43 un | 1 un | **42 un** | Pedido vira Orçamento com `STATUS_RESERVA=1`. Tray é descontada. |
| **3. NF-e Emitida** | 42 un | 0 un | **42 un** | Baixa física concluída no ERP. Reserva liberada. Tray permanece estável. |
| **4. NF-e Cancelada** | 43 un | 0 un | **43 un** | Estorno fiscal restaura o estoque real. Tray recebe o saldo integral. |

---

## 🖥️ Estrutura do Repositório

- `index.html` / `apresentacao_demo_reserva_4141.html`: Apresentação interativa com split-screen, visualizador de evidências em abas, zoom/lightbox e atalhos de teclado.
- `prints/`: Prints reais coletados das consultas de produtos no Retaguarda e no painel da Tray Commerce.
- `evidencias_demo.json`: Dados brutos estruturados de estoque, pedidos e logs coletados na homologação.
- `gera_apresentacao.py`: Script Python para regeneração automática do relatório/dashboard.

---

## 🌐 Como Acessar a Demonstração Online

Acesse diretamente pelo navegador através do GitHub Pages:
👉 **[https://andersonlogicbox.github.io/MODULO_RESERV_PED_TRAY/](https://andersonlogicbox.github.io/MODULO_RESERV_PED_TRAY/)**
