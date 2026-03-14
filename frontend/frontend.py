import streamlit as st
import httpx
import asyncio
import time


url = "http://127.0.0.1:8000"

async def get_user_info():
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            if "user_info" not in st.session_state or "account_name" not in st.session_state:
                response = await client.get(f"{url}/User/me", headers = headers)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state["user_info"] = data.get("id")
                    st.session_state["account_name"] = data.get("account_name")
                else: 
                    logout()
    except Exception as e:
        st.error(f"Authentication error: {e}")

async def get_notes():
    try:
        headers=  {"Authorization": f"Bearer {st.session_state.token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{url}/view",  headers= headers)
            if response.status_code == 200:
                notes_data = response.json()
                if not notes_data:
                    st.info("No notes found.")
                    return

                for data in notes_data:
                    note_text = data.get("note")
                    note_time = data.get("time")
                    formatted_date = note_time.split("T")[0]
                    with st.container(border=True):
                        st.write(note_text)
                        if note_time:
                            st.caption(f"Created: {formatted_date}")
            else:
                st.error("Failed to fetch notes.")
    except Exception as e:
        st.error(f"error: {e}")

async def save_note():

    note_string = st.session_state.get("draft_note", "")
    if not note_string.strip():
        st.warning("Cannot save an empty note!")
        return
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{url}/create", headers= headers , data={"note_content": note_string})
            if response.status_code== 200:
                st.success("Added note successful")
                st.session_state["draft_note"] = ""
            else:
                st.error(f"Something went wrong: {response.status_code}")

    except Exception as e:
        st.error(f"error: {e}")

async def login(email, pwd):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{url}/api/User/token" , data={"username": email, "password": pwd})
            if response.status_code == 200:
                saved_token = response.json().get("access_token")
                st.session_state["token"] = saved_token
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")
    except Exception as e:
        st.error(f"error: {e}")

def logout():
    cookie_manager.delete("auth_token")
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def note_note():
    asyncio.run(save_note())

def set_signup():
    st.session_state.form = "signup" 

def set_login():
    st.session_state.form = "login"

async def signup(name ,email, pwd):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{url}/register", json = {
                "account_name":name,
                "email": email,
                "password": pwd})
            if response.status_code == 200:
                st.success("Signup successful, Now login")
                await asyncio.sleep(2)
                st.rerun()
            elif response.status_code == 409:
                st.success("already Signup, Try login")
                await asyncio.sleep(2)
                st.rerun()
    except Exception as e:
        st.error(f"error: {e}")

if "form" not in st.session_state:
    set_login()

if "token" not in st.session_state:
    st.title("login form")
    if st.session_state.form == "login":
        with st.form("login_form"):
            user_email = st.text_input("Email Address")
            pwd = st.text_input("Password", type= "password")
            btn_login = st.form_submit_button("login")
            signup= st.form_submit_button("signup",  on_click= set_signup)
            if btn_login:
                asyncio.run(login(user_email, pwd))
    elif st.session_state.form == "signup":
        with st.form("signup_form"):
            account_name = st.text_input("Name")
            user_email = st.text_input("Email Address")
            pwd = st.text_input("Password", type= "password")
            btn_signup = st.form_submit_button("signup")
            login= st.form_submit_button("login",  on_click= set_login)
            if btn_signup:
                asyncio.run(signup(account_name ,user_email, pwd))

else:
    st.sidebar.button("Logout", on_click=logout)
    asyncio.run(get_user_info())
    st.title("📝 Notesmaker")
    st.subheader(f"Welcome back, {st.session_state.get('account_name', 'User')}", divider=True)
    
    with st.expander("➕ Add a new note", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.text_area(
                "Markdown Editor (Press Ctrl+Enter to update)", 
                height=200, 
                key="draft_note"
            )
            st.button("Save Note", type="primary", on_click=note_note)
            
        with col2:
            st.write("Live Preview:")
            live_text = st.session_state.get("draft_note", "")
            if live_text:
                st.markdown(live_text)
            else:
                st.caption("*Start typing to see preview...*")

    asyncio.run(get_notes())