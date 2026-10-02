import json
import re
import requests
import streamlit as st

# ------------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Mes Recettes & Macros IA",
    page_icon="🍳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialisation du stockage local des recettes (session Streamlit)
if "recipes" not in st.session_state:
    st.session_state.recipes = []

# ------------------------------------------------------------------------------
# BARRE LATÉRALE : CLÉ API GEMINI
# ------------------------------------------------------------------------------
st.sidebar.header("🔑 Clé API Gemini")
api_key_input = st.sidebar.text_input(
    "Entre ta clé API Google AI Studio :",
    type="password",
    value="AQ.Ab8RN6LPIUOP3-U1l1Z-namuWQITuH1x-IKyumKQj8B49RBKHQ",
    help="Récupère ta clé gratuite sur https://aistudio.google.com/"
)
if api_key_input:
    st.session_state.gemini_api_key = api_key_input

# ------------------------------------------------------------------------------
# EN-TÊTE PRINCIPAL
# ------------------------------------------------------------------------------
st.title("🍳 Mes Recettes & Macros IA")
st.caption("Carnet de recettes virtuel avec analyse nutritionnelle automatique par IA.")

st.divider()

# ------------------------------------------------------------------------------
# SECTION 1 : AJOUTER UNE RECETTE (TEXTE OU VIDÉO)
# ------------------------------------------------------------------------------
st.header("📥 Ajouter une recette")
st.write("Colle le texte d'une publication ou importe une vidéo. L'IA extraira la recette, les calories et les macros.")

recipe_text = st.text_area(
    "Texte de la recette ou description :",
    placeholder="Colle le texte ou la liste des ingrédients ici..."
)

uploaded_video = st.file_uploader(
    "🎥 Choisir ou déposer une vidéo (MP4, MOV, max 20 Mo conseillé)",
    type=["mp4", "mov", "avi", "m4v"]
)

# Fonction d'extraction via la REST API Gemini (requests)
def extract_recipe_with_gemini(text, video_file, key):
    prompt = """Analyse le contenu (texte et/ou vidéo) et extrait les informations sous forme de JSON strict respectant exactement ce schéma :
{
  "title": "Nom du plat",
  "prepTime": "ex: 20 min",
  "baseServings": 4,
  "ingredients": ["200g de chocolat", "3 oeufs"],
  "steps": ["Étape 1...", "Étape 2..."],
  "calories": 350,
  "proteins": 12,
  "carbs": 45,
  "fats": 15
}
baseServings, calories, proteins, carbs et fats doivent être des NOMBRES ENTIERS (calories et macros par portion).
Rends UNIQUEMENT le JSON sans formatage de bloc de code."""

    parts = [{"text": prompt}]
    if text:
        parts.append({"text": f"Texte fourni : {text}"})
    if video_file is not None:
        import base64
        video_bytes = video_file.read()
        b64_data = base64.b64encode(video_bytes).decode('utf-8')
        mime_type = video_file.type or "video/mp4"
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": b64_data
            }
        })

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-latest:generateContent?key={key}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": parts}]}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
    clean_json = raw_text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_json)

if st.button("✨ Extraire avec Macros & Calories", type="primary"):
    current_key = st.session_state.get("gemini_api_key", "")
    if not current_key:
        st.error("Veuillez d'abord saisir votre clé API Gemini dans le menu latéral (à gauche).")
    elif not recipe_text and uploaded_video is None:
        st.warning("Veuillez saisir du texte ou ajouter un fichier vidéo.")
    else:
        with st.spinner("Analyse par l'IA et calcul des valeurs nutritionnelles..."):
            try:
                data = extract_recipe_with_gemini(recipe_text, uploaded_video, current_key)
                
                base_servings = int(data.get("baseServings", 4))
                new_recipe = {
                    "id": len(st.session_state.recipes) + 1,
                    "title": data.get("title", "Nouvelle recette"),
                    "prepTime": data.get("prepTime", "Non précisé"),
                    "baseServings": base_servings,
                    "currentServings": base_servings,
                    "ingredients": data.get("ingredients", []),
                    "steps": data.get("steps", []),
                    "calories": int(data.get("calories", 0)),
                    "proteins": int(data.get("proteins", 0)),
                    "carbs": int(data.get("carbs", 0)),
                    "fats": int(data.get("fats", 0)),
                    "rating": 0,
                    "comment": ""
                }
                st.session_state.recipes.insert(0, new_recipe)
                st.success("Recette ajoutée avec succès !")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur lors de l'extraction : {e}")

st.divider()

# ------------------------------------------------------------------------------
# HELPER : RECALCUL DES INGRÉDIENTS
# ------------------------------------------------------------------------------
def scale_ingredient(ingredient_str, ratio):
    def replace_num(match):
        val = float(match.group(1).replace(',', '.'))
        new_val = round(val * ratio, 1)
        return str(int(new_val)) if new_val.is_integer() else str(new_val)
    return re.sub(r'(\d+(?:[.,]\d+)?)', replace_num, ingredient_str)

# ------------------------------------------------------------------------------
# SECTION 2 : CARNET DE RECETTES
# ------------------------------------------------------------------------------
col_head1, col_head2 = st.columns([2, 1])
with col_head1:
    st.header(f"📖 Mes Recettes ({len(st.session_state.recipes)})")
with col_head2:
    search_query = st.text_input("🔍 Rechercher...", value="", label_visibility="collapsed")

# Filtrage
filtered_recipes = [
    r for r in st.session_state.recipes
    if search_query.lower() in r["title"].lower()
    or any(search_query.lower() in ing.lower() for ing in r["ingredients"])
]

if not filtered_recipes:
    st.info("Aucune recette enregistrée pour le moment.")
else:
    for idx, r in enumerate(filtered_recipes):
        with st.container(border=True):
            st.subheader(r["title"])
            
            # Ligne d'informations principales
            col_info1, col_info2, col_info3 = st.columns([1, 1.5, 1])
            with col_info1:
                st.write(f"⏱️ **{r['prepTime']}**")
            with col_info2:
                r["currentServings"] = st.number_input(
                    "Portions :",
                    min_value=1,
                    max_value=20,
                    value=r.get("currentServings", r["baseServings"]),
                    key=f"servings_{r['id']}_{idx}"
                )
            with col_info3:
                r["rating"] = st.selectbox(
                    "Note :",
                    options=[0, 1, 2, 3, 4, 5],
                    format_func=lambda x: "⭐" * x if x > 0 else "Pas de note",
                    index=r.get("rating", 0),
                    key=f"rating_{r['id']}_{idx}"
                )

            # Tableau des macros
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Calories", f"{r['calories']} kcal")
            c2.metric("Protéines", f"{r['proteins']} g")
            c3.metric("Glucides", f"{r['carbs']} g")
            c4.metric("Lipides", f"{r['fats']} g")

            # Ingrédients ajustés
            st.write("**Ingrédients :**")
            ratio = r["currentServings"] / max(r["baseServings"], 1)
            for ing in r["ingredients"]:
                st.write(f"- {scale_ingredient(ing, ratio)}")

            # Étapes
            if r["steps"]:
                st.write("**Préparation :**")
                for i, step in enumerate(r["steps"], 1):
                    st.write(f"{i}. {step}")

            # Commentaire / Note perso
            if r.get("comment"):
                st.info(f"💬 **Note :** {r['comment']}")

            # Actions : Édition / Suppression
            with st.expander("✏️ Modifier / Supprimer cette recette"):
                with st.form(key=f"edit_form_{r['id']}_{idx}"):
                    edit_title = st.text_input("Titre", value=r["title"])
                    edit_prep = st.text_input("Temps de préparation", value=r["prepTime"])
                    
                    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                    edit_cal = m_col1.number_input("Calories", value=r["calories"])
                    edit_prot = m_col2.number_input("Protéines", value=r["proteins"])
                    edit_carbs = m_col3.number_input("Glucides", value=r["carbs"])
                    edit_fats = m_col4.number_input("Lipides", value=r["fats"])
                    
                    edit_ing = st.text_area("Ingrédients (1 par ligne)", value="\n".join(r["ingredients"]))
                    edit_steps = st.text_area("Étapes (1 par ligne)", value="\n".join(r["steps"]))
                    edit_comment = st.text_area("Notes personnelles", value=r.get("comment", ""))
                    
                    btn_save = st.form_submit_button("Enregistrer les modifications")
                    
                    if btn_save:
                        r["title"] = edit_title
                        r["prepTime"] = edit_prep
                        r["calories"] = edit_cal
                        r["proteins"] = edit_prot
                        r["carbs"] = edit_carbs
                        r["fats"] = edit_fats
                        r["ingredients"] = [i.strip() for i in edit_ing.split("\n") if i.strip()]
                        r["steps"] = [s.strip() for s in edit_steps.split("\n") if s.strip()]
                        r["comment"] = edit_comment
                        st.success("Modifications enregistrées !")
                        st.rerun()

                if st.button("🗑️ Supprimer la recette", key=f"del_{r['id']}_{idx}", type="secondary"):
                    st.session_state.recipes = [rec for rec in st.session_state.recipes if rec["id"] != r["id"]]
                    st.success("Recette supprimée !")
                    st.rerun()
