"""
Gera print FICTICIO da listagem de produtos/estoque no painel Tray (aproximado).
Uso: python -X utf8 gera_estoque_tray_img.py <nome_saida> <est1> <est2> <est3> [legenda]
Ex.:  python -X utf8 gera_estoque_tray_img.py passo1_tray 43 31 59
Saida: prints/<nome_saida>.png  (ordem: 27176, 27218, 27424)
"""
import json, os, sys, html, subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))
JSON_PED = r"E:\bd_clientes\Personalize_24112026\Pedidos\json_ped_4141_20261123_150657.json"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
e = html.escape
nome, est = sys.argv[1], sys.argv[2:5]
legenda = sys.argv[5] if len(sys.argv) > 5 else ""
itens = [i["ProductsSold"] for i in json.load(open(JSON_PED, encoding="utf-8"))[0]["Order"]["ProductsSold"]]

linhas = ""
for p, q in zip(itens, est):
    img = p["ProductSoldImage"][0]["thumbs"]["90"]["https"]
    n = p["name"].split("<br")[0].split(" (Ref")[0].strip()
    cor = "#2e7d32" if int(q) > 10 else "#c62828"
    linhas += """<tr><td><input type=checkbox></td><td class=img><img src="%s"></td>
<td><div class=pn>%s</div><div class=sub>Variação: Balão Látex 5'' &nbsp;·&nbsp; ID %s / var. %s</div></td>
<td>%s</td><td>R$ 14,86</td><td><span class=st style="color:%s">%s un.</span></td><td><span class=on>Ativo</span></td><td class=ac>✎ &nbsp; ⋮</td></tr>""" % (
        e(img), e(n), p["product_id"], p["variant_id"], p["reference"], cor, int(q))

H = """<!doctype html><meta charset=utf-8><style>
*{box-sizing:border-box}body{margin:0;background:#eef0f4;font:13px/1.45 "Segoe UI",Arial,sans-serif;color:#3c4350}
.top{background:#1f2a44;color:#fff;height:48px;display:flex;align-items:center;padding:0 24px;font-weight:600;font-size:15px;gap:24px}
.top span{font-weight:400;font-size:12px;opacity:.7}
.wrap{width:1180px;margin:0 auto;padding:20px 0}
.bc{font-size:12px;color:#8a93a3;margin-bottom:8px}h1{font-size:22px;margin:0 0 14px;font-weight:600;color:#262d3a}
.bar{display:flex;gap:10px;margin-bottom:14px}.bar div{background:#fff;border:1px solid #d5dae3;border-radius:5px;padding:8px 14px;color:#8a93a3}
.bar .s{flex:1}.bar .b{background:#1a73e8;color:#fff;border-color:#1a73e8;font-weight:600}
.card{background:#fff;border:1px solid #dfe3ea;border-radius:6px}
table{width:100%%;border-collapse:collapse}
th{font-size:11px;text-transform:uppercase;color:#8a93a3;text-align:left;padding:10px;border-bottom:1px solid #e1e5ec;background:#fafbfc}
td{padding:10px;border-bottom:1px solid #eef0f4;vertical-align:middle}
td.img{width:70px}td.img img{width:52px;height:52px;object-fit:cover;border:1px solid #e1e5ec;border-radius:4px}
.pn{font-weight:600;color:#262d3a}.sub{font-size:11.5px;color:#7b8494}.st{font-weight:700}
.on{background:#e3f6e6;color:#256b34;border-radius:10px;padding:2px 10px;font-size:12px;font-weight:600}.ac{color:#7b8494}
.cap{margin-top:12px;font-size:12px;color:#8a93a3;text-align:right}
</style>
<div class=top>Tray &nbsp;<span>Painel administrativo &nbsp;›&nbsp; Catálogo &nbsp;›&nbsp; Produtos</span></div>
<div class=wrap><div class=bc>Início › Produtos</div><h1>Produtos &nbsp;·&nbsp; Estoque na loja Tray</h1>
<div class=bar><div class=s>Buscar por nome, referência ou SKU…</div><div>Status: Todos</div><div class=b>Filtrar</div></div>
<div class=card><table><tr><th></th><th></th><th>Produto</th><th>Referência</th><th>Preço</th><th>Estoque</th><th>Status</th><th></th></tr>%s</table></div>
<div class=cap>%s</div></div>""" % (linhas, e(legenda))

saida = os.path.join(AQUI, "prints"); os.makedirs(saida, exist_ok=True)
hp = os.path.join(saida, nome + ".html"); pp = os.path.join(saida, nome + ".png")
open(hp, "w", encoding="utf-8").write(H)
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1280,470",
                "--virtual-time-budget=8000", "--screenshot=" + pp, "file:///" + hp.replace("\\", "/")])
print(pp, os.path.exists(pp))
