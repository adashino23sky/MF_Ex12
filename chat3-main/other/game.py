import streamlit as st
import random
# import session_state

st.title("数字当てゲーム")
st.write("1から100までの数字を10回の試みで当ててください!")

# Streamlitのsession_stateを使用して、セッション間での変数の値を維持します
if 'target_number' not in st.session_state:
    st.session_state.target_number = random.randint(1, 100)
    st.session_state.attempts_left = 10
    st.session_state.guesses = []

# ユーザーの入力を受け取ります
guess = st.number_input("あなたの予測を入力してください:", min_value=1, max_value=100)

if st.button("予測する"):
    # 予測回数を減少
    st.session_state.attempts_left -= 1
    st.session_state.guesses.append(guess)
    
    if guess == st.session_state.target_number:
        st.success(f"正解です！答えは{st.session_state.target_number}でした！")
        st.session_state.target_number = random.randint(1, 100)
        st.session_state.attempts_left = 10
        st.session_state.guesses = []
    elif st.session_state.attempts_left == 0:
        st.error(f"残念！答えは{st.session_state.target_number}でした。")
        st.session_state.target_number = random.randint(1, 100)
        st.session_state.attempts_left = 10
        st.session_state.guesses = []
    elif guess < st.session_state.target_number:
        st.warning("もっと大きい数字を試してください!")
    else:
        st.warning("もっと小さい数字を試してください!")

# これまでの予測と残りの試みを表示します
st.write(f"これまでの予測: {', '.join(map(str, st.session_state.guesses))}")
st.write(f"残りの試み: {st.session_state.attempts_left}回")
