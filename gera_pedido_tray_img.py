"""
Gera imagem do pedido Tray (visual aproximado do painel admin Tray) a partir do JSON salvo pelo integrador.
Uso: python -X utf8 gera_pedido_tray_img.py [json] [--mascara]
Saida: prints/pedido_tray_<id>.html e .png  (renderizado com Chrome headless)
"""
import json, os, sys, html, subprocess, datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
JSON_PADRAO = r"E:\bd_clientes\Personalize_24112026\Pedidos\json_ped_4141_20261123_150657.json"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
MASCARA = "--mascara" in sys.argv
d = json.load(open(args[0] if args else JSON_PADRAO, encoding="utf-8"))[0]["Order"]
e = html.escape


def brl(v):
    try:
        return "R$ " + format(float(v), ",.2f").replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return e(str(v))


def data(v):
    try:
        return datetime.datetime.strptime(v[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return e(v or "-")


def mask(v, tipo):
    if not MASCARA or not v:
        return e(v or "-")
    if tipo == "nome":
        return " ".join(p[0] + "*" * (len(p) - 1) for p in v.split())
    if tipo == "cpf":
        return "***.***.***-" + v[-2:]
    if tipo == "email":
        return v[0] + "***@" + v.split("@")[-1]
    return "*" * len(v)


def cpf(v):
    v = "".join(c for c in v if c.isdigit())
    return "%s.%s.%s-%s" % (v[:3], v[3:6], v[6:9], v[9:]) if len(v) == 11 else v


c = d["Customer"]
pg = d["Payment"][0]["Payment"] if d.get("Payment") else {}
mk = d["MarketplaceOrder"][0]["MarketplaceOrder"] if d.get("MarketplaceOrder") else {}
end = c["CustomerAddresses"][-1]["CustomerAddress"] if c.get("CustomerAddresses") else {}
st = d["OrderStatus"]

linhas = ""
for i in d["ProductsSold"]:
    p = i["ProductsSold"]
    img = (p.get("ProductSoldImage") or [{}])[0].get("thumbs", {}).get("90", {}).get("https", "")
    nome = p["name"].split("<br")[0]
    var = " ".join("%s: %s" % (s["type"], s["value"]) for s in p.get("Sku", []))
    q = int(p["quantity"]); pr = float(p["price"])
    linhas += """<tr><td class=img><img src="%s" onerror="this.style.visibility='hidden'"></td>
<td><div class=pn>%s</div><div class=sub>%s</div><div class=sub>Ref.: %s &nbsp;|&nbsp; EAN: %s &nbsp;|&nbsp; ID produto: %s &nbsp;|&nbsp; Variante: %s</div></td>
<td class=r>%s</td><td class=c>%d</td><td class=r>%s</td></tr>""" % (
        e(img), e(nome), e(var), e(p["reference"]), e(p["ean"]), e(p["product_id"]), e(p["variant_id"]),
        brl(pr), q, brl(pr * q))

H = """<!doctype html><html lang=pt-br><meta charset=utf-8><title>Pedido %(id)s</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#eef0f4;font:13px/1.45 "Segoe UI",Arial,sans-serif;color:#3c4350}
.top{background:#1f2a44;color:#fff;height:48px;display:flex;align-items:center;padding:0 24px;font-size:15px;font-weight:600;gap:24px}
.top span{font-weight:400;font-size:12px;opacity:.7}
.wrap{width:1180px;margin:0 auto;padding:20px 0 30px}
.bc{font-size:12px;color:#8a93a3;margin-bottom:8px}
h1{font-size:22px;margin:0 0 14px;font-weight:600;color:#262d3a;display:flex;align-items:center;gap:12px}
.badge{font-size:11px;font-weight:700;padding:3px 10px;border-radius:12px;background:%(bg)s;color:#256b34;border:1px solid #9ad8a4;text-transform:uppercase}
.tabs{display:flex;gap:2px;border-bottom:2px solid #d9dde5;margin-bottom:16px}
.tabs div{padding:9px 18px;font-weight:600;color:#7b8494;font-size:13px}.tabs .on{color:#1a73e8;border-bottom:3px solid #1a73e8;margin-bottom:-2px}
.card{background:#fff;border:1px solid #dfe3ea;border-radius:6px;margin-bottom:16px}
.card h2{margin:0;padding:12px 18px;font-size:14px;font-weight:700;color:#262d3a;border-bottom:1px solid #e6e9ef;background:#fafbfc;border-radius:6px 6px 0 0;text-transform:uppercase;letter-spacing:.3px}
.body{padding:16px 18px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px 20px}.g3{grid-template-columns:repeat(3,1fr)}
.f label{display:block;font-size:11px;color:#8a93a3;text-transform:uppercase;font-weight:600;margin-bottom:2px}
.f div{color:#262d3a;font-size:13.5px;word-break:break-word}
.span2{grid-column:span 2}.span4{grid-column:span 4}
table{width:100%%;border-collapse:collapse}
th{font-size:11px;text-transform:uppercase;color:#8a93a3;text-align:left;padding:8px 10px;border-bottom:1px solid #e1e5ec;background:#fafbfc}
td{padding:10px;border-bottom:1px solid #eef0f4;vertical-align:middle}
td.img{width:70px}td.img img{width:56px;height:56px;object-fit:cover;border:1px solid #e1e5ec;border-radius:4px;background:#f3f4f7}
.pn{font-weight:600;color:#262d3a}.sub{font-size:11.5px;color:#7b8494}.r{text-align:right}.c{text-align:center}th.r{text-align:right}th.c{text-align:center}
.tot{display:flex;justify-content:flex-end;padding:12px 18px 16px}.tot table{width:330px}.tot td{border:0;padding:3px 10px}
.tot tr.t td{font-size:16px;font-weight:700;color:#262d3a;border-top:2px solid #dfe3ea;padding-top:8px}
.pill{display:inline-block;background:#e8f0fe;color:#1a56b8;border-radius:10px;padding:1px 9px;font-size:12px;font-weight:600}
</style>
<div class=top>Tray &nbsp;<span>Painel administrativo &nbsp;›&nbsp; Vendas &nbsp;›&nbsp; Pedidos</span></div>
<div class=wrap>
<div class=bc>Início › Pedidos › Pedido #%(id)s</div>
<h1>Pedido #%(id)s <span class=badge>%(status)s</span> <span class=pill>%(canal)s</span></h1>
<div class=tabs><div class=on>Dados do pedido</div><div>Histórico</div><div>Nota fiscal</div><div>Rastreio</div></div>

<div class=card><h2>Dados do pedido</h2><div class="body grid">
<div class=f><label>Nº do pedido</label><div>%(id)s</div></div>
<div class=f><label>Data / hora</label><div>%(data)s às %(hora)s</div></div>
<div class=f><label>Status</label><div>%(status)s</div></div>
<div class=f><label>Origem (canal)</label><div>%(canal)s</div></div>
<div class=f><label>Pedido no marketplace</label><div>%(ext)s</div></div>
<div class=f><label>Vendedor</label><div>%(vend)s</div></div>
<div class=f><label>Forma de envio</label><div>%(envio)s</div></div>
<div class=f><label>Prazo de entrega</label><div>%(prazo)s dia(s)</div></div>
<div class="f span4"><label>Observação da loja</label><div>%(note)s</div></div>
</div></div>

<div class=card><h2>Pagamento</h2><div class="body grid">
<div class=f><label>Forma de pagamento</label><div>%(pmeth)s</div></div>
<div class=f><label>Método</label><div>%(pm2)s</div></div>
<div class=f><label>Data do pagamento</label><div>%(pdata)s</div></div>
<div class=f><label>Parcelas</label><div>%(parc)sx</div></div>
<div class=f><label>Valor pago</label><div>%(pval)s</div></div>
<div class="f span2"><label>Comprovante</label><div>%(pnote)s</div></div>
<div class=f><label>Situação</label><div><span class=pill>Pago</span></div></div>
</div></div>

<div class=card><h2>Cliente</h2><div class="body grid">
<div class=f><label>Nome</label><div>%(cnome)s</div></div>
<div class=f><label>CPF</label><div>%(ccpf)s</div></div>
<div class=f><label>E-mail</label><div>%(cmail)s</div></div>
<div class=f><label>Telefone</label><div>%(ctel)s</div></div>
<div class="f span2"><label>Endereço de entrega</label><div>%(cend)s</div></div>
<div class=f><label>Bairro</label><div>%(cbai)s</div></div>
<div class=f><label>CEP</label><div>%(ccep)s</div></div>
<div class=f><label>Cidade / UF</label><div>%(ccid)s</div></div>
<div class=f><label>Complemento</label><div>%(ccomp)s</div></div>
<div class=f><label>Destinatário</label><div>%(cdest)s</div></div>
</div></div>

<div class=card><h2>Itens do pedido</h2>
<table><tr><th></th><th>Produto</th><th class=r>Valor unit.</th><th class=c>Qtd.</th><th class=r>Subtotal</th></tr>%(linhas)s</table>
<div class=tot><table>
<tr><td>Subtotal dos produtos</td><td class=r>%(sub)s</td></tr>
<tr><td>Frete (%(envio)s)</td><td class=r>%(frete)s</td></tr>
<tr><td>Desconto</td><td class=r>%(desc)s</td></tr>
<tr class=t><td>Total do pedido</td><td class=r>%(total)s</td></tr></table></div></div>
</div></html>""" % dict(
    id=e(d["id"]), status=e(d["status"]), bg=e(st.get("background") or "#CAFAD1"), canal=e(d["point_sale"]),
    data=data(d["date"]), hora=e(d["hour"]), ext=e(d["external_code"]), vend=e(mk.get("marketplace_seller_name", "-")),
    envio=e(d["shipment"]), prazo=e(d["delivery_time"]), note=e(d["store_note"]),
    pmeth=e(d["payment_method"]), pm2=e(pg.get("method", "-")), pdata=data(pg.get("date", "")), parc=e(d["installment"]),
    pval=brl(pg.get("value", d["total"])), pnote=e(pg.get("note", "-")),
    cnome=mask(c["name"], "nome"), ccpf=mask(cpf(c["cpf"]), "cpf"), cmail=mask(c["email"], "email"),
    ctel=e(c.get("cellphone") or c.get("phone") or "-"),
    cend=e("%s, %s" % (end.get("address", ""), end.get("number", ""))), cbai=e(end.get("neighborhood", "-")),
    ccep=e(end.get("zip_code", "-")), ccid=e("%s / %s" % (end.get("city", ""), end.get("state", ""))),
    ccomp=e(end.get("complement") or "-"), cdest=mask(end.get("recipient") or c["name"], "nome"),
    linhas=linhas, sub=brl(d["partial_total"]), frete=brl(d["shipment_value"]), desc=brl(d["discount"]),
    total=brl(d["total"]))

saida = os.path.join(AQUI, "prints"); os.makedirs(saida, exist_ok=True)
hp = os.path.join(saida, "pedido_tray_%s.html" % d["id"]); pp = hp[:-5] + ".png"
open(hp, "w", encoding="utf-8").write(H)
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1280,1345",
                "--virtual-time-budget=8000", "--screenshot=" + pp, "file:///" + hp.replace("\\", "/")])
print(hp); print(pp, os.path.exists(pp))
