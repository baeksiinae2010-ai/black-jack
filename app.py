import streamlit as st
import random

# --- 1. 웹페이지 기본 설정 ---
st.set_page_config(page_title="카드 게임", page_icon="🃏", layout="centered")

# --- 2. 테마 세팅 및 세션 관리 ---
# 사용자가 고른 테마를 기억하기 위한 세션 세팅
if 'game_theme' not in st.session_state:
    st.session_state['game_theme'] = "🖤 다크 매트"

# 테마별 리얼 프리미엄 색상 정의
themes = {
    "🖤 다크 매트": {
        "bg": "#121214", "table": "#1E1E24", "text": "#E4E4E7", "sub": "#A1A1AA",
        "card_back": "linear-gradient(135deg, #3F3F46, #18181B)"
    },
    "🤍 라이트 브리즈": {
        "bg": "#F8FAFC", "table": "#FFFFFF", "text": "#0F172A", "sub": "#475569",
        "card_back": "linear-gradient(135deg, #94A3B8, #334155)"
    },
    "💜 사이버 펑크": {
        "bg": "#0D021A", "table": "#1A0933", "text": "#00FFFF", "sub": "#FF007F",
        "card_back": "linear-gradient(135deg, #FF007F, #7000FF)"
    },
    "🌲 모스 그린": {
        "bg": "#061F14", "table": "#0B3A25", "text": "#ECFDF5", "sub": "#A7F3D0",
        "card_back": "linear-gradient(135deg, #10B981, #064E3B)"
    }
}

current_theme = st.session_state['game_theme']
cfg = themes[current_theme]

# --- 3. 💫 에러 방지 + 부드러운 애니메이션을 위한 마법의 CSS ---
# 공백으로 인한 마크다운 깨짐을 원천 차단하고 부드러운 트랜지션을 적용합니다.
st.markdown(f"""
<style>
    /* 전체 배경화면 및 부드러운 색상 전환 */
    .stApp {{
        background-color: {cfg['bg']} !important;
        color: {cfg['text']} !important;
        transition: all 0.5s ease-in-out;
    }}
    /* 글자색 강제 고정 */
    h1, h2, h3, p, span, div {{
        color: {cfg['text']};
        transition: color 0.5s ease-in-out;
    }}
    /* 리얼 모바일 게임 보드 매트 */
    .game-table {{
        background-color: {cfg['table']};
        padding: 25px;
        border-radius: 24px;
        box-shadow: 0px 12px 30px rgba(0,0,0,0.5);
        border: 2px solid rgba(255,255,255,0.1);
        margin-bottom: 25px;
        transition: all 0.5s ease-in-out;
    }}
    /* 현실적인 트럼프 카드 디자인 */
    .card-container {{
        display: flex;
        gap: 12px;
        margin: 15px 0;
        flex-wrap: wrap;
    }}
    .playing-card {{
        width: 85px;
        height: 125px;
        background-color: white;
        border-radius: 12px;
        position: relative;
        box-shadow: 0px 6px 12px rgba(0,0,0,0.3);
        transform: translateY(0);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .playing-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0px 12px 20px rgba(0,0,0,0.4);
    }}
    /* 카드 뒷면 (고급스러운 패턴 입체감) */
    .card-back {{
        width: 85px;
        height: 125px;
        background: {cfg['card_back']};
        border-radius: 12px;
        border: 3px solid #FFFFFF;
        box-shadow: 0px 6px 12px rgba(0,0,0,0.4);
        position: relative;
    }}
    .card-back::after {{
        content: '';
        position: absolute;
        top: 8px; left: 8px; right: 8px; bottom: 8px;
        border: 1px dashed rgba(255,255,255,0.3);
        border-radius: 8px;
    }}
</style>
""", unsafe_allow_html=True)

# 깨짐 방지용 HTML 렌더링 헬퍼 함수
def render_html(html_string):
    clean_html = "".join([line.strip() for line in html_string.split("\n")])
    st.markdown(clean_html, unsafe_allow_html=True)

# --- 4. 게임 핵심 시스템 ---
def create_deck():
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [[suit, rank] for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

def calculate_score(hand):
    score = 0
    aces = 0
    for card in hand:
        rank = card[1]
        if rank in ['J', 'Q', 'K']: score += 10
        elif rank == 'A': score += 11; aces += 1
        else: score += int(rank)
    while score > 21 and aces > 0:
        score -= 10; aces -= 1
    return score

def get_card_element(card):
    suit, rank = card[0], card[1]
    color = "#E53E3E" if suit in ['♥', '♦'] else "#1A202C"
    return f'<div class="playing-card"><div style="position:absolute; top:8px; left:10px; font-size:18px; font-weight:bold; color:{color}; line-height:1;">{rank}</div><div style="position:absolute; top:26px; left:10px; font-size:14px; color:{color};">{suit}</div><div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-size:40px; color:{color};">{suit}</div><div style="position:absolute; bottom:8px; right:10px; font-size:18px; font-weight:bold; color:{color}; transform:rotate(180deg); line-height:1;">{rank}</div></div>'

# --- 5. 게임 세션 초기화 ---
def reset_game():
    st.session_state.deck = create_deck()
    st.session_state.player_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
    st.session_state.dealer_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
    st.session_state.game_over = False
    st.session_state.winner = ""

if 'deck' not in st.session_state:
    reset_game()

player_score = calculate_score(st.session_state.player_hand)
dealer_score = calculate_score(st.session_state.dealer_hand)

if not st.session_state.game_over and player_score == 21:
    st.session_state.game_over = True
    st.session_state.winner = "플레이어(블랙잭)"

# --- 6. 🎮 리얼 모바일 게임 인터페이스 배치 ---
render_html(f"<h1 style='text-align: center; margin-bottom: 5px;'>🃏 카드 게임</h1>")
render_html(f"<p style='text-align: center; color: {cfg['sub']}; font-size: 14px; margin-bottom: 25px;'>실시간으로 반응하는 프리미엄 카드 매트</p>")

# 🟢 [게임 보드 시작]
table_html = f'<div class="game-table">'

# [딜러 구역]
table_html += f'<div style="display:flex; justify-content:space-between; align-items:center;"><span style="font-weight:bold; font-size:16px; color:{cfg["sub"]};">🤖 DEALER TABLE</span>'
if st.session_state.game_over:
    table_html += f'<span style="background:rgba(255,255,255,0.1); padding:3px 10px; border-radius:12px; font-size:14px;">최종 점수: {dealer_score}점</span>'
else:
    table_html += f'<span style="background:rgba(255,255,255,0.1); padding:3px 10px; border-radius:12px; font-size:14px;">점수: 숨김</span>'
table_html += f'</div>'

# 딜러 카드 렌더링 (게임 중일 때는 두 번째 카드를 완벽하게 숨김 백그라운드 처리)
table_html += f'<div class="card-container">'
for i, card in enumerate(st.session_state.dealer_hand):
    if i == 1 and not st.session_state.game_over:
        table_html += '<div class="card-back"></div>'
    else:
        table_html += get_card_element(card)
table_html += f'</div>'

# 중앙 분리선
table_html += f'<hr style="border:0; border-top:1px dashed rgba(255,255,255,0.15); margin:20px 0;">'

# [플레이어 구역]
table_html += f'<div style="display:flex; justify-content:space-between; align-items:center;"><span style="font-weight:bold; font-size:16px; color:{cfg["sub"]};">🙋‍♂️ MY HAND</span><span style="background:rgba(255,255,255,0.1); padding:3px 10px; border-radius:12px; font-size:14px; font-weight:bold;">현재 점수: {player_score}점</span></div>'
table_html += f'<div class="card-container">'
for card in st.session_state.player_hand:
    table_html += get_card_element(card)
table_html += f'</div>'

table_html += f'</div>'
# 🔴 [게임 보드 끝]

render_html(table_html)

# --- 7. 컨트롤러 버튼 시스템 ---
if not st.session_state.game_over:
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("Hit (카드 받기) 🃏", use_container_width=True):
            st.session_state.player_hand.append(st.session_state.deck.pop())
            if calculate_score(st.session_state.player_hand) > 21:
                st.session_state.game_over = True
                st.session_state.winner = "딜러"
            st.rerun()
    with btn_col2:
        if st.button("Stand (멈추기) 🛑", use_container_width=True):
            st.session_state.game_over = True
            while calculate_score(st.session_state.dealer_hand) < 17:
                st.session_state.dealer_hand.append(st.session_state.deck.pop())
            
            f_dealer_score = calculate_score(st.session_state.dealer_hand)
            f_player_score = calculate_score(st.session_state.player_hand)
            
            if f_dealer_score > 21 or f_player_score > f_dealer_score:
                st.session_state.winner = "플레이어"
            elif f_player_score < f_dealer_score:
                st.session_state.winner = "딜러"
            else:
                st.session_state.winner = "무승부"
            st.rerun()

# --- 8. 게임 결과 창 ---
if st.session_state.game_over:
    if st.session_state.winner == "플레이어":
        st.success(f"🎉 승리했습니다! 딜러의 최종 점수는 {dealer_score}점입니다.")
        st.balloons()
    elif st.session_state.winner == "플레이어(블랙잭)":
        st.success(f"👑 블랙잭! 완벽한 대승리입니다!")
        st.balloons()
    elif st.session_state.winner == "딜러":
        if player_score > 21: st.error("💥 버스트(21점 초과)! 패배했습니다.")
        else: st.error(f"😢 패배했습니다. 딜러의 최종 점수는 {dealer_score}점입니다.")
    else:
        st.warning(f"🤝 {dealer_score}점으로 비겼습니다!")
        
    if st.button("🔄 새 게임 시작", use_container_width=True, type="primary"):
        reset_game()
        st.rerun()

# --- 9. ⭐ [핵심 요구사항] 우측 하단 고정 테마 선택창 UI ---
# 여백 확보 후 화면 맨 밑 우측에 레이아웃 배치
st.write("")
st.write("")
st.write("")
ui_col1, ui_col2 = st.columns([2.5, 1.5])
with ui_col2:
    # 팝오버를 사용해 우측 하단에 미니멀한 테마 선택창 구현
    with st.popover("🎨 테마 변경 (Theme)", use_container_width=True):
        selected = st.radio(
            "배경 매트 스타일:",
            ["🖤 다크 매트", "🤍 라이트 브리즈", "💜 사이버 펑크", "🌲 모스 그린"],
            index=["🖤 다크 매트", "🤍 라이트 브리즈", "💜 사이버 펑크", "🌲 모스 그린"].index(current_theme)
        )
        if selected != current_theme:
            st.session_state['game_theme'] = selected
            st.rerun()