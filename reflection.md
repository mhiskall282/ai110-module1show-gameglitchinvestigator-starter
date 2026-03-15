# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

When I first ran the game, it looked functional on the surface — there was an input field, a submit button, and a score display — but things quickly fell apart during actual play. The first bug I noticed was that the hints were completely backwards: when I guessed a number higher than the secret number, the game told me "Too Low," and when I guessed lower, it said "Too High." The second bug was that the attempt counter either didn't update correctly or reset unexpectedly between guesses, making it impossible to track how many tries I had left. I also noticed that the game sometimes never reached a "You Win" state even when I typed the exact correct number, which pointed to a broken equality check in the game logic.

---

## 2. How did you use AI as a teammate?

I used GitHub Copilot inside VS Code as my main AI tool throughout this project, using both the Chat view and Inline Chat. One correct suggestion came when I asked Copilot to explain the `check_guess` function — it correctly identified that the comparison operators were flipped (`>` and `<` were swapped), and suggested the exact one-line fix; I verified this by running the game and confirming the hints now matched my guesses. One misleading suggestion happened when I asked Copilot in Agent Mode to refactor logic into `logic_utils.py` — it moved the function correctly but forgot to update the import statement in `app.py`, which caused a `NameError` crash; I caught this by reading the diff carefully before accepting the changes and added the missing import manually.

---

## 3. Debugging and testing your fixes

I decided a bug was truly fixed only when both the automated test passed *and* the live Streamlit game behaved correctly, because passing a test without checking the UI can still leave subtle issues. For automated testing, I wrote a pytest case in `test/test_game_logic.py` that called `check_guess(60, 50)` and asserted it returned a "Too High" result — before my fix this test failed, and after the fix it passed cleanly. I also manually tested edge cases in the browser, like guessing the exact secret number and guessing 1 and 100 as boundary values. Copilot helped me design the test by suggesting the assertion structure, though I had to correct the expected return value it assumed, which reinforced that I needed to understand my own code's output format.

---

## 4. What did you learn about Streamlit and state?

Streamlit works differently from a normal program — every time a user interacts with the page (clicks a button, types something), the entire Python script reruns from top to bottom. This means any regular variable you create gets wiped out on each rerun, which is why the score and attempt count kept resetting unexpectedly. To keep data alive between reruns, Streamlit gives you `st.session_state`, which acts like a small memory that persists across those reruns. I'd explain it to a friend like this: imagine every button click is like refreshing the page, and `session_state` is a sticky note that survives each refresh while everything else gets erased.

---

## 5. Looking ahead: your developer habits

One habit I want to carry into future projects is always reviewing AI-generated diffs line by line before accepting them, especially in Agent Mode — this project showed me that the AI can be right about the big picture but quietly wrong about small details like imports or return values. Next time I work with AI on a coding task, I would give more specific prompts upfront rather than broad ones, because vague prompts led to changes that were technically correct but didn't match how my specific code was structured. This project genuinely shifted how I see AI-generated code: I no longer assume it's correct just because it looks clean and confident — I now treat it like code from a smart but careless teammate that always needs a human review before it ships.