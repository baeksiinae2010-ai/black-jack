import streamlit as st
import random
import time

# --- 웹페이지 기본 설정 ---
st.set_page_config(page_title="카지노 리얼 블랙잭", page_icon="🎲", layout="centered")

# --- 🎨 1. 테마 및 디자인 설정 (사이드바) ---
st.sidebar.title("🎨 테마 설정")
theme = st.sidebar.radio(
    "원하는 게임 배경을 선택하세요:",
    ["다크 모드 (기본)", "밝은 모드", "클래식 카지노 (그린)", "로열 카지노 (레드)", "미드나잇 (블루)", "럭셔리 (골드)"]
)

# 테마별 색상표 (배경색, 박스색, 글자색)
themes = {
    "다크 모드 (기본)": {"bg": "#121212", "box": "#1E1E1E", "text": "#FFFFFF"},
    "밝은 모드": {"bg": "#F0F2F6", "box": "#FFFFFF", "text": "#000000"},
    "클래식 카지노 (그린)": {"bg": "#0B3B0B", "box": "#155915", "text": "#FFFFFF"},
    "로열 카지노 (레드)": {"bg": "#3B0B0B", "box": "#591515", "text": "#FFFFFF"},
    "미드나잇 (블루)": {"bg": "#0B173B", "box": "#152559", "text": "#FFFFFF"},
    "럭셔리 (골드)": {"bg": "#211A04", "box": "#3A2F0B", "text": "#EED891"}
}

t_bg = themes[theme]["bg"]
t_box = themes[theme]["box"]
t_text = themes[theme]["text"]

# Streamlit 전체 배경 및 글자색을 강제로 바꾸는 마법의 CSS 코드
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {t_bg};
        color: {t_text};
    }}
    h1, h2, h3, p, span, div {{
        color: {t_text};
    }}
    </style>
""", unsafe_allow_html=True)


# --- 2. 기본 함수 세팅 ---
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
        if rank in ['J', 'Q', 'K']:
            score += 10
        elif rank == 'A':
            score += 11
            aces += 1
        else:
            score += int(rank)
    while score > 21 and aces > 0:
        score -= 10
        aces -= 1
    return score

# 🃏 현실적인 카드 모양을 HTML/CSS로 그려주는 함수
def get_card_html(card, hidden=False):
    if hidden:
        # 숨겨진 카드 (카드 뒷면 패턴)
        return '''
        <div style="display:inline-block; width:80px; height:115px; 
        background: repeating-linear-gradient(45deg, #2b2b2b, #2b2b2b 10px, #404040 10px, #404040 20px); 
        border-radius:10px; border:3px solid white; margin-right:10px; 
        box-shadow: 3px 3px 8px rgba(0,0,0,0.4);"></div>
        '''
    else:
        suit, rank = card[0], card[1]
        # 하트와 다이아몬드는 빨간색, 스페이드와 클로버는 검은색
        color = "#D32F2F" if suit in ['♥', '♦'] else "#1E1E1E"
        
        return f'''
        <div style="display:inline-block; width:80px; height:115px; 
        background-color: white; border-radius:10px; border:1px solid #ccc; 
        position:relative; margin-right:10px; box-shadow: 3px 3px 8px rgba(0,0,0,0.4);">
            <div style="position:absolute; top:5px; left:8px; font-size:18px; font-weight:bold; color:{color};">{rank}</div>
            <div style="position:absolute; top:5px; left:8px; margin-top:18px; font-size:18px; color:{color};">{suit}</div>
            
            <div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-size:40px; color:{color};">{suit}</div>
            
            <div style="position:absolute; bottom:5px; right:8px; font-size:18px; font-weight:bold; color:{color}; transform:rotate(180deg);">{rank}</div>
            <div style="position:absolute; bottom:5px; right:8px; margin-bottom:18px; font-size:18px; color:{color}; transform:rotate(180deg);">{suit}</div>
        </div>
        '''

def render_hands_html(hand, hide_second=False):
    html = '<div style="margin-top: 10px; margin-bottom: 20px;">'
    for i, card in enumerate(hand):
        if hide_second and i == 1:
            html += get_card_html(card, hidden=True)
        else:
            html += get_card_html(card, hidden=False)
    html += '</div>'
    return html

# --- 3. 게임 세션 초기화 ---
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

# 시작하자마자 블랙잭인지 확인 (최초 1회만)
if not st.session_state.game_over and player_score == 21:
    st.session_state.game_over = True
    st.session_state.winner = "플레이어(블랙잭)"

# --- 4. 화면 출력부 ---
st.markdown(f"<h1 style='text-align: center; color: {t_text};'>🎲 카지노 리얼 블랙잭</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: {t_text};'>왼쪽 사이드바(화살표)를 눌러 테마를 변경해보세요!</p>", unsafe_allow_html=True)

# 📦 중앙 게임 박스 (컨테이너) 디자인 영역
game_board_html = f"""
<div style="background-color: {t_box}; padding: 30px; border-radius: 20px; box-shadow: 0px 8px 20px rgba(0,0,0,0.4); margin-bottom: 20px;">
    <h3 style="margin-top: 0;">🤖 딜러의 카드</h3>
    {render_hands_html(st.session_state.dealer_hand, hide_second=not st.session_state.game_over)}
    <hr style="border-top: 1px solid rgba(255,255,255,0.2);">
    <h3>🙋‍♂️ 당신의 카드 <span style="font-size: 16px; font-weight: normal;">(현재 점수: {player_score}점)</span></h3>
    {render_hands_html(st.session_state.player_hand)}
</div>
"""
st.markdown(game_board_html, unsafe_allow_html=True)

# --- 5. 조작 버튼 및 게임 로직 ---
if not st.session_state.game_over:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Hit (카드 더 받기) 🃏", use_container_width=True):
            st.session_state.player_hand.append(st.session_state.deck.pop())
            if calculate_score(st.session_state.player_hand) > 21:
                st.session_state.game_over = True
                st.session_state.winner = "딜러"
            st.rerun()
            
    with col2:
        if st.button("Stand (멈추고 결과 보기) 🛑", use_container_width=True):
            st.session_state.game_over = True
            # 딜러 로직 (17점 이상이 될 때까지)
            while calculate_score(st.session_state.dealer_hand) < 17:
                st.session_state.dealer_hand.append(st.session_state.deck.pop())
            
            f_dealer_score = calculate_score(st.session_state.dealer_hand)
            f_player_score = calculate_score(st.session_state.player_hand)
            
            if f_dealer_score > 21:
                st.session_state.winner = "플레이어"
            elif f_player_score > f_dealer_score:
                st.session_state.winner = "플레이어"
            elif f_player_score < f_dealer_score:
                st.session_state.winner = "딜러"
            else:
                st.session_state.winner = "무승부"
            st.rerun()

# --- 6. 최종 승패 결과 ---
if st.session_state.game_over:
    st.markdown("---")
    if st.session_state.winner == "플레이어":
        st.success(f"### 🎉 당신의 승리입니다! (딜러: {dealer_score}점) 👑")
        st.balloons()
    elif st.session_state.winner == "플레이어(블랙잭)":
        st.success(f"### 🎉 시작하자마자 블랙잭!! 완벽한 승리입니다! 👑")
        st.balloons()
    elif st.session_state.winner == "딜러":
        if player_score > 21:
            st.error(f"### 💥 21점 초과(Bust)! 딜러의 승리입니다.")
        else:
            st.error(f"### 😢 딜러의 승리입니다. (딜러: {dealer_score}점)")
    else:
        st.warning(f"### 🤝 무승부입니다! (딜러: {dealer_score}점)")
        
    if st.button("🔄 새 게임 시작하기", use_container_width=True, type="primary"):
        reset_game()
        st.rerun()