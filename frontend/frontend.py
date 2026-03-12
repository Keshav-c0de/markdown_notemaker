import streamlit as st
import httpx
import asyncio
import extra_streamlit_components as stx


url = "http://127.0.0.1:8000"

cookie_manager =stx.CookieManager()
client = httpx.AsyncClient()
cookie_token = cookie_manager.get(cookie="auth_token")

if cookie_token and "token" not in st.session_state:
    st.session_state["token"] = cookie_token

async def get_user_info():
    try:
        headers =headers = {"Authorization": f"Bearer {st.session_state.token}"}
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
        notes = await client.get(f"{url}/me/view")
        for note in notes:
            st.write(note)
    except Exception as e:
        st.error(f"error: {e}")


async def login(email, pwd):
    try:
        response = await client.post(f"{url}/api/User/token" , data={"username": email, "password": pwd})
        if response.status_code == 200:
            saved_token = response.json().get("access_token")
            st.session_state["token"] = saved_token
            cookie_manager.set("auth_token", saved_token, key="set_cookie")
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")
    except Exception as e:
        st.error(f"error: {e}")

def logout():
    st.session_state.clear()
    cookie_manager.delete("auth_token")

def set_signup():
    st.session_state.form = "signup" 

def set_login():
    st.session_state.form = "login"

async def signup(name ,email, pwd):
    try:
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
    user_info = st.session_state.get("user_info", {})
    st.title("📝 Notesmaker")
    st.title(f"Welcome back, {st.session_state.account_name}")
    