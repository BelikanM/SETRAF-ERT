#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

with open('ERTest.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Liste des blocs Paragraph problématiques trouvés
problem_lines = [4056, 4093, 4101, 4113, 4172, 4208, 4216, 4224, 4234, 4243]

fixes = {
    # Ligne 4056 - Résumé exécutif
    (4055, 4062): '''                                    story.append(Paragraph(f"Ce rapport présente les résultats d'une investigation géophysique par tomographie "
                                                          f"de résistivité électrique (ERT) réalisée avec la méthode pyGIMLi. L'étude a porté "
                                                          f"sur {len(survey_points)} points de sondage avec {len(freq_columns)} fréquences de mesure, "
                                                          f"permettant d'analyser le sous-sol jusqu'à {depth_max:.1f} mètres de profondeur.", 
                                                          normal_style))
''',
    
    # Ligne 4093 - Acquisition données
    (4092, 4099): '''                                    story.append(Paragraph(f"<b>2.1 Acquisition des données</b><br/>"
                                                          f"Les mesures de résistivité ont été effectuées avec un dispositif multi-fréquence "
                                                          f"permettant d'obtenir {len(df_pygimli)} mesures réparties sur {len(survey_points)} points. "
                                                          f"Les fréquences varient de {freq_columns[0].replace('freq_', '')} MHz à {freq_columns[-1].replace('freq_', '')} MHz.", 
                                                          normal_style))
''',
    
    # Ligne 4101 - Traitement inversion
    (4100, 4108): '''                                    story.append(Paragraph(f"<b>2.2 Traitement et inversion</b><br/>"
                                                          f"L'inversion des données a été réalisée avec pyGIMLi (Python Geophysical Inversion and Modeling Library). "
                                                          f"Configuration utilisée : schéma <b>{scheme_type.upper()}</b> avec {n_electrodes} électrodes "
                                                          f"espacées de {spacing:.1f} mètres. Le maillage 2D comprend {n_electrodes} × {n_depth_points} points. "
                                                          f"Paramètres d'inversion : λ = 20 (régularisation), {ert_manager.inv.iterations()} itérations, "
                                                          f"RMS error final = {ert_manager.inv.relrms():.3f}.", 
                                                          normal_style))
''',
    
    # Ligne 4113 - Classification hydrogéologique
    (4112, 4116): '''                                    story.append(Paragraph("L'analyse des résistivités mesurées permet d'identifier 4 types d'eau distincts "
                                                          "selon les valeurs de résistivité apparente :", 
                                                          normal_style))
''',
    
    # Ligne 4172 - Modèle lithologique
    (4171, 4175): '''                                    story.append(Paragraph("<b>4.1 Modèle lithologique</b><br/>"
                                                          "L'analyse des résistivités inversées permet de proposer le modèle lithologique suivant :", 
                                                          normal_style))
''',
    
    # Ligne 4208 - Zones favorables
    (4207, 4213): '''                                    story.append(Paragraph("<b>5.1 Zones favorables</b><br/>"
                                                          "Les zones avec résistivités comprises entre <b>50 et 200 Ω·m</b> (sables et graviers) "
                                                          "constituent les cibles prioritaires pour l'implantation de forages d'eau. Ces formations "
                                                          "présentent une bonne perméabilité et un potentiel aquifère élevé.", 
                                                          normal_style))
''',
    
    # Ligne 4216 - Zones à éviter
    (4215, 4221): '''                                    story.append(Paragraph("<b>5.2 Zones à éviter</b><br/>"
                                                          "- <b>Résistivités < 1 Ω·m</b> : Intrusion d'eau salée, risque de contamination<br/>"
                                                          "- <b>Résistivités 1-20 Ω·m</b> : Argiles imperméables, faible productivité<br/>"
                                                          "- <b>Résistivités > 500 Ω·m</b> : Roches compactes, difficulté de forage", 
                                                          normal_style))
''',
    
    # Ligne 4224 - Profondeur optimale
    (4223, 4229): '''                                    story.append(Paragraph("<b>5.3 Profondeur optimale</b><br/>"
                                                          "Selon l'analyse des données, la profondeur optimale pour les forages se situe "
                                                          "dans la plage où les résistivités sont comprises entre 50 et 100 Ω·m, "
                                                          "correspondant généralement aux formations sableuses saturées d'eau douce.", 
                                                          normal_style))
''',
    
    # Ligne 4234 - Conclusions 1
    (4233, 4240): '''                                    story.append(Paragraph(f"L'investigation géophysique par tomographie de résistivité électrique a permis "
                                                          f"de caractériser le sous-sol sur {len(survey_points)} points de mesure jusqu'à "
                                                          f"{depth_max:.1f} mètres de profondeur. Les résultats de l'inversion pyGIMLi "
                                                          f"(RMS error = {ert_manager.inv.relrms():.3f}) montrent une bonne convergence et "
                                                          f"permettent d'établir un modèle hydrogéologique fiable.", 
                                                          normal_style))
''',
    
    # Ligne 4243 - Conclusions 2
    (4242, 4247): '''                                    story.append(Paragraph("La classification hydrogéologique révèle la présence de plusieurs types d'eau "
                                                          "et formations géologiques. Les aquifères d'eau douce exploitables ont été "
                                                          "identifiés et localisés, permettant d'optimiser l'implantation des futurs forages.", 
                                                          normal_style))
''',
}

# Appliquer les corrections dans l'ordre inverse
for (start, end), replacement in sorted(fixes.items(), reverse=True):
    lines[start:end] = [replacement]
    print(f"✅ Corrigé lignes {start+1}-{end}")

with open('ERTest.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\n✅ Total: {len(fixes)} blocs Paragraph corrigés")
