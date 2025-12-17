import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="Space KO Decision Engine",
    page_icon="🛸",
    layout="centered"
)

# --- Styling for High Contrast/Readability ---
st.markdown("""
    <style>
    .big-stat {
        font-size: 26px !important;
        font-weight: bold;
    }
    .metric-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .highlight-green {
        color: #2ecc71;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛸 SPACE KO Decision Engine")

# --- Sidebar: Constants ---
with st.sidebar:
    st.header("⚙️ Tournament Setup")
    buy_in = st.number_input("Buy-in (€)", value=10.0, step=5.0)
    start_stack = st.number_input("Starting Stack", value=20000)
    
    if start_stack > 0:
        chip_value = buy_in / start_stack
        st.caption(f"1 Chip = €{chip_value:.6f}")
    else:
        chip_value = 0

# --- Section 1: The Bounty Converter ---
st.subheader("1. Bounty Conversion")
col_inputs_1, col_inputs_2 = st.columns(2)

with col_inputs_1:
    current_bb = st.number_input("Current Big Blind", value=1000, step=100)
with col_inputs_2:
    bounty_euro = st.number_input("Villain Token Avg (€)", value=5.0, step=0.5, format="%.2f")

# Calculation: Bounty to Cash BB
cash_bb = 0.0
if current_bb > 0 and start_stack > 0:
    bb_cost_euro = current_bb * chip_value
    total_bounty_bb = bounty_euro / bb_cost_euro
    # We only care about the 50% Cash for Pot Odds
    cash_bb = total_bounty_bb * 0.5 

    # Display the Bounty Value prominently
    st.markdown(
        f"""
        <div class="metric-container" style="text-align: center;">
            <span style="font-size: 18px;">Bounty Cash Value (Dead Money)</span><br>
            <span class="cash-value" style="font-size: 40px; color: #2ecc71; font-weight: bold;">
                {cash_bb:.1f} BB
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

# --- Section 2: All-In Pot Odds Calculator ---
st.markdown("---")
st.subheader("2. All-In Decision Calculator")

c1, c2 = st.columns(2)
with c1:
    pot_before = st.number_input("Pot Before Shove (BB)", value=2.5, step=0.5, help="Blinds + Antes + Limps")
with c2:
    call_amount = st.number_input("Amount to Call (BB)", value=15.0, step=1.0, help="Villain's Effective Stack")

if call_amount > 0:
    # --- The Math ---
    # Standard Pot Odds: Call / (Pot + Bet + Call)
    final_pot_std = pot_before + call_amount + call_amount
    req_equity_std = (call_amount / final_pot_std) * 100
    
    # Bounty Pot Odds: Call / (Pot + Bet + Call + Bounty)
    final_pot_bounty = final_pot_std + cash_bb
    req_equity_bounty = (call_amount / final_pot_bounty) * 100
    
    # Discount
    equity_discount = req_equity_std - req_equity_bounty

    # --- Result Display ---
    st.write("### Required Equity to Call")
    
    res_col1, res_col2, res_col3 = st.columns(3)
    
    with res_col1:
        st.metric(label="Standard Spot", value=f"{req_equity_std:.1f}%")
        st.caption("Without Bounty")
        
    with res_col2:
        st.metric(
            label="With Bounty", 
            value=f"{req_equity_bounty:.1f}%", 
            delta=f"-{equity_discount:.1f}%"
        )
        st.caption("▼ Lower is better")
        
    with res_col3:
        # Visual interpretation
        if equity_discount > 10:
            verdict = "HUGE DISCOUNT 🚀"
            color = "green"
        elif equity_discount > 5:
            verdict = "Significant ⚡"
            color = "orange"
        else:
            verdict = "Standard 😐"
            color = "gray"
        
        st.markdown(f"<h3 style='color:{color}; margin-top: 0;'>{verdict}</h3>", unsafe_allow_html=True)
        st.write(f"The bounty reduces required equity by **{equity_discount:.1f}%**")

else:
    st.info("Enter 'Amount to Call' to see required equity.")
