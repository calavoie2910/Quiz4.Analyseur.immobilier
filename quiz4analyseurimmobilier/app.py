"""
King County Real Estate Analyzer
Quiz 4 — Vibe Coding
"""

import io
import os
import pathlib

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import math
import streamlit as st
from dotenv import load_dotenv

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="King County Real Estate Analyzer",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

# Couleurs Premium à Haut Contraste
PALETTE = "#059669"  # Vert Émeraude Profond
ACCENT  = "#F59E0B"  # Ambre Intense / Or (très contrasté)
WARN    = "#EF4444"  # Rouge Erreur / Alerte (mieux que orange pour contraste)
DARK_BG = "#020617"  # Bleu-Noir Profond (Slate 950)
GLASS   = "rgba(15, 23, 42, 0.85)" # Fond de carte très sombre et opaque
TEXT    = "#F8FAFC" # Blanc Cassé / Slate 50 (Contraste maximal)
SUBTEXT = "#CBD5E1" # Slate 300 pour les textes secondaires
CARD_BG = "rgba(15, 23, 42, 0.85)" # Alias pour render_llm_box

def _style_ax(ax):
    # Style transparent pour les graphiques afin qu'ils se fondent dans le dégradé
    ax.set_facecolor("none")
    fig = ax.figure
    fig.patch.set_facecolor("none")
    fig.patch.set_alpha(0.0)
    for spine in ax.spines.values():
        spine.set_edgecolor("#34D399")
        spine.set_alpha(0.5)
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)

# CSS Avancé : Dégradé Dynamique, Image de fond & Scrollbars Stylisées
import base64
def get_base64_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# On tente de charger l'image locale, sinon on garde une couleur de secours
try:
    bg_64 = get_base64_bin_file("background.png")
    bg_css = f"url('data:image/png;base64,{bg_64}')"
except:
    bg_css = "none"

st.markdown(f"""
    <style>
    /* Import de polices premium */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: {TEXT};
    }}

    /* Fond principal : Plus foncé et uni pour un rendu "Enterprise" */
    .stApp {{
        background: linear-gradient(rgba(2, 6, 23, 0.90), rgba(2, 6, 23, 0.97)), 
                    {bg_css};
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }}

    /* === PERSONNALISATION DES BARRES DÉROULANTES === */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: rgba(2, 6, 23, 0.8);
    }}
    ::-webkit-scrollbar-thumb {{
        background: {PALETTE};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {ACCENT};
    }}

    /* Style des barres de sélection (dropdowns) et inputs */
    div[data-testid="stSelectbox"] > div, div[data-testid="stMultiSelect"] > div {{
        background-color: {GLASS} !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 6px !important;
        color: {TEXT} !important;
        font-weight: 500;
        transition: border 0.2s ease;
    }}
    div[data-testid="stSelectbox"] > div:hover, div[data-testid="stMultiSelect"] > div:hover {{
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }}
    
    /* Marge intérieure des Popovers */
    div[data-baseweb="popover"] {{
        background: {DARK_BG} !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
    div[data-baseweb="select"] span {{
        color: {TEXT} !important;
    }}
    
    /* Métriques : Structurées, carrées et minimalistes */
    div[data-testid="stMetric"] {{
        background: rgba(15, 23, 42, 0.6);
        padding: 16px 20px !important;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(15, 23, 42, 0.8);
    }}
    
    [data-testid="stMetricValue"] {{
        color: {TEXT} !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {SUBTEXT} !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.8rem !important;
    }}

    /* Titres sobres et épurés */
    h1 {{
        font-weight: 700 !important;
        font-size: 2.2rem !important;
        color: {TEXT} !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem !important;
    }}
    
    h2, h3 {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }}
    
    .stSidebar {{
        background-color: rgba(2, 6, 23, 0.98) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }}

    /* Boutons : Plats, fonctionnels et solides */
    .stButton>button {{
        background-color: {PALETTE} !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        padding: 0.6rem 2rem !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        text-transform: none;
        letter-spacing: 0.2px;
        transition: all 0.2s ease !important;
        width: 100%;
    }}
    .stButton>button:hover {{
        background-color: #047857 !important; /* Vert plus foncé au vol */
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }}

    /* Tables et Dataframes */
    div[data-testid="stExpander"] {{
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
    }}
    
    /* Contraste élevé pour les textes secondaires */
    p, span, label {{
        color: {TEXT};
    }}
    
    .stMarkdown div p {{
        font-size: 1.05rem;
        line-height: 1.6;
    }}
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 0 — Chargement et préparation des données
# ─────────────────────────────────────────────────────────────────────────────
DATA_URL  = (
    "https://raw.githubusercontent.com/Shreyas3108/house-price-prediction/"
    "master/kc_house_data.csv"
)
LOCAL_CSV = pathlib.Path(__file__).parent / "kc_house_data.csv"


@st.cache_data(show_spinner="Chargement des données…")
def load_data() -> pd.DataFrame:
    if LOCAL_CSV.exists() and LOCAL_CSV.stat().st_size > 100_000:
        df = pd.read_csv(LOCAL_CSV)
    else:
        import requests
        r = requests.get(DATA_URL, timeout=30)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.to_csv(LOCAL_CSV, index=False)

    df["date"]          = pd.to_datetime(df["date"], format="%Y%m%dT000000")
    df["price_per_sqft"] = df["price"] / df["sqft_living"]
    df["age"]            = df["date"].dt.year - df["yr_built"]
    df["is_renovated"]   = df["yr_renovated"] > 0
    df["has_basement"]   = df["sqft_basement"] > 0
    return df


df_full = load_data()

# ─────────────────────────────────────────────────────────────────────────────
# Helper LLM
# ─────────────────────────────────────────────────────────────────────────────
def call_llm(prompt: str, api_key: str) -> str | None:
    """Appelle OpenAI et retourne la réponse, ou None si pas de clé."""
    if not api_key or not api_key.startswith("sk-"):
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=700,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Erreur API : {e}"


def render_llm_box(text: str):
    st.markdown(
        f'<div style="background:{CARD_BG};border-left:4px solid {PALETTE};'
        f'padding:1.2rem 1.5rem;border-radius:8px;color:#E2E8F0;'
        f'font-size:0.95rem;line-height:1.7;">{text}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar — Navigation + Filtres
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.title("KC Real Estate")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "Onglet 1 — Exploration du marché", 
        "Onglet 2 — Analyse de propriété",
        "Onglet 3 — Cartographie",
        "Onglet 4 — Simulateur de rendement"
    ],
    label_visibility="collapsed",
)
st.sidebar.markdown("---")

# Clé API (disponible dans les deux onglets)
api_key = st.sidebar.text_input(
    "Clé OpenAI (optionnel)",
    value=os.getenv("OPENAI_API_KEY", ""),
    type="password",
    help="Nécessaire pour les résumés IA. Laissez vide pour une réponse simulée.",
)

# Filtres Onglet 1 et 3
if page in ["Onglet 1 — Exploration du marché", "Onglet 3 — Cartographie"]:
    st.sidebar.subheader("Filtres")

    p_min, p_max = int(df_full["price"].min()), int(df_full["price"].max())
    price_range = st.sidebar.slider(
        "Prix ($)", p_min, p_max, (p_min, 2_000_000), step=25_000, format="$%d"
    )

    bedroom_opts = sorted(df_full["bedrooms"].unique().tolist())
    bedrooms_sel = st.sidebar.multiselect("Chambres", bedroom_opts, default=bedroom_opts)

    # 3. Salles de bain
    b_min, b_max = float(df_full["bathrooms"].min()), float(df_full["bathrooms"].max())
    bath_range = st.sidebar.slider("Salles de bain", b_min, b_max, (b_min, b_max), step=0.25)

    # 4. Code postal (Zipcode)
    zip_opts = sorted([int(z) for z in df_full["zipcode"].unique()])
    zips_sel = st.sidebar.multiselect("Codes postaux", zip_opts, default=None, help="Laissez vide pour tout sélectionner")

    # 5. Grade de construction
    g_min, g_max = int(df_full["grade"].min()), int(df_full["grade"].max())
    grade_range = st.sidebar.slider("Grade", g_min, g_max, (g_min, g_max))

    # 6. Année de construction
    y_min, y_max = int(df_full["yr_built"].min()), int(df_full["yr_built"].max())
    year_range = st.sidebar.slider("Année de construction", y_min, y_max, (y_min, y_max))

    # 7. Superficies (Above / Basement)
    sa_min, sa_max = int(df_full["sqft_above"].min()), int(df_full["sqft_above"].max())
    sb_min, sb_max = int(df_full["sqft_basement"].min()), int(df_full["sqft_basement"].max())
    
    col_sa, col_sb = st.sidebar.columns(2)
    with col_sa:
        sqft_above_range = st.slider("Sqft Above", sa_min, sa_max, (sa_min, sa_max))
    with col_sb:
        sqft_basement_range = st.slider("Sqft Basement", sb_min, sb_max, (sb_min, sb_max))

    # 8. Vue (0-4)
    v_min, v_max = int(df_full["view"].min()), int(df_full["view"].max())
    view_range = st.sidebar.slider("Vue (0-4)", v_min, v_max, (v_min, v_max))

    # 9. Condition (1-5)
    c_min, c_max = int(df_full["condition"].min()), int(df_full["condition"].max())
    cond_range = st.sidebar.slider("État (1-5)", c_min, c_max, (c_min, c_max))

    # 10. Étages
    floor_opts = sorted(df_full["floors"].unique().tolist())
    floors_sel = st.sidebar.multiselect("Étages", floor_opts, default=floor_opts)

    # 11. Options spécifiques
    col_w, col_r = st.sidebar.columns(2)
    with col_w:
        waterfront_only = st.checkbox("Front de mer", value=False)
    with col_r:
        renovated_only = st.checkbox("Rénovée", value=False)

    mask = (
        df_full["price"].between(*price_range)
        & df_full["bedrooms"].isin(bedrooms_sel if bedrooms_sel else bedroom_opts)
        & df_full["bathrooms"].between(*bath_range)
        & df_full["grade"].between(*grade_range)
        & df_full["yr_built"].between(*year_range)
        & df_full["view"].between(*view_range)
        & df_full["condition"].between(*cond_range)
        & df_full["floors"].isin(floors_sel if floors_sel else floor_opts)
        & df_full["sqft_above"].between(*sqft_above_range)
        & df_full["sqft_basement"].between(*sqft_basement_range)
    )
    if zips_sel:
        mask &= df_full["zipcode"].isin(zips_sel)
    if waterfront_only:
        mask &= df_full["waterfront"] == 1
    if renovated_only:
        mask &= df_full["is_renovated"] == True
    df = df_full[mask].copy()
else:
    df = df_full.copy()

st.sidebar.markdown("---")
st.sidebar.caption(
    f"Dataset : **{len(df_full):,}** transactions · "
    f"{df_full['date'].dt.year.min()}–{df_full['date'].dt.year.max()}"
)

# ═════════════════════════════════════════════════════════════════════════════
# ONGLET 1 — Exploration du marché
# ═════════════════════════════════════════════════════════════════════════════
if page == "Onglet 1 — Exploration du marché":
    st.title("Onglet 1 — Exploration du marché immobilier")
    st.caption("Comté de King (Seattle, WA) · 2014–2015")

    if df.empty:
        st.warning("Aucune propriété ne correspond aux filtres sélectionnés.")
        st.stop()

    # B. KPIs
    st.subheader("Métriques clés")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Propriétés",       f"{len(df):,}")
    k2.metric("Prix moyen",       f"${df['price'].mean():,.0f}")
    k3.metric("Prix médian",      f"${df['price'].median():,.0f}")
    k4.metric("Prix moyen / pi²", f"${df['price_per_sqft'].mean():.2f}")

    st.markdown("---")

    # C. Visualisations
    st.subheader("Visualisations")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.patch.set_facecolor(DARK_BG)
    for ax in axes.flat:
        _style_ax(ax)

    # 1. Histogramme des prix
    ax1 = axes[0, 0]
    ax1.hist(df["price"] / 1e6, bins=50, color=PALETTE, edgecolor=DARK_BG, alpha=0.9)
    mean_m = df["price"].mean() / 1e6
    ax1.axvline(mean_m, color=ACCENT, linewidth=1.8, linestyle="--",
                label=f"Moy. {mean_m:.2f}M$")
    ax1.set_title("Distribution des prix de vente", fontsize=13, fontweight="bold")
    ax1.set_xlabel("Prix (M$)")
    ax1.set_ylabel("Nombre de propriétés")
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}M$"))
    ax1.legend(facecolor="#334155", labelcolor="#F1F5F9", fontsize=9)

    # 2. Scatter prix vs superficie
    ax2 = axes[0, 1]
    sc = ax2.scatter(df["sqft_living"], df["price"] / 1e6,
                     c=df["grade"], cmap="YlOrRd", alpha=0.35, s=8, linewidths=0)
    cbar = fig.colorbar(sc, ax=ax2)
    cbar.set_label("Grade", color=TEXT)
    cbar.ax.yaxis.set_tick_params(color=TEXT)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT)
    ax2.set_title("Prix vs Superficie (coloré par grade)", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Superficie habitable (pi²)")
    ax2.set_ylabel("Prix (M$)")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}M$"))

    # 3. Top 10 zipcodes
    ax3 = axes[1, 0]
    top_zip = df.groupby("zipcode")["price"].mean().sort_values(ascending=False).head(10)
    bars = ax3.barh([str(z) for z in top_zip.index], top_zip.values / 1e3,
                    color=PALETTE, edgecolor=DARK_BG)
    ax3.invert_yaxis()
    ax3.set_title("Top 10 codes postaux — Prix moyen", fontsize=13, fontweight="bold")
    ax3.set_xlabel("Prix moyen (k$)")
    for bar, val in zip(bars, top_zip.values):
        ax3.text(val / 1e3 + 3, bar.get_y() + bar.get_height() / 2,
                 f"${val/1e3:,.0f}k", va="center", color=TEXT, fontsize=8)

    # 4. Matrice de corrélation
    ax4 = axes[1, 1]
    corr_cols = ["price", "sqft_living", "grade", "bedrooms",
                 "bathrooms", "age", "price_per_sqft", "view"]
    corr = df[corr_cols].corr()
    sns.heatmap(corr, ax=ax4, annot=True, fmt=".2f", cmap="coolwarm",
                linewidths=0.5, linecolor=DARK_BG,
                annot_kws={"size": 8, "color": "white"},
                cbar_kws={"shrink": 0.8})
    ax4.set_title("Matrice de corrélation", fontsize=13, fontweight="bold")
    ax4.tick_params(axis="x", rotation=45, colors=TEXT)
    ax4.tick_params(axis="y", rotation=0, colors=TEXT)

    plt.tight_layout(pad=2.5)
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("---")

    # D. Résumé LLM
    st.subheader("Résumé généré par IA")
    if st.button("Générer un résumé du marché", type="primary"):
        grade_dist = (
            df["grade"].value_counts().sort_index()
            .apply(lambda x: f"{x} ({x/len(df)*100:.1f}%)")
            .to_dict()
        )
        pct_waterfront = df["waterfront"].mean() * 100
        prompt = f"""Tu es un analyste immobilier senior. Voici les statistiques d'un segment
du marché immobilier du comté de King (Seattle) :

- Nombre de propriétés : {len(df):,}
- Prix moyen : {df['price'].mean():,.0f} $
- Prix médian : {df['price'].median():,.0f} $
- Prix min / max : {df['price'].min():,.0f} $ / {df['price'].max():,.0f} $
- Prix moyen par pi² : {df['price_per_sqft'].mean():.2f} $
- Superficie habitable moyenne : {df['sqft_living'].mean():,.0f} pi²
- Âge moyen des propriétés : {df['age'].mean():.0f} ans
- % front de mer : {pct_waterfront:.1f}%
- % maisons rénovées : {df['is_renovated'].mean()*100:.1f}%
- Répartition par grade : {grade_dist}

Rédige un résumé exécutif de ce segment en 3-4 paragraphes.
Identifie les tendances clés et les opportunités d'investissement.
Réponds en français, avec le ton d'une note d'analyste professionnelle."""

        with st.spinner("Analyse en cours…"):
            result = call_llm(prompt, api_key)

        if result:
            render_llm_box(result)
        else:
            render_llm_box(
                f"""**Note d'analyste — Segment filtré ({len(df):,} propriétés)**

Le segment analysé présente un prix moyen de **{df['price'].mean():,.0f} $** et un prix médian de **{df['price'].median():,.0f} $**, révélant une distribution légèrement asymétrique caractéristique des marchés immobiliers premium.

Avec un prix moyen au pied carré de **{df['price_per_sqft'].mean():.2f} $** et une superficie moyenne de **{df['sqft_living'].mean():,.0f} pi²**, ce marché se positionne dans un segment intermédiaire-supérieur. L'âge moyen des biens est de **{df['age'].mean():.0f} ans**.

Les propriétés en front de mer représentent **{pct_waterfront:.1f}%** du segment — une rareté qui génère des primes de prix substantielles et mérite une attention particulière pour les investisseurs cherchant des actifs à forte valeur de revente.

*Note : Ajoutez une clé OpenAI dans la barre latérale pour obtenir une analyse IA complète.*"""
            )


# ═════════════════════════════════════════════════════════════════════════════
# ONGLET 2 — Analyse de propriété
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Onglet 2 — Analyse de propriété":
    st.title("Onglet 2 — Analyse de propriété")
    st.caption("Sélectionnez une propriété et comparez-la à ses comparables locaux.")

    # ── A. Sélection progressive ──────────────────────────────────────────────
    st.subheader("Sélection de la propriété")
    col_zip, col_bed, col_prop = st.columns([1, 1, 2])

    with col_zip:
        zip_opts = sorted(df_full["zipcode"].unique().tolist())
        selected_zip = st.selectbox("Code postal", zip_opts, index=0)

    df_zip = df_full[df_full["zipcode"] == selected_zip]

    with col_bed:
        bed_opts = sorted(df_zip["bedrooms"].unique().tolist())
        selected_bed = st.selectbox("Chambres", bed_opts, index=0)

    df_filtered_sel = df_zip[df_zip["bedrooms"] == selected_bed].copy()

    with col_prop:
        df_filtered_sel["label"] = (
            "ID " + df_filtered_sel["id"].astype(str)
            + "  —  $" + df_filtered_sel["price"].apply(lambda x: f"{x:,.0f}")
        )
        prop_label = st.selectbox("Propriété", df_filtered_sel["label"].tolist())

    prop = df_filtered_sel[df_filtered_sel["label"] == prop_label].iloc[0]

    st.markdown("---")

    # ── B. Fiche descriptive ──────────────────────────────────────────────────
    st.subheader("Fiche descriptive")
    fa, fb, fc, fd = st.columns(4)
    fa.metric("Prix de vente",    f"${prop['price']:,.0f}")
    fb.metric("Superficie",       f"{prop['sqft_living']:,.0f} pi²")
    fc.metric("Prix / pi²",       f"${prop['price_per_sqft']:.2f}")
    fd.metric("Grade / Condition", f"{int(prop['grade'])}/13 — {int(prop['condition'])}/5")

    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("Chambres",             int(prop["bedrooms"]))
    r2.metric("Salles de bain",        prop["bathrooms"])
    r3.metric("Année de construction", int(prop["yr_built"]))
    r4.metric("Rénovée",              "Oui" if prop["is_renovated"] else "Non")
    r5.metric("Front de mer",         "Oui" if prop["waterfront"] == 1 else "Non")

    st.markdown("---")

    # ── C. Recherche de comparables ───────────────────────────────────────────
    st.subheader("Comparables (comps)")

    sqft_lo = prop["sqft_living"] * 0.80
    sqft_hi = prop["sqft_living"] * 1.20

    comps = df_full[
        (df_full["zipcode"]   == prop["zipcode"])
        & (df_full["bedrooms"] == prop["bedrooms"])
        & (df_full["sqft_living"].between(sqft_lo, sqft_hi))
        & (df_full["id"]      != prop["id"])
    ].copy()

    # Tri par différence de superficie (les plus proches en premier)
    comps["sqft_diff"] = (comps["sqft_living"] - prop["sqft_living"]).abs()
    comps = comps.sort_values("sqft_diff").head(10)

    if comps.empty:
        st.warning("Aucun comparable trouvé avec ces critères exacts. "
                   "Élargissez le code postal ou le nombre de chambres.")
    else:
        mean_comp_price = comps["price"].mean()
        ecart           = prop["price"] - mean_comp_price
        ecart_pct       = ecart / mean_comp_price * 100

        # Statut surcote / décote
        if ecart_pct > 5:
            statut     = "Surcote"
            statut_txt = "surcotée"
            badge_col  = WARN
        elif ecart_pct < -5:
            statut     = "Décote"
            statut_txt = "décotée"
            badge_col  = PALETTE
        else:
            statut     = "Au prix du marché"
            statut_txt = "dans la moyenne du marché"
            badge_col  = ACCENT

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Comparables trouvés",      len(comps))
        mc2.metric("Prix moyen des comps",      f"${mean_comp_price:,.0f}")
        mc3.metric(
            "Écart vs marché local",
            f"{ecart_pct:+.1f}%",
            delta=f"${ecart:+,.0f}",
            delta_color="inverse",
        )
        st.markdown(
            f'<span style="background:{badge_col};color:white;padding:4px 12px;'
            f'border-radius:16px;font-size:0.9rem;font-weight:600;">'
            f'{statut}</span> — Cette propriété est <b>{statut_txt}</b> par rapport aux comparables locaux.',
            unsafe_allow_html=True,
        )

        # Tableau des comparables
        st.markdown("##### Propriétés comparables")
        display_cols = ["id", "price", "sqft_living", "price_per_sqft",
                        "bedrooms", "grade", "condition", "yr_built"]
        st.dataframe(
            comps[display_cols].rename(columns={
                "id": "ID", "price": "Prix ($)", "sqft_living": "Superficie (pi²)",
                "price_per_sqft": "$/pi²", "bedrooms": "Chambres",
                "grade": "Grade", "condition": "Condition", "yr_built": "Année",
            }).style.format({
                "Prix ($)": "${:,.0f}", "Superficie (pi²)": "{:,.0f}",
                "$/pi²": "${:.2f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")

        # ── D. Visualisation comparative ──────────────────────────────────────
        st.subheader("Comparaison visuelle")

        fig2, (axA, axB) = plt.subplots(1, 2, figsize=(14, 5))
        fig2.patch.set_facecolor(DARK_BG)
        _style_ax(axA)
        _style_ax(axB)

        # Graphique 1 : prix comparatifs (propriété vs comps)
        labels_bar  = [f"Comp {i+1}" for i in range(len(comps))] + ["Sélection"]
        prices_bar  = list(comps["price"].values / 1e3) + [prop["price"] / 1e3]
        colors_bar  = [PALETTE] * len(comps) + [ACCENT]
        bars2 = axA.bar(labels_bar, prices_bar, color=colors_bar, edgecolor=DARK_BG, width=0.6)
        axA.axhline(mean_comp_price / 1e3, color="#94A3B8", linewidth=1.5,
                    linestyle="--", label=f"Moy. comps {mean_comp_price/1e3:,.0f}k$")
        axA.set_title("Prix — Propriété vs Comparables", fontsize=12, fontweight="bold")
        axA.set_ylabel("Prix (k$)")
        axA.tick_params(axis="x", rotation=45, labelsize=8)
        # Annotation sur la barre sélectionnée
        last_bar = bars2[-1]
        axA.annotate(
            f"${prop['price']/1e3:,.0f}k",
            xy=(last_bar.get_x() + last_bar.get_width() / 2, last_bar.get_height()),
            xytext=(0, 6), textcoords="offset points",
            ha="center", color=ACCENT, fontsize=8, fontweight="bold",
        )
        patch_comp = mpatches.Patch(color=PALETTE, label="Comparables")
        patch_sel  = mpatches.Patch(color=ACCENT,  label="Propriété sélectionnée")
        axA.legend(handles=[patch_comp, patch_sel, axA.get_lines()[0]],
                   facecolor="#334155", labelcolor="#F1F5F9", fontsize=8)

        # Graphique 2 : Prix/pi² comparatifs
        ppsqft_bar  = list(comps["price_per_sqft"].values) + [prop["price_per_sqft"]]
        bars3 = axB.bar(labels_bar, ppsqft_bar, color=colors_bar, edgecolor=DARK_BG, width=0.6)
        mean_ppsqft = comps["price_per_sqft"].mean()
        axB.axhline(mean_ppsqft, color="#94A3B8", linewidth=1.5, linestyle="--",
                    label=f"Moy. comps {mean_ppsqft:.0f}$/pi²")
        axB.set_title("Prix/pi² — Propriété vs Comparables", fontsize=12, fontweight="bold")
        axB.set_ylabel("$/pi²")
        axB.tick_params(axis="x", rotation=45, labelsize=8)
        last_bar3 = bars3[-1]
        axB.annotate(
            f"${prop['price_per_sqft']:.0f}/pi²",
            xy=(last_bar3.get_x() + last_bar3.get_width() / 2, last_bar3.get_height()),
            xytext=(0, 6), textcoords="offset points",
            ha="center", color=ACCENT, fontsize=8, fontweight="bold",
        )
        axB.legend(facecolor="#334155", labelcolor="#F1F5F9", fontsize=8)

        plt.tight_layout(pad=2)
        st.pyplot(fig2)
        plt.close(fig2)

        st.markdown("---")

        # ── E. Recommandation LLM ─────────────────────────────────────────────
        st.subheader("Recommandation générée par IA")

        if st.button("Générer une recommandation", type="primary"):
            prompt2 = f"""Tu es un analyste immobilier senior. Évalue cette propriété pour un investisseur :

PROPRIÉTÉ ANALYSÉE :
- Prix : {prop['price']:,.0f} $
- Chambres : {int(prop['bedrooms'])} | Salles de bain : {prop['bathrooms']}
- Superficie : {prop['sqft_living']:,.0f} pi² | Terrain : {prop['sqft_lot']:,.0f} pi²
- Grade : {int(prop['grade'])}/13 | Condition : {int(prop['condition'])}/5
- Année de construction : {int(prop['yr_built'])} | Rénovée : {"Oui" if prop['is_renovated'] else "Non"}
- Front de mer : {"Oui" if prop['waterfront'] == 1 else "Non"} | Vue : {int(prop['view'])}/4
- Âge de la propriété : {int(prop['age'])} ans

ANALYSE COMPARATIVE :
- Nombre de comparables trouvés : {len(comps)}
- Prix moyen des comparables : {mean_comp_price:,.0f} $
- Écart vs comparables : {ecart:+,.0f} $ ({ecart_pct:+.1f}%)
- Statut : {statut_txt}

Rédige une recommandation d'investissement en 3-4 paragraphes.
Inclus : évaluation du prix, forces et faiblesses, verdict final
(Acheter / À surveiller / Éviter) avec justification.
Réponds en français, avec le ton d'un rapport d'analyste immobilier professionnel."""

            with st.spinner("Analyse en cours…"):
                rec = call_llm(prompt2, api_key)

            if rec:
                render_llm_box(rec)
            else:
                verdict = "Acheter" if ecart_pct < -5 else ("À surveiller" if ecart_pct <= 5 else "Éviter")
                render_llm_box(
                    f"""**Recommandation d'investissement — ID {int(prop['id'])}**

Cette propriété de **{int(prop['sqft_living']):,} pi²** ({int(prop['bedrooms'])} chambres, grade {int(prop['grade'])}/13) est proposée à **{prop['price']:,.0f} $**, soit **{ecart_pct:+.1f}%** par rapport à la moyenne de ses {len(comps)} comparables directs dans le zipcode {int(prop['zipcode'])}.

**Forces :** {"Décote avantageuse offrant une marge de sécurité à l'acquisition." if ecart_pct < 0 else "Bien positionné dans son marché local."} Grade {int(prop['grade'])}/13 {"supérieur" if prop['grade'] >= 8 else "dans la moyenne"}. {"Rénovée — risque d'entretien réduit." if prop["is_renovated"] else ""} {"Vue côté eau — premium rare." if prop["waterfront"] == 1 else ""}

**Faiblesses :** {"Surcote par rapport aux comparables — risque de négociation difficile." if ecart_pct > 5 else ""} Âge de {int(prop['age'])} ans {"— prévoir un plan de rénovation." if not prop["is_renovated"] and prop["age"] > 30 else "."}

**Verdict : {verdict}** — {"La décote par rapport au marché local offre une opportunité d'acquisition attractive." if ecart_pct < -5 else "La propriété est valorisée en ligne avec le marché, sans prime ni décote significative." if ecart_pct <= 5 else "La surcote par rapport aux comparables rend cet actif moins attractif à ce prix."}

*Note : Ajoutez une clé OpenAI dans la barre latérale pour une recommandation IA complète.*"""
                )

# ═════════════════════════════════════════════════════════════════════════════
# ONGLET 3 — Cartographie Interactive
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Onglet 3 — Cartographie":
    st.title("Onglet 3 — Cartographie Interactive")
    st.caption("Visualisez la distribution spatiale des ventes dans le comté de King.")
    
    if df.empty:
        st.warning("Aucune propriété ne correspond aux filtres actuels.")
    else:
        st.subheader("Carte des transactions immobilières")
        
        # Plotly Express Scatter Mapbox avec thème 'carto-darkmatter'
        fig_map = px.scatter_mapbox(
            df,
            lat="lat",
            lon="long",
            color="price",
            hover_name="id",
            hover_data={"price": ":$,.0f", "bedrooms": True, "bathrooms": True, "sqft_living": True, "lat": False, "long": False},
            color_continuous_scale=[DARK_BG, "#059669", "#10B981", "#F59E0B", "#EF4444"], # Dégradé clair
            zoom=9.5,
            center={"lat": 47.6, "lon": -122.2},
            mapbox_style="carto-darkmatter",
            height=800
        )
        
        # Décoration Premium & Clarté des points
        fig_map.update_traces(marker=dict(size=4.5, opacity=0.85))
        fig_map.update_layout(
            margin={"r":0, "t":0, "l":0, "b":0},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=TEXT,
        )
        
        # Ajout d'une démarcation claire autour de la carte
        st.markdown(
            f"<div style='border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; "
            f"overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.5); padding: 4px; "
            f"background: {GLASS}; margin-bottom: 20px;'>", 
            unsafe_allow_html=True
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.info("Utilisez la molette de votre souris ou les boutons sur la carte pour zoomer davantage au niveau des rues.")


# ═════════════════════════════════════════════════════════════════════════════
# ONGLET 4 — Simulateur de rendement
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Onglet 4 — Simulateur de rendement":
    st.title("Onglet 4 — Simulateur de financement")
    st.caption("Évaluez la viabilité de votre investissement immobilier.")
    
    col_sim_1, col_sim_2 = st.columns([1, 2])
    
    with col_sim_1:
        st.subheader("Paramètres du prêt")
        st.markdown(f"<div style='background:{GLASS}; padding:20px; border-radius:15px; border:1px solid rgba(255,255,255,0.1); margin-bottom:20px;'>", unsafe_allow_html=True)
        
        prix_defaut = int(df["price"].mean()) if not df.empty else 500000
        prix_achat = st.number_input("Prix d'achat ($)", min_value=10000, value=prix_defaut, step=10000)
        
        mise_de_fonds_pct = st.slider("Mise de fonds (%)", min_value=0, max_value=100, value=20, step=1)
        mise_de_fonds = prix_achat * (mise_de_fonds_pct / 100)
        
        st.write(f"Montant de la mise de fonds : **${mise_de_fonds:,.0f}**")
        
        montant_pret = prix_achat - mise_de_fonds
        
        taux_interet = st.number_input("Taux d'intérêt annuel (%)", min_value=0.1, max_value=20.0, value=5.5, step=0.1)
        duree_annees = st.selectbox("Durée du prêt (années)", [10, 15, 20, 25, 30], index=4)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_sim_2:
        st.subheader("Analyse financière")
        
        # Calcul de la mensualité / math.pow
        r = (taux_interet / 100) / 12  # Taux d'intérêt mensuel
        n = duree_annees * 12  # Nombre de paiements (mois)
        
        if r > 0:
            mensualite = montant_pret * (r * math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)
        else:
            mensualite = montant_pret / n
            
        total_paye = mensualite * n
        total_interets = total_paye - montant_pret
        
        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Paiement mensuel", f"${mensualite:,.0f}")
        metric2.metric("Total des intérêts", f"${total_interets:,.0f}")
        metric3.metric("Coût total d'acquisition", f"${(total_paye + mise_de_fonds):,.0f}")
        
        # Graphique Donut - Répartition
        labels = ["Principal remboursé", "Intérêts"]
        values = [montant_pret, total_interets]
        
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=labels, 
            autopct='%1.1f%%',
            startangle=90, 
            colors=[PALETTE, WARN],
            wedgeprops=dict(width=0.4, edgecolor='none'), # Change to Donut Chart
            textprops=dict(color=TEXT)
        )
        
        plt.setp(autotexts, size=10, weight="bold")
        ax.axis('equal')  
        ax.set_title("Répartition du coût total du prêt", color=TEXT)
        st.pyplot(fig)
        plt.close(fig)
