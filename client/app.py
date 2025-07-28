import streamlit as st
import requests

BASE_URL = "http://localhost:8000/animals"

st.set_page_config(page_title="Ensiklopedia Zoologi", layout="wide")
st.title("📚 Data Zoologi - Pengelompokan Hewan")

# ====================== Fungsi Server API ======================

def get_animals():
    try:
        res = requests.get(BASE_URL)
        return res.json() if res.status_code == 200 else []
    except:
        return []

def add_animal(data):
    return requests.post(BASE_URL, json=data)

def delete_animal(animal_id):
    return requests.delete(f"{BASE_URL}/{animal_id}")

def update_animal(animal_id, data):
    return requests.put(f"{BASE_URL}/{animal_id}", json=data)

# ==================== Form Tambah ============a========

def form_tambah_hewan():
    st.header("➕ Tambah Data Hewan")

    if "form_id" not in st.session_state:
        st.session_state["form_id"] = 1
        st.session_state["form_name"] = ""
        st.session_state["form_group"] = "Mamalia"
        st.session_state["form_description"] = ""
        st.session_state["form_image_url"] = ""

    st.session_state["form_id"] = st.number_input("ID", min_value=1, step=1, value=st.session_state["form_id"], key="input_id")
    st.session_state["form_name"] = st.text_input("Nama Hewan", value=st.session_state["form_name"], key="input_name")
    st.session_state["form_group"] = st.selectbox("Kelompok Zoologi",
        ["Mamalia", "Reptil", "Amfibi", "Burung", "Ikan", "Serangga", "Lainnya"],
        index=["Mamalia", "Reptil", "Amfibi", "Burung", "Ikan", "Serangga", "Lainnya"].index(st.session_state["form_group"]),
        key="input_group")
    st.session_state["form_description"] = st.text_area("Deskripsi Zoologi", value=st.session_state["form_description"], key="input_desc")
    st.session_state["form_image_url"] = st.text_input("URL Gambar", value=st.session_state["form_image_url"], key="input_img")

    if st.button("Tambah Hewan"):
        payload = {
            "id": st.session_state["form_id"],
            "name": st.session_state["form_name"],
            "group": st.session_state["form_group"],
            "description": st.session_state["form_description"],
            "image_url": st.session_state["form_image_url"]
        }
        res = add_animal(payload)
        if res.status_code == 200:
            st.success("Hewan berhasil ditambahkan!")

            # Reset semua field input
            st.session_state["form_id"] += 1
            st.session_state["form_name"] = ""
            st.session_state["form_group"] = "Mamalia"
            st.session_state["form_description"] = ""
            st.session_state["form_image_url"] = ""

            st.rerun()
        else:
            st.error(f"Error: {res.json().get('detail', 'Tidak diketahui')}")


# ==================== Tampilan Detail ====================

def tampilkan_detail(animal, animals):
    st.subheader(f"🔎 Detail Hewan: {animal['name']}")
    st.image(animal["image_url"], width=300)
    st.markdown(f"**Kelompok**: {animal['group']}")
    st.markdown(f"**Deskripsi**:\n\n{animal['description']}")
    st.markdown("---")
    st.markdown("📌 **Hewan Sejenis:**")
    same_group = [a for a in animals if a["group"] == animal["group"] and a["id"] != animal["id"]]

    if same_group:
        cols = st.columns(min(3, len(same_group)))
        for idx, rec in enumerate(same_group[:3]):
            with cols[idx]:
                st.image(rec["image_url"], width=150)
                st.markdown(rec["name"])
    else:
        st.info("Tidak ada hewan sejenis lainnya.")

    if st.button("⬅️ Kembali"):
        st.session_state["detail_mode"] = False
        st.rerun()

# ==================== Form Edit Dinamis ====================

def form_edit(animal):
    st.subheader(f"✏️ Edit Hewan: {animal['name']}")
    new_name = st.text_input("Nama Baru", value=animal["name"], key="edit_name")
    new_group = st.selectbox(
        "Kelompok Baru",
        ["Mamalia", "Reptil", "Amfibi", "Burung", "Ikan", "Serangga", "Lainnya"],
        index=["Mamalia", "Reptil", "Amfibi", "Burung", "Ikan", "Serangga", "Lainnya"].index(animal["group"]),
        key="edit_group"
    )
    new_description = st.text_area("Deskripsi Baru", value=animal["description"], key="edit_desc")
    new_image_url = st.text_input("URL Gambar Baru", value=animal["image_url"], key="edit_img")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("💾 Simpan Perubahan", key=f"save_edit_{animal['id']}"):
            edit_payload = {
                "id": animal["id"],  # ID tidak boleh berubah
                "name": new_name,
                "group": new_group,
                "description": new_description,
                "image_url": new_image_url
            }
            res = requests.put(f"{BASE_URL}/{animal['id']}", json=edit_payload)
            if res.status_code == 200:
                st.success("✅ Data berhasil diperbarui!")
                st.session_state["edit_mode"] = None
                st.rerun()
            else:
                st.error("❌ Gagal memperbarui data.")

    with col2:
        if st.button("❌ Batal", key=f"cancel_edit_{animal['id']}"):
            st.session_state["edit_mode"] = None
            st.rerun()


# ==================== Daftar & Filter Hewan ====================

def daftar_hewan():
    st.header("📖 Lihat Data Hewan")

    col_search, col_group, col_alpha = st.columns([2, 1, 1])
    with col_search:
        search_name = st.text_input("🔍 Cari berdasarkan nama")
    with col_group:
        selected_group = st.selectbox("Kelompok Zoologi", ["Semua", "Mamalia", "Reptil", "Amfibi", "Burung", "Ikan", "Serangga", "Lainnya"])
    with col_alpha:
        alphabet_filter = st.selectbox("Abjad Awal", ["Semua"] + [chr(c) for c in range(ord('A'), ord('Z')+1)])

    animals = get_animals()

    # filter
    if selected_group != "Semua":
        animals = [a for a in animals if a["group"].lower() == selected_group.lower()]
    if search_name:
        animals = [a for a in animals if search_name.lower() in a["name"].lower()]
    if alphabet_filter != "Semua":
        animals = [a for a in animals if a["name"].lower().startswith(alphabet_filter.lower())]

    if st.session_state.get("detail_mode", False):
        tampilkan_detail(st.session_state["detail_animal"], animals)
        return

    if animals:
        cols = st.columns(2)
        for idx, animal in enumerate(animals):
            with cols[idx % 2]:
                st.image(animal["image_url"], width=250, caption=animal["name"])
                st.markdown(f"**Kelompok**: {animal['group']}")
                st.markdown(animal["description"][:150] + "...")

                if st.button("🔍 Detail", key=f"detail_btn_{animal['id']}"):
                    st.session_state["detail_animal"] = animal
                    st.session_state["detail_mode"] = True
                    st.rerun()

                col_edit, col_delete = st.columns(2)
                with col_edit:
                    if st.button("✏️ Edit", key=f"edit_btn_{animal['id']}"):
                        st.session_state["edit_animal"] = animal
                        st.session_state["edit_mode"] = animal["id"]
                        st.rerun()

                with col_delete:
                    if st.button("🗑️ Hapus", key=f"delete_btn_{animal['id']}"):
                        res = delete_animal(animal["id"])
                        if res.status_code == 200:
                            st.success("Hewan berhasil dihapus.")
                            st.rerun()
                        else:
                            st.error("Gagal menghapus.")


    else:
        st.warning("🐾 Tidak ada data ditemukan.")

# ====================== RUN APP ======================
if st.session_state.get("edit_mode"):
    form_edit(st.session_state["edit_animal"])
    st.stop()

form_tambah_hewan()
st.divider()
daftar_hewan()
