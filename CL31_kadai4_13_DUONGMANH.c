#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SIZE 8
#define EMPTY 0
#define BLACK 1
#define WHITE 2

int board[SIZE][SIZE];

int dx[] = {-1, -1, -1, 0, 0, 1, 1, 1};
int dy[] = {-1,  0,  1,-1, 1,-1, 0, 1};

char pname[3][30];
int  mode;

int  is_valid(int row, int col, int player);
int  has_moves(int player);
int  count_flips(int row, int col, int player);
void apply_move(int row, int col, int player);
int  count_pieces(int player);
void ai_turn(int player);
void human_turn(int player);
void print_board(int current);
void print_result(void);

void init_board(void) {
    memset(board, 0, sizeof(board));
    board[3][3] = WHITE;
    board[3][4] = BLACK;
    board[4][3] = BLACK;
    board[4][4] = WHITE;
}

int count_pieces(int player) {
    int n = 0;
    for (int i = 0; i < SIZE; i++)
        for (int j = 0; j < SIZE; j++)
            if (board[i][j] == player) n++;
    return n;
}

int is_valid(int row, int col, int player) {
    if (board[row][col] != EMPTY) return 0;
    int opp = (player == BLACK) ? WHITE : BLACK;
    for (int d = 0; d < 8; d++) {
        int r = row + dx[d], c = col + dy[d], found = 0;
        while (r >= 0 && r < SIZE && c >= 0 && c < SIZE && board[r][c] == opp) {
            r += dx[d]; c += dy[d]; found = 1;
        }
        if (found && r >= 0 && r < SIZE && c >= 0 && c < SIZE && board[r][c] == player)
            return 1;
    }
    return 0;
}

int has_moves(int player) {
    for (int i = 0; i < SIZE; i++)
        for (int j = 0; j < SIZE; j++)
            if (is_valid(i, j, player)) return 1;
    return 0;
}

int count_flips(int row, int col, int player) {
    if (board[row][col] != EMPTY) return 0;
    int opp = (player == BLACK) ? WHITE : BLACK, total = 0;
    for (int d = 0; d < 8; d++) {
        int r = row + dx[d], c = col + dy[d], cnt = 0;
        while (r >= 0 && r < SIZE && c >= 0 && c < SIZE && board[r][c] == opp) {
            r += dx[d]; c += dy[d]; cnt++;
        }
        if (cnt > 0 && r >= 0 && r < SIZE && c >= 0 && c < SIZE && board[r][c] == player)
            total += cnt;
    }
    return total;
}

void apply_move(int row, int col, int player) {
    board[row][col] = player;
    int opp = (player == BLACK) ? WHITE : BLACK;
    for (int d = 0; d < 8; d++) {
        int r = row + dx[d], c = col + dy[d], cnt = 0;
        while (r >= 0 && r < SIZE && c >= 0 && c < SIZE && board[r][c] == opp) {
            r += dx[d]; c += dy[d]; cnt++;
        }
        if (cnt > 0 && r >= 0 && r < SIZE && c >= 0 && c < SIZE && board[r][c] == player) {
            r = row + dx[d]; c = col + dy[d];
            while (board[r][c] == opp) {
                board[r][c] = player;
                r += dx[d]; c += dy[d];
            }
        }
    }
}

void print_board(int current) {
    printf("\n    a   b   c   d   e   f   g   h\n");
    printf("  +---+---+---+---+---+---+---+---+\n");
    for (int i = 0; i < SIZE; i++) {
        printf("%d |", i + 1);
        for (int j = 0; j < SIZE; j++) {
            if      (board[i][j] == BLACK)    printf(" X ");
            else if (board[i][j] == WHITE)    printf(" O ");
            else if (is_valid(i, j, current)) printf(" . ");
            else                              printf("   ");
            printf("|");
        }
        printf("\n");
        printf("  +---+---+---+---+---+---+---+---+\n");
    }
    printf("\n  X %-10s: %d 石   O %-10s: %d 石\n",
           pname[BLACK], count_pieces(BLACK),
           pname[WHITE], count_pieces(WHITE));
    printf("  >> 手番: %s (%s)\n\n",
           current == BLACK ? "X" : "O",
           pname[current]);
}

void human_turn(int player) {
    char input[20];
    int row, col;
    while (1) {
        printf("  [%s] 手を入力 (例: d3) または 'q' で終了: ", pname[player]);
        if (scanf("%19s", input) != 1) continue;

        if (input[0] == 'q' || input[0] == 'Q') {
            printf("\n  ゲームを終了しました。\n");
            exit(0);
        }
        if (strlen(input) >= 2
            && input[0] >= 'a' && input[0] <= 'h'
            && input[1] >= '1' && input[1] <= '8') {
            col = input[0] - 'a';
            row = input[1] - '1';
            if (is_valid(row, col, player)) {
                apply_move(row, col, player);
                printf("  %s が %c%d に置きました\n\n", pname[player], input[0], row + 1);
                return;
            }
            printf("  無効な手です！もう一度試してください。\n");
        } else {
            printf("  形式が違います！ 'd3' のように入力してください。\n");
        }
    }
}

void ai_turn(int player) {
    printf("  [%s] 考え中...\n", pname[player]);

    int corners[4][2] = {{0,0},{0,7},{7,0},{7,7}};
    for (int i = 0; i < 4; i++) {
        int r = corners[i][0], c = corners[i][1];
        if (is_valid(r, c, player)) {
            apply_move(r, c, player);
            printf("  %s が %c%d に置きました\n\n", pname[player], 'a' + c, r + 1);
            return;
        }
    }

    int avoid[12][2] = {
        {0,1},{1,0},{1,1}, {0,6},{1,7},{1,6},
        {6,0},{7,1},{6,1}, {6,7},{7,6},{6,6}
    };

    int best_r = -1, best_c = -1, best = -1;
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            if (!is_valid(i, j, player)) continue;
            int danger = 0;
            for (int k = 0; k < 12; k++) {
                if (avoid[k][0] == i && avoid[k][1] == j) {
                    int gr = (i < 2) ? 0 : 7;
                    int gc = (j < 2) ? 0 : 7;
                    if (board[gr][gc] == EMPTY) { danger = 1; break; }
                }
            }
            int score = count_flips(i, j, player) - (danger ? 100 : 0);
            if (score > best) {
                best = score;
                best_r = i;
                best_c = j;
            }
        }
    }

    if (best_r != -1) {
        apply_move(best_r, best_c, player);
        printf("  %s が %c%d に置きました\n\n", pname[player], 'a' + best_c, best_r + 1);
    }
}

void print_result(void) {
    int b = count_pieces(BLACK);
    int w = count_pieces(WHITE);
    printf("=========================================\n");
    printf("               結果                      \n");
    printf("=========================================\n");
    printf("  X %-10s: %d 石\n", pname[BLACK], b);
    printf("  O %-10s: %d 石\n", pname[WHITE], w);
    if      (b > w) printf("\n  *** %s (X) の勝ち！ ***\n", pname[BLACK]);
    else if (w > b) printf("\n  *** %s (O) の勝ち！ ***\n", pname[WHITE]);
    else            printf("\n  *** 引き分け！ ***\n");
    printf("=========================================\n\n");
}

void run_game(void) {
    init_board();
    int current = BLACK;

    while (1) {
        print_board(current);

        if (!has_moves(BLACK) && !has_moves(WHITE)) break;

        if (!has_moves(current)) {
            printf("  %s は手がありません！スキップします。\n\n", pname[current]);
            current = (current == BLACK) ? WHITE : BLACK;
            continue;
        }

        int is_ai = (mode == 2 && current == WHITE);
        if (is_ai)
            ai_turn(current);
        else
            human_turn(current);

        current = (current == BLACK) ? WHITE : BLACK;
    }

    print_board(current);
    print_result();
}

int main(void) {
#ifdef _WIN32
    system("chcp 65001 > nul");
#endif

    char again;
    do {
        printf("=========================================\n");
        printf("        オセロ  |  OTHELLO - ターミナル版 \n");
        printf("=========================================\n");
        printf("  X = 黒（先手）   O = 白\n");
        printf("  .  = 有効な手\n");
        printf("  入力形式: 列 (a-h) + 行 (1-8)\n");
        printf("  例: d3   f5   c4\n");
        printf("=========================================\n\n");

        printf("  モード選択:\n");
        printf("  [1] 二人対戦\n");
        printf("  [2] 対CPU（一人プレイ）\n");
        printf("  選択 (1/2): ");
        while (scanf("%d", &mode) != 1 || (mode != 1 && mode != 2)) {
            printf("  1 か 2 を入力してください: ");
            while (getchar() != '\n');
        }
        while (getchar() != '\n');

        if (mode == 1) {
            printf("\n  プレイヤー1の名前 (X - 先手): ");
            if (fgets(pname[BLACK], sizeof(pname[BLACK]), stdin)) {
                pname[BLACK][strcspn(pname[BLACK], "\n")] = '\0';
                if (pname[BLACK][0] == '\0') strcpy(pname[BLACK], "プレイヤー1");
            }
            printf("  プレイヤー2の名前 (O): ");
            if (fgets(pname[WHITE], sizeof(pname[WHITE]), stdin)) {
                pname[WHITE][strcspn(pname[WHITE], "\n")] = '\0';
                if (pname[WHITE][0] == '\0') strcpy(pname[WHITE], "プレイヤー2");
            }
        } else {
            printf("\n  あなたの名前 (X - 先手): ");
            if (fgets(pname[BLACK], sizeof(pname[BLACK]), stdin)) {
                pname[BLACK][strcspn(pname[BLACK], "\n")] = '\0';
                if (pname[BLACK][0] == '\0') strcpy(pname[BLACK], "あなた");
            }
            strcpy(pname[WHITE], "CPU");
        }

        printf("\n  === 開始: %s (X) vs %s (O) ===\n", pname[BLACK], pname[WHITE]);
        printf("  いつでも 'q' を入力するとゲームを終了できます。\n\n");

        run_game();

        printf("  もう一度プレイしますか？ (c = はい, 他 = 終了): ");
        scanf(" %c", &again);
        while (getchar() != '\n');
        printf("\n");

    } while (again == 'c' || again == 'C');

    printf("  ありがとうございました！またね。\n\n");
    return 0;
}
