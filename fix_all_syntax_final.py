#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger TOUS les blocs st.markdown et Paragraph avec triple quotes
qui ont une mauvaise indentation causant des SyntaxError
"""

with open('ERTest.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Liste de TOUS les remplacements à effectuer (ordre important: de la fin vers le début)
replacements = [
    # SIDEBAR (fin du fichier)
    (
        '''st.sidebar.markdown("""
**SETRAF - Subaquifère ERT Analysis**  
💧 Outil d'analyse géophysique avancé  
Expert en hydrogéologie et tomographie électrique

**Version Optimisée – 08 Novembre 2025**  
✅ Calculateur Ts intelligent (Ravensgate Sonic)  
✅ Analyse .dat + détection anomalies (K-Means avec cache)  
✅ Tableau résistivité eau (descriptions détaillées)  
✅ Pseudo-sections 2D/3D basées sur vos données réelles  
✅ **NOUVEAU** : Stratigraphie complète (sols + eaux + roches + minéraux)  
✅ **NOUVEAU** : Visualisation 3D interactive des matériaux par couches  
✅ **NOUVEAU** : Précision millimétrique (3 décimales sur tous les axes)  
✅ **NOUVEAU** : Inversion pyGIMLi - ERT géophysique avancée  
✅ Interprétation multi-matériaux : 8 catégories géologiques  
✅ Performance optimisée avec @st.cache_data  
✅ Interpolation cubique cachée pour fluidité  
✅ Ticks basés sur mesures réelles (0.1, 0.2, 0.3...)  
✅ **Export PDF** : Rapports complets avec tous les graphiques

**Exports disponibles** :  
📥 CSV - Données brutes  
📊 Excel - Tableaux formatés  
📄 PDF Standard - Rapport d'analyse DTW (150 DPI)  
📄 PDF Stratigraphique - Classification géologique complète (150 DPI)

**Visualisations avancées** :  
🎨 Coupes 2D par type de matériau (8 plages de résistivité)  
🌐 Modèle 3D interactif (rotation 360°, zoom)  
📊 Histogrammes et profils de distribution  
🗺️ Cartographie spatiale des formations géologiques  
🔬 Inversion pyGIMLi avec classification hydrogéologique

**Catégories géologiques identifiées** :  
💧 Eaux (mer, salée, douce, pure)  
🧱 Argiles & sols saturés  
🏖️ Sables & graviers  
🪨 Roches sédimentaires (calcaire, grès, schiste)  
🌋 Roches ignées & métamorphiques (granite, basalte)  
💎 Minéraux & minerais (graphite, cuivre, or, quartz)

**Plages de résistivité** :  
- 0.001-1 Ω·m : Minéraux métalliques  
- 0.1-10 Ω·m : Eaux salées + argiles marines  
- 10-100 Ω·m : Eaux douces + sols fins  
- 100-1000 Ω·m : Sables saturés + graviers  
- 1000-10000 Ω·m : Roches sédimentaires  
- >10000 Ω·m : Socle cristallin (granite, quartzite)  

**🔬 Module pyGIMLi intégré** :  
- Inversion ERT complète avec algorithmes optimisés  
- Configurations Wenner, Schlumberger, Dipole-Dipole  
- Classification hydrogéologique automatique  
- Visualisation avec palette de couleurs physiques  
""")''',
        '''st.sidebar.markdown("**SETRAF - Subaquifère ERT Analysis**  \\n"
                    "💧 Outil d'analyse géophysique avancé  \\n"
                    "Expert en hydrogéologie et tomographie électrique\\n\\n"
                    "**Version Optimisée – 08 Novembre 2025**  \\n"
                    "✅ Calculateur Ts intelligent (Ravensgate Sonic)  \\n"
                    "✅ Analyse .dat + détection anomalies (K-Means avec cache)  \\n"
                    "✅ Tableau résistivité eau (descriptions détaillées)  \\n"
                    "✅ Pseudo-sections 2D/3D basées sur vos données réelles  \\n"
                    "✅ **NOUVEAU** : Stratigraphie complète (sols + eaux + roches + minéraux)  \\n"
                    "✅ **NOUVEAU** : Visualisation 3D interactive des matériaux par couches  \\n"
                    "✅ **NOUVEAU** : Précision millimétrique (3 décimales sur tous les axes)  \\n"
                    "✅ **NOUVEAU** : Inversion pyGIMLi - ERT géophysique avancée  \\n"
                    "✅ Interprétation multi-matériaux : 8 catégories géologiques  \\n"
                    "✅ Performance optimisée avec @st.cache_data  \\n"
                    "✅ Interpolation cubique cachée pour fluidité  \\n"
                    "✅ Ticks basés sur mesures réelles (0.1, 0.2, 0.3...)  \\n"
                    "✅ **Export PDF** : Rapports complets avec tous les graphiques\\n\\n"
                    "**Exports disponibles** :  \\n"
                    "📥 CSV - Données brutes  \\n"
                    "📊 Excel - Tableaux formatés  \\n"
                    "📄 PDF Standard - Rapport d'analyse DTW (150 DPI)  \\n"
                    "📄 PDF Stratigraphique - Classification géologique complète (150 DPI)\\n\\n"
                    "**Visualisations avancées** :  \\n"
                    "🎨 Coupes 2D par type de matériau (8 plages de résistivité)  \\n"
                    "🌐 Modèle 3D interactif (rotation 360°, zoom)  \\n"
                    "📊 Histogrammes et profils de distribution  \\n"
                    "🗺️ Cartographie spatiale des formations géologiques  \\n"
                    "🔬 Inversion pyGIMLi avec classification hydrogéologique\\n\\n"
                    "**Catégories géologiques identifiées** :  \\n"
                    "💧 Eaux (mer, salée, douce, pure)  \\n"
                    "🧱 Argiles & sols saturés  \\n"
                    "🏖️ Sables & graviers  \\n"
                    "🪨 Roches sédimentaires (calcaire, grès, schiste)  \\n"
                    "🌋 Roches ignées & métamorphiques (granite, basalte)  \\n"
                    "💎 Minéraux & minerais (graphite, cuivre, or, quartz)\\n\\n"
                    "**Plages de résistivité** :  \\n"
                    "- 0.001-1 Ω·m : Minéraux métalliques  \\n"
                    "- 0.1-10 Ω·m : Eaux salées + argiles marines  \\n"
                    "- 10-100 Ω·m : Eaux douces + sols fins  \\n"
                    "- 100-1000 Ω·m : Sables saturés + graviers  \\n"
                    "- 1000-10000 Ω·m : Roches sédimentaires  \\n"
                    "- >10000 Ω·m : Socle cristallin (granite, quartzite)  \\n\\n"
                    "**🔬 Module pyGIMLi intégré** :  \\n"
                    "- Inversion ERT complète avec algorithmes optimisés  \\n"
                    "- Configurations Wenner, Schlumberger, Dipole-Dipole  \\n"
                    "- Classification hydrogéologique automatique  \\n"
                    "- Visualisation avec palette de couleurs physiques")'''
    ),
    
    # Format fichier freq.dat
    (
        '''        st.markdown("""
        **Format attendu du fichier freq.dat :**
        ```
        Projet,Point,Freq1,Freq2,Freq3,...
        Projet Archange Ondimba 2,1,0.119,0.122,0.116,...
        Projet Archange Ondimba 2,2,0.161,0.163,0.164,...
        ...
        ```
        
        **Structure :**
        - Colonne 1 : Nom du projet
        - Colonne 2 : Numéro du point de sondage
        - Colonnes 3+ : Valeurs de résistivité pour chaque fréquence (MHz)
        
        **Note :** Les fréquences sont automatiquement converties en profondeurs pour l'analyse ERT
        
        **Interprétation des couleurs (selon classification standard) :**
        - 🔴 **Rouge vif / Orange** : Eau de mer (0.1 - 1 Ω·m)
        - 🟡 **Jaune / Orange** : Eau salée nappe (1 - 10 Ω·m)
        - 🟢 **Vert / Bleu clair** : Eau douce (10 - 100 Ω·m)
        - 🔵 **Bleu foncé** : Eau très pure (> 100 Ω·m)
        """)''',
        '''        st.markdown("**Format attendu du fichier freq.dat :**\\n"
                    "```\\n"
                    "Projet,Point,Freq1,Freq2,Freq3,...\\n"
                    "Projet Archange Ondimba 2,1,0.119,0.122,0.116,...\\n"
                    "Projet Archange Ondimba 2,2,0.161,0.163,0.164,...\\n"
                    "...\\n"
                    "```\\n\\n"
                    "**Structure :**\\n"
                    "- Colonne 1 : Nom du projet\\n"
                    "- Colonne 2 : Numéro du point de sondage\\n"
                    "- Colonnes 3+ : Valeurs de résistivité pour chaque fréquence (MHz)\\n\\n"
                    "**Note :** Les fréquences sont automatiquement converties en profondeurs pour l'analyse ERT\\n\\n"
                    "**Interprétation des couleurs (selon classification standard) :**\\n"
                    "- 🔴 **Rouge vif / Orange** : Eau de mer (0.1 - 1 Ω·m)\\n"
                    "- 🟡 **Jaune / Orange** : Eau salée nappe (1 - 10 Ω·m)\\n"
                    "- 🟢 **Vert / Bleu clair** : Eau douce (10 - 100 Ω·m)\\n"
                    "- 🔵 **Bleu foncé** : Eau très pure (> 100 Ω·m)")'''
    ),
    
    # st.success pyGIMLi
    (
        '''                        st.success(f"""
                        ✅ **Inversion pyGIMLi terminée avec succès !**
                        - Configuration : {scheme_type} avec {n_electrodes} électrodes
                        - Erreur RMS : {ert_manager.inv.relrms():.3f}
                        - {len(interp_df)} niveaux de profondeur analysés
                        - {len(df_pygimli)} mesures réelles intégrées
                        - Classification hydrogéologique complète
                        """)''',
        '''                        st.success(f"✅ **Inversion pyGIMLi terminée avec succès !**\\n"
                                   f"- Configuration : {scheme_type} avec {n_electrodes} électrodes\\n"
                                   f"- Erreur RMS : {ert_manager.inv.relrms():.3f}\\n"
                                   f"- {len(interp_df)} niveaux de profondeur analysés\\n"
                                   f"- {len(df_pygimli)} mesures réelles intégrées\\n"
                                   f"- Classification hydrogéologique complète")'''
    ),
    
    # Paragraph Points clés
    (
        '''                                    story.append(Paragraph("""
                                    <b>Points clés :</b><br/>
                                    • Classification en 4 types d'eau (mer, salée, douce, pure)<br/>
                                    • Modèle lithologique 9 formations<br/>
                                    • Identification des zones aquifères favorables<br/>
                                    • Recommandations précises pour implantation de forages
                                    """, normal_style))''',
        '''                                    story.append(Paragraph("<b>Points clés :</b><br/>"
                                                          "• Classification en 4 types d'eau (mer, salée, douce, pure)<br/>"
                                                          "• Modèle lithologique 9 formations<br/>"
                                                          "• Identification des zones aquifères favorables<br/>"
                                                          "• Recommandations précises pour implantation de forages", 
                                                          normal_style))'''
    ),
    
    # Paragraph Conclusions 2
    (
        '''                                    story.append(Paragraph("""
                                    La classification hydrogéologique révèle la présence de plusieurs types d'eau 
                                    et formations géologiques. Les aquifères d'eau douce exploitables ont été 
                                    identifiés et localisés, permettant d'optimiser l'implantation des futurs forages.
                                    """, normal_style))''',
        '''                                    story.append(Paragraph("La classification hydrogéologique révèle la présence de plusieurs types d'eau "
                                                          "et formations géologiques. Les aquifères d'eau douce exploitables ont été "
                                                          "identifiés et localisés, permettant d'optimiser l'implantation des futurs forages.", 
                                                          normal_style))'''
    ),
    
    # Paragraph Conclusions 1
    (
        '''                                    story.append(Paragraph(f"""
                                    L'investigation géophysique par tomographie de résistivité électrique a permis 
                                    de caractériser le sous-sol sur {len(survey_points)} points de mesure jusqu'à 
                                    {depth_max:.1f} mètres de profondeur. Les résultats de l'inversion pyGIMLi 
                                    (RMS error = {ert_manager.inv.relrms():.3f}) montrent une bonne convergence et 
                                    permettent d'établir un modèle hydrogéologique fiable.
                                    """, normal_style))''',
        '''                                    story.append(Paragraph(f"L'investigation géophysique par tomographie de résistivité électrique a permis "
                                                          f"de caractériser le sous-sol sur {len(survey_points)} points de mesure jusqu'à "
                                                          f"{depth_max:.1f} mètres de profondeur. Les résultats de l'inversion pyGIMLi "
                                                          f"(RMS error = {ert_manager.inv.relrms():.3f}) montrent une bonne convergence et "
                                                          f"permettent d'établir un modèle hydrogéologique fiable.", 
                                                          normal_style))'''
    ),
    
    # Paragraph Profondeur optimale
    (
        '''                                    story.append(Paragraph("""
                                    <b>5.3 Profondeur optimale</b><br/>
                                    Selon l'analyse des données, la profondeur optimale pour les forages se situe 
                                    dans la plage où les résistivités sont comprises entre 50 et 100 Ω·m, 
                                    correspondant généralement aux formations sableuses saturées d'eau douce.
                                    """, normal_style))''',
        '''                                    story.append(Paragraph("<b>5.3 Profondeur optimale</b><br/>"
                                                          "Selon l'analyse des données, la profondeur optimale pour les forages se situe "
                                                          "dans la plage où les résistivités sont comprises entre 50 et 100 Ω·m, "
                                                          "correspondant généralement aux formations sableuses saturées d'eau douce.", 
                                                          normal_style))'''
    ),
    
    # Paragraph Zones à éviter
    (
        '''                                    story.append(Paragraph("""
                                    <b>5.2 Zones à éviter</b><br/>
                                    - <b>Résistivités < 1 Ω·m</b> : Intrusion d'eau salée, risque de contamination<br/>
                                    - <b>Résistivités 1-20 Ω·m</b> : Argiles imperméables, faible productivité<br/>
                                    - <b>Résistivités > 500 Ω·m</b> : Roches compactes, difficulté de forage
                                    """, normal_style))''',
        '''                                    story.append(Paragraph("<b>5.2 Zones à éviter</b><br/>"
                                                          "- <b>Résistivités < 1 Ω·m</b> : Intrusion d'eau salée, risque de contamination<br/>"
                                                          "- <b>Résistivités 1-20 Ω·m</b> : Argiles imperméables, faible productivité<br/>"
                                                          "- <b>Résistivités > 500 Ω·m</b> : Roches compactes, difficulté de forage", 
                                                          normal_style))'''
    ),
    
    # Paragraph Zones favorables
    (
        '''                                    story.append(Paragraph("""
                                    <b>5.1 Zones favorables</b><br/>
                                    Les zones avec résistivités comprises entre <b>50 et 200 Ω·m</b> (sables et graviers) 
                                    constituent les cibles prioritaires pour l'implantation de forages d'eau. Ces formations 
                                    présentent une bonne perméabilité et un potentiel aquifère élevé.
                                    """, normal_style))''',
        '''                                    story.append(Paragraph("<b>5.1 Zones favorables</b><br/>"
                                                          "Les zones avec résistivités comprises entre <b>50 et 200 Ω·m</b> (sables et graviers) "
                                                          "constituent les cibles prioritaires pour l'implantation de forages d'eau. Ces formations "
                                                          "présentent une bonne perméabilité et un potentiel aquifère élevé.", 
                                                          normal_style))'''
    ),
    
    # Paragraph Modèle lithologique
    (
        '''                                    story.append(Paragraph("""
                                    <b>4.1 Modèle lithologique</b><br/>
                                    L'analyse des résistivités inversées permet de proposer le modèle lithologique suivant :
                                    """, normal_style))''',
        '''                                    story.append(Paragraph("<b>4.1 Modèle lithologique</b><br/>"
                                                          "L'analyse des résistivités inversées permet de proposer le modèle lithologique suivant :", 
                                                          normal_style))'''
    ),
    
    # Paragraph Classification hydrogéologique
    (
        '''                                    story.append(Paragraph("""
                                    L'analyse des résistivités mesurées permet d'identifier 4 types d'eau distincts 
                                    selon les valeurs de résistivité apparente :
                                    """, normal_style))''',
        '''                                    story.append(Paragraph("L'analyse des résistivités mesurées permet d'identifier 4 types d'eau distincts "
                                                          "selon les valeurs de résistivité apparente :", 
                                                          normal_style))'''
    ),
    
    # Paragraph Traitement et inversion
    (
        '''                                    story.append(Paragraph(f"""
                                    <b>2.2 Traitement et inversion</b><br/>
                                    L'inversion des données a été réalisée avec pyGIMLi (Python Geophysical Inversion and Modeling Library).
                                    Configuration utilisée : schéma <b>{scheme_type.upper()}</b> avec {n_electrodes} électrodes 
                                    espacées de {spacing:.1f} mètres. Le maillage 2D comprend {n_electrodes} × {n_depth_points} points.
                                    Paramètres d'inversion : λ = 20 (régularisation), {ert_manager.inv.iterations()} itérations, 
                                    RMS error final = {ert_manager.inv.relrms():.3f}.
                                    """, normal_style))''',
        '''                                    story.append(Paragraph(f"<b>2.2 Traitement et inversion</b><br/>"
                                                          f"L'inversion des données a été réalisée avec pyGIMLi (Python Geophysical Inversion and Modeling Library). "
                                                          f"Configuration utilisée : schéma <b>{scheme_type.upper()}</b> avec {n_electrodes} électrodes "
                                                          f"espacées de {spacing:.1f} mètres. Le maillage 2D comprend {n_electrodes} × {n_depth_points} points. "
                                                          f"Paramètres d'inversion : λ = 20 (régularisation), {ert_manager.inv.iterations()} itérations, "
                                                          f"RMS error final = {ert_manager.inv.relrms():.3f}.", 
                                                          normal_style))'''
    ),
    
    # Paragraph Acquisition données
    (
        '''                                    story.append(Paragraph(f"""
                                    <b>2.1 Acquisition des données</b><br/>
                                    Les mesures de résistivité ont été effectuées avec un dispositif multi-fréquence 
                                    permettant d'obtenir {len(df_pygimli)} mesures réparties sur {len(survey_points)} points.
                                    Les fréquences varient de {freq_columns[0].replace('freq_', '')} MHz à {freq_columns[-1].replace('freq_', '')} MHz.
                                    """, normal_style))''',
        '''                                    story.append(Paragraph(f"<b>2.1 Acquisition des données</b><br/>"
                                                          f"Les mesures de résistivité ont été effectuées avec un dispositif multi-fréquence "
                                                          f"permettant d'obtenir {len(df_pygimli)} mesures réparties sur {len(survey_points)} points. "
                                                          f"Les fréquences varient de {freq_columns[0].replace('freq_', '')} MHz à {freq_columns[-1].replace('freq_', '')} MHz.", 
                                                          normal_style))'''
    ),
    
    # Paragraph Résumé exécutif
    (
        '''                                    story.append(Paragraph(f"""
                                    Ce rapport présente les résultats d'une investigation géophysique par tomographie 
                                    de résistivité électrique (ERT) réalisée avec la méthode pyGIMLi. L'étude a porté 
                                    sur {len(survey_points)} points de sondage avec {len(freq_columns)} fréquences de mesure, 
                                    permettant d'analyser le sous-sol jusqu'à {depth_max:.1f} mètres de profondeur.
                                    """, normal_style))''',
        '''                                    story.append(Paragraph(f"Ce rapport présente les résultats d'une investigation géophysique par tomographie "
                                                          f"de résistivité électrique (ERT) réalisée avec la méthode pyGIMLi. L'étude a porté "
                                                          f"sur {len(survey_points)} points de sondage avec {len(freq_columns)} fréquences de mesure, "
                                                          f"permettant d'analyser le sous-sol jusqu'à {depth_max:.1f} mètres de profondeur.", 
                                                          normal_style))'''
    ),
    
    # st.markdown Modèle lithologique
    (
        '''                            st.markdown("""
                            **Modèle lithologique VRAI (après inversion pyGIMLi) :**

                            Ce modèle présente la **structure réelle du sous-sol** obtenue par inversion tomographique.
                            Les résistivités affichées sont les **valeurs vraies** (non apparentes) après régularisation.

                            **Recommandations pour forages :**
                            - 💧 **Zones cibles** : Jaune/Or (50-100 Ω·m) = Aquifères productifs
                            - ✅ **Bon potentiel** : Vert clair (100-200 Ω·m) = Graviers perméables
                            - ⚠️ **Attention** : Marron/Rouge (< 20 Ω·m) = Argiles imperméables
                            - 🚫 **À éviter** : Rouge foncé (< 1 Ω·m) = Intrusion saline
                            """)''',
        '''                            st.markdown("**Modèle lithologique VRAI (après inversion pyGIMLi) :**\\n\\n"
                                       "Ce modèle présente la **structure réelle du sous-sol** obtenue par inversion tomographique. "
                                       "Les résistivités affichées sont les **valeurs vraies** (non apparentes) après régularisation.\\n\\n"
                                       "**Recommandations pour forages :**\\n"
                                       "- 💧 **Zones cibles** : Jaune/Or (50-100 Ω·m) = Aquifères productifs\\n"
                                       "- ✅ **Bon potentiel** : Vert clair (100-200 Ω·m) = Graviers perméables\\n"
                                       "- ⚠️ **Attention** : Marron/Rouge (< 20 Ω·m) = Argiles imperméables\\n"
                                       "- 🚫 **À éviter** : Rouge foncé (< 1 Ω·m) = Intrusion saline")'''
    ),
    
    # st.markdown Gradients horizontaux
    (
        '''                            st.markdown(f"""
                            **Interprétation des gradients horizontaux :**
                            - **Lignes cyan** : Changements latéraux importants (seuil > {threshold_grad_h:.2f})
                            - **Zones chaudes** : Contacts géologiques latéraux, failles, intrusions
                            - **Applications** : Détection de limites d'aquifères, zones de fractures
                            """)''',
        '''                            st.markdown(f"**Interprétation des gradients horizontaux :**\\n"
                                       f"- **Lignes cyan** : Changements latéraux importants (seuil > {threshold_grad_h:.2f})\\n"
                                       f"- **Zones chaudes** : Contacts géologiques latéraux, failles, intrusions\\n"
                                       f"- **Applications** : Détection de limites d'aquifères, zones de fractures")'''
    ),
    
    # st.markdown Interprétation hydrogéologique
    (
        '''                            st.markdown("""
                            **Interprétation hydrogéologique VRAIE (après inversion, selon tableau) :**
                            - 🔴 **Rouge vif/Orange** (0.1-1 Ω·m) : Eau de mer, intrusion marine
                            - 🟡 **Jaune/Orange** (1-10 Ω·m) : Eau salée (nappe saumâtre)
                            - 🟢 **Vert/Bleu clair** (10-100 Ω·m) : Eau douce exploitable
                            - 🔵 **Bleu foncé** (> 100 Ω·m) : Eau très pure / Roches sèches
                            """)''',
        '''                            st.markdown("**Interprétation hydrogéologique VRAIE (après inversion, selon tableau) :**\\n"
                                       "- 🔴 **Rouge vif/Orange** (0.1-1 Ω·m) : Eau de mer, intrusion marine\\n"
                                       "- 🟡 **Jaune/Orange** (1-10 Ω·m) : Eau salée (nappe saumâtre)\\n"
                                       "- 🟢 **Vert/Bleu clair** (10-100 Ω·m) : Eau douce exploitable\\n"
                                       "- 🔵 **Bleu foncé** (> 100 Ω·m) : Eau très pure / Roches sèches")'''
    ),
]

# Appliquer tous les remplacements
count = 0
for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"✅ Remplacement {count}/{len(replacements)}")
    else:
        print(f"⚠️  Pattern non trouvé pour remplacement {count+1}")

# Écrire le fichier corrigé
with open('ERTest.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n🎉 {count}/{len(replacements)} corrections appliquées")
print(f"Taille finale: {len(content)} caractères")
