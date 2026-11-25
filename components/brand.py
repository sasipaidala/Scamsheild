"""Brand mark and shared identity components."""

import streamlit as st


def render_brand(compact: bool = False) -> None:
    """Render the ScamShield brand using a lightweight inline shield mark."""
    subtitle = "" if compact else '<div class="ss-brand-subtitle">Digital safety workspace</div>'
    st.markdown(
        f"""
        <div class="ss-brand" aria-label="ScamShield AI">
            <div class="ss-brand-mark" aria-hidden="true">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
                     xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2.8 20 6v5.5c0 4.8-3.2 8.1-8 9.7-4.8-1.6-8-4.9-8-9.7V6l8-3.2Z"
                          stroke="currentColor" stroke-width="1.65" stroke-linejoin="round"/>
                    <path d="m8.7 12.1 2.1 2.1 4.6-4.8"
                          stroke="currentColor" stroke-width="1.8" stroke-linecap="round"
                          stroke-linejoin="round"/>
                </svg>
            </div>
            <div>
                <div class="ss-brand-name">ScamShield <span style="color:var(--ss-primary)">AI</span></div>
                {subtitle}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
