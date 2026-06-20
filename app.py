import streamlit as st
import random
import time

# --- 1. 웹페이지 기본 설정 ---
st.set_page_config(page_title="카드 게임", page_icon="🃏", layout="wide")

# --- 2. 게임 세션 및 베팅 시스템 초기화 ---
if 'balance' not in st.session_state:
    st.session_state['balance'] = 1000
if 'current_bet' not in st.session_state:
    st.session_state['current_bet'] = 0
# 게임 스테이지: betting -> playing -> dealer_turn -> resolved
if 'game_stage' not in st.session_state:
    st.session_state['game_stage'] = "betting"
if 'bet_chips' not in st.session_state:
    st.session_state['bet_chips'] = []
if 'bet_confirmed' not in st.session_state:
    st.session_state['bet_confirmed'] = False

# [요구사항 1] 테마 기능 완전 삭제 및 클래식 그린 테이블 분위기 고정
cfg = {
    "bg": "#082E13", "table": "#0A4D26", "text": "#FFFFFF", "sub": "#A7F3D0", "border": "#D4AF37",
    "text_muted": "#86EFAC"
}

# --- 3. 🪄 3D 카드 뒤집기 및 칩 애니메이션 CSS ---
st.markdown(f"""
<style>
    .stApp {{
        background-color: {cfg['bg']} !important;
        color: {cfg['text']} !important;
    }}
    
    h1, h2, h3, p, span, div {{
        color: {cfg['text']};
    }}

    /* --- [베팅 칩 관련 CSS (기존 유지)] --- */
    .chip-bank-container {{
        background: rgba(0, 0, 0, 0.3);
        border: 2px solid {cfg['border']};
        border-radius: 16px;
        padding: 20px;
        box-shadow: inset 0px 4px 10px rgba(0,0,0,0.5);
        position: relative;
    }}
    .bet-status-area {{
        display: flex; justify-content: space-between; align-items: center;
        margin: 2px 0 15px 0; min-height: 80px;
    }}
    .chip-stack-zone {{
        position: relative; width: 65px; height: 80px;
        display: flex; align-items: flex-end; justify-content: center;
    }}
    .stacked-chip {{
        position: absolute;
        width: 52px; height: 20px;
        border-radius: 50%;
        border: 2px dashed rgba(255,255,255,0.6);
        font-size: 10px; font-weight: 900; color: white !important;
        display: flex; align-items: center; justify-content: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        transition: transform 0.2s ease;
        animation: dropChip 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }}
    @keyframes dropChip {{
        0% {{ transform: translateY(-40px) scale(1.1); opacity: 0; }}
        100% {{ transform: translateY(0) scale(1); opacity: 1; }}
    }}
    .stButton > button[key^="btn_chip_"] {{
        width: 58px !important; height: 58px !important;
        border-radius: 50% !important; font-weight: 900 !important; font-size: 14px !important;
        color: white !important; padding: 0 !important; min-width: 58px !important;
        cursor: pointer; transition: transform 0.05s ease, box-shadow 0.05s ease !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
    }}

    /* --- [카지노 테이블 및 카드 슬롯] --- */
    .casino-table {{
        background-color: {cfg['table']};
        border: 4px solid {cfg['border']};
        border-radius: 60px 60px 30px 30px;
        padding: 30px;
        box-shadow: 0px 20px 50px rgba(0,0,0,0.6), inset 0px 0px 50px rgba(0,0,0,0.5);
        position: relative;
        min-height: 520px;
    }}
    
    .slot-container {{
        display: flex; justify-content: center; gap: 15px; min-height: 135px;
        background: rgba(0,0,0,0.12); border: 2px dashed rgba(255,255,255,0.15);
        border-radius: 14px; padding: 10px; margin: 10px auto; max-width: 80%;
    }}

    /* --- [요구사항 2] 진짜 카드 뒷면 무늬 및 글씨 반전 없는 3D 뒤집기 모션 --- */
    .deck-pile {{
        position: absolute; top: 25px; right: 40px; width: 90px; height: 130px;
        background-color: #002244; 
        background-image: 
            linear-gradient(135deg, rgba(255,255,255,0.1) 25%, transparent 25%),
            linear-gradient(225deg, rgba(255,255,255,0.1) 25%, transparent 25%),
            linear-gradient(45deg, rgba(255,255,255,0.1) 25%, transparent 25%),
            linear-gradient(315deg, rgba(255,255,255,0.1) 25%, #002244 25%);
        background-position:  10px 0, 10px 0, 0 0, 0 0;
        background-size: 20px 20px;
        border-radius: 8px; border: 2px solid #FFF;
        box-shadow: -3px 3px 0px #ccc, -6px 6px 0px #999, -9px 9px 15px rgba(0,0,0,0.5);
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; font-size: 12px; color: rgba(255,255,255,0.7); letter-spacing: 1px;
    }}

    .playing-card-container {{
        perspective: 800px;
        width: 85px; height: 125px;
        position: relative;
    }}

    .card-inner-flip {{
        width: 100%; height: 100%; position: relative;
        transform-style: preserve-3d;
        animation: flyAndFlip 0.7s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }}

    .card-inner-hidden {{
        width: 100%; height: 100%; position: relative;
        transform-style: preserve-3d;
        animation: flyFaceDown 0.7s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }}

    .card-front, .card-back-face {{
        position: absolute; width: 100%; height: 100%;
        backface-visibility: hidden; border-radius: 8px;
        box-shadow: 0px 5px 10px rgba(0,0,0,0.3);
    }}

    .card-front {{
        background-color: white !important;
        transform: rotateY(0deg); 
    }}

    .card-back-face {{
        background-color: #002244; 
        background-image: 
            linear-gradient(135deg, rgba(255,255,255,0.15) 25%, transparent 25%),
            linear-gradient(225deg, rgba(255,255,255,0.15) 25%, transparent 25%),
            linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%),
            linear-gradient(315deg, rgba(255,255,255,0.15) 25%, #002244 25%);
        background-position:  10px 0, 10px 0, 0 0, 0 0; background-size: 20px 20px;
        border: 2px solid #FFF;
        transform: rotateY(180deg);
    }}

    @keyframes flyAndFlip {{
        0% {{ transform: translate(250px, -120px) rotateY(180deg) scale(0.9); opacity: 0; }}
        50% {{ transform: translate(0, 0) rotateY(180deg) scale(1); opacity: 1; }}
        100% {{ transform: translate(0, 0) rotateY(0deg) scale(1); opacity: 1; }}
    }}

    @keyframes flyFaceDown {{
        0% {{ transform: translate(250px, -120px) rotateY(180deg) scale(0.9); opacity: 0; }}
        100% {{ transform: translate(0, 0) rotateY(180deg) scale(1); opacity: 1; }}
    }}
</style>
""", unsafe_allow_html=True)

def render_html(html_str):
    st.markdown("".join([line.strip() for line in html_str.split("\n")]), unsafe_allow_html=True)

# --- 4. 게임 핵심 함수 ---
def create_deck():
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [[suit, rank] for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

def calculate_score(hand):
    score = 0; aces = 0
    for card in hand:
        rank = card[1]
        if rank in ['J', 'Q', 'K']: score += 10
        elif rank == 'A': score += 11; aces += 1
        else: score += int(rank)
    while score > 21 and aces > 0: score -= 10; aces -= 1
    return score

def get_card_element(card, hidden=False):
    if hidden:
        return '''
        <div class="playing-card-container">
            <div class="card-inner-hidden">
                <div class="card-front"></div>
                <div class="card-back-face"></div>
            </div>
        </div>
        '''
    suit, rank = card[0], card[1]
    color = "#E53E3E" if suit in ['♥', '♦'] else "#1A202C"
    return f'''
    <div class="playing-card-container">
        <div class="card-inner-flip">
            <div class="card-front">
                <div style="position:absolute; top:6px; left:8px; font-size:16px; font-weight:bold; color:{color};">{rank}</div>
                <div style="position:absolute; top:22px; left:8px; font-size:12px; color:{color};">{suit}</div>
                <div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-size:36px; color:{color};">{suit}</div>
            </div>
            <div class="card-back-face"></div>
        </div>
    </div>
    '''

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

# --- 5. 🎮 게임 화면 레이아웃 디스플레이 ---
# 선생님 제출용으로 깔끔하게 "카드 게임" 타이틀 고정
st.markdown(f"<h1 style='text-align: center; font-weight: 900; margin-bottom: 20px;'>🃏 카드 게임</h1>", unsafe_allow_html=True)

col_bank, col_table = st.columns([1, 3.2])

with col_bank:
    st.markdown("### 🏦 칩 보관함")
    stack_html = ""
    for i, chip_info in enumerate(st.session_state.bet_chips[-12:]):
        bottom_offset = i * 7
        c, e = chip_info["color"], chip_info["edge"]
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
            <div class="chip-stack-zone">{stack_html}</div>
        </div>
        <hr style="border-color: rgba(255,255,255,0.1); margin-bottom: 12px;">
    </div>
    """
    render_html(bank_html)
    
    if st.session_state.game_stage == "betting":
        if not st.session_state.bet_confirmed:
            st.markdown('<div style="text-align: center; margin-top: -15px; margin-bottom: 15px;">', unsafe_allow_html=True)
            chip_cols = st.columns(4)
            chip_values = [10, 50, 100, 500]
            chip_colors = ["#DC2626", "#2563EB", "#16A34A", "#7C3AED"]
            chip_edges = ["#991B1B", "#1E40AF", "#14532D", "#5B21B6"]
            
            for idx, val in enumerate(chip_values):
                with chip_cols[idx]:
                    c, e = chip_colors[idx], chip_edges[idx]
                    st.markdown(f'''
                    <style>
                    .stButton > button[key="btn_chip_{val}"] {{
                        background: radial-gradient(circle at 30% 30%, {c} 0%, {e} 100%) !important;
                        box-shadow: inset 0 2px 4px rgba(255,255,255,0.4), inset 0 -2px 4px rgba(0,0,0,0.3), 0 4px 0 {e}, 0 8px 10px rgba(0,0,0,0.5) !important;
                        border: 4px dashed rgba(255,255,255,0.6) !important; transform: translateY(0) !important;
                    }}
                    .stButton > button[key="btn_chip_{val}"]:active {{
                        box-shadow: inset 0 2px 4px rgba(255,255,255,0.4), inset 0 -2px 4px rgba(0,0,0,0.3), 0 1px 0 {e}, 0 3px 4px rgba(0,0,0,0.5) !important;
                        transform: translateY(3px) !important;
                    }}
                    </style>
                    ''', unsafe_allow_html=True)
                    
                    if st.button(f"${val}", key=f"btn_chip_{val}", use_container_width=True):
                        if st.session_state.balance >= val:
                            st.session_state.current_bet += val; st.session_state.balance -= val
                            st.session_state.bet_chips.append({"val": val, "color": c, "edge": e})
                            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                if st.button("칩 베팅 🪙", use_container_width=True):
                    if st.session_state.current_bet > 0:
                        st.session_state.bet_confirmed = True; st.rerun()
                    else:
                        st.toast("먼저 위 칩을 눌러 판돈을 배팅해주세요!", icon="⚠️")
            with b_col2:
                if st.button("❌ 배팅 취소", use_container_width=True):
                    if st.session_state.current_bet > 0:
                        st.session_state.balance += st.session_state.current_bet
                        st.session_state.current_bet = 0; st.session_state.bet_chips = []
                        st.rerun()
        else:
            st.success("✅ 판돈이 확정되었습니다!")
            st.write("")
            if st.button("🃏 게임 시작 (Deal)", type="primary", use_container_width=True):
                st.session_state.bet_confirmed = False
                start_round()
                st.rerun()
            if st.button("❌ 배팅 다시하기", use_container_width=True):
                st.session_state.balance += st.session_state.current_bet
                st.session_state.current_bet = 0; st.session_state.bet_chips = []
                st.session_state.bet_confirmed = False
                st.rerun()
    else:
        st.write("")
        st.info("🎰 게임이 진행 중입니다.")

with col_table:
    p_score = 0
    if st.session_state.game_stage not in ["betting"]:
        p_score = calculate_score(st.session_state.player_hand)
        if st.session_state.game_stage == "playing" and p_score > 21:
            resolve_round("dealer_win") 
            st.rerun()

    table_html = f'<div class="casino-table"><div class="deck-pile">DECK</div>'
    
    if st.session_state.game_stage == "betting":
        if not st.session_state.bet_confirmed:
            table_html += f'<div style="text-align: center; padding-top: 150px;"><h2 style="font-weight: 700; opacity: 0.6; letter-spacing:2px;">PLACE YOUR BETS</h2><p style="color: {cfg["text_muted"]}; font-size:14px;">1. 칩을 누른 후 <b>[칩 베팅 🪙]</b> 버튼을 누르세요.<br>2. 그 후 <b>[게임 시작 (Deal)]</b>을 눌러 카드를 돌리세요.</p></div>'
        else:
            table_html += f'<div style="text-align: center; padding-top: 150px;"><h2 style="font-weight: 700; opacity: 0.8; letter-spacing:2px; color: #10B981;">READY TO DEAL</h2><p style="color: {cfg["text_muted"]}; font-size:14px;">왼쪽의 <b>[🃏 게임 시작 (Deal)]</b> 버튼을 눌러 승부를 시작하세요!</p></div>'
    else:
        table_html += f'<div style="text-align: center; font-size: 12px; font-weight: bold; color:{cfg["text_muted"]};">🤖 DEALER TABLE SLOT</div><div class="slot-container">'
        for idx, card in enumerate(st.session_state.dealer_hand):
            if idx == 1 and st.session_state.game_stage == "playing":
                table_html += get_card_element(card, hidden=True) 
            else:
                table_html += get_card_element(card, hidden=False)
        table_html += f'</div>'
        
        table_html += f'<div style="text-align:center; color:rgba(255,255,255,0.1); margin:15px 0;">♣ ♦ ♥ ♠ ♣ ♦ ♥ ♠ ♣ ♦ ♥ ♠</div>'
        
        table_html += f'<div class="slot-container">'
        for card in st.session_state.player_hand:
            table_html += get_card_element(card, hidden=False)
        table_html += f'</div><div style="text-align: center; font-size: 12px; font-weight: bold; color:{cfg["text_muted"]};">🙋‍♂️ MY HAND SLOT ({p_score}점)</div>'
    table_html += f'</div>'
    render_html(table_html)

    if st.session_state.game_stage == "playing":
        ctrl_col1, ctrl_col2 = st.columns(2)
        with ctrl_col1:
            if st.button("Hit (카드 받기) 🃏", use_container_width=True):
                st.session_state.player_hand.append(st.session_state.deck.pop())
                st.rerun()
        with ctrl_col2:
            if st.button("Stand (멈추고 딜러 턴) 🛑", use_container_width=True, type="primary"):
                st.session_state.game_stage = "dealer_turn"
                st.rerun()

    if st.session_state.game_stage == "resolved":
        st.write("")
        d_final = calculate_score(st.session_state.dealer_hand)
        
        if p_score > 21: st.error("💥 버스트! 내가 패배했습니다.")
        elif d_final > 21: st.success("🎉 딜러 버스트! 플레이어 대승리!"); st.balloons()
        elif p_score > d_final: st.success(f"🏆 대승리! ({p_score} vs {d_final})"); st.balloons()
        elif p_score < d_final: st.error(f"😢 패배했습니다. 딜러 승리. ({p_score} vs {d_final})")
        else: st.warning(f"🤝 {p_score}점 동점으로 비겼습니다. 판돈을 돌려받습니다.")

        if st.button("🔄 다음 게임 정산 및 진행하기", use_container_width=True, type="primary"):
            st.session_state.game_stage = "betting"
            st.session_state.bet_confirmed = False
            st.rerun()

if st.session_state.game_stage == "dealer_turn":
    time.sleep(1.2) 
    
    d_score = calculate_score(st.session_state.dealer_hand)
    if d_score < 17:
        st.session_state.dealer_hand.append(st.session_state.deck.pop())
        st.rerun()
    else:
        p_score = calculate_score(st.session_state.player_hand)
        if d_score > 21 or p_score > d_score: resolve_round("player_win")
        elif p_score < d_score: resolve_round("dealer_win")
        else: resolve_round("push")
        st.rerun()