import streamlit as st
import requests, uuid, os, re, hmac
from datetime import datetime, timezone
import pandas as pd
import html

# ============================================================
# SITE CONFIGURATION — EDIT THESE
# ============================================================
COLLEGE_NAME = "United College of Engineering and Research"
SITE_NAME = "United Issues"
TAGLINE = "Student's Voice"

EVENT_TITLE = "Peaceful Protest"
EVENT_DATE = "1st October 2026"
EVENT_TIME = "8:30AM"
EVENT_PLACE = "UCER - GateNo.2"

DEMANDS = [
    "Accountability for Gun Gupta",
    "Acceptance of short attendance on medical grounds with doctor's note till valid date",
    "Student Grievance Cell for resolving all student matters with unbiased investigation for every complaint",
]

ORGANIZER_CONTACT = "unitedissues@gmail.com"
SITE_OWNER = "A College Student"
YEAR = "2026"

# ============================================================
# APP SETUP
# ============================================================
st.set_page_config(
    page_title=f"{SITE_NAME} | {COLLEGE_NAME}",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- SECRETS / DATABASE ----------
def secret(name, default=""):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)

SUPABASE_URL = str(secret("SUPABASE_URL")).rstrip("/")
SUPABASE_ANON_KEY = str(secret("SUPABASE_ANON_KEY"))
SUPABASE_SERVICE_KEY = str(secret("SUPABASE_SERVICE_KEY"))
ADMIN_PASSWORD = str(secret("ADMIN_PASSWORD"))
ADMIN_USER = str(secret("ADMIN_USER", "admin"))

def configured():
    return bool(SUPABASE_URL and SUPABASE_ANON_KEY and SUPABASE_SERVICE_KEY and ADMIN_PASSWORD)

def api_request(method, table, payload=None, params=None, admin=False, select="*"):
    key = SUPABASE_SERVICE_KEY if admin else SUPABASE_ANON_KEY
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if method == "POST":
        headers["Prefer"] = "return=representation"
    if method == "PATCH":
        headers["Prefer"] = "return=representation"
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if params is None:
        params = {}
    if select:
        params = {**params, "select": select}
    try:
        r = requests.request(method, url, headers=headers, json=payload, params=params, timeout=15)
        if r.status_code >= 400:
            return False, r.text
        return True, r.json() if r.text else []
    except Exception as e:
        return False, str(e)

def public_insert(table, payload):
    # Writes are performed server-side with the private Supabase key.
    # The key is kept in Streamlit Secrets and is never sent to the browser.
    return api_request("POST", table, payload, admin=True)

def admin_get(table, params=None):
    return api_request("GET", table, params=params, admin=True)

def admin_patch(table, payload, params):
    return api_request("PATCH", table, payload, params=params, admin=True)

# ---------- HELPERS ----------
def esc(x):
    return html.escape(str(x or ""))

def ticket_id(prefix="STU"):
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

def valid_name(s):
    return 1 <= len(s.strip()) <= 120

def logged_in():
    return st.session_state.get("admin_ok", False)

# ---------- CSS ----------
st.markdown("""
<style>
#MainMenu, footer, header {visibility:hidden}
.block-container{max-width:1060px;padding-top:1.2rem;padding-bottom:3rem}
.brand{font-size:.82rem;font-weight:700;letter-spacing:.08em;color:#555;text-transform:uppercase}
.hero{padding:2.1rem 2rem;border:1px solid #e5e7eb;border-radius:18px;background:#fff;margin:.6rem 0 1rem}
.hero h1{font-size:2.7rem;line-height:1.05;margin:.5rem 0}
.hero p{font-size:1.05rem;color:#5f6368;max-width:780px}
.card{border:1px solid #e5e7eb;border-radius:15px;padding:1rem 1.1rem;background:#fff}
.stat{border:1px solid #e5e7eb;border-radius:15px;padding:1rem;background:#fff}
.statnum{font-size:1.8rem;font-weight:750}
.demand{padding:.85rem 1rem;border-left:3px solid #333;background:#f7f7f7;border-radius:8px;margin:.5rem 0}
.notice{padding:.9rem 1rem;border:1px solid #e5e7eb;border-radius:12px;background:#fafafa}
.muted{color:#6b7280;font-size:.84rem}
.smallcaps{font-size:.78rem;text-transform:uppercase;letter-spacing:.07em;color:#6b7280}
hr{margin:1.5rem 0}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown(f'<div class="brand">{esc(COLLEGE_NAME)} · {esc(SITE_NAME)}</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="hero">
<div class="smallcaps">Student-run information & support</div>
<h1>{esc(SITE_NAME)}</h1>
<p>{esc(TAGLINE)}</p>
</div>
""", unsafe_allow_html=True)

if not configured():
    st.error("This app is not connected to its persistent database yet. The organizer must add the four Streamlit secrets described in README.md.")
    st.stop()

# ---------- NAV ----------
page=st.radio(
    "Navigation",
    ["Home","Petition","Report a Problem","Updates","Information","Admin"],
    horizontal=True,label_visibility="collapsed"
)

# ================= HOME =================
if page=="Home":
    ok, rows=admin_get("petition_signatures", {"select":"id"})
    signatures=len(rows) if ok and isinstance(rows,list) else 0

    a,b,c=st.columns(3)
    with a:
        st.markdown(f'<div class="stat"><div class="statnum">{signatures}</div>petition signatures</div>',unsafe_allow_html=True)
    with b:
        st.markdown(f'<div class="stat"><div class="statnum">📝</div>report a campus problem</div>',unsafe_allow_html=True)
    with c:
        st.markdown(f'<div class="stat"><div class="statnum">📢</div>verified updates</div>',unsafe_allow_html=True)

    st.write("")
    st.subheader("What this site is for")
    st.write(
        "This is a student-run platform for everyday campus concerns as well as "
        "organized, peaceful student action. Students can read verified information, "
        "sign a petition, report a problem and check organizer updates."
    )

    st.subheader("Current student requests")
    for i,d in enumerate(DEMANDS,1):
        st.markdown(f'<div class="demand"><b>{i}.</b> {esc(d)}</div>',unsafe_allow_html=True)

    st.write("")
    st.subheader("Action details")
    a,b,c=st.columns(3)
    a.markdown(f"**Date**  \n{esc(EVENT_DATE)}")
    b.markdown(f"**Time**  \n{esc(EVENT_TIME)}")
    c.markdown(f"**Place**  \n{esc(EVENT_PLACE)}")

    st.markdown('<div class="notice"><b>Participation:</b> Keep all participation peaceful, respectful and lawful. Check Updates before relying on event information.</div>',unsafe_allow_html=True)

# ================= PETITION =================
elif page=="Petition":
    st.subheader("Student petition")
    st.write("Sign the petition voluntarily. Individual signatures are private and are not displayed to other students.")

    ok,rows=admin_get("petition_signatures",{"select":"id"})
    count=len(rows) if ok and isinstance(rows,list) else 0
    st.metric("Current signatures",count)

    with st.form("petition",clear_on_submit=True):
        name=st.text_input("Full name *")
        department=st.text_input("Department (optional)")
        year=st.selectbox("Year",["Prefer not to say","1st Year","2nd Year","3rd Year","4th Year","Other"])
        note=st.text_area("Optional message",max_chars=1000,placeholder="Briefly explain your concern or reason for signing.")
        consent=st.checkbox("I am voluntarily signing and agree that organizers may use this submission for presenting the petition.")
        submit=st.form_submit_button("Sign petition",type="primary")

    if submit:
        if not valid_name(name):
            st.error("Please enter your name.")
        elif not consent:
            st.error("Please confirm the consent statement.")
        else:
            ok,result=public_insert("petition_signatures",{
                "name":name.strip(),
                "department":department.strip(),
                "year":year,
                "message":note.strip(),
                "consent":True
            })
            if ok:
                st.success("Your signature has been recorded.")
                st.rerun()
            else:
                st.error("The submission could not be saved.")
                with st.expander("Technical error (for organizer)"):
                    st.code(str(result))

# ================= REPORT PROBLEM =================
elif page=="Report a Problem":
    st.subheader("Report a campus problem")
    st.write("Use this section on regular college days too. You can report an academic, infrastructure, administrative or student-life issue.")

    with st.form("issue",clear_on_submit=True):
        category=st.selectbox("Category",[
            "Academic","Examination","Fees / Finance","Infrastructure",
            "Library / Lab","Hostel","Transport","Administration",
            "Safety / Accessibility","Student Life","Other"
        ])
        title=st.text_input("Short title *",max_chars=120,placeholder="e.g. Broken lab equipment")
        description=st.text_area("Describe the problem *",max_chars=3000)
        department=st.text_input("Department (optional)")
        year=st.selectbox("Your year",["Prefer not to say","1st Year","2nd Year","3rd Year","4th Year","Other"],key="issue_year")
        name=st.text_input("Name (optional)")
        contact=st.text_input("Contact email (optional)")
        anonymous=st.checkbox("Submit without displaying my name to other students.",value=True)
        consent=st.checkbox("I confirm this report is made in good faith and contains no threats or deliberately false information.")
        submit=st.form_submit_button("Submit problem",type="primary")

    if submit:
        if not title.strip() or not description.strip():
            st.error("Please provide a title and description.")
        elif contact and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$",contact.strip()):
            st.error("Please enter a valid email or leave it blank.")
        elif not consent:
            st.error("Please confirm the statement.")
        else:
            tid=ticket_id("ISS")
            ok,result=public_insert("issues",{
                "ticket_id":tid,
                "category":category,
                "title":title.strip(),
                "description":description.strip(),
                "department":department.strip(),
                "year":year,
                "name":name.strip(),
                "contact":contact.strip(),
                "anonymous":anonymous,
                "status":"Received"
            })
            if ok:
                st.success("Problem submitted.")
                st.code(tid)
                st.info("Save this ticket ID. You can use it to ask organizers about the status of your report.")
            else:
                st.error("The report could not be saved.")
                with st.expander("Technical error (for organizer)"):
                    st.code(str(result))

    st.markdown("### Check a report")
    tid=st.text_input("Ticket ID",placeholder="e.g. ISS-AB12CD34")
    if st.button("Check status"):
        if not tid.strip():
            st.error("Enter a ticket ID.")
        else:
            ok,rows=public_insert("issue_status_requests",{"ticket_id":tid.strip().upper()})
            # Public status lookup is handled below using a restricted RPC/table.
            ok2,data=api_request("GET","issues",params={"ticket_id":f"eq.{tid.strip().upper()}"},admin=True,select="ticket_id,status,updated_at")
            if ok2 and data:
                st.info(f"Status: {data[0]['status']}")
                st.caption(f"Last updated: {data[0].get('updated_at','')}")
            else:
                st.warning("No report found with that ticket ID, or it is not available for public status lookup.")

# ================= UPDATES =================
elif page=="Updates":
    st.subheader("Verified updates")
    st.write("Organizer-posted information. Check here for changes before relying on event details.")

    ok,rows=admin_get("public_updates",{"order":"created_at.desc"})
    if ok and rows:
        for r in rows:
            st.markdown(f"""
            <div class="card">
            <b>{esc(r.get('title'))}</b><br>
            <span class="muted">{esc(r.get('created_at'))}</span>
            <p>{esc(r.get('body'))}</p>
            </div>
            """,unsafe_allow_html=True)
    else:
        st.info("No updates have been posted yet.")

# ================= INFORMATION =================
elif page=="Information":
    st.subheader("Information & privacy")
    st.markdown("### For students")
    st.write(
        "Only provide information that is necessary. Do not submit passwords, "
        "financial information, precise home addresses or another person's private information."
    )
    st.markdown("### For student action")
    st.write(
        "Participation should remain peaceful, respectful and lawful. Verify event "
        "details through the Updates page or the organizers' official communication channel."
    )
    st.markdown("### Who operates this site?")
    st.write(f"{SITE_OWNER}. This is a student-run platform and is not an official college website unless explicitly stated otherwise.")
    st.markdown("### Contact")
    st.write(ORGANIZER_CONTACT)
    st.markdown("### Copyright")
    st.write(f"© {YEAR} {SITE_OWNER}. All rights reserved. Content may be reused only with permission unless otherwise stated.")
    st.markdown("### Privacy")
    st.write(
        "Petition signatures and problem reports are stored for organizer use. "
        "Individual submissions are not published publicly by this application. "
        "Data retention should follow the organizers' stated purpose and applicable rules."
    )

# ================= ADMIN =================
else:
    st.subheader("Organizer administration")

    if "admin_ok" not in st.session_state:
        st.session_state.admin_ok=False

    if not st.session_state.admin_ok:
        st.write("Private organizer area.")
        with st.form("login"):
            user=st.text_input("Admin username")
            pw=st.text_input("Admin password",type="password")
            go=st.form_submit_button("Log in",type="primary")
        if go:
            if hmac.compare_digest(user,ADMIN_USER) and hmac.compare_digest(pw,ADMIN_PASSWORD):
                st.session_state.admin_ok=True
                st.rerun()
            else:
                st.error("Incorrect login.")
    else:
        st.success("Admin access enabled.")
        tabs=st.tabs(["Dashboard","Petitions","Problems","Updates"])

        with tabs[0]:
            ok,p=admin_get("petition_signatures",{"select":"id"})
            ok2,i=admin_get("issues",{"select":"id,status"})
            pc=len(p) if ok and isinstance(p,list) else 0
            ic=len(i) if ok2 and isinstance(i,list) else 0
            open_count=sum(1 for x in i if x.get("status") not in ["Resolved","Closed"]) if ok2 and isinstance(i,list) else 0
            a,b,c=st.columns(3)
            a.metric("Petition signatures",pc)
            b.metric("Problem reports",ic)
            c.metric("Open reports",open_count)
            st.caption("Data is stored in the external database configured for this app, not in the Streamlit app filesystem.")

        with tabs[1]:
            ok,rows=admin_get("petition_signatures",{"order":"created_at.desc"})
            df=pd.DataFrame(rows if ok else [])
            if not df.empty:
                st.dataframe(df,use_container_width=True,hide_index=True)
                st.download_button("Download petition CSV",df.to_csv(index=False).encode(), "petition_signatures.csv","text/csv",type="primary")
            else: st.info("No petition signatures.")

        with tabs[2]:
            ok,rows=admin_get("issues",{"order":"created_at.desc"})
            df=pd.DataFrame(rows if ok else [])
            if not df.empty:
                st.dataframe(df,use_container_width=True,hide_index=True)
                st.download_button("Download problems CSV",df.to_csv(index=False).encode(), "student_problem_reports.csv","text/csv")
                st.write("")
                st.markdown("### Update a report")
                ids=df["ticket_id"].tolist()
                selected=st.selectbox("Ticket ID",ids)
                status=st.selectbox("New status",["Received","Under review","In progress","Awaiting response","Resolved","Closed"])
                if st.button("Save status"):
                    ok,_=admin_patch("issues",{"status":status,"updated_at":datetime.now(timezone.utc).isoformat()},{"ticket_id":f"eq.{selected}"})
                    if ok:
                        st.success("Status updated.")
                        st.rerun()
                    else: st.error("Could not update.")
            else: st.info("No problem reports.")

        with tabs[3]:
            ok,rows=admin_get("public_updates",{"order":"created_at.desc"})
            if ok and rows:
                st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
            with st.form("new_update",clear_on_submit=True):
                title=st.text_input("Update title")
                body=st.text_area("Update")
                publish=st.form_submit_button("Publish update",type="primary")
            if publish:
                if title.strip() and body.strip():
                    ok,_=api_request("POST","public_updates",{"title":title.strip(),"body":body.strip()},admin=True)
                    if ok:
                        st.success("Update published.")
                        st.rerun()
                    else: st.error("Could not publish update.")
                else: st.error("Enter both title and update.")

        if st.button("Log out"):
            st.session_state.admin_ok=False
            st.rerun()

st.divider()
st.caption(f"© {YEAR} {SITE_OWNER} · {SITE_NAME} · Student-run platform · Not an official college website unless explicitly stated.")
