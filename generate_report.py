# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Preformatted, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

FONT_DIR = r'C:\Windows\Fonts'
pdfmetrics.registerFont(TTFont('JA',   os.path.join(FONT_DIR, 'NotoSansJP-VF.ttf')))
pdfmetrics.registerFont(TTFont('MONO', os.path.join(FONT_DIR, 'msgothic.ttc'), subfontIndex=0))

JA = 'JA'
MONO = 'MONO'

def S(name, **kw):
    return ParagraphStyle(name, fontName=JA, **kw)

title_s  = S('title',  fontSize=18, leading=28, alignment=TA_CENTER,
             textColor=colors.HexColor('#1a3a5c'), spaceAfter=4)
sub_s    = S('sub',    fontSize=11, leading=18, alignment=TA_CENTER,
             textColor=colors.HexColor('#2e6da4'), spaceAfter=4)
info_s   = S('info',   fontSize=10, leading=16, alignment=TA_CENTER,
             textColor=colors.HexColor('#555555'))
h1_s     = S('h1',     fontSize=13, leading=20, spaceBefore=12, spaceAfter=5,
             textColor=colors.HexColor('#1a3a5c'))
h2_s     = S('h2',     fontSize=11, leading=18, spaceBefore=8,  spaceAfter=4,
             textColor=colors.HexColor('#2e6da4'), leftIndent=4)
body_s   = S('body',   fontSize=10, leading=17, alignment=TA_JUSTIFY, spaceAfter=5)
bullet_s = S('bullet', fontSize=10, leading=16, leftIndent=12, firstLineIndent=-8, spaceAfter=3)
code_s   = ParagraphStyle('code', fontName=MONO, fontSize=8.5, leading=13,
             backColor=colors.HexColor('#f4f6f8'), leftIndent=8, rightIndent=8,
             spaceBefore=3, spaceAfter=6, borderPad=5)
clbl_s   = S('clbl', fontSize=9, textColor=colors.HexColor('#2e6da4'), spaceBefore=6, spaceAfter=2)
cap_s    = S('cap',  fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#666666'), spaceAfter=6)

def hr(c='#2e6da4', t=1):
    return HRFlowable(width='100%', thickness=t, color=colors.HexColor(c),
                      spaceBefore=3, spaceAfter=3)

def H1(text):
    return [Spacer(1,3*mm), hr('#1a3a5c',2), Paragraph(text, h1_s), hr('#2e6da4',0.5)]

def H2(text):
    return [Paragraph(text, h2_s)]

def B(text):
    return Paragraph('*  ' + text, bullet_s)

def CODE(label, src):
    return [Paragraph(label, clbl_s), Preformatted(src.strip('\n'), code_s)]

# ─────────────────────────────────────────────────────────────────────────────
story = []

# ── 表紙 ──────────────────────────────────────────────────────────────────────
story += [
    Spacer(1, 35*mm),
    hr('#1a3a5c', 3),
    Spacer(1, 6*mm),
    Paragraph('オセロ対戦プログラム', title_s),
    Paragraph('思考アルゴリズム 解説レポート', title_s),
    Spacer(1, 5*mm),
    Paragraph('C / C++ 実装指示書', sub_s),
    Spacer(1, 6*mm),
    hr('#1a3a5c', 3),
    Spacer(1, 18*mm),
    Paragraph('提出者: IA13A083_13_DUONGMANH', info_s),
    Paragraph('提出日: 2026年7月6日', info_s),
    PageBreak(),
]

# ── 1. アルゴリズム概要 ────────────────────────────────────────────────────────
story += H1('1.  アルゴリズムの概要')
story.append(Paragraph(
    'コンピュータの思考は以下の3つの処理で構成されている。',
    body_s))
story.append(B('合法手の列挙: 現在の盤面でコンピュータが置けるマスを全て調べる'))
story.append(B('ゲーム木探索: Minimax法 + Alpha-Beta枝刈りで6手先まで読む'))
story.append(B('盤面評価: 各盤面に点数をつけ、最も有利な手を選ぶ'))

# ── 2. 定数とデータ構造 ────────────────────────────────────────────────────────
story += H1('2.  定数とデータ構造')

story += CODE('【定数定義】', '''\
#define SIZE  8   /* 盤面サイズ: 8x8マス */
#define EMPTY 0   /* マスが空き */
#define BLACK 1   /* 黒石 */
#define WHITE 2   /* 白石 */

/* 8方向への移動量 (上/右上/右/右下/下/左下/左/左上) */
int DX[8] = {-1,-1,-1, 0, 0, 1, 1, 1};
int DY[8] = {-1, 0, 1,-1, 1,-1, 0, 1};''')

story.append(Paragraph(
    '盤面は int board[8][8] の2次元配列で管理する。'
    '各マスの値は EMPTY(0)、BLACK(1)、WHITE(2) のいずれかである。',
    body_s))

# ── 3. 合法手の判定 ────────────────────────────────────────────────────────────
story += H1('3.  合法手の判定 ― is_valid()')
story.append(Paragraph(
    'あるマスに石を置けるかどうかを判定する関数。'
    '8方向を順番に調べ、相手の石を1個以上はさんで自分の石があれば合法手と判定する。',
    body_s))

story += CODE('【is_valid() 関数】', '''\
int is_valid(int board[8][8], int row, int col, int player) {
    if (board[row][col] != EMPTY) return 0; /* すでに石がある場合は置けない */

    int opp = (player == BLACK) ? WHITE : BLACK; /* 相手の石の種類 */

    for (int d = 0; d < 8; d++) {      /* 8方向を順番に調べる */
        int r = row + DX[d];
        int c = col + DY[d];
        int found = 0;

        /* 相手の石が続く限り進む */
        while (r>=0 && r<8 && c>=0 && c<8 && board[r][c]==opp) {
            r += DX[d]; c += DY[d]; found = 1;
        }

        /* 相手の石の先に自分の石があれば合法手 */
        if (found && r>=0 && r<8 && c>=0 && c<8 && board[r][c]==player)
            return 1;
    }
    return 0; /* どの方向にも挟める石がなければ不正 */
}''')

# ── 4. 石の反転 ────────────────────────────────────────────────────────────────
story += H1('4.  石の反転 ― apply_move()')
story.append(Paragraph(
    '実際に石を置き、はさんだ相手の石をすべて自分の色に変える関数。'
    'is_valid() と同じ8方向探索を行い、挟める方向の石を全てひっくり返す。',
    body_s))

story += CODE('【apply_move() 関数】', '''\
void apply_move(int board[8][8], int row, int col, int player) {
    board[row][col] = player; /* 指定マスに自分の石を置く */
    int opp = (player == BLACK) ? WHITE : BLACK;

    for (int d = 0; d < 8; d++) { /* 8方向を確認 */
        int r = row + DX[d];
        int c = col + DY[d];
        int cnt = 0;

        /* 相手の石を数えながら進む */
        while (r>=0 && r<8 && c>=0 && c<8 && board[r][c]==opp) {
            r += DX[d]; c += DY[d]; cnt++;
        }

        /* 自分の石で挟めた場合のみ反転する */
        if (cnt>0 && r>=0 && r<8 && c>=0 && c<8 && board[r][c]==player) {
            r = row + DX[d]; c = col + DY[d];
            while (board[r][c] == opp) { /* 挟んだ石を全てひっくり返す */
                board[r][c] = player;
                r += DX[d]; c += DY[d];
            }
        }
    }
}''')

story.append(PageBreak())

# ── 5. 評価関数 ────────────────────────────────────────────────────────────────
story += H1('5.  盤面評価関数 ― evaluate()')
story += H2('5.1  位置的価値テーブル')
story.append(Paragraph(
    'オセロでは盤面の位置によって戦略的な重要度が異なる。'
    'コーナー（角）は一度取れば絶対に取り返されないため最高得点(120点)とし、'
    'コーナー隣接マスは相手にコーナーを渡しやすいため大きなマイナス点(-20, -40)としている。',
    body_s))

story += CODE('【位置的価値テーブルの定義】', '''\
/* 各マスの戦略的価値（値が高いほど有利なマス） */
int WEIGHT[8][8] = {
    {120,-20, 20,  5,  5, 20,-20,120},  /* 角=120点、角隣=-20点 */
    {-20,-40, -5, -5, -5, -5,-40,-20},  /* 角の斜め隣=-40点 */
    { 20, -5, 15,  3,  3, 15, -5, 20},
    {  5, -5,  3,  3,  3,  3, -5,  5},
    {  5, -5,  3,  3,  3,  3, -5,  5},
    { 20, -5, 15,  3,  3, 15, -5, 20},
    {-20,-40, -5, -5, -5, -5,-40,-20},
    {120,-20, 20,  5,  5, 20,-20,120},
};''')

story += H2('5.2  evaluate() 関数')
story.append(Paragraph(
    'evaluate() は現在の盤面がコンピュータにとってどれだけ有利かを数値で返す関数。'
    'スコアが高いほどコンピュータ有利を意味する。',
    body_s))
story.append(B('位置スコア: 自分の石があるマスの重みを合計し、相手の石の重みを引く'))
story.append(B('合法手ボーナス: (自分の合法手数 - 相手の合法手数) x 5 を加算する'))
story.append(Spacer(1, 2*mm))

story += CODE('【evaluate() 関数】', '''\
int evaluate(int board[8][8], int player) {
    int opp   = (player == BLACK) ? WHITE : BLACK;
    int score = 0;

    /* 位置スコアの計算 */
    for (int i = 0; i < 8; i++)
        for (int j = 0; j < 8; j++) {
            if (board[i][j] == player) score += WEIGHT[i][j]; /* 自分の石は加算 */
            if (board[i][j] == opp)    score -= WEIGHT[i][j]; /* 相手の石は減算 */
        }

    /* 合法手ボーナス: 打てる手が多いほど有利 */
    score += 5 * (合法手数(player) - 合法手数(opp));

    return score; /* スコアが高いほどコンピュータに有利 */
}''')

# ── 6. Minimax + Alpha-Beta ────────────────────────────────────────────────────
story += H1('6.  探索アルゴリズム ― Minimax + Alpha-Beta 枝刈り')
story += H2('6.1  Minimax 法とは')
story.append(Paragraph(
    'Minimax法は、自分が最も有利な手を選び、相手は自分に最も不利な手を選ぶという'
    '前提でゲーム木を再帰的に探索するアルゴリズムである。'
    '本プログラムでは6手先まで全パターンを読み、最善手を決定する。',
    body_s))
story.append(B('最大化ノード (自分の手番): 全合法手の中でスコアが最も高い手を選ぶ'))
story.append(B('最小化ノード (相手の手番): 全合法手の中でスコアが最も低い手を選ぶ（コンピュータに不利な手を選ぶ）'))
story.append(B('深さ0に到達したとき: それ以上探索せず evaluate() で盤面を評価してスコアを返す'))
story.append(B('合法手がない場合 (パス): 探索深さを変えず手番だけ交代して探索を続ける'))
story.append(B('双方とも合法手なし: ゲーム終了とみなし evaluate() のスコアを返す'))
story.append(Spacer(1, 2*mm))
story.append(Paragraph(
    '【再帰の流れ】  ai_best_move() が depth=6 で minimax() を呼び出す。'
    'minimax() は各合法手について盤面をコピーして仮に石を置き、depth-1 で自分自身を再帰呼び出しする。'
    'これを depth=0 になるまで繰り返し、最終的に evaluate() のスコアが呼び出し元に返されていく。',
    body_s))

story += H2('6.2  Alpha-Beta 枝刈りとは')
story.append(Paragraph(
    'Alpha-Beta枝刈りはMinimaxの最適化手法である。'
    '探索しても結果に影響しないことが確定した枝（手の組み合わせ）を'
    '早期に打ち切ることで探索量を大幅に削減し、同じ深さでも高速に動作する。',
    body_s))
story.append(B('alpha (下限): コンピュータ側がすでに保証できる最低スコア。初期値は -99999'))
story.append(B('beta  (上限): 相手側がすでに保証できる最高スコア。初期値は +99999'))
story.append(B('beta <= alpha になった時点で「この先を読んでも結果が変わらない」と判断し探索を打ち切る'))
story.append(Paragraph(
    '【枝刈りの具体例】  最大化ノードである手Aを評価してスコア=10 が得られたとする。'
    '次の手Bを評価中に相手（最小化）がスコア=5 以下に誘導できると分かった時点で、'
    'BはAより悪いと確定するため残りの探索を打ち切る（betaカット）。'
    'この仕組みにより探索ノード数が純粋なMinimaxと比べて平均的に大幅削減される。',
    body_s))
story.append(Spacer(1, 2*mm))

story += CODE('【minimax() 関数】', '''\
/*
 * depth     : 残り探索深さ（最初は 6 を渡す）
 * alpha     : 最大化側の保証スコア下限（-99999 で初期化）
 * beta      : 最小化側の保証スコア上限（+99999 で初期化）
 * maximizing: 1=コンピュータの手番  0=相手の手番
 * player    : コンピュータのプレイヤー番号
 */
int minimax(int board[8][8], int depth, int alpha, int beta,
            int maximizing, int player) {

    /* 終端条件: 深さ0 または 双方とも合法手なし */
    if (depth == 0) return evaluate(board, player);
    if (双方手なし)  return evaluate(board, player);

    int cur = maximizing ? player : 相手;   /* 現在の手番を決める */
    合法手リストを取得(board, cur, moves);

    /* 合法手がない場合は手番を交代して継続（パス） */
    if (合法手数 == 0)
        return minimax(board, depth-1, alpha, beta, !maximizing, player);

    if (maximizing) {                         /* コンピュータの手番: 最大化 */
        int best = -99999;
        for (各合法手) {
            盤面をコピーして仮に石を置く;
            int val = minimax(コピー盤面, depth-1, alpha, beta, 0, player);
            if (val > best) best = val;       /* より良い手を記録 */
            if (val > alpha) alpha = val;
            if (beta <= alpha) break;         /* betaカット（枝刈り） */
        }
        return best;

    } else {                                  /* 相手の手番: 最小化 */
        int best = +99999;
        for (各合法手) {
            盤面をコピーして仮に石を置く;
            int val = minimax(コピー盤面, depth-1, alpha, beta, 1, player);
            if (val < best) best = val;       /* より悪い手を記録 */
            if (val < beta) beta = val;
            if (beta <= alpha) break;         /* alphaカット（枝刈り） */
        }
        return best;
    }
}''')

story.append(PageBreak())

# ── 7. エントリポイント ────────────────────────────────────────────────────────
story += H1('7.  エントリポイント ― ai_best_move()')
story.append(Paragraph(
    'ゲームループから呼び出す関数。現在の盤面に対してコンピュータの全合法手を列挙し、'
    '各手について minimax() を起動してスコアを計算する。'
    '最もスコアの高かった手の座標を out_r / out_c に書き込んで返す。',
    body_s))
story.append(B('合法手が1件もない場合は 0 を返す（ゲームループ側でパス処理を行う）'))
story.append(B('各合法手ごとに盤面を memcpy でコピーし、apply_move() で仮に石を置いてから minimax() を呼ぶ'))
story.append(B('minimax() の第3引数 maximizing=0 は「次の手番は相手（最小化）」を意味する'))
story.append(B('全手のスコアを比較し、最大スコアの手を best_r / best_c として記録する'))
story.append(Spacer(1, 2*mm))

story += CODE('【ai_best_move() 関数】', '''\
/*
 * board   : 現在の盤面
 * player  : コンピュータのプレイヤー番号
 * depth   : 探索深さ（本プログラムでは 6）
 * out_r   : 最善手の行番号 (0-7) を書き込む
 * out_c   : 最善手の列番号 (0-7) を書き込む
 * 戻り値  : 1=手あり、0=合法手なし（パス）
 */
int ai_best_move(int board[8][8], int player, int depth,
                 int *out_r, int *out_c) {

    合法手リストを取得(board, player, moves);
    if (合法手数 == 0) return 0;  /* 合法手なし: パス */

    int best_score = -99999;
    int best_r = -1, best_c = -1;

    for (int i = 0; i < n_moves; i++) {
        int b2[8][8];
        memcpy(b2, board, sizeof(b2));
        apply_move(b2, moves[i].r, moves[i].c, player);

        /* この手を打った場合のスコアを6手先まで読んで計算 */
        int score = minimax(b2, depth-1, -99999, +99999, 0, player);

        if (score > best_score) {
            best_score = score;
            best_r = moves[i].r;  /* 最善手の座標を更新 */
            best_c = moves[i].c;
        }
    }

    *out_r = best_r;
    *out_c = best_c;
    return 1;
}

/* --- ゲームループ内での呼び出し例 --- */
int row, col;
if (ai_best_move(board, WHITE, 6, &row, &col)) {
    apply_move(board, row, col, WHITE);  /* 最善手を盤面に反映 */
}''')

# ── 8. 処理の流れ ──────────────────────────────────────────────────────────────
story += H1('8.  処理の流れ（まとめ）')
story.append(Paragraph('コンピュータが1手を決定するまでの流れを以下に示す。', body_s))

steps = [
    ('Step 1', 'ai_best_move() を呼び出す'),
    ('Step 2', '現在の盤面でコンピュータの合法手を全て列挙する'),
    ('Step 3', '合法手が0件の場合はパス（処理終了）'),
    ('Step 4', '各合法手について盤面をコピーし仮に石を置く'),
    ('Step 5', 'minimax() を depth=6、alpha=-99999、beta=+99999 で呼び出す'),
    ('Step 6', '再帰的に6手先まで展開し、途中で枝刈りを行う'),
    ('Step 7', '深さ0または終局に達したら evaluate() でスコアを計算して返す'),
    ('Step 8', '全合法手の中でスコアが最大の手を best_r/best_c に記録'),
    ('Step 9', 'apply_move() で実際に盤面へ反映する'),
]
for step, desc in steps:
    story.append(Paragraph(f'[{step}]  {desc}', bullet_s))

story.append(Spacer(1, 6*mm))
story.append(hr('#1a3a5c', 1))
story.append(Paragraph('以上', cap_s))

# ── Build PDF ─────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'othello_ai_report.pdf')
doc = SimpleDocTemplate(out, pagesize=A4,
    leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm,
    title='オセロAI思考アルゴリズム解説レポート', author='IA13A083_13_DUONGMANH')
doc.build(story)
print('PDF done:', out)
