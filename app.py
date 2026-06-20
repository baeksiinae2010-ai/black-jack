import streamlit as st
import random
import time

# 1. Page Configuration & Theme Initialization
st.set_page_config(page_title="카지노 리얼 블랙잭", page_icon="🎲", layout="wide")

# Theme Definitions
THEMES = {
    "Dark Matte": {
        "bg_color": "#1e1e1e",
        "table_bg": "#2d2d2d",
        "text_color": "#ffffff",
        "accent_color": "#4a90e2",
        "card_bg": "#ffffff",
        "table_border": "#444444"
    },
    "Light Breeze": {
        "bg_color": "#f5f7fa",
        "table_bg": "#ffffff",
        "text_color": "#333333",
        "accent_color": "#3498db",
        "card_bg": "#f9f9f9",
        "table_border": "#dddddd"
    },
    "Cyberpunk": {
        "bg_color": "#0f051d",
        "table_bg": "#1a0b2e",
        "text_color": "#00ffcc",
        "accent_color": "#ff007f",
        "card_bg": "#241442",
        "table_border": "#ff007f"
    },
    "Moss Green": {
        "bg_color": "#0c2b18",
        "table_bg": "#164a29",
        "text_color": "#ffffff",
        "accent_color": "#f1c40f",
        "card_bg": "#ffffff",
        "table_border": "#f1c40f"
    }
}

# Keep theme selection clean and compact at the bottom using a controlled column layout
if "current_theme" not in st.session_state:
    st.session_state.current_theme = "Dark Matte"

theme_style = THEMES[st.session_state.current_theme]

# Inject Custom Theme CSS dynamically based on the selection
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {theme_style['bg_color']};
        color: {theme_style['text_color']};
    }}
    h1, h2, h3, p, span, label {{
        color: {theme_style['text_color']} !important;
    }}
    .game-table {{
        background-color: {theme_style['table_bg']};
        border: 3px solid {theme_style['table_border']};
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
    }}
    .asset-box {{
        background-color: {theme_style['table_bg']};
        border: 1px solid {theme_style['table_border']};
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
    }}
    </style>
""", unsafe_allow_url=True)

# 2. Game Core Functions
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

# Initialize Game State variables
if "bankroll" not in st.session_state:
    st.session_state.bankroll = 1000
if "current_bet" not in st.session_state:
    st.session_state.current_bet = 50
if "game_status" not in st.session_state:
    st.session_state.game_status = "betting" # betting, playing, resolved
if "deck" not in st.session_state:
    st.session_state.deck = []
if "player_hand" not in st.session_state:
    st.session_state.player_hand = []
if "dealer_hand" not in st.session_state:
    st.session_state.dealer_hand = []
if "game_message" not in st.session_state:
    st.session_state.game_message = ""
if "message_type" not in st.session_state:
    st.session_state.message_type = "info"

def render_card_html(card, facedown=False):
    if facedown:
        return f"""
        <div style="display: inline-block; width: 75px; height: 110px; 
                    background: linear-gradient(135deg, #2c3e50, #3498db); 
                    border: 2px solid white; border-radius: 8px; margin: 5px; 
                    box-shadow: 2px 2px 6px rgba(0,0,0,0.3); vertical-align: top;">
        </div>
        """
    suit, rank = card
    color = "red" if suit in ['♥', '♦'] else "black"
    card_bg = theme_style['card_bg']
    text_color = "#333333" if card_bg in ['#ffffff', '#f9f9f9'] else theme_style['text_color']
    
    return f"""
    <div style="display: inline-block; width: 75px; height: 110px; 
                background-color: {card_bg}; color: {color}; 
                border: 2px solid {theme_style['table_border']}; border-radius: 8px; 
                padding: 8px; margin: 5px; box-shadow: 2px 2px 6px rgba(0,0,0,0.2); 
                text-align: center; font-family: 'Arial', sans-serif; vertical-align: top; position: relative;">
        <div style="font-size: 18px; font-weight: bold; text-align: left; line-height: 1;">{rank}</div>
        <div style="font-size: 32px; text-align: center; margin-top: 10px;">{suit}</div>
    </div>
    """

# 3. Layout: Title & Header Area
st.title("🎲 카지노 리얼 블랙잭")
st.write("코딩을 몰라도 누구나 버튼만 눌러서 즐길 수 있는 미니 게임!")
st.markdown("---")

# Split Layout into Sidebar-like asset box and Main Game Screen
col_left, col_right = st.columns([1, 3])

with col_left:
    st.markdown('<div class="asset-box">', unsafe_allow_html=True)
    st.subheader("🏦 내 자산 락커")
    st.metric(label="보유 뱅크롤", value=f"${st.session_state.bankroll}")
    st.metric(label="현재 판돈 베팅액", value=f"${st.session_state.current_bet}")
    
    # Chip Selection (Only interactive during betting phase)
    st.write("베팅액 설정:")
    chip_cols = st.columns(4)
    chips = [10, 50, 100, 500]
    for i, chip in enumerate(chips):
        with chip_cols[i]:
            if st.button(f"${chip}", key=f"chip_{chip}", disabled=(st.session_state.game_status != "betting")):
                if chip <= st.session_state.bankroll:
                    st.session_state.current_bet = chip
                else:
                    st.warning("뱅크롤이 부족합니다!")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    # Main Game Playmat Container
    st.markdown('<div class="game-table">', unsafe_allow_html=True)
    
    if st.session_state.game_status == "betting":
        st.markdown("<h3 style='text-align: center; margin-top: 40px;'>PLACE YOUR BETS</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>베팅액 설정 후아래 [Deal] 버튼을 누르면 카드가 분배됩니다.</p>", unsafe_allow_html=True)
        
        if st.button(" Deal (게임 시작) 🃏", use_container_width=True):
            if st.session_state.current_bet > st.session_state.bankroll:
                st.error("베팅 금액이 보유 자산보다 많습니다!")
            else:
                # Start new round
                st.session_state.deck = create_deck()
                st.session_state.player_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
                st.session_state.dealer_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
                
                p_score = calculate_score(st.session_state.player_hand)
                if p_score == 21:
                    st.session_state.game_status = "resolved"
                    d_score = calculate_score(st.session_state.dealer_hand)
                    if d_score == 21:
                        st.session_state.game_message = "🤝 블랙잭 푸시(비김)! 판돈을 돌려받습니다."
                        st.session_state.message_type = "info"
                    else:
                        st.session_state.game_message = "🎉 내츄럴 블랙잭 승리! 베팅액의 1.5배를 획득합니다!"
                        st.session_state.bankroll += int(st.session_state.current_bet * 1.5)
                        st.session_state.message_type = "success"
                else:
                    st.session_state.game_status = "playing"
                st.rerun()

    else:
        # Render Active Cards Table - Ensuring initial cards are ALWAYS rendered beautifully
        p_score = calculate_score(st.session_state.player_hand)
        d_score = calculate_score(st.session_state.dealer_hand)
        
        # 1. Dealer Table Display
        st.markdown("<h4>👁️ DEALER TABLE</h4>", unsafe_allow_html=True)
        dealer_cards_html = ""
        if st.session_state.game_status == "playing":
            # Show first card face up, second card face down
            dealer_cards_html += render_card_html(st.session_state.dealer_hand[0], facedown=False)
            dealer_cards_html += render_card_html(st.session_state.dealer_hand[1], facedown=True)
            st.markdown(f"<div>{dealer_cards_html}</div>", unsafe_allow_html=True)
            st.write("점수: 숨김")
        else:
            # Show all cards
            for card in st.session_state.dealer_hand:
                dealer_cards_html += render_card_html(card, facedown=False)
            st.markdown(f"<div>{dealer_cards_html}</div>", unsafe_allow_html=True)
            st.write(f"최종 점수: {d_score}점")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. Player Table Display
        st.markdown(f"<h4>🙋 MY HAND (현재 점수: {p_score}점)</h4>", unsafe_allow_html=True)
        player_cards_html = ""
        for card in st.session_state.player_hand:
            player_cards_html += render_card_html(card, facedown=False)
        st.markdown(f"<div>{player_cards_html}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 3. Action Buttons & Logic
        if st.session_state.game_status == "playing":
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Hit (카드 더 받기) 🃏", use_container_width=True):
                    st.session_state.player_hand.append(st.session_state.deck.pop())
                    if calculate_score(st.session_state.player_hand) > 21:
                        st.session_state.game_status = "resolved"
                        st.session_state.bankroll -= st.session_state.current_bet
                        st.session_state.game_message = "💥 버스트! 내가 패배했습니다. (21점 초과)"
                        st.session_state.message_type = "error"
                    st.rerun()
            with btn_col2:
                if st.button("Stand (멈추고 결과 보기) 🛑", use_container_width=True):
                    st.session_state.game_status = "resolved"
                    # Dealer draws until 17 or higher
                    while calculate_score(st.session_state.dealer_hand) < 17:
                        st.session_state.dealer_hand.append(st.session_state.deck.pop())
                    
                    final_p = calculate_score(st.session_state.player_hand)
                    final_d = calculate_score(st.session_state.dealer_hand)
                    
                    if final_d > 21:
                        st.session_state.game_message = f"🏆 딜러 버스트! 내가 승리했습니다! ({final_p} vs {final_d})"
                        st.session_state.bankroll += st.session_state.current_bet
                        st.session_state.message_type = "success"
                    elif final_p > final_d:
                        st.session_state.game_message = f"🏆 대승리! ({final_p} vs {final_d})"
                        st.session_state.bankroll += st.session_state.current_bet
                        st.session_state.message_type = "success"
                    elif final_p < final_d:
                        st.session_state.game_message = f"📉 패배했습니다. ({final_p} vs {final_d})"
                        st.session_state.bankroll -= st.session_state.current_bet
                        st.session_state.message_type = "error"
                    else:
                        st.session_state.game_message = f"🤝 비겼습니다. 무승부! ({final_p} vs {final_d})"
                        st.session_state.message_type = "info"
                    st.rerun()
        
        # 4. Round Resolution / Result Banner
        if st.session_state.game_status == "resolved":
            if st.session_state.message_type == "success":
                st.success(st.session_state.game_message)
            elif st.session_state.message_type == "error":
                st.error(st.session_state.game_message)
            else:
                st.info(st.session_state.game_message)
                
            if st.button("🔄 다음 게임 정산 및 진행하기", use_container_width=True, type="primary"):
                st.session_state.game_status = "betting"
                if st.session_state.bankroll <= 0:
                    st.session_state.bankroll = 1000 # auto-refill if bankrupt
                    st.session_state.game_message = "💸 자산을 모두 잃어 $1,000 충전 해드렸습니다!"
                    st.session_state.message_type = "info"
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# 4. Clean & Compact Theme Selection at the Bottom (Ensuring it does NOT stretch)
st.markdown("<br><br>", unsafe_allow_html=True)
theme_col1, theme_col2, theme_col3 = st.columns([2, 1, 2])
with theme_col2:
    selected_theme = st.selectbox(
        "Theme Style",
        options=list(THEMES.keys()),
        index=list(THEMES.keys()).index(st.session_state.current_theme),
        label_visibility="visible"
    )
    if selected_theme != st.session_state.current_theme:
        st.session_state.current_theme = selected_theme
        st.rerun()