import streamlit as st
import random
import time

# 웹페이지 기본 설정
st.set_page_config(page_title="미니 블랙잭", page_icon="🎲")

# --- 1. 기본 함수 세팅 ---
def create_deck():
    suits = ['♠️', '♥️', '♦️', '♣️']
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

def display_hand(hand):
    return " ".join([f"[{card[0]}{card[1]}]" for card in hand])

# --- 2. 게임 상태(세션) 저장소 초기화 ---
# 웹은 버튼을 누를 때마다 새로고침되므로, 카드가 증발하지 않게 기억(session_state)해둬야 해!
def reset_game():
    st.session_state.deck = create_deck()
    st.session_state.player_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
    st.session_state.dealer_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
    st.session_state.game_over = False
    st.session_state.winner = ""

if 'deck' not in st.session_state:
    reset_game()

# --- 3. 웹 화면 UI 그리기 ---
st.title("🎲 카지노 리얼 블랙잭")
st.write("코딩을 몰라도 누구나 버튼만 눌러서 즐길 수 있는 미니 게임!")
st.divider()

player_score = calculate_score(st.session_state.player_hand)
dealer_score = calculate_score(st.session_state.dealer_hand)

# 딜러 화면
st.subheader("🤖 딜러의 카드")
if not st.session_state.game_over:
    st.write(f"[{st.session_state.dealer_hand[0][0]}{st.session_state.dealer_hand[0][1]}] [❓]")
else:
    st.write(f"**{display_hand(st.session_state.dealer_hand)}** (최종 점수: {dealer_score}점)")

# 플레이어 화면
st.subheader("🙋‍♂️ 당신의 카드")
st.write(f"**{display_hand(st.session_state.player_hand)}** (현재 점수: {player_score}점)")
st.divider()

# --- 4. 게임 조작 버튼 ---
if not st.session_state.game_over:
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Hit (카드 더 받기) 🃏", use_container_width=True):
            st.session_state.player_hand.append(st.session_state.deck.pop())
            if calculate_score(st.session_state.player_hand) > 21:
                st.session_state.game_over = True
                st.session_state.winner = "딜러"
            st.rerun() # 화면 새로고침
            
    with col2:
        if st.button("Stand (멈추고 결과 보기) 🛑", use_container_width=True):
            st.session_state.game_over = True
            # 딜러가 17점 이상이 될 때까지 카드 뽑기
            while calculate_score(st.session_state.dealer_hand) < 17:
                st.session_state.dealer_hand.append(st.session_state.deck.pop())
            
            final_dealer_score = calculate_score(st.session_state.dealer_hand)
            final_player_score = calculate_score(st.session_state.player_hand)
            
            # 승패 판정
            if final_dealer_score > 21:
                st.session_state.winner = "플레이어"
            elif final_player_score > final_dealer_score:
                st.session_state.winner = "플레이어"
            elif final_player_score < final_dealer_score:
                st.session_state.winner = "딜러"
            else:
                st.session_state.winner = "무승부"
            st.rerun()

# --- 5. 최종 결과 출력 ---
if st.session_state.game_over:
    if st.session_state.winner == "플레이어":
        st.success("### 🎉 당신의 승리입니다! 축하합니다! 👑")
        st.balloons() # 승리 시 풍선 이펙트!
    elif st.session_state.winner == "딜러":
        st.error("### 😢 딜러의 승리입니다. (또는 플레이어 버스트)")
    else:
        st.warning("### 🤝 무승부입니다!")
        
    st.write("") # 빈 칸
    if st.button("🔄 새 게임 시작하기", use_container_width=True, type="primary"):
        reset_game()
        st.rerun()
