import random
import streamlit as st
from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮", layout="centered")

# Custom CSS for color-coded feedback and styling
st.markdown("""
<style>
    .hot-hint {
        background-color: #ff4b4b22;
        border-left: 4px solid #ff4b4b;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        color: #ff4b4b;
    }
    .cold-hint {
        background-color: #1c83e122;
        border-left: 4px solid #1c83e1;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        color: #1c83e1;
    }
    .win-box {
        background-color: #21c35422;
        border-left: 4px solid #21c354;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 20px;
        font-weight: bold;
        color: #21c354;
    }
    .lose-box {
        background-color: #ff4b4b22;
        border-left: 4px solid #ff4b4b;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        color: #ff4b4b;
    }
    .score-card {
        background-color: #f0f2f622;
        border: 1px solid #ddd;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .attempt-badge {
        display: inline-block;
        background-color: #7c3aed22;
        color: #7c3aed;
        border-radius: 20px;
        padding: 4px 12px;
        font-weight: bold;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game — now actually playable.")

# Sidebar settings
st.sidebar.header("⚙️ Settings")
difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Normal", "Hard"], index=1)

attempt_limit_map = {"Easy": 6, "Normal": 8, "Hard": 5}
attempt_limit = attempt_limit_map[difficulty]
low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"📏 Range: {low} to {high}")
st.sidebar.caption(f"🎯 Attempts allowed: {attempt_limit}")
st.sidebar.divider()

# Difficulty badge colors
diff_colors = {"Easy": "🟢", "Normal": "🟡", "Hard": "🔴"}
st.sidebar.markdown(f"**Mode:** {diff_colors[difficulty]} {difficulty}")

# Reset game state if difficulty changes
if "difficulty" not in st.session_state:
    st.session_state.difficulty = difficulty

if st.session_state.difficulty != difficulty:
    for key in ["secret", "attempts", "score", "status", "history"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.difficulty = difficulty

# Initialize session state
if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "status" not in st.session_state:
    st.session_state.status = "playing"
if "history" not in st.session_state:
    st.session_state.history = []

# Top stat bar
col_a, col_b, col_c = st.columns(3)
col_a.metric("🎯 Attempts Left", attempt_limit - st.session_state.attempts)
col_b.metric("⭐ Score", st.session_state.score)
col_c.metric("📋 Guesses Made", st.session_state.attempts)

st.divider()

# Hot/Cold temperature indicator
def get_temperature(guess, secret, low, high):
    total_range = high - low
    distance = abs(guess - secret)
    ratio = distance / total_range
    if ratio == 0:
        return "exact"
    elif ratio < 0.1:
        return "🔥 Burning hot!"
    elif ratio < 0.25:
        return "♨️ Very warm..."
    elif ratio < 0.5:
        return "😐 Getting there..."
    elif ratio < 0.75:
        return "🧊 Pretty cold..."
    else:
        return "❄️ Ice cold!"

# Debug expander
with st.expander("🔍 Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts used:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

# Game over state
if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.markdown('<div class="win-box">🎉 You won! Start a new game to play again.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="lose-box">💀 Game over! The secret was <b>{st.session_state.secret}</b>. Better luck next time!</div>', unsafe_allow_html=True)
    
    # Show final session summary table
    if st.session_state.history:
        st.subheader("📊 Your Game Summary")
        table_data = []
        for i, g in enumerate(st.session_state.history):
            if isinstance(g, int):
                diff = g - st.session_state.secret
                if diff == 0:
                    arrow = "✅ Correct!"
                elif diff > 0:
                    arrow = "⬇️ Too High"
                else:
                    arrow = "⬆️ Too Low"
                closeness = get_temperature(g, st.session_state.secret, low, high)
                table_data.append({
                    "Attempt": i + 1,
                    "Your Guess": g,
                    "Result": arrow,
                    "Temperature": closeness
                })
        st.table(table_data)

    if st.button("🔁 Play Again"):
        for key in ["secret", "attempts", "score", "status", "history"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    st.stop()

# Guess input
st.subheader("🤔 Make a Guess")
st.markdown(f"Guess a number between **{low}** and **{high}**")

raw_guess = st.text_input("Enter your guess:", key=f"guess_input_{difficulty}_{st.session_state.attempts}")

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    for key in ["secret", "attempts", "score", "status", "history"]:
        if key in st.session_state:
            del st.session_state[key]
    st.success("New game started!")
    st.rerun()

if submit:
    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.error(f"❌ {err}")
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        outcome, message = check_guess(guess_int, st.session_state.secret)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.markdown(f'<div class="win-box">🎉 You got it! The secret was <b>{st.session_state.secret}</b>. Final score: <b>{st.session_state.score}</b></div>', unsafe_allow_html=True)
            st.rerun()

        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"
            st.rerun()

        else:
            if show_hint:
                temp = get_temperature(guess_int, st.session_state.secret, low, high)
                if outcome == "Too High":
                    st.markdown(f'<div class="hot-hint">📉 Too High! Go lower. &nbsp;&nbsp; {temp}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="cold-hint">📈 Too Low! Go higher. &nbsp;&nbsp; {temp}</div>', unsafe_allow_html=True)

# Live guess history sidebar
if st.session_state.history:
    st.divider()
    st.subheader("📋 Guess History")
    for i, g in enumerate(st.session_state.history):
        if isinstance(g, int):
            diff = g - st.session_state.secret
            if diff > 0:
                icon = "⬇️"
            elif diff < 0:
                icon = "⬆️"
            else:
                icon = "✅"
            st.markdown(f"**Attempt {i+1}:** `{g}` {icon}")

st.divider()
st.caption("Fixed by a human who actually read the code. 🧑‍💻")