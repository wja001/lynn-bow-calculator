# bow_calculator.py — LYNN ARMOUR HANNINGS OFFICIAL — FINAL DEPLOY VERSION
import streamlit as st
from PIL import Image
import base64
from datetime import datetime
import io

st.set_page_config(page_title="Lynn Armour Hannings Bow Calculator", layout="centered")
st.title("Lynn Armour Hannings Bow Calculator")

# INCHES ↔ MM TOGGLE
unit = st.radio("Units", ["Inches (traditional)", "Millimeters (metric)"], horizontal=True, index=0)
inch_to_mm = 25.4
mm_to_inch = 1 / 25.4

def to_display(x_inch):
    return round(x_inch * inch_to_mm, 1) if unit == "Millimeters (metric)" else round(x_inch, 3)

def from_display(x_display):
    return x_display * mm_to_inch if unit == "Millimeters (metric)" else x_display

# Lynn's CURRENT targets — 100% from her latest handwritten corrections
targets = {
    "Violin": {"4/4": ("29 3/4",  60, 9.50), "3/4": ("27",      55, 9.00), "1/2": ("24 1/2",   50, 8.50),
               "1/4": ("21 3/8",  45, 8.00), "1/8": ("19 1/4",   40, 7.50), "1/10":("19 1/4",   35, 7.00),
               "1/16":("15 13/16",30, 6.50)},
    "Viola":  {"4/4": ("29 5/16",70, 9.25), "3/4": ("27",      65, 9.00)},
    "Cello":  {"4/4": ("28 1/16",80, 9.25), "3/4": ("26 1/2",  75, 8.50),
               "1/2": ("25 1/16",70, 7.50), "1/4": ("23 9/16",65, 7.00),
               "1/8": ("20 1/2", 60, 6.75), "1/10":("20 1/2", 55, 6.25)},
    "Bass":   {"German": ("~54–56",125, 7.75), "French": ("~54–56",135, 8.25)}
}

# Safe length conversion (bass stays as text)
def safe_length_to_float(s):
    s = s.strip().replace('"', '')
    if "–" in s or "~" in s: return None
    if ' ' in s:
        whole, frac = s.split()
        num, den = frac.split('/')
        return float(whole) + float(num)/float(den)
    elif '/' in s:
        num, den = s.split('/')
        return float(num)/float(den)
    return float(s)

# Pre-process targets
targets_float = {}
for inst, sizes in targets.items():
    targets_float[inst] = {}
    for sz, (length_str, wt, bal) in sizes.items():
        length_inch = safe_length_to_float(length_str)
        targets_float[inst][sz] = (length_str, length_inch, wt, bal)

lynn_hair = {"Violin": 4.0, "Viola": 5.0, "Cello": 6.0, "Bass": 8.0}

winding_rates = {
    "Silver 0.013″ (thick)": 0.07857,
    "Silver 0.010″ (thin)":  0.05714,
    "Tinsel":                0.02857,
    "Whalebone":             0.02143,
    "Silk":                  0.01429
}

# Customer info
left, right = st.columns([3, 3])
with left:
    customer = st.text_input("Customer name", placeholder="Customer name")
    phone    = st.text_input("Phone number", placeholder="(555) 123-4567")
    bow_id   = st.text_input("Bow stamp / description", placeholder="e.g. Vuillaume")
with right:
    address  = st.text_area("Address", height=100, placeholder="Street\nCity, State ZIP")

inst = st.selectbox("Instrument", ["Violin", "Viola", "Cello", "Bass"])
size = st.selectbox("Size / Style", list(targets[inst].keys()))
length_display, length_inch, wt_ideal, bal_ideal = targets_float[inst][size]

unit_sym = "mm" if unit == "Millimeters (metric)" else "\""
length_text = length_display + "\"" if length_inch is not None else length_display
if length_inch is not None and unit == "Millimeters (metric)":
    length_text = f"{to_display(length_inch)} mm"

st.sidebar.success(f"**Lynn's Current Target**\n"
                   f"Length: {length_text}\n"
                   f"Weight: {wt_ideal} g\n"
                   f"Balance: {to_display(bal_ideal)} {unit_sym} from butt")

# Photos
st.subheader("Photos (up to 6)")
photos = []
cols = st.columns(3)
for i in range(6):
    with cols[i % 3]:
        uploaded = st.file_uploader(f"Photo {i+1}", type=["jpg","jpeg","png"], key=f"ph{i}")
        if uploaded:
            img = Image.open(uploaded)
            photos.append(img)
            st.image(img, width=200)

# As Received
st.subheader("As Received")
r1, r2 = st.columns(2)
with r1: rec_weight = st.number_input("Weight (g)", 0.0, step=0.1, format="%.2f")
with r2: rec_bal_disp = st.number_input(f"Balance ({unit_sym} from butt)", 0.0,
                                         step=0.1 if unit=="Millimeters (metric)" else 0.125)
rec_balance = from_display(rec_bal_disp)

# Calculator
st.subheader("Weight and Balance Calculator")
use_stripped = st.checkbox("Start from stripped bow (hair & winding removed)")

if use_stripped:
    s1, s2 = st.columns(2)
    with s1: stripped_weight = st.number_input("Stripped weight (g)", 0.0, step=0.1)
    with s2: stripped_bal_disp = st.number_input(f"Stripped balance ({unit_sym})", 0.0,
                                                  step=0.1 if unit=="Millimeters (metric)" else 0.125)
    base_weight = stripped_weight
    base_balance = from_display(stripped_bal_disp)
else:
    base_weight = base_balance = 0.0

hair = winding = thumb = tubing = tip = other = 0.0

if st.checkbox("Rehair"):
    hair = st.number_input("Hair (playing weight)", value=lynn_hair[inst], min_value=0.0, step=0.1)

if st.checkbox("New winding + leather"):
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1: material = st.selectbox("Material", list(winding_rates.keys()))
    with c2:
        if unit == "Millimeters (metric)":
            length_mm = st.slider("Winding length (mm)", 10, 100, 70)
        else:
            length_in = st.slider("Winding length (inches)", 0.4, 3.9, 2.76, step=0.01)
            length_mm = round(length_in * inch_to_mm)
    with c3: leather = st.number_input("Leather (g)", value=0.6, min_value=0.0, step=0.1)
    metal = round(length_mm * winding_rates[material], 3)
    winding = metal + leather
    st.success(f"{length_mm} mm {material.split('(')[0]} = {metal:.3f} g + {leather:.1f} g leather = **{winding:.3f} g**")

if st.checkbox("Thumb leather only"): thumb = st.number_input("Thumb leather (g)", 0.6, step=0.1)
if st.checkbox("Surgical tubing"):    tubing = st.number_input("Tubing (g)", 8.0, step=0.1)
if st.checkbox("New tip"):            tip = st.number_input("Tip (g)", 2.0, step=0.1)
if st.checkbox("Other change"):       other = st.number_input("Other (+/- g)", 0.0, step=0.1)

total_added = hair + winding + thumb + tubing + tip + other
st.metric("**Total Added**", f"{total_added:.3f} g")

# Lynn's lifetime rule: every 4 g = ½"
balance_shift_inch = total_added * 0.125
pred_weight = base_weight + total_added
pred_balance_inch = base_balance + balance_shift_inch

# Results
st.subheader("Results")
r1, r2, r3, r4 = st.columns(4)
r1.metric("Predicted weight", f"{pred_weight:.2f} g", f"{pred_weight - wt_ideal:+.2f} g")
r2.metric(f"Predicted balance ({unit_sym})", f"{to_display(pred_balance_inch):.3f}",
          f"{to_display(pred_balance_inch - bal_ideal):+.3f}")
r3.metric("Target weight", f"{wt_ideal} g")
r4.metric(f"Target balance ({unit_sym})", f"{to_display(bal_ideal):.3f}")

# Actual finished
st.subheader("Actual Finished Bow")
a1, a2 = st.columns(2)
with a1: actual_weight = st.number_input("Actual weight (g)", value=0.0, step=0.1)
with a2: actual_bal_disp = st.number_input(f"Actual balance ({unit_sym})", value=0.0,
                                            step=0.1 if unit=="Millimeters (metric)" else 0.125)

# Notes & Save
notes = st.text_area("Work performed / notes", height=100, placeholder="Rehair, silver winding, new grip...")

if st.button("Save & Print Customer Card (PDF)", type="primary"):
    html = f"""
    <h1 style="text-align:center">{customer or 'Customer'} — {bow_id or ''}</h1>
    <p style="text-align:center"><strong>{phone or ''}</strong><br>{address.replace('\n', '<br>') or ''}</p>
    <h2 style="text-align:center">{inst} {size}</h2>
    <p><strong>As Received:</strong> {rec_weight:.2f} g  |  {to_display(rec_balance):.3f} {unit_sym}</p>
    """
    if use_stripped and stripped_weight > 0:
        html += f"<p><strong>Stripped:</strong> {stripped_weight:.2f} g  |  {to_display(from_display(stripped_bal_disp)):.3f} {unit_sym}</p>"
    html += f"""
    <p><strong>Predicted (Lynn's 4g = ½" rule):</strong> {pred_weight:.2f} g  |  {to_display(pred_balance_inch):.3f} {unit_sym}</p>
    """
    if actual_weight > 0:
        html += f"<p><strong>Actual:</strong> {actual_weight:.2f} g  |  {to_display(from_display(actual_bal_disp)):.3f} {unit_sym}</p>"
    html += f"""
    <p><strong>Lynn Target:</strong> {wt_ideal} g  |  {to_display(bal_ideal):.2f} {unit_sym}</p>
    <p><strong>Work performed:</strong><br>{notes.replace('\n', '<br>') or 'Standard rehair & winding'}</p>
    <hr>
    """
    for img in photos:
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        b64 = base64.b64encode(buffered.getvalue()).decode()
        html += f'<img src="data:image/png;base64,{b64}" width="700"><br><br>'

    b64_html = base64.b64encode(html.encode()).decode()
    filename = f"{(customer or 'Customer').replace(' ', '_')}_{inst}_{size}_{datetime.now():%Y-%m-%d}.pdf"
    href = f'<a href="data:text/html;base64,{b64_html}" download="{filename}" style="color:white; text-decoration:none;">Download PDF</a>'
    st.markdown(f"**Ready!** {href}", unsafe_allow_html=True)
    st.success(f"PDF saved: {filename}")
    st.balloons()

st.caption(
    "This is the intellectual property of **Lynn Armour Hannings**.\n"
    "Balance targets = her current handwritten corrections • Prediction = her lifetime rule: **Every 4 grams = ½ inch**\n"
    "Send her a quick email — she'll love this: **lynnh@lahbows.com**"
)
