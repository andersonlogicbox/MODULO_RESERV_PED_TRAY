import json, html, re, os

# Carrega os dados coletados da execução real/mock
ev = json.load(open('evidencias_demo.json', encoding='utf-8'))

itens_info = {
    "27176": "BALAO LISO CHAMPAGNE 5",
    "27218": "BALAO LISO ROSE QUARTZ 5",
    "27424": "BALAO CROMADO ROSE GOLD 5"
}

def render_tabela_estoque(estoque_lista):
    rows = []
    for item in estoque_lista:
        cod = str(item['cod'])
        desc = item['desc']
        real = int(item['real'])
        reservado = int(item['reservado'])
        disponivel = int(item['disponivel'])
        
        badge_res = (
            f'<span class="badge badge-warning">+{reservado} un</span>'
            if reservado > 0 else '<span class="badge badge-muted">0</span>'
        )
        badge_tray = f'<span class="badge badge-success font-mono font-bold text-lg">{disponivel}</span>'
        
        rows.append(f'''
        <tr>
            <td class="font-mono text-cyan-400 font-semibold">{cod}</td>
            <td class="text-slate-200">{desc}</td>
            <td class="text-right font-mono text-slate-300">{real}</td>
            <td class="text-right">{badge_res}</td>
            <td class="text-right">{badge_tray}</td>
        </tr>
        ''')
    
    return f'''
    <div class="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Cód</th>
                    <th>Produto</th>
                    <th class="text-right">Estoque Real</th>
                    <th class="text-right">Reserva Virtual</th>
                    <th class="text-right">Enviado à Tray</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </div>
    '''

def render_logs(lista_logs, filtro=None, max_linhas=6):
    filtrados = [l for l in lista_logs if (not filtro or re.search(filtro, l, re.I))]
    if not filtrados:
        return ''
    corpo = html.escape('\n'.join(l[:220] for l in filtrados[:max_linhas]))
    return f'''
    <div class="terminal-card">
        <div class="terminal-header">
            <span class="terminal-dot red"></span>
            <span class="terminal-dot yellow"></span>
            <span class="terminal-dot green"></span>
            <span class="terminal-title">Log do Integrador Tray</span>
        </div>
        <pre class="terminal-body">{corpo}</pre>
    </div>
    '''

# Dados dos passos
base = ev['p1']['estoque']
r0 = [x['real'] for x in base]
def calc_step(e, real, res): 
    return [dict(x, real=real[i], reservado=res[i], disponivel=real[i]-res[i]) for i, x in enumerate(e)]

p3_estoque = calc_step(base, [x-1 for x in r0], [0, 0, 0])
p4_estoque = calc_step(base, r0, [0, 0, 0])

steps_data = [
    {
        "id": "step0",
        "short_title": "Visão Geral",
        "badge": "Arquitetura",
        "title": "Módulo de Reserva de Estoque – Tray × ERP",
        "subtitle": "Homologação do fluxo completo do Pedido Tray #4141 com 3 produtos",
        "left_html": '''
            <div class="flow-card">
                <h3 class="section-title">Como a Reserva Funciona</h3>
                <p class="description">
                    Para garantir que produtos vendidos na Tray não sofram <b>furo de estoque</b> ou <b>venda duplicada</b> enquanto aguardam faturamento, o integrador aplica uma <b>reserva virtual</b> automática assim que o pedido é importado.
                </p>
                <div class="formula-box">
                    <div class="formula-label">Fórmula enviada à Tray em tempo real:</div>
                    <div class="formula-math">
                        <span class="formula-item">Estoque Real (ERP)</span>
                        <span class="formula-op">−</span>
                        <span class="formula-item highlight">Reservas (Pedidos não faturados)</span>
                        <span class="formula-op">=</span>
                        <span class="formula-item result">Estoque Disponível Tray</span>
                    </div>
                </div>
                <div class="steplist">
                    <div class="steplist-item">
                        <span class="steplist-num">1</span>
                        <div><b>Estoque Inicial:</b> Produtos sem reservas, saldo real sincronizado.</div>
                    </div>
                    <div class="steplist-item">
                        <span class="steplist-num">2</span>
                        <div><b>Importação do Pedido:</b> Reserva ativada (<code>STATUS_RESERVA=1</code>) e estoque Tray descontado.</div>
                    </div>
                    <div class="steplist-item">
                        <span class="steplist-num">3</span>
                        <div><b>Faturamento (NF-e):</b> Baixa do estoque real no ERP e liberação da reserva. O saldo na Tray não sofre duplo desconto.</div>
                    </div>
                    <div class="steplist-item">
                        <span class="steplist-num">4</span>
                        <div><b>Cancelamento da NF-e:</b> Estorno fiscal restaura o estoque real e atualiza a Tray.</div>
                    </div>
                </div>
            </div>
        ''',
        "tabs": [
            {
                "label": "🛒 Pedido Tray #4141",
                "img": "prints/pedido_tray_4141.png",
                "legend": "Espelho do Pedido #4141 com 3 itens (1 unidade cada) originado na Tray"
            },
            {
                "label": "📦 Estoque Inicial Tray",
                "img": "prints/passo1_tray.png",
                "legend": "Estoque dos 3 itens na plataforma Tray antes da importação"
            }
        ]
    },
    {
        "id": "step1",
        "short_title": "1. Antes da Importação",
        "badge": "Passo 1",
        "title": "Estoque Inicial no ERP e na Tray",
        "subtitle": "Sem pedidos pendentes. O estoque enviado à Tray é 100% o estoque físico real.",
        "left_html": f'''
            <div class="info-group">
                <p class="description">
                    Antes da importação do pedido 4141, a consulta de produtos no retaguarda mostra <b>Reserva = 0</b> na barra inferior.
                </p>
                {render_tabela_estoque(ev['p1']['estoque'])}
                <div class="callout callout-info">
                    <span class="callout-icon">ℹ️</span>
                    <div>
                        <b>Saldo Integral:</b> A Tray exibe exatamente a quantidade física do ERP (43, 31 e 59 unidades).
                    </div>
                </div>
            </div>
        ''',
        "tabs": [
            {"label": "Cód 27176 (Champagne)", "img": "prints/passo1_item1.png", "legend": "ERP Retaguarda: Saldo 43, Reserva 0"},
            {"label": "Cód 27218 (Rose Quartz)", "img": "prints/passo1_item2.png", "legend": "ERP Retaguarda: Saldo 31, Reserva 0"},
            {"label": "Cód 27424 (Chrome Rose)", "img": "prints/passo1_item3.png", "legend": "ERP Retaguarda: Saldo 59, Reserva 0"},
            {"label": "🛒 Painel Tray", "img": "prints/passo1_tray.png", "legend": "Painel Tray: Produtos com estoque pleno inicial"}
        ]
    },
    {
        "id": "step2",
        "short_title": "2. Importação & Reserva",
        "badge": "Passo 2",
        "title": "Importação do Pedido #4141 → Reserva Ativada",
        "subtitle": "O integrador grava o orçamento 42146 com STATUS_RESERVA=1",
        "left_html": f'''
            <div class="info-group">
                <p class="description">
                    Ao ler o pedido da Tray, o integrador cria o orçamento <b>{ev['p2']['pedido'][0]}</b> no ERP e ativa a reserva nativa para cada um dos itens.
                </p>
                {render_logs(ev['p2']['log'], 'Pedido Tray|aplicada|item reservado')}
                <div class="callout callout-warning">
                    <span class="callout-icon">⚡</span>
                    <div>
                        <b>Cálculo Imediato:</b> A rotina recalcula o saldo disponível de cada produto: <code>Real − Reserva = Enviado à Tray</code>.
                    </div>
                </div>
            </div>
        ''',
        "tabs": [
            {"label": "🛒 Pedido Tray 4141", "img": "prints/pedido_tray_4141.png", "legend": "Dados do pedido importado da Tray"},
            {"label": "📄 Orçamento ERP & Logs", "img": "prints/passo2.png", "legend": "Orçamento gerado no Retaguarda com a reserva ativada"}
        ]
    },
    {
        "id": "step2_1",
        "short_title": "2.1 Estoque Reservado",
        "badge": "Passo 2.1",
        "title": "Estoque com Reserva Visível no ERP",
        "subtitle": "A reserva de 1 unidade aparece na barra inferior e a Tray já reflete o saldo abatido",
        "left_html": f'''
            <div class="info-group">
                <p class="description">
                    No ERP, a quantidade reservada passa a ser exibida na barra inferior. A Tray recebe imediatamente a atualização com o estoque descontado, prevenindo que outro comprador adquira a mesma peça.
                </p>
                {render_tabela_estoque(ev['p21']['estoque'])}
                {render_logs(ev['p2']['log'], 'enviado ao Tray: \\d+$')}
                <div class="callout callout-success">
                    <span class="callout-icon">🛡️</span>
                    <div>
                        <b>Proteção Ativa:</b> A Tray recebeu 42, 30 e 58 unidades. O saldo físico continua 43, 31 e 59 até o faturamento.
                    </div>
                </div>
            </div>
        ''',
        "tabs": [
            {"label": "Cód 27176 (Reserva: 1)", "img": "prints/passo2-1_item1.png", "legend": "Barra inferior ERP: Estoque 43 | Reserva 1 | Disponível 42"},
            {"label": "Cód 27218 (Reserva: 1)", "img": "prints/passo2-1_item2.png", "legend": "Barra inferior ERP: Estoque 31 | Reserva 1 | Disponível 30"},
            {"label": "Cód 27424 (Reserva: 1)", "img": "prints/passo2-1_item3.png", "legend": "Barra inferior ERP: Estoque 59 | Reserva 1 | Disponível 58"}
        ]
    },
    {
        "id": "step3",
        "short_title": "3. Faturamento NF-e",
        "badge": "Passo 3",
        "title": "Venda Faturada (Emissão de NF-e)",
        "subtitle": "Baixa física do estoque e desativação da reserva sem duplicidade",
        "left_html": f'''
            <div class="info-group">
                <p class="description">
                    Ao emitir a NF-e do orçamento, o ERP realiza a baixa física real (Estoque Real cai 1 un) e <b>desativa a reserva virtual</b>.
                </p>
                {render_tabela_estoque(p3_estoque)}
                {render_logs(ev['p3']['log'], 'reserva em pedidos nao faturados: 1 -> 0|enviado ao Tray: \\d+')}
                <div class="callout callout-info">
                    <span class="callout-icon">✨</span>
                    <div>
                        <b>Sem Duplo Desconto:</b> O estoque enviado à Tray continua sendo <b>42, 30 e 58</b>. A transição da reserva virtual para a baixa real é 100% transparente.
                    </div>
                </div>
            </div>
        ''',
        "tabs": [
            {"label": "📄 NF-e Emitida no ERP", "img": "prints/passo3.png", "legend": "Comprovante de faturamento / NF-e emitida"},
            {"label": "Cód 27176 (Faturado)", "img": "prints/passo3_item1.png", "legend": "ERP: Estoque real agora é 42 e Reserva zerada"},
            {"label": "Cód 27218 (Faturado)", "img": "prints/passo3_item2.png", "legend": "ERP: Estoque real agora é 30 e Reserva zerada"},
            {"label": "Cód 27424 (Faturado)", "img": "prints/passo3_item3.png", "legend": "ERP: Estoque real agora é 58 e Reserva zerada"}
        ]
    },
    {
        "id": "step4",
        "short_title": "4. Cancelamento NF-e",
        "badge": "Passo 4",
        "title": "Cancelamento da NF-e e Restauração",
        "subtitle": "O estorno fiscal reverte a baixa e o estoque é reenviado integralmente",
        "left_html": f'''
            <div class="info-group">
                <p class="description">
                    Caso a nota fiscal seja cancelada, o ERP desfaz a baixa de estoque. O integrador detecta a alteração e atualiza a Tray imediatamente com os valores originais.
                </p>
                {render_tabela_estoque(p4_estoque)}
                {render_logs(ev['p4']['log'], 'enviado ao Tray: \\d+')}
                <div class="callout callout-success">
                    <span class="callout-icon">🔄</span>
                    <div>
                        <b>Restauração Completa:</b> Os produtos voltam para 43, 31 e 59 unidades tanto no ERP quanto no marketplace Tray.
                    </div>
                </div>
            </div>
        ''',
        "tabs": [
            {"label": "❌ Cancelamento NF-e", "img": "prints/passo4.png", "legend": "Registro de cancelamento da NF-e no ERP"},
            {"label": "Cód 27176 (Restaurado)", "img": "prints/passo4_item1.png", "legend": "ERP: Estoque restaurado para 43"},
            {"label": "Cód 27218 (Restaurado)", "img": "prints/passo4_item2.png", "legend": "ERP: Estoque restaurado para 31"},
            {"label": "Cód 27424 (Restaurado)", "img": "prints/passo4_item3.png", "legend": "ERP: Estoque restaurado para 59"},
            {"label": "🛒 Painel Tray Restaurado", "img": "prints/passo4_tray.png", "legend": "Tray: Estoque novamente sincronizado ao valor original"}
        ]
    },
    {
        "id": "step5",
        "short_title": "Resumo Comparativo",
        "badge": "Conclusão",
        "title": "Matriz Comparativa do Ciclo de Vida",
        "subtitle": "Visão consolidada da evolução de saldos em todas as etapas",
        "left_html": f'''
            <div class="info-group">
                <p class="description">
                    Acompanhamento do produto principal <b>27176 (BALAO LISO CHAMPAGNE 5)</b> ao longo de todas as etapas:
                </p>
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Etapa do Ciclo</th>
                                <th class="text-right">Estoque Real</th>
                                <th class="text-right">Reserva</th>
                                <th class="text-right">Disponível Tray</th>
                                <th>Status Operacional</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><b>1. Inicial (Sem pedidos)</b></td>
                                <td class="text-right font-mono">43</td>
                                <td class="text-right font-mono">0</td>
                                <td class="text-right font-mono text-emerald-400 font-bold">43</td>
                                <td><span class="badge badge-muted">Livre</span></td>
                            </tr>
                            <tr class="highlight-row">
                                <td><b>2. Pedido 4141 Importado</b></td>
                                <td class="text-right font-mono">43</td>
                                <td class="text-right font-mono text-amber-400 font-bold">1</td>
                                <td class="text-right font-mono text-emerald-400 font-bold">42</td>
                                <td><span class="badge badge-warning">Reserva Ativa</span></td>
                            </tr>
                            <tr>
                                <td><b>3. Pedido Faturado (NF-e)</b></td>
                                <td class="text-right font-mono">42</td>
                                <td class="text-right font-mono">0</td>
                                <td class="text-right font-mono text-emerald-400 font-bold">42</td>
                                <td><span class="badge badge-info">Baixa Real</span></td>
                            </tr>
                            <tr>
                                <td><b>4. NF-e Cancelada</b></td>
                                <td class="text-right font-mono">43</td>
                                <td class="text-right font-mono">0</td>
                                <td class="text-right font-mono text-emerald-400 font-bold">43</td>
                                <td><span class="badge badge-success">Estornado</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="summary-bullets">
                    <div class="bullet-box">
                        <div class="bullet-title">✅ Sem Furo de Estoque</div>
                        <div class="bullet-text">A reserva virtual imediata impede que o mesmo item seja vendido duas vezes na Tray durante a separação.</div>
                    </div>
                    <div class="bullet-box">
                        <div class="bullet-title">✅ Sem Duplo Desconto</div>
                        <div class="bullet-text">Ao faturar a NF-e, a reserva desativa simultaneamente com a baixa real, mantendo o saldo da Tray perfeitamente estável.</div>
                    </div>
                    <div class="bullet-box">
                        <div class="bullet-title">✅ Independência do PDV Físico</div>
                        <div class="bullet-text">O retaguarda e as lojas físicas visualizam o estoque real e a reserva na barra inferior sem travar rotinas locais.</div>
                    </div>
                </div>
            </div>
        ''',
        "tabs": [
            {"label": "🛒 Pedido de Origem", "img": "prints/pedido_tray_4141.png", "legend": "Pedido #4141 que originou todo o teste"},
            {"label": "📄 Orçamento Gerado", "img": "prints/passo2.png", "legend": "Orçamento 42146 com STATUS_RESERVA=1"},
            {"label": "📄 NF-e e Faturamento", "img": "prints/passo3.png", "legend": "Baixa fiscal e liberação da reserva"},
            {"label": "🛒 Painel Tray Final", "img": "prints/passo4_tray.png", "legend": "Tray com estoque restaurado após cancelamento"}
        ]
    }
]

# Monta o HTML do Stepper (Barra superior)
stepper_items = []
for idx, s in enumerate(steps_data):
    stepper_items.append(f'''
    <button class="step-btn {'active' if idx==0 else ''}" onclick="goToStep({idx})" id="step-btn-{idx}">
        <span class="step-idx">{idx}</span>
        <span class="step-label">{s['short_title']}</span>
    </button>
    ''')
stepper_html = ''.join(stepper_items)

# Monta os painéis de passos
panels_html = []
for idx, s in enumerate(steps_data):
    # Renderiza abas da direita
    tab_buttons = []
    tab_contents = []
    
    for t_idx, tab in enumerate(s['tabs']):
        tab_active = 'active' if t_idx == 0 else ''
        tab_buttons.append(f'''
        <button class="tab-btn {tab_active}" onclick="switchTab('{s['id']}', {t_idx})" id="tab-btn-{s['id']}-{t_idx}">
            {tab['label']}
        </button>
        ''')
        
        tab_contents.append(f'''
        <div class="tab-pane {tab_active}" id="tab-pane-{s['id']}-{t_idx}">
            <div class="img-preview-box" onclick="openLightbox('{tab['img']}', '{html.escape(tab['legend'])}')">
                <img src="{tab['img']}" alt="{html.escape(tab['label'])}" class="evidence-img" onerror="this.onerror=null;this.parentElement.innerHTML='<div class=img-missing>Imagem não encontrada: {tab['img']}</div>'">
                <div class="zoom-badge">🔍 Clique para ampliar</div>
            </div>
            <div class="evidence-caption">{tab['legend']}</div>
        </div>
        ''')
    
    panels_html.append(f'''
    <section class="step-section {'active' if idx==0 else ''}" id="{s['id']}">
        <div class="step-layout">
            <!-- Coluna Esquerda: Contexto, Tabelas e Logs -->
            <div class="col-left">
                <div class="step-header">
                    <span class="step-tag">{s['badge']}</span>
                    <h2 class="step-title">{s['title']}</h2>
                    <p class="step-subtitle">{s['subtitle']}</p>
                </div>
                <div class="col-left-content">
                    {s['left_html']}
                </div>
            </div>
            
            <!-- Coluna Direita: Visualizador de Evidências com Abas -->
            <div class="col-right">
                <div class="evidence-card">
                    <div class="evidence-header">
                        <div class="evidence-tabs">
                            {''.join(tab_buttons)}
                        </div>
                    </div>
                    <div class="evidence-body">
                        {''.join(tab_contents)}
                    </div>
                </div>
            </div>
        </div>
    </section>
    ''')

doc_html = f'''<!doctype html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demonstração Executiva: Reserva de Estoque Tray × ERP</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #0b111a;
            --bg-surface: #131b26;
            --bg-elevated: #1a2433;
            --border: #243247;
            --border-focus: #3b82f6;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --text-sub: #cbd5e1;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.15);
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --info: #0ea5e9;
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg-base);
            color: var(--text-main);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            -webkit-font-smoothing: antialiased;
        }}

        /* Barra de Navegação Superior (Stepper) */
        header {{
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border);
            padding: 10px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-shrink: 0;
            z-index: 10;
        }}
        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 260px;
        }}
        .brand-logo {{
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, #0ea5e9, #6366f1);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 16px;
            color: #fff;
            box-shadow: 0 0 16px rgba(14, 165, 233, 0.35);
        }}
        .brand-text h1 {{
            font-size: 15px;
            font-weight: 700;
            letter-spacing: -0.01em;
            color: #fff;
        }}
        .brand-text p {{
            font-size: 11px;
            color: var(--text-muted);
        }}

        /* Stepper Buttons */
        .stepper-nav {{
            display: flex;
            align-items: center;
            gap: 6px;
            overflow-x: auto;
            padding: 4px;
        }}
        .step-btn {{
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-muted);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
            transition: all 0.2s ease;
        }}
        .step-btn:hover {{
            color: var(--text-main);
            background: rgba(255,255,255,0.04);
        }}
        .step-btn.active {{
            background: var(--bg-elevated);
            color: var(--accent);
            border-color: var(--border-focus);
            box-shadow: 0 0 12px var(--accent-glow);
        }}
        .step-idx {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: rgba(255,255,255,0.1);
            font-size: 10px;
            font-weight: 700;
        }}
        .step-btn.active .step-idx {{
            background: var(--accent);
            color: #0b111a;
        }}

        /* Controles de Navegação (Anterior / Próximo) */
        .nav-controls {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-shrink: 0;
        }}
        .ctrl-btn {{
            background: var(--bg-elevated);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 7px 14px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }}
        .ctrl-btn:hover:not(:disabled) {{
            border-color: var(--accent);
            background: #223044;
        }}
        .ctrl-btn:disabled {{
            opacity: 0.35;
            cursor: not-allowed;
        }}

        /* Container Principal */
        main {{
            flex: 1;
            position: relative;
            overflow: hidden;
            display: flex;
        }}

        .step-section {{
            display: none;
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
            opacity: 0;
            transition: opacity 0.25s ease;
        }}
        .step-section.active {{
            display: flex;
            opacity: 1;
        }}

        .step-layout {{
            width: 100%;
            height: 100%;
            display: grid;
            grid-template-columns: 48% 52%;
            gap: 20px;
            padding: 24px;
        }}

        /* Coluna da Esquerda (Textos e Métricas) */
        .col-left {{
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            padding-right: 12px;
        }}
        .step-header {{
            margin-bottom: 20px;
        }}
        .step-tag {{
            display: inline-block;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--accent);
            background: var(--accent-glow);
            padding: 3px 10px;
            border-radius: 20px;
            margin-bottom: 8px;
            border: 1px solid rgba(56, 189, 248, 0.3);
        }}
        .step-title {{
            font-size: 24px;
            font-weight: 700;
            color: #fff;
            letter-spacing: -0.02em;
            margin-bottom: 6px;
        }}
        .step-subtitle {{
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.5;
        }}

        .col-left-content {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .description {{
            font-size: 14px;
            line-height: 1.6;
            color: var(--text-sub);
        }}

        /* Tabela Moderna */
        .table-container {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        .data-table th {{
            background: var(--bg-elevated);
            color: var(--text-muted);
            font-weight: 600;
            text-align: left;
            padding: 10px 14px;
            border-bottom: 1px solid var(--border);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .data-table td {{
            padding: 10px 14px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            color: var(--text-sub);
        }}
        .data-table tr:last-child td {{
            border-bottom: none;
        }}
        .highlight-row {{
            background: rgba(245, 158, 11, 0.06);
        }}

        /* Badges */
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }}
        .badge-warning {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .badge-success {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}
        .badge-info {{ background: rgba(14, 165, 233, 0.15); color: #38bdf8; border: 1px solid rgba(14, 165, 233, 0.3); }}
        .badge-muted {{ background: rgba(255,255,255,0.06); color: var(--text-muted); }}

        /* Callouts / Avisos */
        .callout {{
            display: flex;
            gap: 12px;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 13px;
            line-height: 1.5;
        }}
        .callout-info {{
            background: rgba(14, 165, 233, 0.08);
            border: 1px solid rgba(14, 165, 233, 0.25);
            color: #bae6fd;
        }}
        .callout-warning {{
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.25);
            color: #fde68a;
        }}
        .callout-success {{
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.25);
            color: #a7f3d0;
        }}
        .callout-icon {{
            font-size: 16px;
            flex-shrink: 0;
        }}

        /* Terminal Card (Logs) */
        .terminal-card {{
            background: #070d14;
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            font-family: 'JetBrains Mono', Consolas, monospace;
        }}
        .terminal-header {{
            background: #0d1520;
            padding: 8px 12px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .terminal-dot {{
            width: 9px;
            height: 9px;
            border-radius: 50%;
        }}
        .terminal-dot.red {{ background: #ef4444; }}
        .terminal-dot.yellow {{ background: #f59e0b; }}
        .terminal-dot.green {{ background: #10b981; }}
        .terminal-title {{
            font-size: 11px;
            color: var(--text-muted);
            margin-left: 6px;
        }}
        .terminal-body {{
            padding: 12px;
            font-size: 11px;
            line-height: 1.6;
            color: #93c5fd;
            overflow-x: auto;
            white-space: pre-wrap;
            max-height: 150px;
        }}

        /* Fórmula Card (Step 0) */
        .formula-box {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            margin: 14px 0;
        }}
        .formula-label {{
            font-size: 11px;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 8px;
            font-weight: 600;
        }}
        .formula-math {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
            font-size: 13px;
        }}
        .formula-item {{
            background: var(--bg-elevated);
            padding: 6px 12px;
            border-radius: 6px;
            border: 1px solid var(--border);
            font-weight: 500;
        }}
        .formula-item.highlight {{
            border-color: var(--warning);
            color: #fbbf24;
            background: rgba(245, 158, 11, 0.1);
        }}
        .formula-item.result {{
            border-color: var(--success);
            color: #34d399;
            background: rgba(16, 185, 129, 0.1);
            font-weight: 700;
        }}
        .formula-op {{
            font-size: 16px;
            font-weight: bold;
            color: var(--text-muted);
        }}

        .steplist {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 14px;
        }}
        .steplist-item {{
            display: flex;
            gap: 12px;
            align-items: flex-start;
            font-size: 13px;
            color: var(--text-sub);
        }}
        .steplist-num {{
            background: var(--accent);
            color: #0b111a;
            font-weight: 700;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            flex-shrink: 0;
            margin-top: 1px;
        }}

        /* Bullets do Resumo */
        .summary-bullets {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 14px;
        }}
        .bullet-box {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-left: 3px solid var(--accent);
            border-radius: 6px;
            padding: 10px 14px;
        }}
        .bullet-title {{
            font-size: 13px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 2px;
        }}
        .bullet-text {{
            font-size: 12px;
            color: var(--text-muted);
            line-height: 1.4;
        }}

        /* Coluna da Direita (Card de Evidências) */
        .col-right {{
            display: flex;
            flex-direction: column;
            height: 100%;
        }}
        .evidence-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            height: 100%;
            overflow: hidden;
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
        }}
        .evidence-header {{
            background: var(--bg-elevated);
            border-bottom: 1px solid var(--border);
            padding: 8px 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .evidence-tabs {{
            display: flex;
            gap: 6px;
            overflow-x: auto;
            width: 100%;
        }}
        .tab-btn {{
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-muted);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s;
        }}
        .tab-btn:hover {{
            color: var(--text-main);
            background: rgba(255,255,255,0.05);
        }}
        .tab-btn.active {{
            background: var(--bg-surface);
            color: var(--accent);
            border-color: var(--border);
            font-weight: 600;
        }}

        .evidence-body {{
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 16px;
            overflow: hidden;
            background: #090e16;
        }}
        .tab-pane {{
            display: none;
            flex-direction: column;
            height: 100%;
            width: 100%;
        }}
        .tab-pane.active {{
            display: flex;
        }}
        .img-preview-box {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            background: #05080d;
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            cursor: zoom-in;
            min-height: 200px;
        }}
        .evidence-img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            display: block;
            transition: transform 0.2s ease;
        }}
        .img-preview-box:hover .evidence-img {{
            transform: scale(1.01);
        }}
        .zoom-badge {{
            position: absolute;
            bottom: 12px;
            right: 12px;
            background: rgba(11, 17, 26, 0.85);
            backdrop-filter: blur(4px);
            border: 1px solid var(--border);
            color: var(--text-sub);
            font-size: 11px;
            font-weight: 500;
            padding: 4px 10px;
            border-radius: 20px;
            pointer-events: none;
        }}
        .evidence-caption {{
            margin-top: 10px;
            font-size: 12px;
            color: var(--text-muted);
            text-align: center;
        }}

        .img-missing {{
            padding: 40px;
            color: var(--danger);
            font-size: 13px;
            text-align: center;
        }}

        /* Lightbox Modal (Zoom) */
        .lightbox-modal {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(5, 9, 14, 0.92);
            backdrop-filter: blur(8px);
            z-index: 1000;
            display: none;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            padding: 30px;
        }}
        .lightbox-modal.open {{
            display: flex;
        }}
        .lightbox-content {{
            max-width: 95vw;
            max-height: 85vh;
            border-radius: 8px;
            border: 1px solid var(--border);
            box-shadow: 0 20px 50px rgba(0,0,0,0.8);
            object-fit: contain;
        }}
        .lightbox-caption {{
            color: #fff;
            margin-top: 14px;
            font-size: 14px;
            background: rgba(255,255,255,0.08);
            padding: 6px 18px;
            border-radius: 20px;
        }}
        .lightbox-close {{
            position: absolute;
            top: 20px;
            right: 24px;
            background: rgba(255,255,255,0.1);
            border: none;
            color: #fff;
            font-size: 24px;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }}
        .lightbox-close:hover {{
            background: rgba(255,255,255,0.25);
        }}

        /* Utilitários */
        .font-mono {{ font-family: 'JetBrains Mono', Consolas, monospace; }}
        .font-bold {{ font-weight: 700; }}
        .text-right {{ text-align: right; }}
        .text-cyan-400 {{ color: #22d3ee; }}
        .text-slate-200 {{ color: #e2e8f0; }}
        .text-slate-300 {{ color: #cbd5e1; }}
        .text-emerald-400 {{ color: #34d399; }}
        .text-amber-400 {{ color: #fbbf24; }}
        .text-lg {{ font-size: 15px; }}

        /* Barra de Rodapé */
        footer {{
            background: var(--bg-surface);
            border-top: 1px solid var(--border);
            padding: 6px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 11px;
            color: var(--text-muted);
            flex-shrink: 0;
        }}
        .kbd-hint {{
            display: inline-block;
            background: var(--bg-elevated);
            border: 1px solid var(--border);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: inherit;
            color: var(--text-sub);
            font-size: 10px;
        }}
    </style>
</head>
<body>

    <!-- Header / Stepper Superior -->
    <header>
        <div class="brand">
            <div class="brand-logo">T</div>
            <div class="brand-text">
                <h1>Logidoc × Tray Commerce</h1>
                <p>Módulo de Reserva Virtual (Pedido #4141)</p>
            </div>
        </div>

        <nav class="stepper-nav">
            {stepper_html}
        </nav>

        <div class="nav-controls">
            <button class="ctrl-btn" onclick="prevStep()" id="btn-prev" disabled>
                <span>←</span> Anterior
            </button>
            <button class="ctrl-btn" onclick="nextStep()" id="btn-next">
                Próximo <span>→</span>
            </button>
        </div>
    </header>

    <!-- Conteúdo Principal -->
    <main>
        {''.join(panels_html)}
    </main>

    <!-- Lightbox Modal -->
    <div class="lightbox-modal" id="lightbox" onclick="closeLightbox()">
        <button class="lightbox-close" onclick="closeLightbox()">&times;</button>
        <img src="" alt="" class="lightbox-content" id="lightbox-img" onclick="event.stopPropagation()">
        <div class="lightbox-caption" id="lightbox-caption"></div>
    </div>

    <!-- Rodapé -->
    <footer>
        <div>
            Status: <span style="color:var(--success);font-weight:600">● Homologado em Ambiente de Teste</span> (Mock Tray + ERP Retaguarda)
        </div>
        <div>
            Navegação: <span class="kbd-hint">←</span> <span class="kbd-hint">→</span> para passos | <span class="kbd-hint">1</span>...<span class="kbd-hint">5</span> para abas | <span class="kbd-hint">ESC</span> para fechar zoom
        </div>
    </footer>

    <script>
        let currentStep = 0;
        const totalSteps = {len(steps_data)};

        function updateUI() {{
            // Alterna seções
            document.querySelectorAll('.step-section').forEach((sec, idx) => {{
                sec.classList.toggle('active', idx === currentStep);
            }});

            // Alterna botões do stepper
            document.querySelectorAll('.step-btn').forEach((btn, idx) => {{
                btn.classList.toggle('active', idx === currentStep);
            }});

            // Atualiza botões Anterior/Próximo
            document.getElementById('btn-prev').disabled = (currentStep === 0);
            const btnNext = document.getElementById('btn-next');
            if (currentStep === totalSteps - 1) {{
                btnNext.innerHTML = 'Reiniciar <span>↻</span>';
            }} else {{
                btnNext.innerHTML = 'Próximo <span>→</span>';
            }}
        }}

        function goToStep(idx) {{
            if (idx >= 0 && idx < totalSteps) {{
                currentStep = idx;
                updateUI();
            }}
        }}

        function nextStep() {{
            if (currentStep < totalSteps - 1) {{
                currentStep++;
            }} else {{
                currentStep = 0;
            }}
            updateUI();
        }}

        function prevStep() {{
            if (currentStep > 0) {{
                currentStep--;
                updateUI();
            }}
        }}

        function switchTab(stepId, tabIdx) {{
            const sec = document.getElementById(stepId);
            if (!sec) return;

            // Alterna botões da aba
            sec.querySelectorAll('.tab-btn').forEach((btn, idx) => {{
                btn.classList.toggle('active', idx === tabIdx);
            }});

            // Alterna painéis da aba
            sec.querySelectorAll('.tab-pane').forEach((pane, idx) => {{
                pane.classList.toggle('active', idx === tabIdx);
            }});
        }}

        // Lightbox
        function openLightbox(imgSrc, caption) {{
            const modal = document.getElementById('lightbox');
            const img = document.getElementById('lightbox-img');
            const cap = document.getElementById('lightbox-caption');
            img.src = imgSrc;
            cap.innerText = caption;
            modal.classList.add('open');
        }}

        function closeLightbox() {{
            document.getElementById('lightbox').classList.remove('open');
        }}

        // Atalhos de Teclado
        document.addEventListener('keydown', (e) => {{
            if (document.getElementById('lightbox').classList.contains('open')) {{
                if (e.key === 'Escape') closeLightbox();
                return;
            }}

            if (e.key === 'ArrowRight' || e.key === 'PageDown') {{
                nextStep();
            }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
                prevStep();
            }} else if (['1', '2', '3', '4', '5'].includes(e.key)) {{
                const tabIdx = parseInt(e.key) - 1;
                const activeSection = document.querySelector('.step-section.active');
                if (activeSection) {{
                    const btns = activeSection.querySelectorAll('.tab-btn');
                    if (btns[tabIdx]) btns[tabIdx].click();
                }}
            }}
        }});
    </script>
</body>
</html>
'''

with open('apresentacao_demo_reserva_4141.html', 'w', encoding='utf-8') as f:
    f.write(doc_html)

print("Apresentacao v2 gerada com sucesso! Tamanho:", len(doc_html), "bytes")
