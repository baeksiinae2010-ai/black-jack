import streamlit as st
import random

# --- 1. 웹페이지 기본 설정 ---
st.set_page_config(page_title="카드 게임", page_icon="🃏", layout="wide")

# --- 2. 게임 세션 및 베팅 시스템 초기화 ---
if 'game_theme' not in st.session_state:
    st.session_state['game_theme'] = "🌲 모스 그린"
if 'balance' not in st.session_state:
    st.session_state['balance'] = 1000
if 'current_bet' not in st.session_state:
    st.session_state['current_bet'] = 0
if 'game_stage' not in st.session_state:
    st.session_state['game_stage'] = "betting"
# 클릭된 칩 목록을 저장하여 쌓이는 효과를 주기 위한 리스트
if 'bet_chips' not in st.session_state:
    st.session_state['bet_chips'] = []

themes = {
    "🌲 모스 그린": {
        "bg": "#0B301D", "table": "#0D472A", "text": "#FFFFFF", "sub": "#A7F3D0", "border": "#D4AF37",
        "card_back": "linear-gradient(135deg, #15803D, #14532D)", "text_muted": "#86EFAC"
    },
    "🖤 다크 매트": {
        "bg": "#0F0F11", "table": "#1A1A1E", "text": "#F4F4F5", "sub": "#A1A1AA", "border": "#3F3F46",
        "card_back": "linear-gradient(135deg, #52525B, #18181B)", "text_muted": "#71717A"
    },
    "🤍 라이트 브리즈": {
        "bg": "#F1F5F9", "table": "#FFFFFF", "text": "#0F172A", "sub": "#475569", "border": "#CBD5E1",
        "card_back": "linear-gradient(135deg, #64748B, #334155)", "text_muted": "#64748B"
    },
    "💜 사이버 펑크": {
        "bg": "#0B0314", "table": "#16072B", "text": "#00FFFF", "sub": "#FF007F", "border": "#FF007F",
        "card_back": "linear-gradient(135deg, #BC00DD, #49007A)", "text_muted": "#BD10E0"
    }
}

current_theme = st.session_state['game_theme']
cfg = themes[current_theme]

# --- 3. 🪄 0.7초 초정밀 카드 딜링 & 3D 테이블 CSS ---
st.markdown(f"""
<style>
    .stApp {{
        background-color: {cfg['bg']} !important;
        color: {cfg['text']} !important;
        transition: background-color 0.3s ease, color 0.3s ease;
    }}
    
    h1, h2, h3, p, span, div {{
        color: {cfg['text']};
    }}

    /* 칩 보관함 레이아웃 */
    .chip-bank-container {{
        background: rgba(0, 0, 0, 0.3);
        border: 2px solid {cfg['border']};
        border-radius: 16px;
        padding: 20px;
        box-shadow: inset 0px 4px 10px rgba(0,0,0,0.5);
        position: relative;
    }}

    /* 판돈 정보와 쌓이는 칩을 나란히 놓기 위한 플렉스 상자 */
    .bet-status-area {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2px 0 15px 0;
        min-height: 80px;
    }}

    /* 칩이 차곡차곡 쌓이는 스택 컨테이너 */
    .chip-stack-zone {{
        position: relative;
        width: 65px;
        height: 80px;
        display: flex;
        align-items: flex-end;
        justify-content: center;
    }}

    /* 3D 누적 스택 칩 애니메이션 요소 (옆면의 두께가 보이도록 형태 변경) */
    .stacked-chip {{
        position: absolute;
        width: 52px; height: 20px;
        border-radius: 50%;
        border: 2px dashed rgba(255,255,255,0.6);
        font-size: 10px;
        font-weight: 900;
        color: white !important;
        display: flex;
        align-items: center;
        justify-content: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        transition: transform 0.2s ease;
        animation: dropChip 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }}

    @keyframes dropChip {{
        0% {{ transform: translateY(-40px) scale(1.1); opacity: 0; }}
        100% {{ transform: translateY(0) scale(1); opacity: 1; }}
    }}

    /* 리얼 3D 칩 버튼 공통 규격 */
    .stButton > button[key^="btn_chip_"] {{
        width: 58px !important;
        height: 58px !important;
        border-radius: 50% !important;
        font-weight: 900 !important;
        font-size: 14px !important;
        color: white !important;
        padding: 0 !important;
        min-width: 58px !important;
        cursor: pointer;
        transition: transform 0.05s ease, box-shadow 0.05s ease !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
    }}

    /* 리얼 카지노 테이블 매트 */
    .casino-table {{
        background-color: {cfg['table']};
        border: 4px solid {cfg['border']};
        border-radius: 60px 60px 30px 30px;
        padding: 30px;
        box-shadow: 0px 20px 50px rgba(0,0,0,0.6), inset 0px 0px 50px rgba(0,0,0,0.5);
        position: relative;
        min-height: 520px;
    }}

    /* [오른쪽 상단] 입체 카드 덱 (딜링 슈) */
    .deck-pile {{
        position: absolute;
        top: 25px; right: 40px;
        width: 90px; height: 130px;
        background: {cfg['card_back']};
        border-radius: 8px;
        border: 2px solid #FFF;
        box-shadow: -3px 3px 0px #ccc, -6px 6px 0px #999, -9px 9px 15px rgba(0,0,0,0.5);
        display: flex;
        align-items: center; justify-content: center;
        font-weight: bold; font-size: 12px;
        color: rgba(255,255,255,0.7);
        letter-spacing: 1px;
    }}

    /* 카드 전용 지정 슬롯 (점선 구역) */
    .slot-container {{
        display: flex;
        justify-content: center;
        gap: 15px;
        min-height: 135px;
        background: rgba(0,0,0,0.12);
        border: 2px dashed rgba(255,255,255,0.15);
        border-radius: 14px;
        padding: 10px;
        margin: 10px auto;
        max-width: 80%;
    }}

    /* 0.7초 리얼 드로잉 & 플립 애니메이션 */
    .playing-card {{
        width: 85px; height: 125px;
        background-color: white !important;
        border-radius: 8px;
        position: relative;
        box-shadow: 0px 5px 10px rgba(0,0,0,0.3);
        transform-style: preserve-3d;
        animation: flyAndFlip 0.7s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }}
    
    .card-back-animate {{
        width: 85px; height: 125px;
        background: {cfg['card_back']};
        border-radius: 8px;
        border: 2px solid #FFF;
        box-shadow: 0px 5px 10px rgba(0,0,0,0.3);
        animation: flyFaceDown 0.7s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }}

    @keyframes flyAndFlip {{
        0% {{
            transform: translate(250px, -120px) rotateX(0deg) rotateY(180deg) scale(0.9);
            opacity: 0;
        }}
        60% {{
            transform: translate(0, 0) rotateX(0deg) rotateY(180deg) scale(1);
            opacity: 1;
        }}
        100% {{
            transform: translate(0, 0) rotateX(0deg) rotateY(0deg) scale(1);
            opacity: 1;
        }}
    }}

    @keyframes flyFaceDown {{
        0% {{
            transform: translate(250px, -120px) rotate(-20deg) scale(0.9);
            opacity: 0;
        }}
        100% {{
            transform: translate(0, 0) rotate(0deg) scale(1);
            opacity: 1;
        }}
    }}

    /* 테마 선택창 고정 우측 하단 구석 강제 처박기 */
    div[data-testid="stPopover"] {{
        position: fixed !important;
        bottom: 15px !important;
        right: 15px !important;
        z-index: 9999 !important;
    }}
</style>
""", unsafe_allow_html=True)

def render_html(html_str):
    st.markdown("".join([line.strip() for line in html_str.split("\n")]), unsafe_allow_html=True)

# --- 4. 카드 시스템 핵심 함수 ---
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
    return f'<div class="playing-card"><div style="position:absolute; top:6px; left:8px; font-size:16px; font-weight:bold; color:{color};">{rank}</div><div style="position:absolute; top:22px; left:8px; font-size:12px; color:{color};">{suit}</div><div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-size:36px; color:{color};">{suit}</div></div>'

def start_round():
    if st.session_state.current_bet <= 0: return
    st.session_state.deck = create_deck()
    st.session_state.player_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
    st.session_state.dealer_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
    st.session_state.game_stage = "playing"

def resolve_round(result):
    st.session_state.game_stage = "resolved"
    if result == "player_blackjack": st.session_state.balance += int(st.session_state.current_bet * 2.5)
    elif result == "player_win": st.session_state.balance += st.session_state.current_bet * 2
    elif result == "push": st.session_state.balance += st.session_state.current_bet
    st.session_state.current_bet = 0
    st.session_state.bet_chips = []

# --- 5. 🎮 게임 화면 레이아웃 그리기 ---
st.markdown(f"<h1 style='text-align: center; font-weight: 900; margin-bottom: 20px;'>🃏 카드 게임</h1>", unsafe_allow_html=True)

col_bank, col_table = st.columns([1, 3.2])

# [왼쪽 영역: 칩 보관 은행 박스]
with col_bank:
    st.markdown("### 🏦 칩 보관함")
    
    # 누적된 칩들을 입체적으로 쌓아 올릴 HTML 코드 동적 생성
    stack_html = ""
    for i, chip_info in enumerate(st.session_state.bet_chips[-12:]): # 최대 12개까지 화려하게 쌓기
        bottom_offset = i * 7
        c = chip_info["color"]
        e = chip_info["edge"]
        # 3D 원통형 측면 두께를 만들어내는 핵심 다중 그림자 코드
        shadows = f"inset 0 1px 3px rgba(255,255,255,0.5), inset 0 -2px 3px rgba(0,0,0,0.3), 0 1px 0 {e}, 0 2px 0 {e}, 0 3px 0 {e}, 0 4px 0 {e}, 0 6px 6px rgba(0,0,0,0.6)"
        stack_html += f'<div class="stacked-chip" style="background:{c}; bottom:{bottom_offset}px; box-shadow:{shadows};">${chip_info["val"]}</div>'

    bank_html = f"""
    <div class="chip-bank-container">
        <p style="font-size: 12px; color: {cfg['text_muted']}; margin: 0;">보유 자산</p>
        <h2 style="color: #FBBF24 !important; font-weight: 900; margin: 2px 0 12px 0;">${st.session_state.balance}</h2>
        <div class="bet-status-area">
            <div>
                <p style="font-size: 12px; color: {cfg['text_muted']}; margin: 0; text-align: left;">베팅된 판돈</p>
                <h3 style="color: #EF4444 !important; font-weight: 700; margin: 2px 0 0 0; text-align: left;">${st.session_state.current_bet}</h3>
            </div>
            <div class="chip-stack-zone">
                {stack_html}
            </div>
        </div>
        <hr style="border-color: rgba(255,255,255,0.1); margin-bottom: 12px;">
    </div>
    """
    render_html(bank_html)
    
    if st.session_state.game_stage == "betting":
        st.markdown('<div style="text-align: center; margin-top: -15px; margin-bottom: 15px;">', unsafe_allow_html=True)
        chip_cols = st.columns(4)
        chip_values = [10, 50, 100, 500]
        # 칩 표면 색상과 측면 두께 색상(어두운 톤)
        chip_colors = ["#DC2626", "#2563EB", "#16A34A", "#7C3AED"]
        chip_edges = ["#991B1B", "#1E40AF", "#14532D", "#5B21B6"]
        
        for idx, val in enumerate(chip_values):
            with chip_cols[idx]:
                c = chip_colors[idx]
                e = chip_edges[idx]
                # 각 칩 버튼에 입체 질감 그라데이션 및 측면 두께 3D 음영 부여, 클릭 시 내려앉는 CSS 인젝션
                st.markdown(f'''
                <style>
                .stButton > button[key="btn_chip_{val}"] {{
                    background: radial-gradient(circle at 30% 30%, {c} 0%, {e} 100%) !important;
                    box-shadow: inset 0 2px 4px rgba(255,255,255,0.4), inset 0 -2px 4px rgba(0,0,0,0.3), 0 4px 0 {e}, 0 8px 10px rgba(0,0,0,0.5) !important;
                    border: 4px dashed rgba(255,255,255,0.6) !important;
                    transform: translateY(0) !important;
                }}
                .stButton > button[key="btn_chip_{val}"]:active {{
                    box-shadow: inset 0 2px 4px rgba(255,255,255,0.4), inset 0 -2px 4px rgba(0,0,0,0.3), 0 1px 0 {e}, 0 3px 4px rgba(0,0,0,0.5) !important;
                    transform: translateY(3px) !important;
                }}
                </style>
                ''', unsafe_allow_html=True)
                
                if st.button(f"${val}", key=f"btn_chip_{val}", use_container_width=True):
                    if st.session_state.balance >= val:
                        st.session_state.current_bet += val
                        st.session_state.balance -= val
                        # 스택 구역에 그릴 색상, 음영, 값 정보 추가 저장
                        st.session_state.bet_chips.append({"val": val, "color": c, "edge": e})
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("칩 베팅 🪙", use_container_width=True):
            pass 
            
        if st.session_state.current_bet > 0:
            st.write("")
            if st.button("🃏 게임 시작 (Deal)", type="primary", use_container_width=True):
                start_round()
                st.rerun()
            if st.button("❌ 베팅 취소", use_container_width=True):
                st.session_state.balance += st.session_state.current_bet
                st.session_state.current_bet = 0
                st.session_state.bet_chips = []
                st.rerun()
    else:
        st.write("")
        st.info("🎰 게임이 진행 중입니다.")

# [오른쪽 영역: 3D 카지노 게임 테이블]
with col_table:
    if st.session_state.game_stage != "betting":
        p_score = calculate_score(st.session_state.player_hand)
        d_score = calculate_score(st.session_state.dealer_hand)
        if st.session_state.game_stage == "playing" and p_score == 21:
            resolve_round("player_blackjack")
            st.rerun()

    # 테이블 펠트 시작
    table_html = f'<div class="casino-table">'
    table_html += f'<div class="deck-pile">DECK</div>'
    
    if st.session_state.game_stage == "betting":
        table_html += f"""
        <div style="text-align: center; padding-top: 150px;">
            <h2 style="font-weight: 700; opacity: 0.6; letter-spacing:2px;">PLACE YOUR BETS</h2>
            <p style="color: {cfg['text_muted']}; font-size:14px;">원하는 칩을 클릭하여 베팅한 후 Deal 버튼을 누르면 0.7초 카드 모션이 시작됩니다.</p>
        </div>
        """
    else:
        table_html += f'<div style="text-align: center; font-size: 12px; font-weight: bold; color:{cfg["text_muted"]};">🤖 DEALER TABLE SLOT</div>'
        table_html += f'<div class="slot-container">'
        for idx, card in enumerate(st.session_state.dealer_hand):
            if idx == 1 and st.session_state.game_stage == "playing":
                table_html += '<div class="card-back-animate"></div>'
            else:
                table_html += get_card_element(card)
        table_html += f'</div>'
        
        table_html += f'<div style="text-align:center; color:rgba(255,255,255,0.1); margin:15px 0;">♣ ♦ ♥ ♠ ♣ ♦ ♥ ♠ ♣ ♦ ♥ ♠</div>'
        
        table_html += f'<div class="slot-container">'
        for card in st.session_state.player_hand:
            table_html += get_card_element(card)
        table_html += f'</div>'
        table_html += f'<div style="text-align: center; font-size: 12px; font-weight: bold; color:{cfg["text_muted"]};">🙋‍♂️ MY HAND SLOT ({p_score}점)</div>'

    table_html += f'</div>'
    render_html(table_html)

    # 제어용 작동 버튼
    if st.session_state.game_stage == "playing":
        ctrl_col1, ctrl_col2 = st.columns(2)
        with ctrl_col1:
            if st.button("Hit (카드 받기) 🃏", use_container_width=True):
                st.session_state.player_hand.append(st.session_state.deck.pop())
                if calculate_score(st.session_state.player_hand) > 21:
                    resolve_round("dealer_win")
                st.rerun()
        with ctrl_col2:
            if st.button("Stand (결과 보기) 🛑", use_container_width=True, type="primary"):
                while calculate_score(st.session_state.dealer_hand) < 17:
                    st.session_state.dealer_hand.append(st.session_state.deck.pop())
                
                final_d = calculate_score(st.session_state.dealer_hand)
                final_p = calculate_score(st.session_state.player_hand)
                
                if final_d > 21 or final_p > final_d: resolve_round("player_win")
                elif final_p < final_d: resolve_round("dealer_win")
                else: resolve_round("push")
                st.rerun()

    # 정산 결과 창
    if st.session_state.game_stage == "resolved":
        st.write("")
        p_final = calculate_score(st.session_state.player_hand)
        d_final = calculate_score(st.session_state.dealer_hand)
        
        if p_final > 21: st.error("💥 버스트! 내가 패배했습니다.")
        elif d_final > 21: st.success("🎉 딜러 버스트! 플레이어 대승리!"); st.balloons()
        elif p_final > d_final: st.success(f"🏆 대승리! ({p_final} vs {d_final})"); st.balloons()
        elif p_final < d_final: st.error(f"😢 패배했습니다. 딜러 승리. ({p_final} vs {d_final})")
        else: st.warning(f"🤝 {p_final}점 동점으로 비겼습니다. 판돈을 돌려받습니다.")

        if st.button("🔄 다음 게임 정산 및 진행하기", use_container_width=True, type="primary"):
            st.session_state.game_stage = "betting"
            st.rerun()

# [오른쪽 구석 강제 처박기 테마 선택 버튼]
with st.popover("🎨 테마"):
    selected = st.radio(
        "테마 선택", ["🌲 모스 그린", "🖤 다크 매트", "🤍 라이트 브리즈", "💜 사이버 펑크"],
        index=["🌲 모스 그린", "🖤 다크 매트", "🤍 라이트 브리즈", "💜 사이버 펑크"].index(current_theme)
    )
    if selected != current_theme:
        st.session_state['game_theme'] = selected
        st.rerun()