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

                with st.container(border=True):
                    if not notes_data:
                        st.info("Start making your notes. :}")
                        return

                    for data in notes_data:
                        note_text =data.get("note")
                        note_time = data.get("time")
                        note_id = data.get("id")
                        formatted_date = note_time.split("T")[0] if note_time  else ""

                        with st.container(border=True):

                            if st.session_state.get("editing_note_id") == note_id:
                                st.text_area(
                                    "Edit note:", 
                                    value=note_text, 
                                    key = f"edit_box_{note_id}",
                                    height=150)

                                col1_, col2_, col3_ = st.columns([2, 2, 6])
                                with col1_:
                                    st.button("Save", key=f"save_{note_id}", type="primary", on_click=save_edit, args=(note_id,))
                                with col2_:
                                    st.button("Cancel", key=f"cancel_{note_id}", on_click=cancel_edit)

                            else:
                                left, right ,more_right =st.columns([8, 1, 1])
                                left.markdown(note_text)
                                right.button("✏️", key=f"edit_button_{note_id}", on_click = start_edit, args=(note_id,), width='stretch')
                                more_right.button("🗑️", key= f"delete_button_{note_id}" , on_click =delete_note, args=(note_id,), width='stretch')
                                if note_time:
                                    left.caption(f"Created: {formatted_date}")

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
            if  response.status_code == 200:
                st.success("Saved note successful")
            else:
                st.error(f"Something went wrong: {response.status_code}")
    except Exception as e:
        st.error(f"error: {e}")
            

async def update_note(note_id, new_text):
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        async with httpx.AsyncClient() as client:
            response = await client.patch(f"{url}/edit/{note_id}", headers= headers , json={"notes": new_text})
            if  response.status_code == 200:
                st.success("Update note successful")
            else:
                st.error(f"Something went wrong: {response.status_code}")

    except Exception as e:
        st.error(f"error: {e}")

async def remove_note(note_id):
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{url}/remove/{note_id}", headers= headers)
            if  response.status_code == 200:
                st.success("Removed note successful")
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
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def start_edit(note_id):
    st.session_state["editing_note_id"] = note_id

def cancel_edit():
    st.session_state["editing_note_id"] = None

def save_edit(note_id):
    new_text = st.session_state.get(f"edit_box_{note_id}")
    if new_text:
        asyncio.run(update_note(note_id, new_text))
    st.session_state["editing_note_id"] = None

def toggle_view():
    st.session_state.image = not st.session_state.image
    

def note_note():
    asyncio.run(save_note())

def delete_note(note_id):
    asyncio.run(remove_note(note_id))

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
            if response.status_code == 201:
                st.success("Signup successful, Now login")
                await asyncio.sleep(2)
                st.rerun()
            elif response.status_code == 400:
                st.success("already Signup, Try login")
                await asyncio.sleep(2)
                st.rerun()
            else:
                st.error(f"Something is not right: {response.status_code}")
                st.rerun()
    except Exception as e:
        st.error(f"error: {e}")

if "form" not in st.session_state:
    set_login()

if "editing_note_id" not in st.session_state:
    st.session_state["editing_note_id"] = None

if "image" not in st.session_state:
    st.session_state.image = True


if "token" not in st.session_state:
    if st.session_state.form == "login":
        st.title("login form")
        with st.form("login_form"):
            user_email = st.text_input("Email Address")
            pwd = st.text_input("Password", type= "password")
            col1, col2 = st.columns([5, 1])
            with col2:
                btn_login = st.form_submit_button("login")
            with col1:
                signup= st.form_submit_button("signup",  on_click= set_signup)
            if btn_login:
                asyncio.run(login(user_email, pwd))
    elif st.session_state.form == "signup":
        st.title("signup form")
        with st.form("signup_form"):
            account_name = st.text_input("Name")
            user_email = st.text_input("Email Address")
            pwd = st.text_input("Password", type= "password")
            coli1, coli2 = st.columns([5, 1])
            with coli2:
                btn_signup = st.form_submit_button("signup")
            with coli1:
                login= st.form_submit_button("login",  on_click= set_login)
            if btn_signup:
                asyncio.run(signup(account_name ,user_email, pwd))

else:
    asyncio.run(get_user_info())
    wel_col, logout_col = st.columns([7,1])
    logout_col.button("Logout", on_click=logout)
    wel_col.title("📝 Notesmaker")
    st.subheader(f"Welcome back, {st.session_state.get('account_name', 'User')}", divider=True)
    if st.session_state.image:
        st.image("frontend/image.png",
        width='stretch',
        caption="Click 'Add note' to start writing!")
        st.button("Add note", on_click=toggle_view)

    else:
        with st.expander("Create new note", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.text_area(
                    "Markdown Editor", 
                    height=200, 
                    key="draft_note"
                )
                col1_, col2_, col3_ = st.columns([4, 4, 1])
                with col1_:
                    st.button("Save Note", type="primary", on_click=note_note)
                with col2_:
                    st.button("Cancel", on_click= toggle_view)
            with col2:
                st.write("Preview:")
                live_text = st.session_state.get("draft_note", "")
                if live_text:
                    st.markdown(live_text)
                else:
                    st.caption("*Start typing to see preview...*")
    asyncio.run(get_notes())