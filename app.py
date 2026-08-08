import os

from pathlib import Path
import sys
import pandas as pd
from nicegui import ui

# --- 1. CONFIGURATION DES CHEMINS ---
if len(sys.argv) > 2:
  json_path = Path(sys.argv[1])
  csv_path = Path(sys.argv[2])
else:
  json_path = Path(
      "/Users/dominiqueboulanger/Desktop/Appli_TCF/referentiel_tcf.json"
  )
  csv_path = Path("/Users/dominiqueboulanger/Desktop/Appli_TCF/tcf_data.csv")


# --- 2. FONCTION DE COULEUR DU TEXTE PAR NIVEAU ---
def get_level_text_color(niveau):
  if not niveau:
    return "text-gray-800 border-l-gray-300"
  niv = str(niveau).strip().upper()
  if "A1" in niv:
    return "text-blue-700 border-l-blue-500"
  elif "A2" in niv:
    return "text-cyan-700 border-l-cyan-500"
  elif "B1" in niv:
    return "text-emerald-700 border-l-emerald-500"
  elif "B2" in niv:
    return "text-amber-700 border-l-amber-500"
  elif "C1" in niv:
    return "text-purple-700 border-l-purple-500"
  elif "C2" in niv:
    return "text-rose-700 border-l-rose-500"
  else:
    return "text-gray-800 border-l-gray-300"


# --- 3. INTERFACE PRINCIPALE ---
def main_interface():
  if not csv_path.exists():
    ui.label(
        f"Erreur : Le fichier CSV est introuvable à l'emplacement :"
        f" {csv_path}"
    ).classes("text-red-500 font-bold")
    return

  try:
    df = pd.read_csv(csv_path, sep=";", encoding="utf-8")
  except Exception as e:
    ui.label(f"Erreur lors de la lecture du CSV : {e}").classes(
        "text-red-500 font-bold"
    )
    return

  df.columns = [c.strip().lower() for c in df.columns]

  if "descripteur" not in df.columns:
    ui.label("Colonne 'descripteur' introuvable dans le fichier CSV.").classes(
        "text-red-500"
    )
    return

  niveaux_disponibles = (
      sorted(df["niveau_cecrl"].dropna().unique().tolist())
      if "niveau_cecrl" in df.columns
      else []
  )

  state = {
      "selected_index": 0,
      "evaluations": {},
  }

  ui.label("Assistant d'Évaluation Orale - TCF").classes(
      "text-2xl font-bold text-primary mb-2"
  )

  header_refs = {}
  row_containers = []

  def update_header_and_styles(scroll_to_item=True):
    if not (0 <= state["selected_index"] < len(df)):
      return

    row_data = df.iloc[state["selected_index"]]
    c_niv = str(row_data.get("niveau_cecrl", "-"))
    c_tach = str(row_data.get("tache", "-"))
    c_comp = str(row_data.get("competence", "-"))

    if "niveau_label" in header_refs:
      header_refs["niveau_label"].text = f"Niveau : {c_niv}"
    if "tache_label" in header_refs:
      header_refs["tache_label"].text = f"Tâche : {c_tach}"
    if "comp_label" in header_refs:
      header_refs["comp_label"].text = f"Compétence : {c_comp}"

    for i, container in enumerate(row_containers):
      if i == state["selected_index"]:
        container.classes(
            remove="bg-white border-gray-200",
            add="bg-blue-50 border-blue-400 shadow-sm",
        )
        # Défilement direct et précis vers l'élément sélectionné
        if scroll_to_item:
          container.run_method(
              "scrollIntoView", {"behavior": "smooth", "block": "center"}
          )
      else:
        container.classes(
            remove="bg-blue-50 border-blue-400 shadow-sm",
            add="bg-white border-gray-200",
        )

  # --- BARRE DE SAUT / NAVIGATION RAPIDE PAR NIVEAU ---
  with ui.card().classes(
      "w-full p-3 mb-2 bg-gray-50 border border-gray-200 shadow-xs"
  ):
    with ui.row().classes("w-full items-center justify-between gap-2"):
      ui.label("Sauter au 1er descripteur du niveau :").classes(
          "text-sm font-semibold text-gray-700"
      )

      def on_jump_niveau(e):
        nouveau_niveau = e.value
        if nouveau_niveau:
          match = df[
              df["niveau_cecrl"]
              .astype(str)
              .str.strip()
              .str.upper()
              == str(nouveau_niveau).strip().upper()
          ]
          if not match.empty:
            state["selected_index"] = match.index[0]
            update_header_and_styles(scroll_to_item=True)
            jump_select.value = None

      jump_select = (
          ui.select(
              options=niveaux_disponibles,
              value=None,
          )
          .classes("bg-white rounded min-w-[120px]")
          .props('dense outlined label="Choisir..."')
          .on_value_change(on_jump_niveau)
      )

  # --- EN-TÊTE FIXE ---
  with ui.card().classes(
      "w-full p-4 mb-3 bg-blue-50 border border-blue-200 shadow-sm"
  ):
    with ui.row().classes(
        "w-full items-center justify-between gap-4 flex-wrap"
    ):
      row_data_init = df.iloc[state["selected_index"]]
      init_niv = str(row_data_init.get("niveau_cecrl", "-"))
      init_tach = str(row_data_init.get("tache", "-"))
      init_comp = str(row_data_init.get("competence", "-"))

      header_refs["niveau_label"] = ui.label(f"Niveau : {init_niv}").classes(
          "flex-1 min-w-[120px] px-3 py-2 bg-white rounded border text-blue-900"
          " font-medium text-center shadow-xs"
      )

      header_refs["tache_label"] = ui.label(f"Tâche : {init_tach}").classes(
          "flex-1 min-w-[130px] px-3 py-2 bg-white rounded border text-blue-900"
          " font-medium text-center shadow-xs"
      )

      header_refs["comp_label"] = ui.label(
          f"Compétence : {init_comp}"
      ).classes(
          "flex-1 min-w-[150px] px-3 py-2 bg-white rounded border text-blue-900"
          " font-medium text-center shadow-xs"
      )

  # --- LISTE DES DESCRIPTEURS ---
  with ui.card().classes("w-full p-4 shadow-md"):
    ui.label(f"Référentiel complet ({len(df)} descripteurs)").classes(
        "font-bold text-lg mb-2"
    )

    with ui.scroll_area().classes("w-full h-[64vh] pr-2"):
      for idx, row in df.iterrows():
        desc = row.get("descripteur", "Description indisponible")
        exemple = row.get("exemple", "")
        niveau = row.get("niveau_cecrl", "")

        color_class = get_level_text_color(niveau)
        is_selected = idx == 0
        bg_style = (
            "bg-blue-50 border-blue-400 shadow-sm"
            if is_selected
            else "bg-white border-gray-200"
        )

        def make_click_handler(i):
          def handler():
            state["selected_index"] = i
            update_header_and_styles(scroll_to_item=False)

          return handler

        with ui.row().classes(
            f"w-full items-center justify-between border-b border-l-4"
            f" {color_class.split()[1]} py-3 pl-3 pr-2 my-1 rounded-r cursor-pointer"
            f" {bg_style}"
        ).on("click", make_click_handler(idx)) as row_elem:

          row_containers.append(row_elem)

          with ui.column().classes("flex-1 gap-0.5 pr-2"):
            ui.label(str(desc)).classes(
                f"text-base font-medium {color_class.split()[0]}"
            )
            if pd.notna(exemple) and str(exemple).strip() != "":
              ui.label(f"Exemple : {exemple}").classes(
                  "text-xs italic text-gray-400 mt-0.5"
              )

          def make_eval_handler(i):
            return lambda e: state["evaluations"].update({i: e.value})

          with ui.row().classes("items-center gap-2 shrink-0").on(
              "click.stop.prevent", lambda: None
          ):
            ui.radio(
                options=["-", "=", "+"],
                value=state["evaluations"].get(idx, None),
            ).props("inline dense").classes("text-sm").on_value_change(
                make_eval_handler(idx)
            )


main_interface()

# --- 4. CONFIGURATION ET LANCEMENT SERVEUR ---
ui.run(
    title="TCF Oral Examiner",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8080)),
    reload=False,
    reconnect_timeout=30,
    show=False,
    storage_secret="tcf_secret_key",
)
