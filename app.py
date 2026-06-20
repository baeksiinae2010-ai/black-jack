import streamlit as st
import random

# --- 1. 웹페이지 기본 설정 ---
st.set_page_config(page_title="럭셔리 카지노 블랙잭", page_icon="🃏", layout="wide")

# --- 2. 게임 세션 및 베팅 시스템 초기화 ---
if 'game_theme' not in st.session_state:
    st.session_state['game_theme'] = "🎰 라스베이거스 클래식"
if 'balance' not in st.session_state:
    st.session_state['balance'] = 1000
if 'current_bet' not in st.session_state:
    st.session_state['current_bet'] = 0
if 'game_stage' not in st.session_state:
    st.session_state['game_stage'] = "betting"

# 리얼 카지노 무드를 위한 주변 분위기 테마셋 (테이블 매트는 초록색 고정)
themes = {
    "🎰 라스베이거스 클래식": {
        "bg": "#121110", "text": "#F5E6C8", "sub": "#D4AF37", "border": "#8B5A2B",
        "card_back": "linear-gradient(135deg, #B22222, #7B0000)", "text_muted": "#A89F91"
    },
    "👑 몬테카를로 VIP 룸": {
        "bg": "#1C0610", "text": "#FFFFFF", "sub": "#F1C40F", "border": "#D4AF37",
        "card_back": "linear-gradient(135deg, #1F3A60, #0F1E36)", "text_muted": "#C7B3C3"
    },
    "💎 마카오 프리미엄": {
        "bg": "#070B14", "text": "#E2E8F0", "sub": "#38BDF8", "border": "#475569",
        "card_back": "linear-gradient(135deg, #2D1B4E, #1A0F33)", "text_muted": "#94A3B8"
    },
    "🕶️ 싱가포르 하이롤러": {
        "bg": "#0D0D0E", "text": "#E4E4E7", "sub": "#A1A1AA", "border": "#27272A",
        "card_back": "linear-gradient(135deg, #34495E, #222F3D)", "text_muted": "#71717A"
    }
}

current_theme = st.session_state['game_theme']
cfg = themes[current_theme]

# --- 3. 🪄 고정형 초록 테이블 매트 & 3D 카드 플립 CSS ---
st.markdown(f"""
<style>
    .stApp {{
        background-color: {cfg['bg']} !important;
        color: {cfg['text']} !important;
        transition: background-color 0.4s ease;
    }}
    
    h1, h2, h3, p, span, div {{
        color: {cfg['text']};
    }}

    /* 칩 보관함 오버홀 */
    .chip-bank-container {{
        background: rgba(0, 0, 0, 0.4);
        border: 2px solid {cfg['border']};
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: inset 0px 4px 12px rgba(0,0,0,0.6);
    }}
    
    .casino-chip {{
        width: 55px; height: 55px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center; justify-content: center;
        font-weight: bold; font-size: 13px;
        color: white !important;
        border: 4px dashed #FFF;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.4);
        margin: 4px;
    }}
    .chip-10 {{ background: #DC2626; }}
    .chip-50 {{ background: #2563EB; }}
    .chip-100 {{ background: #16A34A; }}
    .chip-500 {{ background: #7C3AED; }}

    /* [초록색 리얼 원목 테두리 테이블 매트 고정] */
    .casino-table {{
        background-color: #0A4D34 !important; /* 테마 무관 딥 카지노 그린 고정 */
        border: 14px solid #4A2711 !important; /* 리얼 원목 대나무 느낌 마감 */
        box-shadow: inset 0 0 0 3px #D4AF37, inset 0 0 40px rgba(0,0,0,0.7), 0 15px 35px rgba(0,0,0,0.6) !important;
        border-radius: 50px;
        padding: 35px;
        position: relative;
        min-height: 500px;
    }}

    /* 우측 상단 원목 테이블 내부 슈케이스 덮어둔 덱 파일 */
    .deck-pile {{
        position: absolute;
        top: 25px; right: 35px;
        width: 85px; height: 125px;
        background: {cfg['card_back']};
        border-radius: 8px;
        border: 2px solid #FFF;
        box-shadow: -2px 2px 0px #AAA, -4px 4px 0px #777, -7px 7px 12px rgba(0,0,0,0.6);
        display: flex;
        align-items: center; justify-content: center;
        font-weight: 900; font-size: 13px;
        color: rgba(255,255,255,0.8);
        letter-spacing: 1px;
    }}

    /* [슬롯 좌우 늘어남 방지 패치] 무조건 카드 크기만큼만 예쁘게 정렬 */
    .slot-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
        min-height: 145px;
        width: fit-content !important;
        min-width: 280px;
        background: rgba(0,0,0,0.25);
        border: 2px dashed rgba(255,255,255,0.2);
        border-radius: 12px;
        padding: 10px 20px;
        margin: 10px auto !important;
    }}

    /* --- 완벽한 3D 카드 딜링 시스템 (날아올땐 뒷면 -> 안착 후 0.7초 플립) --- */
    .card-container {{
        perspective: 1000px;
        width: 85px; height: 125px;
        display: inline-block;
        position: relative;
    }}
    .card-inner {{
        width: 100%; height: 100%;
        position: relative;
        transform-style: preserve-3d;
    }}
    .card-front, .card-back {{
        position: absolute;
        width: 100%; height: 100%;
        backface-visibility: hidden;
        border-radius: 8px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.4);
    }}
    .card-back {{
        background: {cfg['card_back']};
        border: 2px solid #FFF;
        transform: rotateY(0deg);
    }}
    .card-front {{
        background: white !important;
        transform: rotateY(180deg);
    }}

    /* 0.7초 드로우앤플립 애니메이션 (비행시 뒷면유지 -> 후반부 뒤집기) */
    .flip-card-animate {{
        animation: flyAndFlip 0.7s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }}
    
    /* 딜러 히든카드는 날아와서 뒤집지 않고 뒷면 고정 */
    .hidden-card-animate {{
        animation: flyFaceDown 0.7s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }}

    @keyframes flyAndFlip {{
        0% {{
            transform: translate(260px, -140px) rotateY(0deg) scale(0.8);
            opacity: 0;
        }}
        55% {{
            transform: translate(0, 0) rotateY(0deg) scale(1);
            opacity: 1;
        }}
        100% {{
            transform: translate(0, 0) rotateY(180deg) scale(1);
            opacity: 1;
        }}
    }}

    @keyframes flyFaceDown {{
        0% {{
            transform: translate(260px, -140px) scale(0.8);
            opacity: 0;
        }}
        100% {{
            transform: translate(0, 0) scale(1);
            opacity: 1;
        }}
    }}

    /* --- [우측 상단 알람방식 알림창 커스텀 앵커] --- */
    div:has(> #toast-anchor) + div {{
        position: fixed !important;
        top: 25px !important;
        right: 25px !important;
        width: 310px !important;
        background: #1E293B !important;
        border: 2px solid #D4AF37 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        z-index: 999999 !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6) !important;
        animation: slideInToast 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
    
    @keyframes slideInToast {{
        0% {{ transform: translateX(120%); opacity: 0; }}
        100% {{ transform: translateX(0); opacity: 1; }}
    }}

    /* 결과 문구만 슉 사라지는 효과 */
    .toast-text-fade {{
        animation: fadeOutText 3.8s ease forwards;
    }}
    @keyframes fadeOutText {{
        0% {{ opacity: 1; transform: translateY(0); }}
        80% {{ opacity: 1; transform: translateY(0); }}
        100% {{ opacity: 0; transform: translateY(-10px); height: 0; margin: 0; padding: 0; overflow: hidden; }}
    }}

    /* 하단 팝오버 고정 마감 */
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

# --- 4. 카드 엔진 코어 모듈 ---
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

# 3D 렌더링에 매칭되는 카드 빌더 함수 (글자 밀림/좌우반전 결함 완전 교정)
def get_card_element(card, is_hidden=False):
    if is_hidden:
        return '<div class="card-container"><div class="card-inner hidden-card-animate"><div class="card-back"></div></div></div>'
    
    suit, rank = card[0], card[1]
    color = "#E53E3E" if suit in ['♥', '♦'] else "#1A202C"
    return f"""
    <div class="card-container">
        <div class="card-inner flip-card-animate">
            <div class="card-back"></div>
            <div class="card-front">
                <div style="position:absolute; top:6px; left:8px; font-size:16px; font-weight:bold; color:{color};">{rank}</div>
                <div style="position:absolute; top:22px; left:8px; font-size:12px; color:{color};">{suit}</div>
                <div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-size:36px; color:{color};">{suit}</div>
            </div>
        </div>
    </div>
    """

def start_round():
    if st.session_state.current_bet <= 0: return
    st.session_state.deck = create_deck()
    st.session_state.player_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
    st.session_state.dealer_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
    st.session_state.game_stage = "playing"

def resolve_round(result):
    st.session_state.game_stage = "resolved"
    st.session_state.round_result = result
    if result == "player_blackjack": st.session_state.balance += int(st.session_state.current_bet * 2.5)
    elif result == "player_win": st.session_state.balance += st.session_state.current_bet * 2
    elif result == "push": st.session_state.balance += st.session_state.current_bet
    st.session_state.current_bet = 0

# --- 5. UI 그리기 디스플레이 ---
st.markdown("<h1 style='text-align: center; font-weight: 900; margin-bottom: 20px;'>🎰 LUXURY BLACKJACK</h1>", unsafe_allow_html=True)

col_bank, col_table = st.columns([1, 3.2])

# [왼쪽 영역: 사이드 뱅킹 박스]
with col_bank:
    st.markdown("### 🏦 내 자산 락커")
    bank_html = f"""
    <div class="chip-bank-container">
        <p style="font-size: 12px; color: {cfg['text_muted']}; margin: 0;">보유 뱅크론</p>
        <h2 style="color: #FBBF24 !important; font-weight: 900; margin: 2px 0 12px 0;">${st.session_state.balance}</h2>
        <p style="font-size: 12px; color: {cfg['text_muted']}; margin: 0;">현재 판돈 베팅액</p>
        <h3 style="color: #EF4444 !important; font-weight: 700; margin: 2px 0 15px 0;">${st.session_state.current_bet}</h3>
        <hr style="border-color: rgba(255,255,255,0.1); margin-bottom: 12px;">
        <div class="casino-chip chip-10">$10</div>
        <div class="casino-chip chip-50">$50</div>
        <div class="casino-chip chip-100">$100</div>
        <div class="casino-chip chip-500">$500</div>
    </div>
    """
    render_html(bank_html)
    
    if st.session_state.game_stage == "betting":
        st.write("")
        b_c1, b_c2 = st.columns(2)
        with b_c1: chip_val = st.selectbox("칩 선택", [10, 50, 100, 500], label_visibility="collapsed")
        with b_c2:
            if st.button("배팅 추가 🪙", use_container_width=True):
                if st.session_state.balance >= chip_val:
                    st.session_state.current_bet += chip_val
                    st.session_state.balance -= chip_val
                    st.rerun()
        if st.session_state.current_bet > 0:
            if st.button("🃏 패 나누기 (Deal)", type="primary", use_container_width=True):
                start_round()
                st.rerun()
            if st.button("❌ 베팅 전액 취소", use_container_width=True):
                st.session_state.balance += st.session_state.current_bet
                st.session_state.current_bet = 0
                st.rerun()
    else:
        st.write("")
        st.info("🃏 딜러와의 승부가 진행 중입니다.")

# [오른쪽 영역: 고정형 녹색 벨벳 카지노 데스크]
with col_table:
    if st.session_state.game_stage != "betting":
        p_score = calculate_score(st.session_state.player_hand)
        d_score = calculate_score(st.session_state.dealer_hand)
        if st.session_state.game_stage == "playing" and p_score == 21:
            resolve_round("player_blackjack")
            st.rerun()

    # 원목 그린 Felt 테이블 시작
    table_html = '<div class="casino-table">'
    table_html += '<div class="deck-pile">DECK</div>'  # 우측 상단 덮어둔 카드 덱 파일 구조물
    
    if st.session_state.game_stage == "betting":
        # 군더더기 문구 모두 제거하고 요구한 메인 타이틀만 깔끔하게 배치
        table_html += """
        <div style="text-align: center; padding-top: 160px;">
            <h2 style="font-weight: 800; opacity: 0.75; letter-spacing: 5px; color: #D4AF37 !important; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">PLACE YOUR BETS</h2>
        </div>
        """
    else:
        # 딜러 영역 및 카드 지정 슬롯 상단 배치
        table_html += f'<div style="text-align: center; font-size: 11px; font-weight: bold; color: rgba(255,255,255,0.6); letter-spacing:1px;">DEALER HAND</div>'
        table_html += '<div class="slot-container">'
        for idx, card in enumerate(st.session_state.dealer_hand):
            if idx == 1 and st.session_state.game_stage == "playing":
                table_html += get_card_element(card, is_hidden=True)
            else:
                table_html += get_card_element(card)
        table_html += '</div>'
        
        table_html += '<div style="text-align:center; color:rgba(255,255,255,0.15); margin:20px 0; font-size:12px;">★ BLACKJACK PAYS 3 TO 2 ★</div>'
        
        # 플레이어 영역 및 카드 지정 슬롯 하단 배치
        table_html += '<div class="slot-container">'
        for card in st.session_state.player_hand:
            table_html += get_card_element(card)
        table_html += '</div>'
        table_html += f'<div style="text-align: center; font-size: 13px; font-weight: 800; color: #FBBF24;">MY HAND ({p_score}점)</div>'

    table_html += '</div>'
    render_html(table_html)

    # 진행 컨트롤 버튼 액션
    if st.session_state.game_stage == "playing":
        st.write("")
        ctrl_col1, ctrl_col2 = st.columns(2)
        with ctrl_col1:
            if st.button("Hit (카드 더 받기) 🃏", use_container_width=True):
                st.session_state.player_hand.append(st.session_state.deck.pop())
                if calculate_score(st.session_state.player_hand) > 21:
                    resolve_round("dealer_win")
                st.rerun()
        with ctrl_col2:
            if st.button("Stand (멈추고 결과 비교) 🛑", use_container_width=True, type="primary"):
                # 내가 스탠드를 하면 비로소 상대(딜러)도 한 장씩 카드를 채워나가는 모션 구현
                while calculate_score(st.session_state.dealer_hand) < 17:
                    st.session_state.dealer_hand.append(st.session_state.deck.pop())
                
                final_d = calculate_score(st.session_state.dealer_hand)
                final_p = calculate_score(st.session_state.player_hand)
                
                if final_d > 21 or final_p > final_d: resolve_round("player_win")
                elif final_p < final_d: resolve_round("dealer_win")
                else: resolve_round("push")
                st.rerun()

# --- 6. 🔔 우측 상단 알람방식 결과 통보창 및 고정식 재시작 버튼 패치 ---
if st.session_state.game_stage == "resolved":
    p_final = calculate_score(st.session_state.player_hand)
    d_final = calculate_score(st.session_state.dealer_hand)
    res = st.session_state.round_result
    
    # 알람창 스타일 매핑 설정
    if p_final > 21: title_text, border_c = "💥 버스트 패배!", "#EF4444"
    elif d_final > 21: title_text, border_c = "🎉 딜러 버스트 승리!", "#10B981"; st.balloons()
    elif res == "player_blackjack": title_text, border_c = "🃏 천하무적 블랙잭!", "#F59E0B"; st.balloons()
    elif res == "player_win": title_text, border_c = f"🏆 승리! ({p_final} vs {d_final})", "#10B981"; st.balloons()
    elif res == "dealer_win": title_text, border_c = f"😢 패배... ({p_final} vs {d_final})", "#EF4444"
    else: title_text, border_c = f"🤝 무승부 푸시 ({p_final}점)", "#64748B"

    # 히든 앵커를 선언하고 CSS를 통해 다음 컨테이너 전체를 우측 상단에 알람창처럼 오버레이 고정시킴
    st.markdown('<div id="toast-anchor"></div>', unsafe_allow_html=True)
    with st.container():
        # 결과 텍스트 구역 (CSS 스케줄러로 3.8초 뒤 자연스럽게 투명해지며 사라짐)
        st.markdown(f"""
        <div class="toast-text-fade" style="border-left: 4px solid {border_c}; padding-left: 10px; margin-bottom: 12px;">
            <p style="font-size: 11px; color:#94A3B8; margin:0;">ROUND RESULT</p>
            <h4 style="color: white !important; font-weight:900; margin: 2px 0 0 0; font-size:15px;">{title_text}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # 다시시작 제어 컴포넌트 (사라지지 않고 고정되어 유저가 누를 때까지 상시 유지)
        if st.button("🔄 다음 게임 정산 및 시작", use_container_width=True, type="primary"):
            st.session_state.game_stage = "betting"
            st.rerun()

# [우측 하단 구석 고정 전용 팝오버]
with st.popover("🎨 VIP 라운지 테마 조명 변경"):
    selected = st.radio(
        "주변 분위기 전환", list(themes.keys()),
        index=list(themes.keys()).index(current_theme)
    )
    if selected != current_theme:
        st.session_state['game_theme'] = selected
        st.rerun()