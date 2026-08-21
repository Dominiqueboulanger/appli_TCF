from collections import Counter
from nicegui import ui


class CarouselEvaluationTCF:

  def __init__(self):
    self.criteres = [
        {
            "titre": "Débit",
            "paliers": [
                ("A1", "lent"),
                ("A2", "pause + hésitation"),
                ("B1", "influence langue maternelle"),
                ("B2", "longtemps"),
                ("C1", "sans effort"),
                ("C2", "sans effort"),
            ],
        },
        {
            "titre": "Prononciation",
            "paliers": [
                ("A1", "des efforts"),
                ("A2", ""),
                ("B1", ""),
                ("B2", "élision, langage oral, sans tension"),
                ("C1", ""),
                ("C2", ""),
            ],
        },
        {
            "titre": "Lexique",
            "paliers": [
                ("A1", "mots isolés élémentaire"),
                ("A2", "limité"),
                ("B1", "suffisant"),
                ("B2", "périphrases"),
                ("C1", "fine nuance"),
                ("C2", "vaste"),
            ],
        },
        {
            "titre": "Conjugaison",
            "paliers": [
                ("A1", "présent"),
                ("A2", "passé composé + imparfait"),
                ("B1", "futur + conditionnel + plus que parfait"),
                ("B2", ""),
                ("C1", "futur antérieur + subjonctif"),
                ("C2", "parfaite"),
            ],
        },
        {
            "titre": "Syntaxe",
            "paliers": [
                ("A1", ""),
                ("A2", ""),
                ("B1", ""),
                ("B2", "+"),
                ("C1", "++"),
                ("C2", ""),
            ],
        },
        {
            "titre": "Connecteurs",
            "paliers": [
                ("A1", "et, alors"),
                ("A2", "et, mais, parce que, après"),
                ("B1", "que"),
                ("B2", "premièrement, donc qui"),
                (
                    "C1",
                    (
                        "cependant, et puis, afin que, dès que, Si, en résumé,"
                        " a mon avis, comme, bien que"
                    ),
                ),
                ("C2", ""),
            ],
        },
        {
            "titre": "Sociolinguistique",
            "paliers": [
                ("A1", ""),
                ("A2", "ne conduit pas la conversation"),
                ("B1", ""),
                ("B2", "peut garder la parole"),
                ("C1", ""),
                ("C2", ""),
            ],
        },
        {
            "titre": "Questionnement",
            "paliers": [
                ("A1", "tu habites où, c'est combien ?"),
                ("A2", "qu'est ce que, est-ce que, comment ?"),
                ("B1", "Pourquoi, si, quel?"),
                ("B2", "pourquoi, quels sont les risques"),
                ("C1", "jusqu'où"),
                (
                    "C2",
                    (
                        "Quels sont les critères ? morale ou légale ? Le devoir"
                        " de secours est-il une obligation"
                    ),
                ),
            ],
        },
    ]

    self.selections = {}
    self.init_ui()

  def init_ui(self):
    with ui.column().classes("w-full min-h-screen bg-slate-100 p-6 items-center"):
      with ui.row().classes(
          "w-full max-w-5xl justify-between items-center mb-4"
      ):
        with ui.column().classes("gap-0"):
          ui.label(
              "Évaluation Orale TCF — Grille et Bilan Global"
          ).classes("text-2xl font-extrabold text-slate-800")
          ui.label(
              "Renseignez les critères et consultez la synthèse finale ci-dessous"
          ).classes("text-sm text-slate-500")

      # --- CARROUSEL HORIZONTAL DES CRITÈRES ---
      with ui.row().classes(
          "w-full max-w-7xl overflow-x-auto flex-nowrap gap-6 p-4 items-stretch"
          " no-scrollbar"
      ):
        for idx, critere in enumerate(self.criteres):
          self.creer_carte_critere(idx, critere)

      # --- PANNEAU D'ÉVALUATION FINALE (SYNTHÈSE) ---
      with ui.card().classes(
          "w-full max-w-5xl p-6 bg-white shadow-md border border-slate-200"
          " rounded-2xl mt-6 flex flex-col gap-4"
      ):
        ui.label("Synthèse & Évaluation Finale du Candidat").classes(
            "text-lg font-bold text-slate-800 border-b pb-2"
        )

        with ui.row().classes("w-full justify-between items-center gap-4"):
          with ui.column().classes("flex-grow"):
            ui.label(
                "Tendance suggérée par les critères :"
            ).classes("text-xs text-slate-400 font-bold uppercase")
            self.lbl_tendance = ui.label(
                "En attente d'évaluations..."
            ).classes("text-sm font-semibold text-blue-700")

          with ui.row().classes("items-center gap-2"):
            ui.label("Niveau Global Attribué :").classes(
                "text-sm font-bold text-slate-700"
            )
            self.select_niveau_global = ui.select(
                options=["A1", "A2", "B1", "B2", "C1", "C2"],
                value="B1",
                label="Niveau",
            ).props("dense outlined").classes("w-28")

        self.textarea_synthese = (
            ui.textarea(
                placeholder=(
                    "Ajoutez ici votre appréciation globale ou justification"
                    " pour le jury..."
                )
            )
            .props("outlined dense")
            .classes("w-full text-xs bg-slate-50")
        )

        ui.button(
            "Valider et archiver l'évaluation", on_click=self.valider_evaluation
        ).classes("bg-blue-600 text-white font-bold self-end px-4 py-2 rounded")

  def creer_carte_critere(self, idx, critere):
    with ui.card().classes(
        "flex-shrink-0 w-80 p-5 bg-white shadow-md border border-slate-200"
        " rounded-2xl flex flex-col justify-between hover:shadow-lg"
        " transition-shadow"
    ):
      with ui.column().classes("w-full gap-3"):
        ui.label(critere["titre"]).classes(
            "text-lg font-bold text-slate-700 border-b pb-2 border-slate-100"
        )

        lbl_choix = ui.label("Non noté").classes(
            "text-xs font-medium text-amber-600 bg-amber-50 px-2 py-1 rounded"
            " w-fit"
        )
        setattr(self, f"lbl_choix_{idx}", lbl_choix)

        with ui.column().classes("w-full gap-2.5 mt-2"):
          for p_idx, (niveau, desc) in enumerate(critere["paliers"]):
            self.creer_ligne_epuree(idx, p_idx, critere, niveau, desc)

  def creer_ligne_epuree(self, crit_idx, pal_idx, critere, niveau, description):
    classes_couleurs = {
        "A1": "bg-sky-100 text-sky-800 hover:bg-sky-200",
        "A2": "bg-blue-200 text-blue-900 hover:bg-blue-300",
        "B1": "bg-blue-400 text-white hover:bg-blue-500",
        "B2": "bg-blue-600 text-white hover:bg-blue-700",
        "C1": "bg-blue-800 text-white hover:bg-blue-900",
        "C2": "bg-slate-900 text-white hover:bg-black",
    }
    style_badge = classes_couleurs.get(
        niveau, "bg-blue-100 text-blue-800 hover:bg-blue-200"
    )

    with ui.row().classes(
        "w-full p-2 bg-slate-50 rounded-lg items-center gap-2 border"
        " border-slate-100"
    ):

      async def clic_selectionner():
        self.selections[critere["titre"]] = niveau

        lbl = getattr(self, f"lbl_choix_{crit_idx}")
        lbl.text = f"Niveau {niveau}"
        lbl.classes(
            replace=(
                "text-xs font-bold text-white bg-blue-600 px-2 py-1 rounded w-fit"
            )
        )

        self.mettre_a_jour_tendance()
        ui.notify(
            f"{critere['titre']} validé à {niveau}",
            color="positive",
            position="top",
        )

      ui.button(niveau, on_click=clic_selectionner).props(
          "flat dense"
      ).classes(
          f"text-xs font-extrabold px-2 py-1 rounded transition-colors"
          f" {style_badge}"
      ).tooltip(
          f"Cliquer pour valider le niveau {niveau}"
      )

      input_desc = (
          ui.textarea(value=description)
          .props("autogrow dense borderless")
          .classes("text-xs text-slate-700 flex-grow bg-white px-2 py-1 rounded")
      )

      def mettre_a_jour_texte(e):
        critere["paliers"][pal_idx] = (niveau, e.value)

      input_desc.on("update:model-value", mettre_a_jour_texte)

  def mettre_a_jour_tendance(self):
    if not self.selections:
      self.lbl_tendance.text = "En attente d'évaluations..."
      return

    niveaux_notes = list(self.selections.values())
    compte = Counter(niveaux_notes)
    niveau_frequent, occurrence = compte.most_common(1)[0]

    recap_str = " | ".join([f"{k}: {v}" for k, v in self.selections.items()])
    self.lbl_tendance.text = (
        f"Tendance majoritaire : {niveau_frequent} ({occurrence}"
        f" critère(s)) — Détails : [{recap_str}]"
    )
    self.select_niveau_global.value = niveau_frequent

  def valider_evaluation(self):
    niveau_final = self.select_niveau_global.value
    # Notification simple sans l'argument 'type="ongoing"' pour éviter l'animation en boucle
    ui.notify(
        f"Évaluation enregistrée avec succès ! Niveau global : {niveau_final}",
        color="positive",
    )


@ui.page("/")
def main_page():
  CarouselEvaluationTCF()


ui.run(port=8080, reload=False)
