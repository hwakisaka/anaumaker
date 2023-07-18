from scipy.stats import rankdata
import dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output, State
# 問題文を準備する
mondaibun = '''
生殖器系は性によって機能的にも構造的にも異なる発生過程をたどる。
ふつうは性染色体の一つ、Y染色体があると男性になる。男性はY染色体上の
SRY遺伝子が働くことにより、頭尾方向に伸びる左右一対の体腔への膨らみと
して存在する生殖腺の原基が、精巣として分化する。SRY遺伝子が働かないと
自動的に女性型になり、生殖腺原基は卵巣に分化する。X染色体は大型の染色体で
多数の遺伝子を担っているので、男女で数が異なると遺伝子発現量の差による
不都合が生じるので余分なX染色体を不活性化する機能が働く。性染色体の数に
よる先天異常は、流産や重い障害を伴う常染色体の数の異常に比べて、この不活性
化機能により障害が抑えられ、成人まで成長できる場合が多い。精子や卵子の元に
なる始原生殖細胞はもともと卵黄嚢壁にあったものが遊走して左右の生殖腺原基に
入り込む。生殖腺原基の外側には頸部から尾方に向かって前腎、中腎が形成され、
前腎はすぐに消失し、中腎は尿を作り、総排泄腔に伸びる中腎管（ウォルフ管）に流す。
さらに外側には中腎傍管（ミュラー管）が形成される。発生が進むと中腎管（ウォルフ管）の総排泄腔
出口付近から管が伸び出し、周囲の細胞と相互作用を起こし、腎臓を形成する。
男性の場合、精巣内に精子形成を支持するセルトリ細胞や男性ホルモンを産生する
ライディッヒ細胞が分化する。セルトリ細胞はミュラー管抑制因子を作り、これにより
中腎傍管（ミュラー管）が退化する。男性ホルモンにより発達した中腎管（ウォルフ管）は、精巣と
連絡することにより精子を運ぶための通路である射精管として転用される。同時に
中腎管（ウォルフ管）の一部が膨らみだし、精液の成分を作る精嚢や前立腺などの分泌腺を
形成する。精巣は、精子形成に体温より低い環境を必要とするため、精巣導帯に
引っ張られて体壁を降下して鼠径管を経て陰嚢内に収納される。男性では精巣が
鼠径管を通過するため、鼠径管が緩くなり腹圧により腸がはまり込みやすい。
これを鼠径ヘルニアという。女性の場合、中腎管（ウォルフ管）に代わり中腎傍管
（ミュラー管）が発達し、卵管、子宮、膣といった女性内生殖器を形成する。男性
ホルモンがほとんど産生されないため中腎管（ウォルフ管）はほとんど退化する。
アンドロゲン不応症は男性ホルモン受容体の異常により引き起こされる先天異常で、
染色体は男性型で精巣は正常に形成されるが、外生殖器や体つきは女性型となる一方、
ミュラー管抑制因子が生産されるので中腎傍管（ミュラー管）が退化し、卵管、子宮
および膣の大半ができず、不妊となる。
'''
# 穴埋めにしたい用語
ana = []
# 選択肢に混ぜておきたい用語（本文には出現しない用語であること）
alt = []
# 穴埋め部分の部分の表記に使う記号文字：前から順に1文字ずつ使われる（勘違い防止のためにOとかIをのぞく可能性もあり）
marker = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
#marker = 'いろはにほへとちりぬるをわかよたれそつねならむうゐのおくやまけふこえてあさきゆめみしゑひもせすん'
#marker = 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん'



# JupyterDashインスタンスの作成
app = JupyterDash(__name__)

# layout属性にレイアウトを渡す（ドロップダウンとグラフ）
app.layout = html.Div([
                       # 問題文を表示するTEXTBOXを表示
                       html.Div([
                                html.H3('穴埋め本文',
                                        id='honbun_title',
                                        ),
                                 dcc.Textarea(
                                     id='mondai_text',
                                     title='問題文入力エリア',
                                     value=mondaibun,
                                     style={'width': '80%', 'height': 500},
                                     ),
                                 ],
                                style={'background-color':'#fabea7'}
                       ),
                       # 正解選択肢関連
                       html.Div([
                                 html.Div([
                                           dcc.Input(
                                               id='item_canditate',
                                               debounce=True,
                                               ),
                                           html.Button(
                                               "穴項目追加",
                                               id='item_add_btn',
                                               n_clicks=0
                                               ),
                                           html.Div(id='item_canditate_confirm')
                                           ]),
                                 html.H3('穴埋め項目選択肢'),
                                 dcc.Dropdown(id="items_dropdown",
                                              options=[],
                                              value=[],
                                              multi=True,
                                              ),
                                 ],
                                style={'background-color':'#ffe0b6','padding':'0.5em'}
                       ),
                       # 不正解選択肢関連
                       html.Div([
                                 html.Div([
                                           dcc.Input(
                                               id='false_canditate',
                                               debounce=True,
                                               ),
                                           html.Button(
                                               "不正解項目追加",
                                               id='false_add_btn',
                                               n_clicks=0
                                               ),
                                           html.Div(id='false_canditate_confirm')
                                           ]),
                                 html.H3('不正解穴埋め項目選択肢'),
                                 dcc.Dropdown(id="false_items_dropdown",
                                              options=[],
                                              value=[],
                                              multi=True,
                                              ),
                                 ],
                                style={'background-color':'#e1eec1','padding':'0.5em'}
                       ),
                       # 穴埋めの穴マーカー洗濯関連
                       html.Div([
                                 html.H3('埋め穴のマーカー選択'),
                                 # 穴埋め部分の部分の表記に使う記号文字：前から順に1文字ずつ使われる（勘違い防止のためにOとかIをのぞく可能性もあり）
                                 # 将来的にはlistで渡せるようにする（Input type=TEXT）
                                 dcc.RadioItems(id='marker_select',
                                                options=[
                                                         {'label':'大文字アルファベット（ABCD...）最大26穴','value':'ABCDEFGHIJKLMNOPQRSTUVWXYZ'},
                                                         {'label':'いろはにほへと　最大48穴','value':'いろはにほへとちりぬるをわかよたれそつねならむうゐのおくやまけふこえてあさきゆめみしゑひもせすん'},
                                                         {'label':'あいうえお　最大46穴','value':'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん'},
                                                         ],
                                                value='ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                                labelStyle={'display': 'block','fontsize':'3.0em'}
                                                ),
                                 ],
                                style={'background-color':'#aeb5dc','padding':'0.5em'}
                       ),
                       # さまざまな内容表示
                       html.Div([
                                 html.H3('表示内容選択'),
                                 dcc.RadioItems(id='contents_select',
                                                options=[
                                                         {'label':'選択肢一覧', 'value':'選択肢一覧'},
                                                         {'label':'問題文出力', 'value':'問題文出力'},
                                                         {'label':'答え付き問題文', 'value':'答え付き問題文'},
                                                         {'label':'回答欄出力', 'value':'回答欄出力'},
                                                         {'label':'答え付き回答欄', 'value':'答え付き回答欄'},
                                                         ],
                                                labelStyle={'display': 'inline-block','fontsize':'3.0em','padding':'1.0em'}
                                                ),
                                 dcc.Textarea(id='output',
                                              value='',
                                              style={'width': '80%', 'height': 500},
                                              )
                                 ],
                                style={'background-color':'#e5b7be','padding':'0.5em'}
                       )

], style={'display':'block'})

# 選択肢候補のチェック
# global変数が利用できないのでStateでDropdownのoptionsを受け渡す
@app.callback(
    Output('item_canditate','value'),
    Output('items_dropdown','options'),
    Output('items_dropdown','value'),
    Output('item_canditate_confirm','children'),
    Input('item_add_btn','n_clicks'),
    State('items_dropdown','options'),
    State('items_dropdown','value'),
    State('item_canditate','value'),
    State('mondai_text','value')
)
def update_items(n_clicks,options,dd_values,add_value,mondaibun):
  v = dd_values
  opt = options
  if n_clicks > 0:
    # 適当に挟まれた改行コードを削除する
    s = mondaibun.replace('\n','')
    # anaのすべての項が本文中に含まれるかどうかのチェックをする
    # 選択肢の内包化されたものがある場合、文字数の長いものを優先的に置き換える
    # 【脊髄神経】は【脊髄】より先に置き換えられる
    opt.append({'value':add_value, 'label':add_value})
    v.append(add_value)
    v.sort(key=len,reverse=True)
    s_check = s[:]
    for target in v:
      if s_check.find(target) == -1:
        msg = '**{}** が本文中に見つかりませんでした。選択肢か本文を見直してください。'.format(target)
        return '', dash.no_update, dash.no_update, msg
      else:
        #長い選択肢を見つけたら問題文から削っていく処理を行う
        s_check = s_check.replace(target, '', -1)
    return '', opt, v, ''
  else:
    # PreventUpdate prevents ALL outputs updating
    raise dash.exceptions.PreventUpdate

# 不正解選択肢候補のチェック
@app.callback(
    Output('false_canditate','value'),
    Output('false_items_dropdown','options'),
    Output('false_items_dropdown','value'),
    Output('false_canditate_confirm','children'),
    Input('false_add_btn','n_clicks'),
    State('false_items_dropdown','options'),
    State('false_items_dropdown','value'),
    State('false_canditate','value'),
    State('mondai_text','value')
)
def update_items(n_clicks,options,dd_values,add_value,mondaibun):
  v = dd_values
  opt = options
  if n_clicks > 0:
    # 適当に挟まれた改行コードを削除する
    s = mondaibun.replace('\n','')
    # すべての項が本文中に含まれていなかどうかのチェックをする
    opt.append({'value':add_value, 'label':add_value})
    v.append(add_value)
    # alt選択肢が本文中に出現しないかどうかチェックする
    for target in v:
      if s.find(target) >= 0:
        msg = '**{0}** が本文中に見つかりました。非正解選択肢を変えてください。'.format(target)
        return '', dash.no_update, dash.no_update, msg
    return '', opt, v, ''
  else:
    # PreventUpdate prevents ALL outputs updating
    raise dash.exceptions.PreventUpdate


# 問題の本文や回答欄および答え付きの出力
@app.callback(
    Output('output','value'),
    Input('contents_select','value'),
    Input('marker_select','value'),
    State('items_dropdown','value'),
    State('false_items_dropdown','value'),
    State('mondai_text','value')
)
def update_contents(mode,marker,items,f_items,honbun):
  # 適当に挟まれた改行コードを削除する
  s = honbun.replace('\n','')
  # 選択肢一覧を作成する
  choices = list(items + f_items)
  # 選択肢を文字列順にソートする
  choices.sort()
  # 1: 選択肢1, 2: 選択肢2の形式に直す
  cc = []
  for i, choice in enumerate(choices):
    cc.append('{0}: {1}'.format(i+1,choice))
  # 選択肢から選択肢番号の辞書を作る
  dc = {}
  for itm in cc:
    n, ky = itm.split(': ')
    dc[ky] = n
  # 正解選択肢の本文中の出現位置順に表記文字を設定する
  ranks = rankdata([s.find(target) for target in items]).astype(int)
  a = [marker[target-1] for target in ranks]
  # rep_dic は正解選択肢の辞書 {'用語1':'C', '用語2':'D', ...}のような形式
  rep_dic = dict(zip(items,a))
  # 実際の本文中に穴埋め部分の表記を埋め込む
  sq = s[:]
  sc = s[:]
  for k, v in rep_dic.items():
    # [ A ] の文字列形式
    vs = '[ ' + v + ' ]'
    #pk = '[' + k + ']'
    pk = '[' + dc[k] + ':' + k + ']'
    sq = sq.replace(k,vs)
    # 内包化された選択肢が二重にかっこがつかないようにする
    #print('key:{} = {}'.format(k,''.join(ana).count(k)))
    if ''.join(items).count(k) == 1:
      sc = sc.replace(k,pk)
  # 回答欄を作成する
  answ = { rep_dic[a]:dc[a] for a in items }
  answ2 = sorted(answ.items(), key=lambda x:marker.index(x[0]))
  if mode == '選択肢一覧':
    # 選択肢一覧を文字列で出力
    return ', '.join(cc)
  elif mode == '問題文出力':
    return sq
  elif mode == '答え付き問題文':
    return sc
  elif mode == '回答欄出力':
    # タブ区切り回答欄文字列
    return '\t\t'.join([a[0] for a in answ2])
  elif mode == '答え付き回答欄':
    # タブ区切り回答欄と正解選択肢番号の文字列
    return '\t'.join(sum(answ2,()))

# ノート上で実行
app.run_server(mode="inline")

