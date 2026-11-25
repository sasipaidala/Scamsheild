"""Practical security-awareness lessons and locally saved quiz progress."""
from __future__ import annotations

import streamlit as st

from core.config import Settings
from services.learning_support import TOPICS, get_awareness_progress, save_awareness_progress


def render() -> None:
    db = Settings.from_env().database_path
    st.markdown('<div class="ss-eyebrow">LEARN · PROTECT YOURSELF</div>', unsafe_allow_html=True)
    st.title("Security Awareness")
    st.write("Short, practical lessons for recognizing scams and protecting accounts, money and personal information.")
    st.info("Learning content is educational guidance, not a guarantee that a message, person or transaction is safe.")

    progress = get_awareness_progress(db)
    done = sum(1 for result in progress.values() if result["score"] == 100)
    st.progress(done / len(TOPICS), text=f"Learning progress: {done} of {len(TOPICS)} topics completed (100% quiz score)")
    st.caption("Your quiz scores are saved locally in this ScamShield database.")

    topic = st.selectbox("Choose a learning topic", list(TOPICS))
    lesson = TOPICS[topic]
    left, right = st.columns([3, 1])
    with left:
        st.subheader(topic)
        st.write(lesson["summary"])
    with right:
        st.metric("Estimated time", f"{lesson['minutes']} min")
        st.caption(lesson["level"])

    st.markdown("#### Key practices")
    for item in lesson["content"]:
        st.markdown(f"- {item}")

    st.divider()
    st.markdown("#### Knowledge check")
    answers = []
    for index, (question, options, correct, explanation) in enumerate(lesson["quiz"]):
        st.write(question)
        choice = st.radio("Select one answer", options, key=f"awareness_{topic}_{index}", label_visibility="collapsed")
        answers.append((options.index(choice), correct, explanation))
    if st.button("Submit knowledge check", type="primary", key="submit_awareness"):
        score = round(100 * sum(a == c for a, c, _ in answers) / max(1, len(answers)))
        save_awareness_progress(db, topic, score)
        if score == 100:
            st.success(f"Correct — {score}%. Your progress has been saved.")
        else:
            st.warning(f"Score: {score}%. Review the explanation below and try again.")
        for index, (_, correct, explanation) in enumerate(answers):
            if answers[index][0] == correct:
                st.success(explanation)
            else:
                st.info(explanation)
        st.rerun()

    if topic in progress:
        st.caption(f"Previous result: {progress[topic]['score']}% · {progress[topic]['completed_at']}")

    with st.expander("Emergency actions if you have been scammed"):
        st.markdown("""
        1. Contact your bank or payment provider immediately and ask them to secure the account or transaction.
        2. In India, call **1930** promptly for cyber financial fraud and submit the details at **https://cybercrime.gov.in/**.
        3. Change compromised passwords from the official service, revoke sessions and enable multi-factor authentication.
        4. Preserve transaction IDs, messages, email headers and screenshots. Do not edit or publicly post sensitive evidence.
        5. Do not pay anyone promising guaranteed recovery of lost funds.
        """)
