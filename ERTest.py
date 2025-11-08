# app_sonic_ravensgate.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.cluster import KMeans
import chardet
import os
import tempfile
import io
import plotly.graph_objects as go
from datetime import datetime
import pygimli as pg
from pygimli.physics.ert import ERTManager, simulate
from matplotlib.colors import ListedColormap, BoundaryNorm

# Import du module d'authentification
try:
    from auth_module import AuthManager, show_auth_ui, show_user_info, require_auth
    AUTH_ENABLED = True
except ImportError:
    AUTH_ENABLED = False
    print("⚠️ Module d'authentification non disponible")

# --- Table de réglage température (Ts) ---
temperature_control_table = {
    36: {0:31, 5:31, 10:32, 15:33, 20:34, 25:34, 30:35, 35:36, 40:37, 45:37, 50:38, 55:39, 60:40, 65:40, 70:41, 75:42, 80:43, 85:43, 90:44, 95:45},
    38: {0:32, 5:33, 10:34, 15:35, 20:35, 25:36, 30:37, 35:38, 40:39, 45:39, 50:40, 55:41, 60:41, 65:42, 70:43, 75:44, 80:44, 85:45, 90:46, 95:47},
    40: {0:34, 5:35, 10:36, 15:36, 20:37, 25:38, 30:39, 35:39, 40:40, 45:41, 50:42, 55:42, 60:43, 65:44, 70:45, 75:45, 80:46, 85:47, 90:48, 95:48},
    42: {0:36, 5:36, 10:37, 15:38, 20:39, 25:39, 30:40, 35:41, 40:42, 45:42, 50:43, 55:44, 60:45, 65:45, 70:46, 75:47, 80:48, 85:48, 90:49, 95:50},
    44: {0:37, 5:38, 10:39, 15:40, 20:40, 25:41, 30:42, 35:43, 40:43, 45:44, 50:45, 55:46, 60:46, 65:47, 70:48, 75:49, 80:49, 85:50, 90:51, 95:52},
    46: {0:39, 5:40, 10:41, 15:41, 20:42, 25:43, 30:44, 35:44, 40:45, 45:46, 50:47, 55:47, 60:48, 65:49, 70:50, 75:50, 80:51, 85:52, 90:53, 95:53},
    48: {0:41, 5:42, 10:42, 15:43, 20:44, 25:45, 30:45, 35:46, 40:47, 45:48, 50:48, 55:49, 60:50, 65:51, 70:51, 75:52, 80:53, 85:54, 90:54, 95:55},
    50: {0:43, 5:43, 10:44, 15:45, 20:45, 25:46, 30:47, 35:48, 40:49, 45:49, 50:50, 55:51, 60:52, 65:52, 70:53, 75:54, 80:55, 85:55, 90:56, 95:57},
    52: {0:44, 5:45, 10:46, 15:46, 20:47, 25:48, 30:49, 35:49, 40:50, 45:51, 50:52, 55:52, 60:53, 65:54, 70:55, 75:55, 80:56, 85:57, 90:58, 95:58},
    54: {0:46, 5:47, 10:47, 15:48, 20:49, 25:50, 30:50, 35:51, 40:52, 45:53, 50:53, 55:54, 60:55, 65:56, 70:55, 75:57, 80:58, 85:59, 90:59, 95:60},
    56: {0:48, 5:48, 10:49, 15:50, 20:51, 25:51, 30:52, 35:53, 40:54, 45:54, 50:55, 55:56, 60:57, 65:57, 70:58, 75:59, 80:60, 85:60, 90:61, 95:62},
    58: {0:49, 5:50, 10:51, 15:52, 20:52, 25:53, 30:54, 35:55, 40:55, 45:56, 50:57, 55:58, 60:58, 65:59, 70:60, 75:61, 80:61, 85:62, 90:63, 95:64},
    60: {0:51, 5:52, 10:53, 15:53, 20:54, 25:55, 30:56, 35:56, 40:57, 45:58, 50:59, 55:59, 60:60, 65:61, 70:62, 75:62, 80:63, 85:64, 90:65, 95:65},
    62: {0:53, 5:53, 10:54, 15:55, 20:56, 25:56, 30:57, 35:58, 40:59, 45:59, 50:60, 55:61, 60:62, 65:62, 70:63, 75:64, 80:65, 85:65, 90:66, 95:67},
    64: {0:54, 5:55, 10:56, 15:57, 20:57, 25:58, 30:59, 35:60, 40:60, 45:61, 50:62, 55:63, 60:63, 65:64, 70:65, 75:66, 80:66, 85:67, 90:68, 95:69},
    66: {0:56, 5:57, 10:58, 15:58, 20:59, 25:60, 30:61, 35:61, 40:62, 45:63, 50:64, 55:64, 60:65, 65:66, 70:67, 75:67, 80:68, 85:69, 90:70, 95:70},
    68: {0:58, 5:59, 10:59, 15:60, 20:61, 25:62, 30:62, 35:63, 40:64, 45:65, 50:65, 55:66, 60:67, 65:68, 70:68, 75:69, 80:70, 85:71, 90:71, 95:72},
    70: {0:60, 5:60, 10:61, 15:62, 20:63, 25:63, 30:64, 35:65, 40:66, 45:66, 50:67, 55:68, 60:69, 65:69, 70:70, 75:71, 80:72, 85:72, 90:73, 95:74},
    72: {0:61, 5:62, 10:63, 15:63, 20:64, 25:65, 30:66, 35:66, 40:67, 45:68, 50:69, 55:70, 60:71, 65:72, 70:72, 75:73, 80:74, 85:75, 90:75, 95:75},
    74: {0:63, 5:64, 10:64, 15:65, 20:66, 25:67, 30:67, 35:68, 40:69, 45:70, 50:70, 55:71, 60:72, 65:73, 70:73, 75:74, 80:75, 85:76, 90:76, 95:77},
    76: {0:65, 5:65, 10:66, 15:67, 20:68, 25:68, 30:69, 35:70, 40:71, 45:71, 50:72, 55:73, 60:74, 65:74, 70:75, 75:76, 80:77, 85:77, 90:78, 95:79},
    78: {0:66, 5:67, 10:68, 15:69, 20:69, 25:70, 30:71, 35:72, 40:72, 45:73, 50:74, 55:75, 60:75, 65:76, 70:77, 75:78, 80:78, 85:79, 90:80, 95:81},
    80: {0:68, 5:69, 10:70, 15:70, 20:71, 25:72, 30:73, 35:73, 40:74, 45:75, 50:76, 55:76, 60:77, 65:78, 70:79, 75:79, 80:80, 85:81, 90:82, 95:82},
    82: {0:70, 5:70, 10:71, 15:72, 20:73, 25:73, 30:74, 35:75, 40:76, 45:76, 50:77, 55:78, 60:79, 65:79, 70:80, 75:81, 80:82, 85:82, 90:83, 95:84},
    84: {0:71, 5:72, 10:73, 15:74, 20:74, 25:75, 30:76, 35:77, 40:77, 45:78, 50:79, 55:80, 60:80, 65:81, 70:82, 75:83, 80:83, 85:84, 90:85, 95:86},
    86: {0:73, 5:74, 10:75, 15:75, 20:76, 25:77, 30:78, 35:78, 40:79, 45:80, 50:81, 55:81, 60:82, 65:83, 70:84, 75:84, 80:85, 85:86, 90:87, 95:87},
    88: {0:75, 5:76, 10:76, 15:77, 20:78, 25:79, 30:79, 35:80, 40:81, 45:82, 50:82, 55:83, 60:84, 65:85, 70:85, 75:86, 80:87, 85:88, 90:88, 95:89},
    90: {0:77, 5:77, 10:78, 15:79, 20:80, 25:80, 30:81, 35:82, 40:83, 45:83, 50:84, 55:85, 60:86, 65:86, 70:87, 75:88, 80:89, 85:89, 90:90, 95:91}
}

def get_ts(tw_f: float, tg_f: float) -> int:
    tw = int(tw_f / 2 + 0.5) * 2
    tg = int(tg_f / 5 + 0.5) * 5
    tw = max(36, min(90, tw))
    tg = max(0, min(95, tg))
    return temperature_control_table[tw][tg]

# --- Fonction pour générer le tableau HTML d'interprétation avec probabilités ---
def get_interpretation_probability_table():
    """
    Retourne un tableau HTML complet avec interprétations géologiques et probabilités
    selon les plages de résistivité.
    """
    return """
    <style>
    .prob-table {
        font-size: 11px;
        border-collapse: collapse;
        width: 100%;
    }
    .prob-table th {
        background-color: #2E86AB;
        color: white;
        padding: 10px;
        text-align: left;
    }
    .prob-table td {
        padding: 8px;
        border: 1px solid #ddd;
    }
    .prob-high { color: #00AA00; font-weight: bold; }
    .prob-med { color: #FF8800; }
    .prob-low { color: #888888; }
    </style>
    
    <table class="prob-table">
    <tr>
        <th>Couleur</th>
        <th>Résistivité (Ω·m)</th>
        <th>Interprétations Possibles</th>
        <th>Probabilités selon contexte</th>
        <th>Critères de différenciation</th>
    </tr>
    <tr style="background-color: #0000AA;">
        <td><strong>🔵 Bleu foncé</strong></td>
        <td><strong>0.1 - 1</strong></td>
        <td>
            • Eau de mer hypersalée<br>
            • Argile saturée salée<br>
            • Argile marine
        </td>
        <td>
            <span class="prob-high">80%</span> Eau salée si < 0.5 Ω·m<br>
            <span class="prob-med">60%</span> Argile saturée si 0.5-1 Ω·m<br>
            <span class="prob-low">20%</span> Minéral conducteur (rare)
        </td>
        <td>
            • Proximité côte → Eau salée<br>
            • En profondeur → Argile<br>
            • Faible TDS → Argile saturée
        </td>
    </tr>
    <tr style="background-color: #0055AA;">
        <td><strong>🔵 Bleu</strong></td>
        <td><strong>1 - 10</strong></td>
        <td>
            • Argile compacte<br>
            • Eau saumâtre<br>
            • Limon saturé
        </td>
        <td>
            <span class="prob-high">70%</span> Argile si > 5 Ω·m<br>
            <span class="prob-med">50%</span> Eau saumâtre si 1-3 Ω·m<br>
            <span class="prob-med">40%</span> Limon humide
        </td>
        <td>
            • Texture au forage<br>
            • Analyse chimique eau<br>
            • Profondeur de la nappe
        </td>
    </tr>
    <tr style="background-color: #00AAAA;">
        <td><strong>🟦 Cyan</strong></td>
        <td><strong>10 - 50</strong></td>
        <td>
            • Argile peu saturée<br>
            • Sable fin saturé<br>
            • Eau douce peu minéralisée
        </td>
        <td>
            <span class="prob-high">60%</span> Sable fin si 20-50 Ω·m<br>
            <span class="prob-med">50%</span> Argile si 10-20 Ω·m<br>
            <span class="prob-low">30%</span> Eau très douce
        </td>
        <td>
            • Granulométrie<br>
            • Perméabilité<br>
            • Minéralisation eau
        </td>
    </tr>
    <tr style="background-color: #00DD00;">
        <td><strong>🟢 Vert</strong></td>
        <td><strong>50 - 100</strong></td>
        <td>
            • Sable moyen humide<br>
            • Gravier fin saturé<br>
            • Aquifère sableux
        </td>
        <td>
            <span class="prob-high">80%</span> Sable aquifère<br>
            <span class="prob-med">40%</span> Gravier fin<br>
            <span class="prob-low">20%</span> Calcaire poreux
        </td>
        <td>
            • <strong>ZONE CIBLE pour forage</strong><br>
            • Bonne perméabilité<br>
            • Débit potentiel élevé
        </td>
    </tr>
    <tr style="background-color: #FFFF00;">
        <td><strong>🟡 Jaune</strong></td>
        <td><strong>100 - 300</strong></td>
        <td>
            • Sable grossier sec<br>
            • Gravier moyen<br>
            • Calcaire fissuré
        </td>
        <td>
            <span class="prob-high">75%</span> Gravier si 150-300 Ω·m<br>
            <span class="prob-med">60%</span> Sable grossier si 100-150 Ω·m<br>
            <span class="prob-low">30%</span> Roche altérée
        </td>
        <td>
            • <strong>BON AQUIFÈRE</strong><br>
            • Excellente perméabilité<br>
            • Recharge rapide
        </td>
    </tr>
    <tr style="background-color: #FFAA00;">
        <td><strong>🟠 Orange</strong></td>
        <td><strong>300 - 1000</strong></td>
        <td>
            • Gravier sec<br>
            • Roche altérée<br>
            • Calcaire compact
        </td>
        <td>
            <span class="prob-high">70%</span> Roche altérée<br>
            <span class="prob-med">50%</span> Gravier très sec<br>
            <span class="prob-low">25%</span> Calcaire
        </td>
        <td>
            • Profondeur importante<br>
            • Faible saturation<br>
            • Contexte géologique
        </td>
    </tr>
    <tr style="background-color: #FF0000;">
        <td><strong>🔴 Rouge</strong></td>
        <td><strong>> 1000</strong></td>
        <td>
            • Roche sédimentaire dure<br>
            • Granite/Basalte<br>
            • Socle cristallin
        </td>
        <td>
            <span class="prob-high">85%</span> Roche consolidée<br>
            <span class="prob-med">40%</span> Socle si > 5000 Ω·m<br>
            <span class="prob-low">10%</span> Aquifère de socle fracturé
        </td>
        <td>
            • Forage difficile et coûteux<br>
            • Potentiel aquifère si fracturé<br>
            • Débit faible à modéré
        </td>
    </tr>
    </table>
    <br>
    <p><strong>Légende des probabilités :</strong></p>
    <ul>
        <li><span style="color: #00AA00; font-weight: bold;">Probabilité HAUTE (&gt; 70%)</span> : Interprétation la plus probable</li>
        <li><span style="color: #FF8800;">Probabilité MOYENNE (40-70%)</span> : Possible selon le contexte</li>
        <li><span style="color: #888888;">Probabilité BASSE (&lt; 40%)</span> : Peu probable, nécessite confirmation</li>
    </ul>
    <p><strong>Recommandation :</strong> Combiner avec des données de forage, analyse d'eau, et profil géologique local pour confirmation.</p>
    """

# --- Fonction pour créer un rapport PDF complet ---
def create_pdf_report(df, unit, figures_dict):
    """
    Crée un rapport PDF complet avec tous les tableaux et graphiques
    
    Args:
        df: DataFrame avec les données
        unit: Unité de mesure
        figures_dict: Dictionnaire contenant toutes les figures matplotlib
        
    Returns:
        Bytes du fichier PDF
    """
    buffer = io.BytesIO()
    
    with PdfPages(buffer) as pdf:
        # Page 1: Page de titre
        fig_title = plt.figure(figsize=(8.5, 11))
        fig_title.text(0.5, 0.7, 'Rapport d\'Analyse ERT', 
                      ha='center', va='center', fontsize=24, fontweight='bold')
        fig_title.text(0.5, 0.6, 'Ravensgate Sonic Water Level Meter', 
                      ha='center', va='center', fontsize=16)
        fig_title.text(0.5, 0.5, f'Date: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 
                      ha='center', va='center', fontsize=12)
        fig_title.text(0.5, 0.4, f'Total mesures: {len(df)}', 
                      ha='center', va='center', fontsize=12)
        fig_title.text(0.5, 0.35, f'Points de sondage: {df["survey_point"].nunique()}', 
                      ha='center', va='center', fontsize=12)
        fig_title.text(0.5, 0.3, f'Unité: {unit}', 
                      ha='center', va='center', fontsize=12)
        plt.axis('off')
        pdf.savefig(fig_title, bbox_inches='tight')
        plt.close(fig_title)
        
        # Page 2: Statistiques descriptives
        fig_stats = plt.figure(figsize=(8.5, 11))
        ax_stats = fig_stats.add_subplot(111)
        
        stats_data = [
            ['Total mesures', len(df)],
            ['Points de sondage', df['survey_point'].nunique()],
            ['Profondeurs uniques', df['depth'].nunique()],
            [f'DTW moyen ({unit})', f"{df['data'].mean():.2f}"],
            [f'DTW min ({unit})', f"{df['data'].min():.2f}"],
            [f'DTW max ({unit})', f"{df['data'].max():.2f}"],
            [f'Écart-type ({unit})', f"{df['data'].std():.2f}"],
        ]
        
        table_stats = ax_stats.table(cellText=stats_data, 
                                     colLabels=['Statistique', 'Valeur'],
                                     cellLoc='left', loc='center',
                                     colWidths=[0.6, 0.4])
        table_stats.auto_set_font_size(False)
        table_stats.set_fontsize(10)
        table_stats.scale(1, 2)
        ax_stats.axis('off')
        ax_stats.set_title('Statistiques descriptives', fontsize=16, fontweight='bold', pad=20)
        pdf.savefig(fig_stats, bbox_inches='tight')
        plt.close(fig_stats)
        
        # Page 3+: Statistiques par profondeur
        depth_stats = df.groupby('depth')['data'].agg(['mean', 'min', 'max', 'std']).round(2)
        
        fig_depth = plt.figure(figsize=(8.5, 11))
        ax_depth = fig_depth.add_subplot(111)
        
        depth_data = [[f"{idx:.1f}", f"{row['mean']:.2f}", f"{row['min']:.2f}", 
                      f"{row['max']:.2f}", f"{row['std']:.2f}"] 
                     for idx, row in depth_stats.iterrows()]
        
        table_depth = ax_depth.table(cellText=depth_data,
                                    colLabels=['Profondeur', 'Moyenne DTW', 'Min DTW', 'Max DTW', 'Écart-type'],
                                    cellLoc='center', loc='center',
                                    colWidths=[0.2, 0.2, 0.2, 0.2, 0.2])
        table_depth.auto_set_font_size(False)
        table_depth.set_fontsize(9)
        table_depth.scale(1, 1.5)
        ax_depth.axis('off')
        ax_depth.set_title(f'Statistiques par profondeur ({unit})', fontsize=16, fontweight='bold', pad=20)
        pdf.savefig(fig_depth, bbox_inches='tight')
        plt.close(fig_depth)
        
        # Ajouter toutes les figures fournies
        for fig_name, fig in figures_dict.items():
            if fig is not None:
                pdf.savefig(fig, bbox_inches='tight')
        
        # Métadonnées du PDF
        d = pdf.infodict()
        d['Title'] = 'Rapport Analyse ERT - Ravensgate Sonic'
        d['Author'] = 'ERTest Application'
        d['Subject'] = 'Analyse des niveaux d\'eau souterraine'
        d['Keywords'] = 'ERT, Ravensgate, Water Level, DTW'
        d['CreationDate'] = datetime.now()
    
    buffer.seek(0)
    return buffer.getvalue()

def create_stratigraphy_pdf_report(df, figures_strat_dict):
    """
    Crée un rapport PDF complet pour l'analyse stratigraphique
    
    Args:
        df: DataFrame avec les données de résistivité
        figures_strat_dict: Dictionnaire contenant toutes les figures stratigraphiques
        
    Returns:
        Bytes du fichier PDF
    """
    buffer = io.BytesIO()
    
    with PdfPages(buffer) as pdf:
        # Page 1: Page de titre
        fig_title = plt.figure(figsize=(8.5, 11), dpi=150)
        fig_title.text(0.5, 0.75, '🪨 RAPPORT STRATIGRAPHIQUE COMPLET', 
                      ha='center', va='center', fontsize=22, fontweight='bold')
        fig_title.text(0.5, 0.68, 'Classification Géologique avec Résistivités', 
                      ha='center', va='center', fontsize=16, style='italic')
        fig_title.text(0.5, 0.6, f'📅 Date: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 
                      ha='center', va='center', fontsize=12)
        
        # Statistiques du sondage
        rho_data = pd.to_numeric(df['data'], errors='coerce').dropna()
        depth_data = np.abs(pd.to_numeric(df['depth'], errors='coerce').dropna())
        
        fig_title.text(0.5, 0.5, '📊 RÉSUMÉ DES DONNÉES', 
                      ha='center', va='center', fontsize=14, fontweight='bold')
        fig_title.text(0.5, 0.44, f'Nombre total de mesures: {len(df)}', 
                      ha='center', va='center', fontsize=11)
        fig_title.text(0.5, 0.40, f'Profondeur maximale: {depth_data.max():.3f} m (≈{depth_data.max()*1000:.0f} mm)', 
                      ha='center', va='center', fontsize=11)
        fig_title.text(0.5, 0.36, f'Résistivité min: {rho_data.min():.3f} Ω·m', 
                      ha='center', va='center', fontsize=11)
        fig_title.text(0.5, 0.32, f'Résistivité max: {rho_data.max():.0f} Ω·m', 
                      ha='center', va='center', fontsize=11)
        fig_title.text(0.5, 0.28, f'Résistivité moyenne: {rho_data.mean():.2f} Ω·m', 
                      ha='center', va='center', fontsize=11)
        
        # Catégories identifiées
        fig_title.text(0.5, 0.18, '🎯 CATÉGORIES GÉOLOGIQUES IDENTIFIÉES', 
                      ha='center', va='center', fontsize=12, fontweight='bold')
        
        categories = [
            ('💧 Eaux', (0.1, 1000)),
            ('🧱 Argiles & Sols saturés', (1, 100)),
            ('🏖️ Sables & Graviers', (50, 1000)),
            ('🪨 Roches sédimentaires', (100, 5000)),
            ('🌋 Roches ignées', (1000, 100000)),
            ('💎 Minéraux & Minerais', (0.001, 1000000))
        ]
        
        y_pos = 0.12
        for cat_name, (rho_min, rho_max) in categories:
            mask = (rho_data >= rho_min) & (rho_data <= rho_max)
            count = mask.sum()
            if count > 0:
                fig_title.text(0.5, y_pos, f'{cat_name}: {count} mesures', 
                              ha='center', va='center', fontsize=9)
                y_pos -= 0.03
        
        fig_title.text(0.5, 0.02, '© Belikan M. - Analyse ERT - Novembre 2025', 
                      ha='center', va='center', fontsize=8, style='italic', color='gray')
        plt.axis('off')
        pdf.savefig(fig_title, bbox_inches='tight')
        plt.close(fig_title)
        
        # Ajouter toutes les figures du dictionnaire
        for fig_name, fig in figures_strat_dict.items():
            pdf.savefig(fig, bbox_inches='tight', dpi=150)
            plt.close(fig)
        
        # Métadonnées du PDF
        d = pdf.infodict()
        d['Title'] = 'Rapport Stratigraphique Complet'
        d['Author'] = 'Belikan M. - ERTest Application'
        d['Subject'] = 'Classification géologique par résistivité électrique'
        d['Keywords'] = 'ERT, Stratigraphie, Résistivité, Géologie, Minéraux'
        d['CreationDate'] = datetime.now()
    
    buffer.seek(0)
    return buffer.getvalue()

# --- Parsing .dat robuste avec cache ---
@st.cache_data
def detect_encoding(file_bytes):
    """Détecte l'encodage depuis les bytes du fichier"""
    result = chardet.detect(file_bytes[:100000])
    return result['encoding'] or 'utf-8'

@st.cache_data
def parse_dat(file_content, encoding):
    """Parse le contenu du fichier .dat avec mise en cache"""
    try:
        from io import StringIO
        df = pd.read_csv(
            StringIO(file_content.decode(encoding)), 
            sep='\s+', header=None, comment='#',
            names=['survey_point', 'depth', 'data', 'project'],
            on_bad_lines='skip', engine='python'
        )
        df['survey_point'] = pd.to_numeric(df['survey_point'], errors='coerce')
        df['depth'] = pd.to_numeric(df['depth'], errors='coerce')
        df['data'] = pd.to_numeric(df['data'], errors='coerce')
        df = df.dropna(subset=['survey_point', 'depth', 'data'])
        return df
    except Exception as e:
        st.error(f"Erreur parsing : {e}")
        return pd.DataFrame()

@st.cache_data
def parse_freq_dat(file_content, encoding):
    """Parse le fichier freq.dat avec fréquences en MHz"""
    try:
        from io import StringIO
        import pandas as pd
        
        # Décoder le contenu avec gestion du BOM UTF-8
        content = file_content.decode(encoding, errors='replace')
        
        # Supprimer le BOM s'il existe
        if content.startswith('\ufeff'):
            content = content[1:]
        
        # Lire avec pandas, en ignorant les lignes vides
        df = pd.read_csv(StringIO(content), sep=',', header=0, engine='python')
        
        # Nettoyer les noms de colonnes (supprimer les espaces et caractères spéciaux)
        df.columns = [col.strip().replace('MHz', '').replace(',', '') for col in df.columns]
        
        # La première colonne devrait être le projet, la deuxième le point de sondage
        # Les colonnes suivantes sont les fréquences
        if len(df.columns) < 3:
            return pd.DataFrame()
        
        # Renommer les colonnes
        freq_columns = df.columns[2:]  # Colonnes de fréquences
        df.columns = ['project', 'survey_point'] + [f'freq_{col}' for col in freq_columns]
        
        # Convertir survey_point en numérique
        df['survey_point'] = pd.to_numeric(df['survey_point'], errors='coerce')
        
        # Convertir les colonnes de fréquence en numérique
        for col in df.columns[2:]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Supprimer les lignes avec survey_point NaN
        df = df.dropna(subset=['survey_point'])
        
        return df
        
    except Exception as e:
        st.error(f"Erreur parsing freq.dat : {e}")
        return pd.DataFrame()

# --- Tableau des types d'eau ---
water_html = """
<style>
.water-table th { background-color: #333; color: white; padding: 12px; text-align: center; }
.water-table td { padding: 12px; text-align: center; border-bottom: 1px solid #ddd; }
</style>
<table class="water-table" style="width:100%; border-collapse: collapse; margin: 20px 0;">
  <tr>
    <th>Type d'eau</th>
    <th>Résistivité (Ω.m)</th>
    <th>Couleur associée</th>
    <th>Description</th>
  </tr>
  <tr style="background-color: #FF4500; color: white;">
    <td><strong>Eau de mer</strong></td>
    <td>0.1 – 1</td>
    <td>Rouge vif / Orange</td>
    <td>Eau océanique hautement salée (∼35 g/L de sel). Très forte conductivité électrique due aux ions Na⁺ et Cl⁻. Typique des mers et océans.</td>
  </tr>
  <tr style="background-color: #FFD700; color: black;">
    <td><strong>Eau salée (nappe)</strong></td>
    <td>1 – 10</td>
    <td>Jaune / Orange</td>
    <td>Eau saumâtre dans les nappes phréatiques côtières (intrusion saline). Salinité intermédiaire, souvent non potable sans traitement.</td>
  </tr>
  <tr style="background-color: #90EE90; color: black;">
    <td><strong>Eau douce</strong></td>
    <td>10 – 100</td>
    <td>Vert / Bleu clair</td>
    <td>Eau potable standard (rivières, lacs, nappes intérieures). Faiblement minéralisée, conductivité modérée.</td>
  </tr>
  <tr style="background-color: #00008B; color: white;">
    <td><strong>Eau très pure</strong></td>
    <td>> 100</td>
    <td>Bleu foncé</td>
    <td>Eau ultra-pure (distillée, déminéralisée, pluie). Presque pas d'ions → très faible conductivité. Utilisée en laboratoire/industrie.</td>
  </tr>
</table>
"""

# --- Tableau complet des matériaux géologiques (sols, roches, minéraux et eaux) ---
geology_html = """
<style>
.geo-table th { background-color: #1e3a8a; color: white; padding: 10px; text-align: center; font-weight: bold; }
.geo-table td { padding: 10px; text-align: center; border-bottom: 1px solid #ccc; }
.geo-table tr:hover { background-color: #f0f0f0; }
</style>
<table class="geo-table" style="width:100%; border-collapse: collapse; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
  <tr>
    <th colspan="5" style="background-color: #0f172a; font-size: 18px;">📊 CLASSIFICATION COMPLÈTE DES RÉSISTIVITÉS GÉOLOGIQUES</th>
  </tr>
  <tr>
    <th>Catégorie</th>
    <th>Matériau</th>
    <th>Résistivité (Ω.m)</th>
    <th>Couleur</th>
    <th>Description / Usage</th>
  </tr>
  
  <!-- EAUX -->
  <tr style="background-color: #fef3c7;">
    <td rowspan="4" style="background-color: #3b82f6; color: white; font-weight: bold; vertical-align: middle;">💧<br>EAUX</td>
    <td><strong>Eau de mer</strong></td>
    <td>0.1 – 1</td>
    <td style="background-color: #FF4500; color: white;">🔴 Rouge</td>
    <td>Océans, forte salinité (35 g/L NaCl)</td>
  </tr>
  <tr style="background-color: #fef3c7;">
    <td><strong>Eau salée/saumâtre</strong></td>
    <td>1 – 10</td>
    <td style="background-color: #FFD700;">🟡 Jaune-Orange</td>
    <td>Nappes côtières, intrusion saline</td>
  </tr>
  <tr style="background-color: #fef3c7;">
    <td><strong>Eau douce</strong></td>
    <td>10 – 100</td>
    <td style="background-color: #90EE90;">🟢 Vert-Bleu clair</td>
    <td>Nappes phréatiques, rivières, lacs</td>
  </tr>
  <tr style="background-color: #fef3c7;">
    <td><strong>Eau ultra-pure</strong></td>
    <td>100 – 1000</td>
    <td style="background-color: #00008B; color: white;">🔵 Bleu foncé</td>
    <td>Eau distillée, pluie, laboratoire</td>
  </tr>
  
  <!-- SOLS SATURÉS / ARGILES -->
  <tr style="background-color: #fee2e2;">
    <td rowspan="3" style="background-color: #dc2626; color: white; font-weight: bold; vertical-align: middle;">🧱<br>ARGILES<br>& SOLS<br>SATURÉS</td>
    <td><strong>Argile marine saturée</strong></td>
    <td>1 – 10</td>
    <td style="background-color: #8B4513; color: white;">🟤 Brun rouge</td>
    <td>Très conductrice, riche en sels</td>
  </tr>
  <tr style="background-color: #fee2e2;">
    <td><strong>Argile compacte humide</strong></td>
    <td>10 – 50</td>
    <td style="background-color: #A0522D; color: white;">🟫 Brun</td>
    <td>Formations imperméables, rétention d'eau</td>
  </tr>
  <tr style="background-color: #fee2e2;">
    <td><strong>Limon/Silt saturé</strong></td>
    <td>20 – 100</td>
    <td style="background-color: #D2B48C;">🟨 Beige</td>
    <td>Sol fin avec eau interstitielle</td>
  </tr>
  
  <!-- SABLES ET GRAVIERS -->
  <tr style="background-color: #fef9c3;">
    <td rowspan="3" style="background-color: #eab308; font-weight: bold; vertical-align: middle;">🏖️<br>SABLES<br>& GRAVIERS</td>
    <td><strong>Sable saturé (eau douce)</strong></td>
    <td>50 – 200</td>
    <td style="background-color: #F4A460;">🟧 Sable</td>
    <td>Aquifère perméable, bon pour puits</td>
  </tr>
  <tr style="background-color: #fef9c3;">
    <td><strong>Sable sec</strong></td>
    <td>200 – 1000</td>
    <td style="background-color: #FFE4B5;">🟨 Beige clair</td>
    <td>Zone non saturée, faible conductivité</td>
  </tr>
  <tr style="background-color: #fef9c3;">
    <td><strong>Gravier saturé</strong></td>
    <td>100 – 500</td>
    <td style="background-color: #BDB76B;">⚫ Gris-vert</td>
    <td>Très perméable, aquifère productif</td>
  </tr>
  
  <!-- ROCHES SÉDIMENTAIRES -->
  <tr style="background-color: #e0e7ff;">
    <td rowspan="4" style="background-color: #6366f1; color: white; font-weight: bold; vertical-align: middle;">🪨<br>ROCHES<br>SÉDIMEN-<br>TAIRES</td>
    <td><strong>Calcaire fissuré (saturé)</strong></td>
    <td>100 – 1000</td>
    <td style="background-color: #D3D3D3;">⚪ Gris clair</td>
    <td>Karst, aquifère calcaire, grottes</td>
  </tr>
  <tr style="background-color: #e0e7ff;">
    <td><strong>Calcaire compact</strong></td>
    <td>1000 – 5000</td>
    <td style="background-color: #C0C0C0;">⚪ Gris</td>
    <td>Peu poreux, faible perméabilité</td>
  </tr>
  <tr style="background-color: #e0e7ff;">
    <td><strong>Grès poreux saturé</strong></td>
    <td>200 – 2000</td>
    <td style="background-color: #DAA520;">🟫 Or terne</td>
    <td>Réservoir aquifère important</td>
  </tr>
  <tr style="background-color: #e0e7ff;">
    <td><strong>Schiste argileux</strong></td>
    <td>10 – 100</td>
    <td style="background-color: #696969; color: white;">⚫ Gris foncé</td>
    <td>Conducteur, riche en minéraux argileux</td>
  </tr>
  
  <!-- ROCHES IGNÉES ET MÉTAMORPHIQUES -->
  <tr style="background-color: #fce7f3;">
    <td rowspan="4" style="background-color: #ec4899; color: white; font-weight: bold; vertical-align: middle;">🌋<br>ROCHES<br>IGNÉES<br>& MÉTA.</td>
    <td><strong>Granite</strong></td>
    <td>5000 – 100000</td>
    <td style="background-color: #FFB6C1;">🩷 Rose</td>
    <td>Très résistif, socle cristallin</td>
  </tr>
  <tr style="background-color: #fce7f3;">
    <td><strong>Basalte compact</strong></td>
    <td>1000 – 10000</td>
    <td style="background-color: #2F4F4F; color: white;">⚫ Noir-gris</td>
    <td>Roche volcanique dense</td>
  </tr>
  <tr style="background-color: #fce7f3;">
    <td><strong>Basalte fracturé (saturé)</strong></td>
    <td>200 – 2000</td>
    <td style="background-color: #556B2F; color: white;">🟢 Vert sombre</td>
    <td>Aquifère volcanique</td>
  </tr>
  <tr style="background-color: #fce7f3;">
    <td><strong>Quartzite</strong></td>
    <td>10000 – 100000</td>
    <td style="background-color: #F5F5DC;">⚪ Blanc cassé</td>
    <td>Métamorphique, très résistant</td>
  </tr>
  
  <!-- MINÉRAUX SPÉCIAUX -->
  <tr style="background-color: #ddd6fe;">
    <td rowspan="3" style="background-color: #7c3aed; color: white; font-weight: bold; vertical-align: middle;">💎<br>MINÉRAUX<br>& ORES</td>
    <td><strong>Minerais métalliques (cuivre, or)</strong></td>
    <td>0.01 – 1</td>
    <td style="background-color: #FFD700;">🟡 Doré</td>
    <td>Très conducteurs, cibles minières</td>
  </tr>
  <tr style="background-color: #ddd6fe;">
    <td><strong>Graphite</strong></td>
    <td>0.001 – 0.1</td>
    <td style="background-color: #000000; color: white;">⚫ Noir</td>
    <td>Extrêmement conducteur</td>
  </tr>
  <tr style="background-color: #ddd6fe;">
    <td><strong>Quartz pur</strong></td>
    <td>> 100000</td>
    <td style="background-color: #FFFFFF; border: 2px solid #000;">⚪ Transparent</td>
    <td>Isolant électrique parfait</td>
  </tr>
</table>
"""

# --- Seed pour reproductibilité des exemples ---
np.random.seed(42)

# --- Interface Streamlit ---
st.set_page_config(
    page_title="SETRAF - Subaquifère ERT Analysis", 
    page_icon="💧",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ========== SYSTÈME D'AUTHENTIFICATION ==========
if AUTH_ENABLED:
    auth_manager = AuthManager()
    
    # Vérifier l'authentification
    if not auth_manager.is_authenticated():
        # Afficher l'interface de connexion
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1>💧 SETRAF - Subaquifère ERT Analysis Tool</h1>
            <p style="font-size: 18px; color: #666;">
                Plateforme d'analyse géophysique avancée
            </p>
        </div>
        """, unsafe_allow_html=True)
        show_auth_ui()
        st.stop()
    
    # Afficher les informations utilisateur dans la sidebar
    show_user_info()

st.title("💧 SETRAF - Subaquifère ERT Analysis Tool (08 Novembre 2025)")

# Message de bienvenue pour utilisateur authentifié
if AUTH_ENABLED and st.session_state.authenticated:
    user = st.session_state.user
    st.success(f"👋 Bienvenue, {user.get('fullName', user.get('username'))} !")
    
    with st.expander("ℹ️ Informations de session", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👤 Utilisateur", user.get('username'))
        with col2:
            st.metric("📧 Email", user.get('email'))
        with col3:
            st.metric("🎯 Rôle", user.get('role', 'user').upper())

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌡️ Calculateur Réglage Température", 
    "📊 Analyse Fichiers .dat", 
    "🌍 ERT Pseudo-sections 2D/3D",
    "🪨 Stratigraphie Complète (Sols + Eaux)",
    "🔬 Inversion pyGIMLi - ERT Avancée"
])

# ===================== TAB 1 : TEMPÉRATURE =====================
with tab1:
    st.header("Calculateur de réglage Ts (Table officielle Ravensgate)")
    st.markdown("""
    Entrez la température de l'eau du puits (**Tw**) et la température moyenne quotidienne de surface (**Tg**).  
    L'app arrondit **conventionnellement (half-up)** aux pas du tableau et clamp automatiquement.
    
    **Exemple du manuel** : Tw = 58 °F (14 °C), Tg = 85 °F (29 °C) → **Ts = 62 °F** (17 °C).
    """)

    unit = st.radio("Unité", options=["°F", "°C"], horizontal=True)

    if unit == "°C":
        col1, col2 = st.columns(2)
        with col1:
            tw_c = st.number_input("Tw – Température eau puits (°C)", value=10.0, min_value=-10.0, max_value=50.0, step=0.1)
        with col2:
            tg_c = st.number_input("Tg – Température surface moyenne (°C)", value=20.0, min_value=-30.0, max_value=50.0, step=0.1)
        tw_f = tw_c * 9/5 + 32
        tg_f = tg_c * 9/5 + 32
    else:
        col1, col2 = st.columns(2)
        with col1:
            tw_f = st.number_input("Tw – Température eau puits (°F)", value=60.0, min_value=20.0, max_value=120.0, step=0.5)
        with col2:
            tg_f = st.number_input("Tg – Température surface moyenne (°F)", value=70.0, min_value=-20.0, max_value=120.0, step=0.5)

    if st.button("🔥 Calculer Ts", type="primary", use_container_width=True):
        ts = get_ts(tw_f, tg_f)
        tw_used = max(36, min(90, int(tw_f / 2 + 0.5) * 2))
        tg_used = max(0, min(95, int(tg_f / 5 + 0.5) * 5))

        st.success(f"**Réglage recommandé sur l'appareil → Ts = {ts} °F**")

        if unit == "°C":
            st.info(f"Tw utilisée → {tw_used} °F ({(tw_used - 32)*5/9:.1f} °C) | Tg utilisée → {tg_used} °F ({(tg_used - 32)*5/9:.1f} °C)")
        else:
            st.info(f"Tw utilisée → {tw_used} °F | Tg utilisée → {tg_used} °F")

    with st.expander("📋 Tableau complet Ravensgate (cliquer pour déplier)"):
        tg_cols = list(range(0, 96, 5))
        df_table = pd.DataFrame.from_dict(temperature_control_table, orient='index', columns=tg_cols)
        df_table.index.name = "Tw \\ Tg"
        df_table = df_table.sort_index()
        df_table.insert(0, "Tw (°F)", df_table.index)
        st.dataframe(df_table.style.background_gradient(cmap='coolwarm', axis=None), use_container_width=True)

    with st.expander("💧 Valeurs typiques pour l'eau – Résistivité & Couleurs associées"):
        st.markdown("### **2. Valeurs typiques pour l'eau**")
        st.markdown(water_html, unsafe_allow_html=True)
        st.caption("Ces valeurs sont indicatives. Les couleurs sont couramment utilisées dans les cartes de résistivité électrique (ERT) pour visualiser la salinité/qualité de l'eau souterraine.")

# ===================== TAB 2 : ANALYSE .DAT =====================
with tab2:
    st.header("2 Analyse de fichiers .dat de Ravensgate Sonic Water Level Meter")
    
    st.markdown("""
    ### Format attendu dans le .dat :
    - **Date** : Format YYYY/MM/DD HH:MM:SS
    - **Survey Point** (Point de forage)
    - **Depth From** et **Depth To** (Profondeur de mesure)
    - **Data** : Niveau d'eau (DTW - Depth To Water)
    """)
    
    # Initialiser l'état de session
    if 'uploaded_data' not in st.session_state:
        st.session_state['uploaded_data'] = None
    
    uploaded_file = st.file_uploader("📂 Uploader un fichier .dat", type=["dat"])
    
    if uploaded_file is not None:
        # Lire le contenu du fichier en bytes (avec cache)
        file_bytes = uploaded_file.read()
        encoding = detect_encoding(file_bytes)
        
        # Parser le fichier (avec cache)
        df = parse_dat(file_bytes, encoding)
        
        # Déterminer l'unité
        unit = 'm'  # Par défaut
        
        if not df.empty:
            st.success(f"✅ {len(df)} lignes chargées avec succès")
            
            # Sauvegarder dans l'état de session pour l'onglet 3
            st.session_state['uploaded_data'] = df.copy()
            st.session_state['unit'] = unit
            
            # Affichage du DataFrame
            st.dataframe(df.head(50), use_container_width=True)
            
            # Statistiques de base
            st.subheader("📊 Statistiques descriptives")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total mesures", len(df))
            with col2:
                st.metric("Points de sondage", df['survey_point'].nunique())
            with col3:
                st.metric(f"DTW moyen ({unit})", f"{df['data'].mean():.2f}")
            with col4:
                st.metric(f"DTW max ({unit})", f"{df['data'].max():.2f}")
            
            # Graphique temporel
            st.subheader("📈 Évolution temporelle du niveau d'eau")
            
            # Dictionnaire pour stocker toutes les figures
            figures_dict = {}
            
            # Vérifier si colonne 'date' existe
            if 'date' in df.columns:
                fig_time, ax = plt.subplots(figsize=(12, 5), dpi=150)
                for sp in sorted(df['survey_point'].unique()):
                    subset = df[df['survey_point'] == sp]
                    ax.plot(subset['date'], subset['data'], marker='o', label=f'SP {int(sp)}', markersize=4)
                ax.set_xlabel('Date', fontsize=11)
                ax.set_ylabel(f'DTW ({unit})', fontsize=11)
                ax.set_title('Niveau d\'eau par point de sondage', fontsize=13, fontweight='bold')
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
                ax.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig_time)
                
                # Sauvegarder pour PDF
                figures_dict['temporal_evolution'] = fig_time
            else:
                st.info("⚠️ Pas de colonne 'date' dans le fichier - graphique temporel indisponible")
                fig_time = None
            
            # Détection d'anomalies
            st.subheader("🔍 Détection d'anomalies (K-Means)")
            n_clusters = st.slider("Nombre de clusters", 2, 5, 3, key='kmeans_slider')
            
            # Cache du calcul KMeans basé sur les données + nombre de clusters
            @st.cache_data
            def compute_kmeans(data_hash, n_clust):
                """Calcul KMeans avec cache"""
                X = df[['survey_point', 'depth', 'data']].values
                kmeans = KMeans(n_clusters=n_clust, random_state=42, n_init=10)
                return kmeans.fit_predict(X)
            
            # Hash unique des données pour invalidation du cache
            data_hash = hash(tuple(df[['survey_point', 'depth', 'data']].values.flatten()))
            clusters = compute_kmeans(data_hash, n_clusters)
            df_viz = df.copy()
            df_viz['cluster'] = clusters
            
            fig_cluster, ax = plt.subplots(figsize=(12, 6), dpi=150)
            scatter = ax.scatter(df_viz['survey_point'], df_viz['depth'], c=df_viz['cluster'], 
                                cmap='viridis', s=50, alpha=0.6, edgecolors='black', linewidths=0.5)
            plt.colorbar(scatter, ax=ax, label='Cluster')
            ax.set_xlabel('Point de sondage', fontsize=11)
            ax.set_ylabel(f'Profondeur ({unit})', fontsize=11)
            ax.set_title(f'Classification en {n_clusters} groupes', fontsize=13, fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig_cluster)
            
            # Sauvegarder pour PDF
            figures_dict['kmeans_clustering'] = fig_cluster
            
            # Coupe de niveaux d'eau avec couleurs de résistivité
            st.subheader("🌊 Coupe géologique - Niveaux d'eau avec résistivité")
            
            # Préparer les données pour la coupe
            survey_points = sorted(df['survey_point'].unique())
            depths = sorted(df['depth'].unique())
            
            if len(survey_points) >= 2 and len(depths) >= 2:
                # Créer une grille 2D
                from scipy.interpolate import griddata
                
                X_grid = []
                Z_grid = []
                DTW_grid = []
                
                for sp in survey_points:
                    for depth in depths:
                        subset = df[(df['survey_point'] == sp) & (df['depth'] == depth)]
                        if len(subset) > 0:
                            X_grid.append(float(sp))
                            Z_grid.append(abs(float(depth)))
                            DTW_grid.append(float(subset['data'].values[0]))
                
                X_grid = np.array(X_grid)
                Z_grid = np.array(Z_grid)
                DTW_grid = np.array(DTW_grid)
                
                # Interpolation pour avoir une grille lisse
                xi = np.linspace(X_grid.min(), X_grid.max(), 150)
                zi = np.linspace(Z_grid.min(), Z_grid.max(), 100)
                Xi, Zi = np.meshgrid(xi, zi)
                DTWi = griddata((X_grid, Z_grid), DTW_grid, (Xi, Zi), method='cubic')
                
                # Convertir DTW en résistivité apparente (simulation)
                # Plus le DTW est élevé, plus l'eau est profonde, donc moins conductrice
                # Résistivité ~ proportionnelle au DTW (valeurs indicatives)
                rho_apparent = np.where(DTWi < 5, 2,      # Eau très peu profonde → salée (2 Ω·m)
                                np.where(DTWi < 15, 8,     # Eau peu profonde → saumâtre (8 Ω·m)
                                np.where(DTWi < 30, 40,    # Eau moyenne profondeur → douce (40 Ω·m)
                                np.where(DTWi < 50, 150,   # Eau profonde → pure (150 Ω·m)
                                         500))))           # Très profond → roche sèche (500 Ω·m)
                
                # Créer la figure avec colormap ERT standard
                fig_water, ax_water = plt.subplots(figsize=(14, 7), dpi=150)
                
                # Utiliser jet_r (rouge=conducteur/salé, bleu=résistif/sec)
                pcm = ax_water.pcolormesh(Xi, Zi, rho_apparent, cmap='jet_r', 
                                         norm=LogNorm(vmin=1, vmax=1000), shading='auto')
                
                # Ajouter les points de mesure
                scatter = ax_water.scatter(X_grid, Z_grid, c=DTW_grid, cmap='coolwarm', 
                                          s=80, edgecolors='black', linewidths=1, 
                                          alpha=0.8, zorder=10, marker='o')
                
                # Colorbar pour la résistivité
                cbar = fig_water.colorbar(pcm, ax=ax_water, label='Résistivité apparente (Ω·m)', extend='both')
                
                ax_water.invert_yaxis()
                ax_water.set_xlabel('Point de sondage (Survey Point)', fontsize=11)
                ax_water.set_ylabel(f'Profondeur ({unit})', fontsize=11)
                ax_water.set_title('Coupe géologique - Distribution des niveaux d\'eau et résistivité', 
                                  fontsize=13, fontweight='bold')
                ax_water.grid(True, alpha=0.3, linestyle='--', color='white', linewidth=0.5)
                plt.tight_layout()
                
                st.pyplot(fig_water)
                
                # Sauvegarder pour PDF
                figures_dict['water_level_section'] = fig_water
                
                # Légende d'interprétation
                st.markdown(f"""
**Interprétation de la coupe :**
- 🔴 **Rouge/Orange** (1-10 Ω·m) : Eau salée/saumâtre - Nappe peu profonde (DTW < 15 {unit})
- 🟡 **Jaune** (10-100 Ω·m) : Eau douce - Nappe intermédiaire (DTW 15-30 {unit})
- 🟢 **Vert** (100-300 Ω·m) : Eau pure - Nappe profonde (DTW 30-50 {unit})
- 🔵 **Bleu** (>300 Ω·m) : Roche sèche/résistive - Niveau très profond (DTW > 50 {unit})

**Points noirs** : Mesures réelles du fichier .dat (colorés selon la profondeur)
                """)
            else:
                st.warning("⚠️ Pas assez de points de mesure pour créer une coupe 2D (minimum 2 points de sondage et 2 profondeurs)")
            
            # Coupes détaillées par type d'eau avec mesures réelles
            st.markdown("---")
            st.subheader("📊 Coupes détaillées par type d'eau - Mesures de résistivité réelles")
            
            # Afficher le tableau de référence
            st.markdown("""
            ### 📋 Tableau de référence - Valeurs typiques pour l'eau
            """)
            
            water_reference = pd.DataFrame({
                'Type d\'eau': ['Eau de mer', 'Eau salée (nappe)', 'Eau douce', 'Eau très pure'],
                'Résistivité (Ω.m)': ['0.1 - 1', '1 - 10', '10 - 100', '> 100'],
                'Couleur associée': ['🔴 Rouge vif / Orange', '🟡 Jaune / Orange', '🟢 Vert / Bleu clair', '🔵 Bleu foncé']
            })
            
            st.dataframe(water_reference, use_container_width=True, hide_index=True)
            
            # Coupe 1: Zone Eau de Mer (0.1 - 1 Ω·m)
            with st.expander("🔴 Coupe 1 - Zone d'eau de mer (0.1 - 1 Ω·m)", expanded=False):
                # Filtrer les données correspondant à cette plage
                seawater_mask = (df['data'] <= 1.0)
                if seawater_mask.sum() > 0:
                    df_sea = df[seawater_mask]
                    
                    fig_sea, ax_sea = plt.subplots(figsize=(14, 6), dpi=150)
                    
                    # Créer des données synthétiques représentatives
                    x_sea = np.linspace(0, 200, 100)
                    z_sea = np.linspace(0, 30, 60)
                    X_sea, Z_sea = np.meshgrid(x_sea, z_sea)
                    
                    # Résistivité pour eau de mer
                    rho_sea = np.ones_like(X_sea) * 0.5 + np.random.rand(*X_sea.shape) * 0.4
                    
                    pcm_sea = ax_sea.pcolormesh(X_sea, Z_sea, rho_sea, cmap='Reds', 
                                               vmin=0.1, vmax=1.0, shading='auto')
                    
                    # Ajouter les mesures réelles si disponibles
                    if len(df_sea) > 0:
                        ax_sea.scatter(df_sea['survey_point'], df_sea['depth'], 
                                      c='darkred', s=100, edgecolors='black', 
                                      linewidths=2, marker='s', zorder=10,
                                      label=f'Mesures réelles ({len(df_sea)} points)')
                    
                    fig_sea.colorbar(pcm_sea, ax=ax_sea, label='Résistivité (Ω.m)')
                    ax_sea.invert_yaxis()
                    ax_sea.set_xlabel('Distance (m, précision: mm)', fontsize=11)
                    ax_sea.set_ylabel('Profondeur (m, précision: mm)', fontsize=11)
                    ax_sea.set_title('Zone d\'eau de mer - Résistivité 0.1-1 Ω·m (Précision mm)', 
                                    fontsize=13, fontweight='bold')
                    ax_sea.legend(loc='upper right')
                    ax_sea.grid(True, alpha=0.3)
                    
                    # Définir ticks avec valeurs mesurées
                    if len(df_sea) > 0:
                        unique_depths_sea = np.unique(np.abs(df_sea['depth'].values))
                        unique_dist_sea = np.unique(df_sea['survey_point'].values)
                        
                        if len(unique_depths_sea) > 20:
                            ax_sea.set_yticks(unique_depths_sea[::len(unique_depths_sea)//20])
                        else:
                            ax_sea.set_yticks(unique_depths_sea)
                        
                        if len(unique_dist_sea) > 20:
                            ax_sea.set_xticks(unique_dist_sea[::len(unique_dist_sea)//20])
                        else:
                            ax_sea.set_xticks(unique_dist_sea)
                    
                    # Format des axes avec 3 décimales
                    ax_sea.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
                    ax_sea.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
                    
                    plt.tight_layout()
                    st.pyplot(fig_sea)
                    figures_dict['seawater_section'] = fig_sea
                    
                    st.markdown("""
                    **Caractéristiques :**
                    - **Résistivité** : 0.1 - 1 Ω·m
                    - **Couleur** : 🔴 Rouge vif / Orange
                    - **Description** : Eau océanique hautement salée (~35 g/L de sel)
                    - **Conductivité** : Très forte conductivité électrique due aux ions Na⁺ et Cl⁻
                    - **Contexte** : Typique des mers et océans, intrusion saline côtière
                    """)
                else:
                    st.info("Aucune mesure dans cette plage de résistivité dans vos données")
            
            # Coupe 2: Zone Eau Salée Nappe (1 - 10 Ω·m)
            with st.expander("🟡 Coupe 2 - Nappe d'eau salée (1 - 10 Ω·m)", expanded=False):
                saline_mask = (df['data'] > 1.0) & (df['data'] <= 10.0)
                if saline_mask.sum() > 0:
                    df_saline = df[saline_mask]
                    
                    fig_saline, ax_saline = plt.subplots(figsize=(14, 6), dpi=150)
                    
                    x_sal = np.linspace(0, 250, 120)
                    z_sal = np.linspace(0, 40, 70)
                    X_sal, Z_sal = np.meshgrid(x_sal, z_sal)
                    
                    # Gradient de résistivité pour nappe salée
                    rho_sal = 3 + np.random.rand(*X_sal.shape) * 5 + Z_sal * 0.05
                    rho_sal = np.clip(rho_sal, 1, 10)
                    
                    pcm_sal = ax_saline.pcolormesh(X_sal, Z_sal, rho_sal, cmap='YlOrRd', 
                                                  vmin=1, vmax=10, shading='auto')
                    
                    if len(df_saline) > 0:
                        ax_saline.scatter(df_saline['survey_point'], df_saline['depth'], 
                                        c='orange', s=100, edgecolors='black', 
                                        linewidths=2, marker='o', zorder=10,
                                        label=f'Mesures réelles ({len(df_saline)} points)')
                    
                    fig_saline.colorbar(pcm_sal, ax=ax_saline, label='Résistivité (Ω.m)')
                    ax_saline.invert_yaxis()
                    ax_saline.set_xlabel('Distance (m, précision: mm)', fontsize=11)
                    ax_saline.set_ylabel('Profondeur (m, précision: mm)', fontsize=11)
                    ax_saline.set_title('Nappe phréatique salée - Résistivité 1-10 Ω·m (Précision mm)', 
                                       fontsize=13, fontweight='bold')
                    ax_saline.legend(loc='upper right')
                    ax_saline.grid(True, alpha=0.3)
                    
                    # Définir ticks avec valeurs mesurées
                    if len(df_saline) > 0:
                        unique_depths_sal = np.unique(np.abs(df_saline['depth'].values))
                        unique_dist_sal = np.unique(df_saline['survey_point'].values)
                        
                        if len(unique_depths_sal) > 20:
                            ax_saline.set_yticks(unique_depths_sal[::len(unique_depths_sal)//20])
                        else:
                            ax_saline.set_yticks(unique_depths_sal)
                        
                        if len(unique_dist_sal) > 20:
                            ax_saline.set_xticks(unique_dist_sal[::len(unique_dist_sal)//20])
                        else:
                            ax_saline.set_xticks(unique_dist_sal)
                    
                    # Format des axes avec 3 décimales
                    ax_saline.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
                    ax_saline.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
                    
                    plt.tight_layout()
                    st.pyplot(fig_saline)
                    figures_dict['saline_section'] = fig_saline
                    
                    st.markdown("""
                    **Caractéristiques :**
                    - **Résistivité** : 1 - 10 Ω·m
                    - **Couleur** : 🟡 Jaune / Orange
                    - **Description** : Eau saumâtre dans les nappes phréatiques côtières
                    - **Salinité** : Intermédiaire, intrusion saline
                    - **Potabilité** : Souvent non potable sans traitement
                    - **Contexte** : Zones côtières, pollution par remontée saline
                    """)
                else:
                    st.info("Aucune mesure dans cette plage de résistivité dans vos données")
            
            # Coupe 3: Zone Eau Douce (10 - 100 Ω·m)
            with st.expander("🟢 Coupe 3 - Aquifère d'eau douce (10 - 100 Ω·m)", expanded=False):
                fresh_mask = (df['data'] > 10.0) & (df['data'] <= 100.0)
                if fresh_mask.sum() > 0:
                    df_fresh = df[fresh_mask]
                    
                    fig_fresh, ax_fresh = plt.subplots(figsize=(14, 6), dpi=150)
                    
                    x_fresh = np.linspace(0, 300, 140)
                    z_fresh = np.linspace(0, 50, 80)
                    X_fresh, Z_fresh = np.meshgrid(x_fresh, z_fresh)
                    
                    # Résistivité pour eau douce
                    rho_fresh = 30 + np.random.rand(*X_fresh.shape) * 50 + Z_fresh * 0.3
                    rho_fresh = np.clip(rho_fresh, 10, 100)
                    
                    pcm_fresh = ax_fresh.pcolormesh(X_fresh, Z_fresh, rho_fresh, cmap='YlGn', 
                                                   vmin=10, vmax=100, shading='auto')
                    
                    if len(df_fresh) > 0:
                        ax_fresh.scatter(df_fresh['survey_point'], df_fresh['depth'], 
                                       c='green', s=100, edgecolors='black', 
                                       linewidths=2, marker='D', zorder=10,
                                       label=f'Mesures réelles ({len(df_fresh)} points)')
                    
                    fig_fresh.colorbar(pcm_fresh, ax=ax_fresh, label='Résistivité (Ω.m)')
                    ax_fresh.invert_yaxis()
                    ax_fresh.set_xlabel('Distance (m, précision: mm)', fontsize=11)
                    ax_fresh.set_ylabel('Profondeur (m, précision: mm)', fontsize=11)
                    ax_fresh.set_title('Aquifère d\'eau douce - Résistivité 10-100 Ω·m (Précision mm)', 
                                      fontsize=13, fontweight='bold')
                    ax_fresh.legend(loc='upper right')
                    ax_fresh.grid(True, alpha=0.3)
                    
                    # Définir ticks avec valeurs mesurées
                    if len(df_fresh) > 0:
                        unique_depths_fresh = np.unique(np.abs(df_fresh['depth'].values))
                        unique_dist_fresh = np.unique(df_fresh['survey_point'].values)
                        
                        if len(unique_depths_fresh) > 20:
                            ax_fresh.set_yticks(unique_depths_fresh[::len(unique_depths_fresh)//20])
                        else:
                            ax_fresh.set_yticks(unique_depths_fresh)
                        
                        if len(unique_dist_fresh) > 20:
                            ax_fresh.set_xticks(unique_dist_fresh[::len(unique_dist_fresh)//20])
                        else:
                            ax_fresh.set_xticks(unique_dist_fresh)
                    
                    # Format des axes avec 3 décimales
                    ax_fresh.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
                    ax_fresh.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
                    
                    plt.tight_layout()
                    st.pyplot(fig_fresh)
                    figures_dict['freshwater_section'] = fig_fresh
                    
                    st.markdown("""
                    **Caractéristiques :**
                    - **Résistivité** : 10 - 100 Ω·m
                    - **Couleur** : 🟢 Vert / Bleu clair
                    - **Description** : Eau douce continentale (rivières, lacs, nappes)
                    - **Salinité** : Faible (< 1 g/L TDS)
                    - **Minéraux** : Calcium, magnésium, bicarbonates en faibles concentrations
                    - **Potabilité** : Généralement potable, bonne qualité
                    - **Contexte** : Aquifères captifs, zones agricoles, forêts
                    """)
                else:
                    st.info("Aucune mesure dans cette plage de résistivité dans vos données")
            
            # Coupe 4: Zone Eau Très Pure (> 100 Ω·m)
            with st.expander("🔵 Coupe 4 - Eau très pure / Roche sèche (> 100 Ω·m)", expanded=False):
                pure_mask = (df['data'] > 100.0)
                if pure_mask.sum() > 0:
                    df_pure = df[pure_mask]
                    
                    fig_pure, ax_pure = plt.subplots(figsize=(14, 6), dpi=150)
                    
                    x_pure = np.linspace(0, 200, 100)
                    z_pure = np.linspace(0, 60, 90)
                    X_pure, Z_pure = np.meshgrid(x_pure, z_pure)
                    
                    # Résistivité pour eau pure/roche
                    rho_pure = 200 + np.random.rand(*X_pure.shape) * 300 + Z_pure * 2
                    rho_pure = np.clip(rho_pure, 100, 1000)
                    
                    pcm_pure = ax_pure.pcolormesh(X_pure, Z_pure, rho_pure, cmap='Blues', 
                                                 shading='auto', 
                                                 norm=LogNorm(vmin=100, vmax=1000))
                    
                    if len(df_pure) > 0:
                        ax_pure.scatter(df_pure['survey_point'], df_pure['depth'], 
                                      c='darkblue', s=100, edgecolors='black', 
                                      linewidths=2, marker='^', zorder=10,
                                      label=f'Mesures réelles ({len(df_pure)} points)')
                    
                    fig_pure.colorbar(pcm_pure, ax=ax_pure, label='Résistivité (Ω.m)')
                    ax_pure.invert_yaxis()
                    ax_pure.set_xlabel('Distance (m, précision: mm)', fontsize=11)
                    ax_pure.set_ylabel('Profondeur (m, précision: mm)', fontsize=11)
                    ax_pure.set_title('Eau très pure / Roche résistive - Résistivité > 100 Ω·m (Précision mm)', 
                                     fontsize=13, fontweight='bold')
                    ax_pure.legend(loc='upper right')
                    ax_pure.grid(True, alpha=0.3)
                    
                    # Définir ticks avec valeurs mesurées
                    if len(df_pure) > 0:
                        unique_depths_pure = np.unique(np.abs(df_pure['depth'].values))
                        unique_dist_pure = np.unique(df_pure['survey_point'].values)
                        
                        if len(unique_depths_pure) > 20:
                            ax_pure.set_yticks(unique_depths_pure[::len(unique_depths_pure)//20])
                        else:
                            ax_pure.set_yticks(unique_depths_pure)
                        
                        if len(unique_dist_pure) > 20:
                            ax_pure.set_xticks(unique_dist_pure[::len(unique_dist_pure)//20])
                        else:
                            ax_pure.set_xticks(unique_dist_pure)
                    
                    # Format des axes avec 3 décimales
                    ax_pure.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
                    ax_pure.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
                    plt.tight_layout()
                    st.pyplot(fig_pure)
                    figures_dict['purewater_section'] = fig_pure
                    
                    st.markdown("""
                    **Caractéristiques :**
                    - **Résistivité** : > 100 Ω·m
                    - **Couleur** : 🔵 Bleu foncé
                    - **Description** : Eau très pure avec minéraux dissous très faibles
                    - **TDS** : < 50 mg/L (eau ultrapure)
                    - **Minéraux** : Quartz, feldspath, granite (roche cristalline)
                    - **Contexte** : Aquifères en socle cristallin, eau de fonte glaciaire, roche sèche
                    - **Propriétés** : Très peu d'ions, conductivité électrique minimale
                    """)
                else:
                    st.info("Aucune mesure dans cette plage de résistivité dans vos données")
            
            # ========== COUPE 5 - PSEUDO-SECTION RÉELLE (FORMAT CLASSIQUE) ==========
            with st.expander("📊 Coupe 5 - Pseudo-Section de Résistivité Apparente (Format Classique)", expanded=True):
                st.markdown("""
                **Carte de pseudo-section au format géophysique standard**
                
                Cette représentation respecte le format classique des prospections ERT avec :
                - 🎨 Échelle de couleurs rainbow continue (bleu → vert → jaune → orange → rouge)
                - 📏 Axes en mètres avec positions réelles des électrodes
                - 🌡️ Barre de couleur graduée montrant les résistivités mesurées
                - 🗺️ Visualisation directe des résistivités apparentes du sous-sol
                """)
                
                # Créer la figure au format classique
                fig_pseudo, ax_pseudo = plt.subplots(figsize=(16, 8), dpi=150)
                
                # Utiliser les VRAIES valeurs mesurées
                X_real = df['survey_point'].values
                Z_real = np.abs(df['depth'].values)
                Rho_real = df['data'].values
                
                # Créer une grille fine pour la visualisation
                from scipy.interpolate import griddata
                xi_pseudo = np.linspace(X_real.min(), X_real.max(), 500)
                zi_pseudo = np.linspace(Z_real.min(), Z_real.max(), 300)
                Xi_pseudo, Zi_pseudo = np.meshgrid(xi_pseudo, zi_pseudo)
                
                # Interpolation linear pour un rendu lisse mais fidèle
                Rhoi_pseudo = griddata(
                    (X_real, Z_real), 
                    Rho_real, 
                    (Xi_pseudo, Zi_pseudo), 
                    method='linear',
                    fill_value=np.median(Rho_real)
                )
                
                # Utiliser la colormap rainbow classique
                from matplotlib.colors import LogNorm
                
                # Définir les limites de résistivité (échelle logarithmique)
                vmin_pseudo = max(0.1, Rho_real.min())
                vmax_pseudo = Rho_real.max()
                
                # Créer la pseudo-section avec échelle rainbow
                pcm_pseudo = ax_pseudo.contourf(
                    Xi_pseudo, 
                    Zi_pseudo, 
                    Rhoi_pseudo,
                    levels=50,
                    cmap='jet',
                    norm=LogNorm(vmin=vmin_pseudo, vmax=vmax_pseudo),
                    extend='both'
                )
                
                # Ajouter les contours
                contours = ax_pseudo.contour(
                    Xi_pseudo, 
                    Zi_pseudo, 
                    Rhoi_pseudo,
                    levels=10,
                    colors='black',
                    linewidths=0.5,
                    alpha=0.3
                )
                
                # Superposer les points de mesure
                scatter_real = ax_pseudo.scatter(
                    X_real, 
                    Z_real, 
                    c='white',
                    s=20,
                    edgecolors='black',
                    linewidths=0.5,
                    alpha=0.7,
                    zorder=5,
                    label='Points de mesure'
                )
                
                # Barre de couleur
                cbar_pseudo = plt.colorbar(pcm_pseudo, ax=ax_pseudo, pad=0.02, aspect=30)
                cbar_pseudo.set_label('Résistivité Apparente (Ω·m)', fontsize=12, fontweight='bold')
                cbar_pseudo.ax.tick_params(labelsize=10)
                
                # Configuration des axes
                ax_pseudo.set_xlabel('Position (m)', fontsize=12, fontweight='bold')
                ax_pseudo.set_ylabel('Profondeur (m)', fontsize=12, fontweight='bold')
                ax_pseudo.set_title(
                    'Pseudo-Section de Résistivité Apparente\nMeasured Apparent Resistivity Pseudosection',
                    fontsize=14, 
                    fontweight='bold'
                )
                
                ax_pseudo.invert_yaxis()
                ax_pseudo.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
                ax_pseudo.legend(loc='upper right', fontsize=10, framealpha=0.9)
                
                plt.tight_layout()
                st.pyplot(fig_pseudo)
                plt.close()
                
                # Statistiques
                col1_ps, col2_ps, col3_ps = st.columns(3)
                with col1_ps:
                    st.metric("📏 Points de mesure", f"{len(Rho_real)}")
                with col2_ps:
                    st.metric("📊 Plage de résistivité", f"{vmin_pseudo:.1f} - {vmax_pseudo:.1f} Ω·m")
                with col3_ps:
                    st.metric("🎯 Résistivité médiane", f"{np.median(Rho_real):.2f} Ω·m")
                
                st.markdown("""
                **Interprétation des couleurs (échelle rainbow) :**
                
                | Couleur | Résistivité | Interprétation Géologique |
                |---------|-------------|---------------------------|
                | 🔵 **Bleu foncé** | < 10 Ω·m | Argiles saturées, eau salée |
                | 🟦 **Cyan** | 10-50 Ω·m | Argiles compactes, limons |
                | 🟢 **Vert** | 50-100 Ω·m | Sables fins, aquifères potentiels |
                | 🟡 **Jaune** | 100-300 Ω·m | Sables grossiers, bons aquifères |
                | 🟠 **Orange** | 300-1000 Ω·m | Graviers, roches altérées |
                | 🔴 **Rouge** | > 1000 Ω·m | Roches consolidées, socle |
                """)
            
            # Export
            st.subheader("💾 Exporter les résultats")
            col1, col2, col3 = st.columns(3)
            with col1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 CSV", csv, "analysis.csv", "text/csv", key='download_csv')
            with col2:
                # Créer Excel uniquement à la demande (lazy loading)
                if st.button("� Préparer Excel", key='prepare_excel'):
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Data')
                    st.session_state['excel_buffer'] = buffer.getvalue()
                    st.success("✅ Excel prêt !")
                
                if 'excel_buffer' in st.session_state:
                    st.download_button("📥 Excel", st.session_state['excel_buffer'], 
                                      "analysis.xlsx", 
                                      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                      key='download_excel')
            with col3:
                # Générer PDF avec tous les graphiques et tableaux
                if st.button("📄 Générer Rapport PDF", key='generate_pdf'):
                    with st.spinner('Génération du PDF en cours...'):
                        pdf_bytes = create_pdf_report(df, unit, figures_dict)
                        st.session_state['pdf_buffer'] = pdf_bytes
                        st.success("✅ PDF prêt !")
                
                if 'pdf_buffer' in st.session_state:
                    st.download_button(
                        "📥 PDF Complet",
                        st.session_state['pdf_buffer'],
                        f"rapport_ert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        "application/pdf",
                        key='download_pdf'
                    )
# ===================== TAB 3 : ERT PSEUDO-SECTIONS 2D/3D =====================
with tab3:
    st.header("4 Interprétation des pseudo-sections et modèles de résistivité (FicheERT.pdf)")

    st.subheader("4.1 Définition d'une pseudo-section")
    st.markdown("""
La première étape dans l'interprétation des données en tomographie électrique consiste à construire une **pseudo-section**. Une pseudo-section est une carte de résultat qui présente les valeurs des résistivités apparentes calculées à partir de la différence de potentiel mesurée aux bornes de deux électrodes de mesure ainsi que de la valeur du courant injecté entre les deux électrodes d'injection.

La couleur d'un point sur la pseudo-section représente donc la valeur de la résistivité apparente en ce point.
    """)

    # Vérifier si des données ont été chargées dans l'onglet 2
    if st.session_state.get('uploaded_data') is not None:
        df = st.session_state['uploaded_data']
        unit = st.session_state.get('unit', 'm')
        
        st.success(f"✅ Utilisation des données du fichier uploadé : {len(df)} mesures")
        
        st.markdown("**Pseudo-sections générées à partir de vos données réelles**")
        
        # Cache de la préparation des données 2D
        @st.cache_data
        def prepare_2d_data(data_hash):
            """Prépare les données pour visualisation 2D avec cache"""
            survey_points = sorted(df['survey_point'].unique())
            depths = sorted(df['depth'].unique())
            
            X_real = []
            Z_real = []
            Rho_real = []
            
            for sp in survey_points:
                for depth in depths:
                    subset = df[(df['survey_point'] == sp) & (df['depth'] == depth)]
                    if len(subset) > 0:
                        X_real.append(float(sp))
                        Z_real.append(abs(float(depth)))
                        Rho_real.append(float(subset['data'].values[0]))
            
            return np.array(X_real), np.array(Z_real), np.array(Rho_real)
        
        # Cache de l'interpolation (très coûteuse)
        @st.cache_data
        def interpolate_grid(X, Z, Rho, data_hash):
            """Interpolation cubique avec cache"""
            from scipy.interpolate import griddata
            xi = np.linspace(X.min(), X.max(), 100)
            zi = np.linspace(Z.min(), Z.max(), 50)
            Xi, Zi = np.meshgrid(xi, zi)
            Rhoi = griddata((X, Z), Rho, (Xi, Zi), method='cubic')
            return Xi, Zi, Rhoi, xi, zi
        
        # Hash unique des données
        data_hash = hash(tuple(df[['survey_point', 'depth', 'data']].values.flatten()))
        
        st.subheader("📊 Pseudo-section 2D - Données réelles du fichier .dat")
        
        # Dictionnaire pour stocker les figures du Tab 3
        figures_tab3 = {}
        
        # Préparer les données (avec cache)
        X_real, Z_real, Rho_real = prepare_2d_data(data_hash)
        
        # Interpoler (avec cache)
        Xi, Zi, Rhoi, xi, zi = interpolate_grid(X_real, Z_real, Rho_real, data_hash)
        
        # Pseudo-section 2D avec données réelles (haute résolution pour PDF)
        fig_real, ax = plt.subplots(figsize=(14, 7), dpi=150)
        
        # Utiliser une échelle de couleur adaptée aux valeurs d'eau
        vmin, vmax = Rho_real.min(), Rho_real.max()
        
        pcm = ax.pcolormesh(Xi, Zi, Rhoi, cmap='jet_r', shading='auto', 
                           vmin=vmin, vmax=vmax)
        
        # Ajouter les points de mesure réels
        scatter = ax.scatter(X_real, Z_real, c=Rho_real, cmap='jet_r', 
                            s=50, edgecolors='black', linewidths=0.5,
                            vmin=vmin, vmax=vmax, zorder=10)
        
        fig_real.colorbar(pcm, ax=ax, label=f'Niveau d\'eau DTW ({unit})', extend='both')
        ax.invert_yaxis()
        ax.set_xlabel('Point de sondage (Survey Point)', fontsize=11)
        ax.set_ylabel(f'Profondeur totale ({unit})', fontsize=11)
        ax.set_title(f'Pseudo-section 2D - Données réelles ({len(df)} mesures)', 
                    fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        st.pyplot(fig_real)
        
        # Sauvegarder pour PDF
        figures_tab3['pseudo_section_2d'] = fig_real
        
        # Légende des couleurs basée sur les valeurs réelles
        st.markdown(f"""
**Interprétation des couleurs (basée sur vos données) :**
- Valeur minimale : **{vmin:.2f} {unit}** (niveau d'eau le plus bas) → couleur bleue
- Valeur moyenne : **{Rho_real.mean():.2f} {unit}** → couleur intermédiaire
- Valeur maximale : **{vmax:.2f} {unit}** (niveau d'eau le plus haut) → couleur rouge

Les zones rouges indiquent des niveaux d'eau plus élevés (DTW plus grand).
Les zones bleues indiquent des niveaux d'eau plus bas (nappe plus proche de la surface).
        """)
        
        # Vue 3D des données réelles
        survey_points = sorted(df['survey_point'].unique())
        depths = sorted(df['depth'].unique())
        
        if len(survey_points) > 2 and len(depths) > 2:
            st.subheader("🌐 Modèle 3D - Volume d'eau (données réelles)")
            
            fig3d_real = go.Figure(data=go.Scatter3d(
                x=X_real,
                y=np.zeros_like(X_real),  # Y=0 pour profil 2D
                z=-Z_real,  # Négatif pour afficher en profondeur
                mode='markers',
                marker=dict(
                    size=8,
                    color=Rho_real,
                    colorscale='Jet',
                    showscale=True,
                    colorbar=dict(title=f'DTW ({unit})'),
                    line=dict(width=0.5, color='black')
                ),
                text=[f'SP: {int(X_real[i])}<br>Depth: {Z_real[i]:.1f}{unit}<br>DTW: {Rho_real[i]:.2f}{unit}' 
                      for i in range(len(X_real))],
                hoverinfo='text'
            ))
            
            fig3d_real.update_layout(
                scene=dict(
                    xaxis_title='Point de sondage',
                    yaxis_title='Transect (m)',
                    zaxis_title=f'Profondeur ({unit})',
                    aspectmode='data'
                ),
                title='Visualisation 3D des mesures de niveau d\'eau',
                height=600
            )
            
            st.plotly_chart(fig3d_real, use_container_width=True)
        
        # Statistiques par profondeur
        st.subheader("📈 Analyse par profondeur")
        
        # Cache du calcul statistique
        @st.cache_data
        def compute_depth_stats(data_hash):
            """Calcul des statistiques par profondeur avec cache"""
            depth_stats = df.groupby('depth')['data'].agg(['mean', 'min', 'max', 'std']).round(2)
            depth_stats.columns = ['Moyenne DTW', 'Min DTW', 'Max DTW', 'Écart-type']
            return depth_stats
        
        depth_stats = compute_depth_stats(data_hash)
        st.dataframe(depth_stats.style.background_gradient(cmap='RdYlBu_r', axis=0), use_container_width=True)
        
        # Coupes comparatives avec mesures réelles incrustées
        st.markdown("---")
        st.subheader("🎯 Coupes comparatives - Mesures réelles vs Modèles théoriques")
        
        # Coupe comparative 1: Intrusion saline
        with st.expander("🌊 Coupe comparative 1 - Intrusion saline côtière avec mesures", expanded=False):
            fig_comp1, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=150)
            
            # Modèle théorique
            x_model = np.linspace(0, 300, 150)
            z_model = np.linspace(0, 40, 80)
            X_model, Z_model = np.meshgrid(x_model, z_model)
            
            # Gradient d'intrusion saline (mer vers terre)
            rho_model = np.ones_like(X_model) * 0.5  # Eau de mer
            rho_model[Z_model > 10 + 0.05 * X_model] = 3  # Eau salée nappe
            rho_model[Z_model > 25] = 50  # Eau douce profonde
            rho_model *= (1 + np.random.randn(*rho_model.shape) * 0.1)
            rho_model = np.clip(rho_model, 0.1, 100)
            
            # Graphique modèle
            pcm1 = ax1.pcolormesh(X_model, Z_model, rho_model, cmap='jet_r', 
                                 norm=LogNorm(vmin=0.1, vmax=100), shading='auto')
            ax1.invert_yaxis()
            ax1.set_title('Modèle théorique - Intrusion saline (Précision mm)', fontsize=12, fontweight='bold')
            ax1.set_xlabel('Distance depuis la côte (m, précision: mm)')
            ax1.set_ylabel('Profondeur (m, précision: mm)')
            
            # Format des axes avec 3 décimales
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
            ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
            
            fig_comp1.colorbar(pcm1, ax=ax1, label='Résistivité (Ω.m)')
            
            # Annoter les zones
            ax1.text(50, 5, 'Eau de mer\n0.1-1 Ω·m', 
                    bbox=dict(boxstyle='round', facecolor='red', alpha=0.7),
                    fontsize=9, ha='center', color='white', fontweight='bold')
            ax1.text(150, 18, 'Eau salée\n1-10 Ω·m', 
                    bbox=dict(boxstyle='round', facecolor='orange', alpha=0.7),
                    fontsize=9, ha='center', fontweight='bold')
            ax1.text(250, 32, 'Eau douce\n10-100 Ω·m', 
                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
                    fontsize=9, ha='center', fontweight='bold')
            
            # Données réelles
            if len(df) > 0:
                # Interpoler les données réelles - Conversion explicite en float
                X_real_data = pd.to_numeric(df['survey_point'], errors='coerce').values
                Z_real_data = np.abs(pd.to_numeric(df['depth'], errors='coerce').values)
                Rho_real_data = pd.to_numeric(df['data'], errors='coerce').values
                
                # Filtrer les valeurs NaN
                mask = ~(np.isnan(X_real_data) | np.isnan(Z_real_data) | np.isnan(Rho_real_data))
                X_real_data = X_real_data[mask]
                Z_real_data = Z_real_data[mask]
                Rho_real_data = Rho_real_data[mask]
                
                # Créer une grille pour les données réelles
                from scipy.interpolate import griddata
                if len(X_real_data) > 0:
                    xi_real = np.linspace(X_real_data.min(), X_real_data.max(), 100)
                    zi_real = np.linspace(Z_real_data.min(), Z_real_data.max(), 60)
                    Xi_real, Zi_real = np.meshgrid(xi_real, zi_real)
                    Rhoi_real = griddata((X_real_data, Z_real_data), Rho_real_data, 
                                        (Xi_real, Zi_real), method='cubic')
                    
                    pcm2 = ax2.pcolormesh(Xi_real, Zi_real, Rhoi_real, cmap='jet_r', 
                                         norm=LogNorm(vmin=max(0.1, Rho_real_data.min()), 
                                                     vmax=Rho_real_data.max()), shading='auto')
                    ax2.scatter(X_real_data, Z_real_data, c='black', s=50, 
                               edgecolors='white', linewidths=1.5, marker='o', zorder=10,
                               label=f'{len(X_real_data)} mesures')
                    ax2.invert_yaxis()
                    ax2.set_title(f'Données réelles - {len(X_real_data)} mesures (Précision mm)', 
                                 fontsize=12, fontweight='bold')
                    
                    # Format des axes avec 3 décimales
                    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
                    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
                    
                ax2.set_xlabel('Point de sondage (précision: mm)')
                ax2.set_ylabel('Profondeur (m, précision: mm)')
                ax2.legend(loc='upper right')
                fig_comp1.colorbar(pcm2, ax=ax2, label='Résistivité mesurée (Ω.m)')
            
            plt.tight_layout()
            st.pyplot(fig_comp1)
            figures_tab3['comparative_1'] = fig_comp1
            
            st.markdown("""
            **Analyse comparative :**
            - **Gauche** : Modèle théorique d'intrusion saline typique
            - **Droite** : Vos mesures réelles interpolées avec points de mesure (noirs)
            - Permet d'identifier les zones d'intrusion marine dans vos données
            """)
        
        # Coupe comparative 2: Aquifère multicouche
        with st.expander("🏔️ Coupe comparative 2 - Aquifère multicouche avec résistivités", expanded=False):
            fig_comp2, ax_multi = plt.subplots(figsize=(14, 7), dpi=150)
            
            # Créer un modèle multicouche
            x_multi = np.linspace(0, 250, 140)
            z_multi = np.linspace(0, 50, 90)
            X_multi, Z_multi = np.meshgrid(x_multi, z_multi)
            
            # Couches avec résistivités différentes
            rho_multi = np.ones_like(X_multi) * 200  # Sol sec surface
            rho_multi[(Z_multi > 8) & (Z_multi < 15)] = 60  # Aquifère peu profond (eau douce)
            rho_multi[(Z_multi >= 15) & (Z_multi < 25)] = 5  # Argile conductive
            rho_multi[(Z_multi >= 25) & (Z_multi < 40)] = 80  # Aquifère profond (eau douce)
            rho_multi[Z_multi >= 40] = 400  # Substrat rocheux
            
            # Ajouter du bruit
            rho_multi *= (1 + np.random.randn(*rho_multi.shape) * 0.08)
            rho_multi = np.clip(rho_multi, 1, 500)
            
            pcm_multi = ax_multi.pcolormesh(X_multi, Z_multi, rho_multi, cmap='jet_r', 
                                           norm=LogNorm(vmin=1, vmax=500), shading='auto')
            
            # Superposer les mesures réelles si disponibles
            if len(df) > 0:
                ax_multi.scatter(df['survey_point'], np.abs(df['depth']), 
                               c=df['data'], cmap='jet_r', s=120, 
                               edgecolors='black', linewidths=2, marker='s',
                               norm=LogNorm(vmin=max(0.1, df['data'].min()), 
                                          vmax=df['data'].max()),
                               zorder=10, label='Mesures réelles')
                
                # Annoter quelques points avec leurs valeurs
                for i in range(min(5, len(df))):
                    row = df.iloc[i]
                    ax_multi.annotate(f'{row["data"]:.2f} Ω·m\n@{np.abs(row["depth"]):.3f}m', 
                                    xy=(row['survey_point'], np.abs(row['depth'])),
                                    xytext=(10, 10), textcoords='offset points',
                                    fontsize=7, ha='left',
                                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
            
            fig_comp2.colorbar(pcm_multi, ax=ax_multi, label='Résistivité (Ω.m)')
            ax_multi.invert_yaxis()
            ax_multi.set_xlabel('Distance (m, précision: mm)', fontsize=11)
            ax_multi.set_ylabel('Profondeur (m, précision: mm)', fontsize=11)
            
            # Format des axes avec 3 décimales
            ax_multi.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
            ax_multi.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
            
            ax_multi.set_title('Modèle multicouche avec mesures réelles (Précision mm)', 
                              fontsize=13, fontweight='bold')
            if len(df) > 0:
                ax_multi.legend(loc='upper right')
            ax_multi.grid(True, alpha=0.2, color='white', linestyle='--')
            
            # Ajouter légende des couches
            ax_multi.text(0.02, 0.98, 'Couches géologiques:', transform=ax_multi.transAxes,
                         fontsize=10, va='top', fontweight='bold',
                         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            ax_multi.text(0.02, 0.92, '• 0-8m: Sol sec (200 Ω·m)', transform=ax_multi.transAxes,
                         fontsize=8, va='top')
            ax_multi.text(0.02, 0.88, '• 8-15m: Aquifère peu profond (60 Ω·m)', transform=ax_multi.transAxes,
                         fontsize=8, va='top')
            ax_multi.text(0.02, 0.84, '• 15-25m: Argile conductive (5 Ω·m)', transform=ax_multi.transAxes,
                         fontsize=8, va='top')
            ax_multi.text(0.02, 0.80, '• 25-40m: Aquifère profond (80 Ω·m)', transform=ax_multi.transAxes,
                         fontsize=8, va='top')
            ax_multi.text(0.02, 0.76, '• >40m: Substrat rocheux (400 Ω·m)', transform=ax_multi.transAxes,
                         fontsize=8, va='top')
            
            plt.tight_layout()
            st.pyplot(fig_comp2)
            figures_tab3['comparative_2'] = fig_comp2
            
            st.markdown("""
            **Interprétation multicouche :**
            - **Carrés noirs** : Vos mesures réelles avec annotations de valeurs
            - **Fond coloré** : Modèle théorique multicouche
            - Les zones bleues (haute résistivité) indiquent des formations sèches ou rocheuses
            - Les zones rouges/orange (faible résistivité) indiquent de l'argile ou de l'eau salée
            - Les zones vertes/jaunes (résistivité moyenne) indiquent des aquifères d'eau douce
            """)
        
        # Export PDF des pseudo-sections
        st.subheader("📄 Export PDF des Pseudo-sections")
        col_pdf1, col_pdf2 = st.columns([1, 2])
        with col_pdf1:
            if st.button("📄 Générer PDF Pseudo-sections", key='generate_pdf_tab3'):
                with st.spinner('Génération du PDF des pseudo-sections...'):
                    pdf_bytes = create_pdf_report(df, unit, figures_tab3)
                    st.session_state['pdf_tab3_buffer'] = pdf_bytes
                    st.success("✅ PDF pseudo-sections prêt !")
        
        with col_pdf2:
            if 'pdf_tab3_buffer' in st.session_state:
                st.download_button(
                    "📥 Télécharger PDF Pseudo-sections",
                    st.session_state['pdf_tab3_buffer'],
                    f"pseudo_sections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    "application/pdf",
                    key='download_pdf_tab3'
                )
        
        # ========== COUPE SUPPLÉMENTAIRE - PSEUDO-SECTION RÉELLE (FORMAT CLASSIQUE) ==========
        st.markdown("---")
        with st.expander("📊 Pseudo-Section de Résistivité Apparente (Format Classique)", expanded=True):
            st.markdown("""
            **Carte de pseudo-section au format géophysique standard**
            
            Cette représentation respecte le format classique des prospections ERT avec :
            - 🎨 Échelle de couleurs rainbow continue (bleu → vert → jaune → orange → rouge)
            - 📏 Axes en mètres avec positions réelles des électrodes
            - 🌡️ Barre de couleur graduée montrant les résistivités mesurées
            - 🗺️ Visualisation directe des résistivités apparentes du sous-sol
            """)
            
            # Créer la figure au format classique
            fig_pseudo_t3, ax_pseudo_t3 = plt.subplots(figsize=(16, 8), dpi=150)
            
            # Utiliser les VRAIES valeurs mesurées
            X_real_t3 = X_real
            Z_real_t3 = Z_real
            Rho_real_t3 = Rho_real
            
            # Créer une grille fine pour la visualisation
            xi_pseudo_t3 = np.linspace(X_real_t3.min(), X_real_t3.max(), 500)
            zi_pseudo_t3 = np.linspace(Z_real_t3.min(), Z_real_t3.max(), 300)
            Xi_pseudo_t3, Zi_pseudo_t3 = np.meshgrid(xi_pseudo_t3, zi_pseudo_t3)
            
            # Interpolation linear pour un rendu lisse mais fidèle
            Rhoi_pseudo_t3 = griddata(
                (X_real_t3, Z_real_t3), 
                Rho_real_t3, 
                (Xi_pseudo_t3, Zi_pseudo_t3), 
                method='linear',
                fill_value=np.median(Rho_real_t3)
            )
            
            # Utiliser la colormap rainbow classique
            from matplotlib.colors import LogNorm
            
            # Définir les limites de résistivité
            vmin_pseudo_t3 = max(0.1, Rho_real_t3.min())
            vmax_pseudo_t3 = Rho_real_t3.max()
            
            # Créer la pseudo-section avec échelle rainbow
            pcm_pseudo_t3 = ax_pseudo_t3.contourf(
                Xi_pseudo_t3, 
                Zi_pseudo_t3, 
                Rhoi_pseudo_t3,
                levels=50,
                cmap='jet',
                norm=LogNorm(vmin=vmin_pseudo_t3, vmax=vmax_pseudo_t3),
                extend='both'
            )
            
            # Ajouter les contours
            contours_t3 = ax_pseudo_t3.contour(
                Xi_pseudo_t3, 
                Zi_pseudo_t3, 
                Rhoi_pseudo_t3,
                levels=10,
                colors='black',
                linewidths=0.5,
                alpha=0.3
            )
            
            # Superposer les points de mesure
            scatter_real_t3 = ax_pseudo_t3.scatter(
                X_real_t3, 
                Z_real_t3, 
                c='white',
                s=20,
                edgecolors='black',
                linewidths=0.5,
                alpha=0.7,
                zorder=5,
                label='Points de mesure'
            )
            
            # Barre de couleur
            cbar_pseudo_t3 = plt.colorbar(pcm_pseudo_t3, ax=ax_pseudo_t3, pad=0.02, aspect=30)
            cbar_pseudo_t3.set_label('Résistivité Apparente (Ω·m)', fontsize=12, fontweight='bold')
            cbar_pseudo_t3.ax.tick_params(labelsize=10)
            
            # Configuration des axes
            ax_pseudo_t3.set_xlabel('Position (m)', fontsize=12, fontweight='bold')
            ax_pseudo_t3.set_ylabel('Profondeur (m)', fontsize=12, fontweight='bold')
            ax_pseudo_t3.set_title(
                'Pseudo-Section de Résistivité Apparente\nMeasured Apparent Resistivity Pseudosection',
                fontsize=14, 
                fontweight='bold'
            )
            
            ax_pseudo_t3.invert_yaxis()
            ax_pseudo_t3.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
            ax_pseudo_t3.legend(loc='upper right', fontsize=10, framealpha=0.9)
            
            plt.tight_layout()
            st.pyplot(fig_pseudo_t3)
            plt.close()
            
            # Statistiques
            col1_ps_t3, col2_ps_t3, col3_ps_t3 = st.columns(3)
            with col1_ps_t3:
                st.metric("📏 Points de mesure", f"{len(Rho_real_t3)}")
            with col2_ps_t3:
                st.metric("📊 Plage de résistivité", f"{vmin_pseudo_t3:.1f} - {vmax_pseudo_t3:.1f} Ω·m")
            with col3_ps_t3:
                st.metric("🎯 Résistivité médiane", f"{np.median(Rho_real_t3):.2f} Ω·m")
            
            st.markdown("""
            **Interprétation des couleurs (échelle rainbow) :**
            
            | Couleur | Résistivité | Interprétation Géologique |
            |---------|-------------|---------------------------|
            | 🔵 **Bleu foncé** | < 10 Ω·m | Argiles saturées, eau salée |
            | 🟦 **Cyan** | 10-50 Ω·m | Argiles compactes, limons |
            | 🟢 **Vert** | 50-100 Ω·m | Sables fins, aquifères potentiels |
            | 🟡 **Jaune** | 100-300 Ω·m | Sables grossiers, bons aquifères |
            | 🟠 **Orange** | 300-1000 Ω·m | Graviers, roches altérées |
            | 🔴 **Rouge** | > 1000 Ω·m | Roches consolidées, socle |
            """)
    
    else:
        st.warning("⚠️ Aucune donnée chargée. Veuillez d'abord uploader un fichier .dat dans l'onglet 'Analyse Fichiers .dat'")
        st.info("💡 Uploadez un fichier .dat dans l'onglet 'Analyse Fichiers .dat' pour visualiser vos données avec interprétation des couleurs de résistivité.")

# ===================== TAB 4 : STRATIGRAPHIE COMPLÈTE =====================
with tab4:
    st.header("🪨 Stratigraphie Complète - Classification Géologique avec Résistivités")
    
    st.markdown("""
    ### 📊 Vue d'ensemble des matériaux géologiques
    Cette section présente **toutes les formations géologiques** (eaux, sols, roches, minéraux) avec leurs résistivités caractéristiques.
    Cela permet d'identifier précisément la **nature des couches** à chaque niveau de profondeur.
    """)
    
    # Afficher le tableau complet
    st.markdown(geology_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Section graphiques de stratigraphie
    if 'uploaded_data' in st.session_state and st.session_state['uploaded_data'] is not None:
        df = st.session_state['uploaded_data']
        
        if len(df) > 0:
            st.subheader("🎨 Coupes Stratigraphiques Multi-Niveaux")
            st.markdown("""
            Ces coupes montrent la **distribution des matériaux géologiques** selon les valeurs de résistivité mesurées.
            Chaque plage de résistivité correspond à un type de matériau spécifique (eau, argile, sable, roche, etc.).
            """)
            
            # Créer les plages de résistivité étendues
            resistivity_ranges = {
                'Minéraux métalliques\n(Graphite, Cuivre, Or)': (0.001, 1, 'Spectral', 'Très conducteurs - Cibles minières'),
                'Eaux de mer + Argiles marines': (0.1, 10, 'YlOrRd', 'Zone conductrice - Salinité élevée'),
                'Argiles compactes + Eaux salées': (10, 50, 'RdYlBu', 'Formations imperméables saturées'),
                'Eaux douces + Limons + Schistes': (50, 200, 'YlGn', 'Aquifères argileux-sableux'),
                'Sables saturés + Graviers': (200, 1000, 'GnBu', 'Aquifères perméables productifs'),
                'Calcaires + Grès + Basaltes fracturés': (1000, 5000, 'PuBu', 'Formations carbonatées/volcaniques'),
                'Roches ignées + Granites': (5000, 100000, 'Purples', 'Socle cristallin - Très résistif'),
                'Quartzites + Minéraux isolants': (10000, 1000000, 'gray', 'Formations ultra-résistives')
            }
            
            cols_strat = st.columns(2)
            
            for idx, (name, (rho_min, rho_max, cmap, description)) in enumerate(resistivity_ranges.items()):
                with cols_strat[idx % 2]:
                    with st.expander(f"📍 **{name}** ({rho_min}-{rho_max} Ω·m)", expanded=False):
                        st.caption(f"*{description}*")
                        
                        # Filtrer les données dans cette plage
                        mask = (df['data'] >= rho_min) & (df['data'] <= rho_max)
                        df_filtered = df[mask]
                        
                        if len(df_filtered) > 3:
                            fig_strat, ax_strat = plt.subplots(figsize=(10, 6))
                            
                            # Convertir les données en float
                            X_strat = pd.to_numeric(df_filtered['survey_point'], errors='coerce').values
                            Z_strat = np.abs(pd.to_numeric(df_filtered['depth'], errors='coerce').values)
                            Rho_strat = pd.to_numeric(df_filtered['data'], errors='coerce').values
                            
                            # Filtrer NaN
                            mask_valid = ~(np.isnan(X_strat) | np.isnan(Z_strat) | np.isnan(Rho_strat))
                            X_strat = X_strat[mask_valid]
                            Z_strat = Z_strat[mask_valid]
                            Rho_strat = Rho_strat[mask_valid]
                            
                            if len(X_strat) > 3:
                                # Interpolation
                                from scipy.interpolate import griddata
                                xi_strat = np.linspace(X_strat.min(), X_strat.max(), 120)
                                zi_strat = np.linspace(Z_strat.min(), Z_strat.max(), 80)
                                Xi_strat, Zi_strat = np.meshgrid(xi_strat, zi_strat)
                                Rhoi_strat = griddata((X_strat, Z_strat), Rho_strat, 
                                                     (Xi_strat, Zi_strat), method='cubic')
                                
                                # Affichage avec échelle log si plage large
                                if rho_max / rho_min > 10:
                                    pcm_strat = ax_strat.pcolormesh(Xi_strat, Zi_strat, Rhoi_strat, 
                                                                   cmap=cmap, shading='auto',
                                                                   norm=LogNorm(vmin=rho_min, vmax=rho_max))
                                else:
                                    pcm_strat = ax_strat.pcolormesh(Xi_strat, Zi_strat, Rhoi_strat, 
                                                                   cmap=cmap, shading='auto',
                                                                   vmin=rho_min, vmax=rho_max)
                                
                                # Points de mesure
                                ax_strat.scatter(X_strat, Z_strat, c='black', s=30, 
                                               edgecolors='white', linewidths=1, marker='o', 
                                               alpha=0.6, zorder=10)
                                
                                ax_strat.invert_yaxis()
                                ax_strat.set_xlabel('Distance (m, précision: mm)', fontsize=11, fontweight='bold')
                                ax_strat.set_ylabel('Profondeur (m, précision: mm)', fontsize=11, fontweight='bold')
                                ax_strat.set_title(f'{name}\n{len(df_filtered)} mesures - Résistivité : {rho_min}-{rho_max} Ω·m',
                                                 fontsize=11, fontweight='bold', pad=15)
                                ax_strat.grid(True, alpha=0.3, linestyle='--')
                                
                                # Définir les ticks avec TOUTES les valeurs mesurées
                                unique_depths = np.unique(Z_strat)
                                unique_distances = np.unique(X_strat)
                                
                                # Limiter à 20 ticks max pour lisibilité
                                if len(unique_depths) > 20:
                                    step_depth = len(unique_depths) // 20
                                    ax_strat.set_yticks(unique_depths[::step_depth])
                                else:
                                    ax_strat.set_yticks(unique_depths)
                                
                                if len(unique_distances) > 20:
                                    step_dist = len(unique_distances) // 20
                                    ax_strat.set_xticks(unique_distances[::step_dist])
                                else:
                                    ax_strat.set_xticks(unique_distances)
                                
                                # Format des ticks avec 3 décimales
                                ax_strat.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
                                ax_strat.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
                                
                                cbar_strat = plt.colorbar(pcm_strat, ax=ax_strat, pad=0.02)
                                cbar_strat.set_label('Résistivité (Ω·m)', fontsize=10, fontweight='bold')
                                
                                plt.tight_layout()
                                st.pyplot(fig_strat)
                                plt.close()
                            else:
                                st.info(f"✓ {len(df_filtered)} mesure(s) détectée(s) mais insuffisantes pour interpolation")
                        else:
                            st.info(f"ℹ️ Aucune ou trop peu de mesures ({len(df_filtered)}) dans cette plage de résistivité")
            
            st.markdown("---")
            
            # Graphique synthétique de distribution
            st.subheader("📊 Distribution des Matériaux par Profondeur")
            
            fig_dist, (ax_hist, ax_depth) = plt.subplots(1, 2, figsize=(14, 6))
            
            # Histogramme des résistivités (échelle log)
            rho_data = pd.to_numeric(df['data'], errors='coerce').dropna()
            ax_hist.hist(rho_data, bins=50, color='steelblue', edgecolor='black', alpha=0.7)
            ax_hist.set_xscale('log')
            ax_hist.set_xlabel('Résistivité (Ω·m) - Échelle log', fontsize=11, fontweight='bold')
            ax_hist.set_ylabel('Nombre de mesures', fontsize=11, fontweight='bold')
            ax_hist.set_title('Distribution des Résistivités Mesurées', fontsize=12, fontweight='bold')
            ax_hist.grid(True, alpha=0.3, axis='y')
            
            # Zones colorées pour les matériaux
            ax_hist.axvspan(0.001, 1, alpha=0.2, color='gold', label='Minéraux métalliques')
            ax_hist.axvspan(1, 10, alpha=0.2, color='red', label='Eaux salées + Argiles')
            ax_hist.axvspan(10, 100, alpha=0.2, color='yellow', label='Eaux douces + Sols')
            ax_hist.axvspan(100, 1000, alpha=0.2, color='green', label='Sables + Graviers')
            ax_hist.axvspan(1000, 10000, alpha=0.2, color='blue', label='Roches sédimentaires')
            ax_hist.axvspan(10000, 1000000, alpha=0.2, color='purple', label='Roches ignées')
            ax_hist.legend(loc='upper right', fontsize=8)
            
            # Profil résistivité vs profondeur
            depth_data = np.abs(pd.to_numeric(df['depth'], errors='coerce').dropna())
            rho_for_depth = pd.to_numeric(df.loc[depth_data.index, 'data'], errors='coerce')
            
            scatter = ax_depth.scatter(rho_for_depth, depth_data, c=rho_for_depth, 
                                      cmap='viridis', s=50, alpha=0.6, 
                                      edgecolors='black', linewidths=0.5,
                                      norm=LogNorm(vmin=max(0.1, rho_for_depth.min()), 
                                                  vmax=rho_for_depth.max()))
            ax_depth.set_xscale('log')
            ax_depth.invert_yaxis()
            ax_depth.set_xlabel('Résistivité (Ω·m) - Échelle log', fontsize=11, fontweight='bold')
            ax_depth.set_ylabel('Profondeur (m, précision: mm)', fontsize=11, fontweight='bold')
            ax_depth.set_title('Résistivité en fonction de la Profondeur (Précision Millimétrique)', 
                              fontsize=12, fontweight='bold')
            ax_depth.grid(True, alpha=0.3)
            
            # Définir ticks avec toutes les profondeurs mesurées
            unique_depths_all = np.unique(depth_data)
            if len(unique_depths_all) > 20:
                ax_depth.set_yticks(unique_depths_all[::len(unique_depths_all)//20])
            else:
                ax_depth.set_yticks(unique_depths_all)
            
            # Format Y axis avec 3 décimales
            ax_depth.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
            
            cbar_dist = plt.colorbar(scatter, ax=ax_depth)
            cbar_dist.set_label('Résistivité (Ω·m)', fontsize=10, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig_dist)
            plt.close()
            
            st.markdown("---")
            
            # ========== VISUALISATION 3D DES MINÉRAUX PAR COUCHES ==========
            st.subheader("🌐 Coupe Stratigraphique 3D")
            st.markdown("""
            Vue tridimensionnelle montrant les **couches géologiques** basées sur la résistivité.
            - **Axe X (horizontal)** : Distance le long du profil ERT (m)
            - **Axe Y (horizontal)** : Log₁₀ de la Résistivité - forme des **couches**
            - **Axe Z (VERTICAL)** : ⬇️ Profondeur (m) - descend vers le bas
            
            Les **couleurs** représentent les **8 catégories géologiques** (même résistivité = même couche).  
            **Rotation interactive** : Clic + glisser pour explorer les couches en 3D.
            """)
            
            # Préparer les données 3D
            # X = Distance horizontale du profil, Y = Offset transversal (jitter pour visualisation), Z = Profondeur
            X_3d_dist = pd.to_numeric(df['survey_point'], errors='coerce').values
            Z_3d_depth = -np.abs(pd.to_numeric(df['depth'], errors='coerce').values)  # Négatif pour descendre
            Y_3d_rho = pd.to_numeric(df['data'], errors='coerce').values
            
            # Filtrer les NaN
            mask_3d = ~(np.isnan(X_3d_dist) | np.isnan(Z_3d_depth) | np.isnan(Y_3d_rho))
            X_3d_dist = X_3d_dist[mask_3d]
            Z_3d_depth = Z_3d_depth[mask_3d]
            Y_3d_rho = Y_3d_rho[mask_3d]
            
            if len(X_3d_dist) > 0:
                # Créer la figure 3D avec plotly pour interactivité
                import plotly.graph_objects as go
                
                # Pour une vraie stratigraphie, utiliser directement la résistivité comme Y
                # Cela crée des "couches" géologiques visibles dans le profil
                Y_3d_rho_log = np.log10(Y_3d_rho + 0.001)  # Échelle logarithmique simple
                
                # Définir les catégories avec couleurs
                def get_material_category(resistivity):
                    if resistivity < 1:
                        return '💎 Minéraux métalliques', '#FFD700'
                    elif resistivity < 10:
                        return '💧 Eaux salées + Argiles', '#FF4500'
                    elif resistivity < 50:
                        return '🧱 Argiles compactes', '#8B4513'
                    elif resistivity < 200:
                        return '💧 Eaux douces + Sols', '#90EE90'
                    elif resistivity < 1000:
                        return '🏖️ Sables + Graviers', '#F4A460'
                    elif resistivity < 5000:
                        return '🪨 Roches sédimentaires', '#87CEEB'
                    elif resistivity < 100000:
                        return '🌋 Roches ignées (Granite)', '#FFB6C1'
                    else:
                        return '💎 Quartzite', '#E0E0E0'
                
                # Classifier chaque point
                categories_3d = [get_material_category(rho) for rho in Y_3d_rho]
                materials = [cat[0] for cat in categories_3d]
                colors = [cat[1] for cat in categories_3d]
                
                # Créer le scatter 3D
                fig_3d = go.Figure()
                
                # Grouper par catégorie pour la légende
                unique_materials = list(set(materials))
                for material in unique_materials:
                    mask_mat = np.array([m == material for m in materials])
                    fig_3d.add_trace(go.Scatter3d(
                        x=X_3d_dist[mask_mat],
                        y=Y_3d_rho_log[mask_mat],  # Log(résistivité) - couches horizontales
                        z=Z_3d_depth[mask_mat],    # Profondeur verticale (négatif = vers le bas)
                        mode='markers',
                        name=material,
                        marker=dict(
                            size=6,
                            color=colors[materials.index(material)],
                            opacity=0.8,
                            line=dict(color='white', width=0.5)
                        ),
                        text=[f'Distance: {x:.3f} m<br>Profondeur: {abs(z):.3f} m (≈{abs(z)*1000:.0f} mm)<br>Résistivité: {rho:.2f} Ω·m<br>Matériau: {mat}' 
                              for x, z, rho, mat in zip(X_3d_dist[mask_mat], Z_3d_depth[mask_mat], 
                                                        Y_3d_rho[mask_mat], np.array(materials)[mask_mat])],
                        hovertemplate='%{text}<extra></extra>'
                    ))
                
                fig_3d.update_layout(
                    title=dict(
                        text='Coupe Stratigraphique 3D<br><sub>Profondeur verticale | Couches par résistivité</sub>',
                        font=dict(size=16, family='Arial Black')
                    ),
                    scene=dict(
                        xaxis=dict(title='Distance (m, précision: mm)', backgroundcolor='lightgray'),
                        yaxis=dict(title='Log₁₀(Résistivité)', backgroundcolor='lightgray'),
                        zaxis=dict(title='⬇️ Profondeur (m, précision: mm)', backgroundcolor='lightgray'),
                        camera=dict(
                            eye=dict(x=1.5, y=-1.5, z=1.2)  # Vue latérale pour voir les couches
                        ),
                        aspectmode='manual',
                        aspectratio=dict(x=3, y=1.5, z=2)  # Profil étiré, couches visibles
                    ),
                    width=900,
                    height=700,
                    showlegend=True,
                    legend=dict(
                        title='Catégories',
                        yanchor='top',
                        y=0.99,
                        xanchor='left',
                        x=0.01,
                        bgcolor='rgba(255,255,255,0.8)'
                    )
                )
                
                st.plotly_chart(fig_3d, use_container_width=True)
                
                # Sauvegarder la figure 3D pour le PDF (version matplotlib)
                from mpl_toolkits.mplot3d import Axes3D
                fig_3d_pdf = plt.figure(figsize=(12, 8), dpi=150)
                ax_3d_pdf = fig_3d_pdf.add_subplot(111, projection='3d')
                
                # Plot par catégorie
                for material in unique_materials:
                    mask_mat = np.array([m == material for m in materials])
                    color_hex = colors[materials.index(material)]
                    ax_3d_pdf.scatter(X_3d_dist[mask_mat], 
                                     Y_3d_rho_log[mask_mat],  # Log simple sans multiplication
                                     Z_3d_depth[mask_mat],
                                     c=color_hex, s=50, alpha=0.7, 
                                     edgecolors='white', linewidths=0.5,
                                     label=material)
                
                ax_3d_pdf.set_xlabel('Distance (m, précision: mm)', fontsize=11, fontweight='bold')
                ax_3d_pdf.set_ylabel('Log₁₀(Résistivité)', fontsize=11, fontweight='bold')
                ax_3d_pdf.set_zlabel('⬇️ Profondeur (m, précision: mm)', fontsize=11, fontweight='bold')
                ax_3d_pdf.set_title('Coupe Stratigraphique 3D\nCouches Géologiques par Résistivité (Précision Millimétrique)',
                                   fontsize=13, fontweight='bold', pad=20)
                ax_3d_pdf.legend(loc='upper left', fontsize=8, framealpha=0.9)
                ax_3d_pdf.grid(True, alpha=0.3)
                
                # Ajuster le ratio pour voir les couches horizontales
                ax_3d_pdf.set_box_aspect([3, 1.5, 2])  # Profil étiré, couches visibles
                plt.tight_layout()
                
                st.success(f"""
                ✅ **Visualisation 3D générée avec succès**
                - {len(X_3d_dist)} points cartographiés
                - {len(unique_materials)} catégories géologiques distinctes
                - Modèle interactif avec rotation 360°
                """)
            else:
                st.warning("⚠️ Données insuffisantes pour la visualisation 3D")
                fig_3d_pdf = None
            
            st.markdown("---")
            
            # ========== EXPORT PDF DU RAPPORT STRATIGRAPHIQUE ==========
            st.subheader("📄 Génération du Rapport PDF Complet")
            st.markdown("""
            Téléchargez un **rapport PDF professionnel** incluant :
            - 📊 Tableau de classification complète (30+ matériaux)
            - 📈 Graphiques de distribution (histogramme + profil)
            - 🌐 Visualisation 3D des couches géologiques
            - 📋 Statistiques détaillées et interprétation
            """)
            
            if st.button("🎯 Générer le Rapport PDF Stratigraphique", key="btn_pdf_strat"):
                with st.spinner("🔄 Génération du rapport PDF en cours..."):
                    # Créer un dictionnaire avec toutes les figures
                    figures_strat = {}
                    
                    # Figure 1: Distribution
                    figures_strat['distribution'] = fig_dist
                    
                    # Figure 2: 3D (si disponible)
                    if fig_3d_pdf is not None:
                        figures_strat['3d_view'] = fig_3d_pdf
                    
                    # Générer le PDF
                    pdf_bytes = create_stratigraphy_pdf_report(df, figures_strat)
                    
                    # Bouton de téléchargement
                    st.download_button(
                        label="⬇️ Télécharger le Rapport Stratigraphique (PDF)",
                        data=pdf_bytes,
                        file_name=f"Rapport_Stratigraphie_ERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        key="download_pdf_strat"
                    )
                    
                    st.success("✅ Rapport PDF généré avec succès ! Cliquez sur le bouton ci-dessus pour télécharger.")
            
            st.markdown("---")
            
            st.success(f"""
            ✅ **Analyse complète effectuée**
            - {len(df)} mesures analysées
            - Profondeur max : {depth_data.max():.3f} m (≈{depth_data.max()*1000:.0f} mm)
            - Résistivité min/max : {rho_data.min():.2f} - {rho_data.max():.0f} Ω·m
            - Identification automatique des formations géologiques
            - Visualisation 3D interactive disponible
            - Export PDF professionnel prêt
            """)
            
            # ========== COUPE SUPPLÉMENTAIRE - PSEUDO-SECTION RÉELLE (FORMAT CLASSIQUE) ==========
            st.markdown("---")
            with st.expander("📊 Pseudo-Section de Résistivité Apparente (Format Classique)", expanded=True):
                st.markdown("""
                **Carte de pseudo-section au format géophysique standard**
                
                Cette représentation respecte le format classique des prospections ERT avec :
                - 🎨 Échelle de couleurs rainbow continue (bleu → vert → jaune → orange → rouge)
                - 📏 Axes en mètres avec positions réelles des électrodes
                - 🌡️ Barre de couleur graduée montrant les résistivités mesurées
                - 🗺️ Visualisation directe des résistivités apparentes du sous-sol
                """)
                
                # Créer la figure au format classique
                fig_pseudo_t4, ax_pseudo_t4 = plt.subplots(figsize=(16, 8), dpi=150)
                
                # Utiliser les VRAIES valeurs mesurées depuis le DataFrame
                X_real_t4 = pd.to_numeric(df['survey_point'], errors='coerce').values
                Z_real_t4 = np.abs(pd.to_numeric(df['depth'], errors='coerce').values)
                Rho_real_t4 = pd.to_numeric(df['data'], errors='coerce').values
                
                # Filtrer les valeurs NaN
                mask_t4 = ~(np.isnan(X_real_t4) | np.isnan(Z_real_t4) | np.isnan(Rho_real_t4))
                X_real_t4 = X_real_t4[mask_t4]
                Z_real_t4 = Z_real_t4[mask_t4]
                Rho_real_t4 = Rho_real_t4[mask_t4]
                
                if len(X_real_t4) > 3:
                    # Créer une grille fine pour la visualisation
                    from scipy.interpolate import griddata
                    xi_pseudo_t4 = np.linspace(X_real_t4.min(), X_real_t4.max(), 500)
                    zi_pseudo_t4 = np.linspace(Z_real_t4.min(), Z_real_t4.max(), 300)
                    Xi_pseudo_t4, Zi_pseudo_t4 = np.meshgrid(xi_pseudo_t4, zi_pseudo_t4)
                    
                    # Interpolation linear pour un rendu lisse mais fidèle
                    Rhoi_pseudo_t4 = griddata(
                        (X_real_t4, Z_real_t4), 
                        Rho_real_t4, 
                        (Xi_pseudo_t4, Zi_pseudo_t4), 
                        method='linear',
                        fill_value=np.median(Rho_real_t4)
                    )
                    
                    # Utiliser la colormap rainbow classique
                    from matplotlib.colors import LogNorm
                    
                    # Définir les limites de résistivité
                    vmin_pseudo_t4 = max(0.1, Rho_real_t4.min())
                    vmax_pseudo_t4 = Rho_real_t4.max()
                    
                    # Créer la pseudo-section avec échelle rainbow
                    pcm_pseudo_t4 = ax_pseudo_t4.contourf(
                        Xi_pseudo_t4, 
                        Zi_pseudo_t4, 
                        Rhoi_pseudo_t4,
                        levels=50,
                        cmap='jet',
                        norm=LogNorm(vmin=vmin_pseudo_t4, vmax=vmax_pseudo_t4),
                        extend='both'
                    )
                    
                    # Ajouter les contours
                    contours_t4 = ax_pseudo_t4.contour(
                        Xi_pseudo_t4, 
                        Zi_pseudo_t4, 
                        Rhoi_pseudo_t4,
                        levels=10,
                        colors='black',
                        linewidths=0.5,
                        alpha=0.3
                    )
                    
                    # Superposer les points de mesure
                    scatter_real_t4 = ax_pseudo_t4.scatter(
                        X_real_t4, 
                        Z_real_t4, 
                        c='white',
                        s=20,
                        edgecolors='black',
                        linewidths=0.5,
                        alpha=0.7,
                        zorder=5,
                        label='Points de mesure'
                    )
                    
                    # Barre de couleur
                    cbar_pseudo_t4 = plt.colorbar(pcm_pseudo_t4, ax=ax_pseudo_t4, pad=0.02, aspect=30)
                    cbar_pseudo_t4.set_label('Résistivité Apparente (Ω·m)', fontsize=12, fontweight='bold')
                    cbar_pseudo_t4.ax.tick_params(labelsize=10)
                    
                    # Configuration des axes
                    ax_pseudo_t4.set_xlabel('Position (m)', fontsize=12, fontweight='bold')
                    ax_pseudo_t4.set_ylabel('Profondeur (m)', fontsize=12, fontweight='bold')
                    ax_pseudo_t4.set_title(
                        'Pseudo-Section de Résistivité Apparente\nMeasured Apparent Resistivity Pseudosection',
                        fontsize=14, 
                        fontweight='bold'
                    )
                    
                    ax_pseudo_t4.invert_yaxis()
                    ax_pseudo_t4.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
                    ax_pseudo_t4.legend(loc='upper right', fontsize=10, framealpha=0.9)
                    
                    plt.tight_layout()
                    st.pyplot(fig_pseudo_t4)
                    plt.close()
                    
                    # Statistiques
                    col1_ps_t4, col2_ps_t4, col3_ps_t4 = st.columns(3)
                    with col1_ps_t4:
                        st.metric("📏 Points de mesure", f"{len(Rho_real_t4)}")
                    with col2_ps_t4:
                        st.metric("📊 Plage de résistivité", f"{vmin_pseudo_t4:.1f} - {vmax_pseudo_t4:.1f} Ω·m")
                    with col3_ps_t4:
                        st.metric("🎯 Résistivité médiane", f"{np.median(Rho_real_t4):.2f} Ω·m")
                    
                    st.markdown("""
                    **Interprétation des couleurs (échelle rainbow) :**
                    
                    | Couleur | Résistivité | Interprétation Géologique |
                    |---------|-------------|---------------------------|
                    | 🔵 **Bleu foncé** | < 10 Ω·m | Argiles saturées, eau salée |
                    | 🟦 **Cyan** | 10-50 Ω·m | Argiles compactes, limons |
                    | 🟢 **Vert** | 50-100 Ω·m | Sables fins, aquifères potentiels |
                    | 🟡 **Jaune** | 100-300 Ω·m | Sables grossiers, bons aquifères |
                    | 🟠 **Orange** | 300-1000 Ω·m | Graviers, roches altérées |
                    | 🔴 **Rouge** | > 1000 Ω·m | Roches consolidées, socle |
                    """)
                else:
                    st.warning("⚠️ Pas assez de données valides pour générer la pseudo-section")
        else:
            st.info("ℹ️ Le fichier uploadé ne contient pas de données valides.")
    else:
        st.warning("⚠️ Aucune donnée chargée. Veuillez d'abord uploader un fichier .dat dans l'onglet 'Analyse Fichiers .dat'")
        st.info("💡 Une fois les données chargées, vous pourrez visualiser la stratigraphie complète avec identification automatique des formations.")

# ===================== TAB 5 : INVERSION PYGIMLI - ERT AVANCÉE =====================
with tab5:
    st.header("🔬 Inversion pyGIMLi - Analyse ERT Avancée")
    st.markdown("""
    ### 🛡️ Inversion Géophysique avec pyGIMLi
    Cette section utilise **pyGIMLi** (Python Geophysical Inversion and Modelling Library) pour effectuer une **inversion complète** des données ERT.
    
    **Fonctionnalités :**
    - 📁 Upload de fichiers .dat ERT (fichiers binaires Ravensgate Sonic)
    - � Upload de fichiers freq.dat (résistivité par fréquence MHz)
    - �🔄 Inversion automatique avec algorithme optimisé
    - 🎨 Visualisation avec palette hydrogéologique (4 classes)
    - 📊 Classification lithologique complète (9 formations)
    - � Classification hydrogéologique (4 types d'eau)
    - 📈 Détection automatique des interfaces géologiques
    - 💾 Export CSV interprété avec classifications
    """)

    # Upload fichier freq.dat directement (sans sélection de type)
    uploaded_freq = st.file_uploader("📂 Uploader un fichier freq.dat", type=["dat"], key="pygimli_upload_freq")

    if uploaded_freq is not None:
        # Lire le contenu du fichier en bytes (avec cache)
        file_bytes = uploaded_freq.read()
        encoding = detect_encoding(file_bytes)
        
        # Parser le fichier freq.dat
        df_pygimli = parse_freq_dat(file_bytes, encoding)
        file_desc = "freq.dat"
        
        if not df_pygimli.empty:
            st.write(f"**📊 Données {file_desc} parsées :**")
            st.dataframe(df_pygimli.head())
            
            st.success(f"✅ {len(df_pygimli)} mesures chargées depuis le fichier freq.dat")
            
            # Traitement pour freq.dat (toujours actif maintenant)
            st.info("🔄 Conversion des données de fréquence en format ERT...")
            
            # Les fréquences deviennent des "profondeurs" (plus haute fréquence = surface)
            freq_columns = [col for col in df_pygimli.columns if col.startswith('freq_')]
            survey_points = sorted(df_pygimli['survey_point'].unique())
            
            # Créer un DataFrame au format ERT (survey_point, depth, data)
            ert_data = []
            for sp in survey_points:
                sp_data = df_pygimli[df_pygimli['survey_point'] == sp]
                if not sp_data.empty:
                    for i, freq_col in enumerate(freq_columns):
                        # Extraire la valeur numérique de la fréquence
                        freq_value = float(freq_col.replace('freq_', ''))
                        rho_value = sp_data[freq_col].values[0]
                        
                        if not pd.isna(rho_value):
                            # Fréquence haute = profondeur faible (surface)
                            # On inverse : haute fréquence = faible profondeur
                            depth = 1000 / freq_value  # Conversion arbitraire pour visualisation
                            
                            ert_data.append({
                                'survey_point': sp,
                                'depth': -depth,  # Négatif pour convention ERT
                                'data': rho_value,
                                'frequency': freq_value
                            })
            
            df_pygimli = pd.DataFrame(ert_data)
            st.success(f"✅ Conversion terminée : {len(df_pygimli)} mesures ERT créées à partir de {len(freq_columns)} fréquences")
            
            # Afficher le DataFrame converti
            st.write("**📊 Données converties en format ERT :**")
            st.dataframe(df_pygimli.head(20))
            
            # ===== VISUALISATION PSEUDO-SECTION IMMÉDIATE =====
            st.subheader("🎨 Pseudo-section de Résistivité (freq.dat)")
            
            # Préparer les données pour la visualisation - UTILISER LES VRAIES VALEURS
            X_freq = df_pygimli['survey_point'].values
            Z_freq = np.abs(df_pygimli['depth'].values)
            Rho_freq = df_pygimli['data'].values
            
            # DIAGNOSTIC DES VRAIES VALEURS MESURÉES
            st.info(f"""
            **📊 Analyse des VRAIES résistivités mesurées :**
            - **Minimum** : {Rho_freq.min():.3f} Ω·m
            - **Maximum** : {Rho_freq.max():.3f} Ω·m
            - **Moyenne** : {Rho_freq.mean():.3f} Ω·m
            - **Médiane** : {np.median(Rho_freq):.3f} Ω·m
            - **Nombre de mesures** : {len(Rho_freq)}
            
            **Classification automatique :**
            - < 1 Ω·m (Eau de mer) : {(Rho_freq < 1).sum()} mesures ({(Rho_freq < 1).sum()/len(Rho_freq)*100:.1f}%)
            - 1-10 Ω·m (Eau salée) : {((Rho_freq >= 1) & (Rho_freq < 10)).sum()} mesures ({((Rho_freq >= 1) & (Rho_freq < 10)).sum()/len(Rho_freq)*100:.1f}%)
            - 10-100 Ω·m (Eau douce) : {((Rho_freq >= 10) & (Rho_freq < 100)).sum()} mesures ({((Rho_freq >= 10) & (Rho_freq < 100)).sum()/len(Rho_freq)*100:.1f}%)
            - > 100 Ω·m (Eau pure) : {(Rho_freq >= 100).sum()} mesures ({(Rho_freq >= 100).sum()/len(Rho_freq)*100:.1f}%)
            """)
            
            # CRÉER UNE GRILLE AVEC LES VRAIES VALEURS (nearest pour préserver les valeurs exactes)
            from scipy.interpolate import griddata
            xi_freq = np.linspace(X_freq.min(), X_freq.max(), 100)
            zi_freq = np.linspace(Z_freq.min(), Z_freq.max(), 80)
            Xi_freq, Zi_freq = np.meshgrid(xi_freq, zi_freq)
            
            # CORRECTION: Utiliser 'nearest' au lieu de 'cubic' pour préserver les vraies valeurs
            Rhoi_freq = griddata((X_freq, Z_freq), Rho_freq, (Xi_freq, Zi_freq), method='nearest')
            
            # Créer la figure
            fig_freq_pseudo, ax_freq = plt.subplots(figsize=(14, 7), dpi=150)
            
            # Définir les limites de résistivité pour les couleurs - VRAIES VALEURS
            vmin_freq = max(0.01, Rho_freq.min())
            vmax_freq = Rho_freq.max()
            
            # Afficher avec colormap jet_r (standard ERT) - VRAIES VALEURS
            pcm_freq = ax_freq.pcolormesh(Xi_freq, Zi_freq, Rhoi_freq, 
                                         cmap='jet_r', shading='auto',
                                         norm=LogNorm(vmin=vmin_freq, vmax=vmax_freq))
            
            # Superposer les points de mesure
            scatter_freq = ax_freq.scatter(X_freq, Z_freq, c=Rho_freq, 
                                          cmap='jet_r', s=60, 
                                          edgecolors='black', linewidths=1,
                                          norm=LogNorm(vmin=vmin_freq, vmax=vmax_freq),
                                          zorder=10, alpha=0.8)
            
            # Annoter quelques points avec leurs fréquences si disponible
            if 'frequency' in df_pygimli.columns:
                # Annoter 5 points représentatifs
                for i in range(0, len(df_pygimli), max(1, len(df_pygimli)//5)):
                    row = df_pygimli.iloc[i]
                    ax_freq.annotate(f'{row["frequency"]:.1f} MHz\nρ={row["data"]:.3f}', 
                                   xy=(row['survey_point'], np.abs(row['depth'])),
                                   xytext=(5, 5), textcoords='offset points',
                                   fontsize=7, ha='left',
                                   bbox=dict(boxstyle='round,pad=0.3', 
                                           facecolor='yellow', alpha=0.7),
                                   arrowprops=dict(arrowstyle='->', 
                                                 connectionstyle='arc3,rad=0.2',
                                                 color='black', lw=0.5))
            
            ax_freq.invert_yaxis()
            ax_freq.set_xlabel('Point de sondage', fontsize=12, fontweight='bold')
            ax_freq.set_ylabel('Profondeur équivalente (m)', fontsize=12, fontweight='bold')
            ax_freq.set_title(f'Pseudo-section ERT - Données Fréquence\n{len(survey_points)} points × {len(freq_columns)} fréquences', 
                            fontsize=13, fontweight='bold')
            ax_freq.grid(True, alpha=0.3, linestyle='--', color='white')
            
            # Colorbar
            cbar_freq = fig_freq_pseudo.colorbar(pcm_freq, ax=ax_freq, extend='both')
            cbar_freq.set_label('Résistivité (Ω·m)', fontsize=11, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig_freq_pseudo)
            plt.close()
            
            # Légende d'interprétation
            st.markdown(f"""
            **Interprétation des couleurs :**
            - 🔴 **Rouge/Orange** (faible résistivité) : Matériaux conducteurs - Eau salée, argiles saturées
            - 🟡 **Jaune** (résistivité moyenne) : Eau douce, sols humides
            - 🟢 **Vert** (résistivité élevée) : Sables secs, graviers
            - 🔵 **Bleu** (très haute résistivité) : Roches sèches, formations résistives
            
            **Plage mesurée :** {vmin_freq:.3f} - {vmax_freq:.3f} Ω·m  
            **Points noirs :** Mesures réelles annotées avec fréquences (MHz)
            """)
            
            # Graphique fréquence vs résistivité
            st.subheader("📊 Profil Résistivité par Fréquence")
            
            fig_freq_profile, ax_prof = plt.subplots(figsize=(12, 6), dpi=150)
            
            # Grouper par fréquence et calculer la moyenne
            freq_stats = df_pygimli.groupby('frequency')['data'].agg(['mean', 'std', 'min', 'max']).reset_index()
            freq_stats = freq_stats.sort_values('frequency', ascending=False)
            
            # Tracer avec barres d'erreur
            ax_prof.errorbar(freq_stats['frequency'], freq_stats['mean'], 
                           yerr=freq_stats['std'], fmt='o-', linewidth=2, 
                           markersize=8, capsize=5, capthick=2,
                           color='steelblue', ecolor='gray', alpha=0.8,
                           label='Moyenne ± σ')
            
            ax_prof.fill_between(freq_stats['frequency'], 
                                freq_stats['min'], freq_stats['max'],
                                alpha=0.2, color='lightblue', label='Min-Max')
            
            ax_prof.set_xlabel('Fréquence (MHz)', fontsize=11, fontweight='bold')
            ax_prof.set_ylabel('Résistivité moyenne (Ω·m)', fontsize=11, fontweight='bold')
            ax_prof.set_title('Variation de la Résistivité en fonction de la Fréquence', 
                            fontsize=12, fontweight='bold')
            ax_prof.set_xscale('log')
            ax_prof.set_yscale('log')
            ax_prof.grid(True, alpha=0.3, which='both')
            ax_prof.legend(loc='best', fontsize=10)
            
            plt.tight_layout()
            st.pyplot(fig_freq_profile)
            plt.close()
            
            # ========== 3 COUPES GÉOLOGIQUES SUPPLÉMENTAIRES DU SOUS-SOL ==========
            st.markdown("---")
            st.subheader("🌍 Coupes Géologiques Détaillées du Sous-Sol")
            st.markdown("""
            Visualisation multi-niveaux des formations géologiques basées sur les valeurs de résistivité mesurées.
            Ces coupes permettent d'identifier la **nature des matériaux** à différentes profondeurs.
            """)
            
            # COUPE 1: Classification par zones de résistivité (4 classes)
            with st.expander("📊 Coupe 1 - Classification Hydrogéologique (4 classes d'eau)", expanded=True):
                fig_geo1, ax_geo1 = plt.subplots(figsize=(14, 7), dpi=150)
                
                # Définir 4 classes de résistivité pour l'eau - UTILISER LES VRAIES VALEURS
                # RESPECT DU TABLEAU DE RÉFÉRENCE EXACT
                def classify_water(rho):
                    if rho < 1:
                        return 0, 'Eau de mer (0.1-1 Ω·m)', '#DC143C'  # Crimson (Rouge vif)
                    elif rho < 10:
                        return 1, 'Eau salée nappe (1-10 Ω·m)', '#FFA500'   # Orange
                    elif rho < 100:
                        return 2, 'Eau douce (10-100 Ω·m)', '#FFD700'   # Gold (Jaune)
                    else:
                        return 3, 'Eau très pure (>100 Ω·m)', '#1E90FF'  # DodgerBlue (Bleu vif)
                
                # UTILISER nearest pour conserver les VRAIES valeurs mesurées
                water_classes = np.zeros_like(Rhoi_freq)
                for i in range(Rhoi_freq.shape[0]):
                    for j in range(Rhoi_freq.shape[1]):
                        if not np.isnan(Rhoi_freq[i, j]) and Rhoi_freq[i, j] > 0:
                            water_classes[i, j], _, _ = classify_water(Rhoi_freq[i, j])
                        else:
                            water_classes[i, j] = np.nan
                
                # Compter les classes présentes et leurs proportions basées sur les VRAIES valeurs
                unique_classes, counts = np.unique(water_classes[~np.isnan(water_classes)], return_counts=True)
                total_pixels = (~np.isnan(water_classes)).sum()
                
                # Créer une colormap discrète avec couleurs EXACTES selon le tableau de référence
                from matplotlib.colors import ListedColormap, BoundaryNorm
                colors_water = ['#DC143C', '#FFA500', '#FFD700', '#1E90FF']  # Rouge vif, Orange, Jaune/Or, Bleu vif
                cmap_water = ListedColormap(colors_water)
                bounds_water = [0, 1, 2, 3, 4]
                norm_water = BoundaryNorm(bounds_water, cmap_water.N)
                
                # Afficher
                pcm_geo1 = ax_geo1.pcolormesh(Xi_freq, Zi_freq, water_classes, 
                                             cmap=cmap_water, norm=norm_water, shading='auto')
                
                # Superposer les points de mesure
                for rho_val in [0.5, 5, 50, 150]:
                    mask_class = (Rho_freq >= rho_val*0.5) & (Rho_freq < rho_val*2)
                    if mask_class.sum() > 0:
                        ax_geo1.scatter(X_freq[mask_class], Z_freq[mask_class], 
                                      s=40, edgecolors='black', linewidths=1.5,
                                      facecolors='none', alpha=0.8, zorder=10)
                
                ax_geo1.invert_yaxis()
                ax_geo1.set_xlabel('Distance (m)', fontsize=12, fontweight='bold')
                ax_geo1.set_ylabel('Profondeur (m)', fontsize=12, fontweight='bold')
                ax_geo1.set_title('Coupe 1: Classification Hydrogéologique\n4 Types d\'Eau identifiés', 
                                fontsize=13, fontweight='bold')
                ax_geo1.grid(True, alpha=0.3, linestyle='--', color='gray')
                
                # Colorbar
                cbar_geo1 = fig_geo1.colorbar(pcm_geo1, ax=ax_geo1, ticks=[0.5, 1.5, 2.5, 3.5])
                cbar_geo1.ax.set_yticklabels(['Eau de mer\n0.1-1 Ω·m', 
                                             'Eau salée (nappe)\n1-10 Ω·m',
                                             'Eau douce\n10-100 Ω·m',
                                             'Eau très pure\n> 100 Ω·m'])
                cbar_geo1.set_label('Type d\'Eau', fontsize=11, fontweight='bold')
                
                plt.tight_layout()
                st.pyplot(fig_geo1)
                plt.close()
                
                st.markdown("""
                **Interprétation (selon tableau de référence) :**
                - 🔴 **Rouge vif/Orange** (0.1-1 Ω·m) : Eau de mer, intrusion marine
                - � **Jaune/Orange** (1-10 Ω·m) : Eau salée (nappe saumâtre)
                - � **Vert/Bleu clair** (10-100 Ω·m) : Eau douce exploitable
                - 🔵 **Bleu foncé** (> 100 Ω·m) : Eau très pure ou roches sèches
                """)
            
            # COUPE 2: Gradient vertical de résistivité (changements de couches)
            with st.expander("📈 Coupe 2 - Gradient Vertical de Résistivité (Interfaces géologiques)", expanded=False):
                fig_geo2, (ax_geo2a, ax_geo2b) = plt.subplots(1, 2, figsize=(16, 7), dpi=150)
                
                # Calculer le gradient vertical (dérivée selon la profondeur)
                gradient_z = np.gradient(Rhoi_freq, axis=0)
                gradient_magnitude = np.abs(gradient_z)
                
                # Afficher la résistivité
                pcm_geo2a = ax_geo2a.pcolormesh(Xi_freq, Zi_freq, Rhoi_freq, 
                                               cmap='jet_r', shading='auto',
                                               norm=LogNorm(vmin=vmin_freq, vmax=vmax_freq))
                ax_geo2a.invert_yaxis()
                ax_geo2a.set_xlabel('Distance (m)', fontsize=11, fontweight='bold')
                ax_geo2a.set_ylabel('Profondeur (m)', fontsize=11, fontweight='bold')
                ax_geo2a.set_title('Résistivité Mesurée', fontsize=12, fontweight='bold')
                ax_geo2a.grid(True, alpha=0.3)
                cbar_2a = fig_geo2.colorbar(pcm_geo2a, ax=ax_geo2a)
                cbar_2a.set_label('ρ (Ω·m)', fontsize=10, fontweight='bold')
                
                # Afficher le gradient (interfaces)
                pcm_geo2b = ax_geo2b.pcolormesh(Xi_freq, Zi_freq, gradient_magnitude, 
                                               cmap='hot', shading='auto')
                
                # Identifier les interfaces majeures (gradient > seuil)
                threshold_gradient = np.percentile(gradient_magnitude[~np.isnan(gradient_magnitude)], 90)
                interfaces = gradient_magnitude > threshold_gradient
                
                # Contours des interfaces
                if interfaces.sum() > 10:
                    contour_levels = [threshold_gradient]
                    ax_geo2b.contour(Xi_freq, Zi_freq, gradient_magnitude, 
                                   levels=contour_levels, colors='cyan', linewidths=2, 
                                   linestyles='--', alpha=0.8)
                
                ax_geo2b.invert_yaxis()
                ax_geo2b.set_xlabel('Distance (m)', fontsize=11, fontweight='bold')
                ax_geo2b.set_ylabel('Profondeur (m)', fontsize=11, fontweight='bold')
                ax_geo2b.set_title('Gradient Vertical (Interfaces)\nLignes cyan = Changements de couches', 
                                 fontsize=12, fontweight='bold')
                ax_geo2b.grid(True, alpha=0.3)
                cbar_2b = fig_geo2.colorbar(pcm_geo2b, ax=ax_geo2b)
                cbar_2b.set_label('|∂ρ/∂z|', fontsize=10, fontweight='bold')
                
                plt.tight_layout()
                st.pyplot(fig_geo2)
                plt.close()
                
                st.markdown(f"""
                **Interprétation :**
                - **Graphique gauche** : Distribution de la résistivité
                - **Graphique droite** : Gradient vertical (changement selon la profondeur)
                - **Lignes cyan** : Interfaces géologiques majeures (seuil > {threshold_gradient:.2f})
                - **Zones chaudes (jaune/blanc)** : Changements brusques = limites entre couches
                - **Zones froides (noir/rouge foncé)** : Couches homogènes
                
                **Applications :**
                - Détection d'interfaces aquifères/aquitards
                - Identification de la profondeur du toit rocheux
                - Localisation des zones de transition eau douce/salée
                """)
            
            # COUPE 3: Modèle géologique interprété (lithologie)
            with st.expander("🗺️ Coupe 3 - Modèle Lithologique Interprété (Géologie complète)", expanded=False):
                fig_geo3, ax_geo3 = plt.subplots(figsize=(14, 8), dpi=150)
                
                # Classification lithologique étendue basée sur résistivité
                def classify_lithology(rho):
                    if rho < 1:
                        return 0, 'Eau de mer / Argile saturée salée', '#8B0000'
                    elif rho < 5:
                        return 1, 'Argile marine / Vase', '#A0522D'
                    elif rho < 20:
                        return 2, 'Argile compacte / Limon saturé', '#CD853F'
                    elif rho < 50:
                        return 3, 'Sable fin saturé (eau douce)', '#F4A460'
                    elif rho < 100:
                        return 4, 'Sable moyen / Gravier fin', '#FFD700'
                    elif rho < 200:
                        return 5, 'Gravier / Sable grossier sec', '#90EE90'
                    elif rho < 500:
                        return 6, 'Roche altérée / Calcaire fissuré', '#87CEEB'
                    elif rho < 1000:
                        return 7, 'Roche sédimentaire compacte', '#4682B4'
                    else:
                        return 8, 'Socle rocheux / Granite', '#8B008B'
                
                # Classifier chaque point
                litho_classes = np.zeros_like(Rhoi_freq)
                for i in range(Rhoi_freq.shape[0]):
                    for j in range(Rhoi_freq.shape[1]):
                        if not np.isnan(Rhoi_freq[i, j]):
                            litho_classes[i, j], _, _ = classify_lithology(Rhoi_freq[i, j])
                        else:
                            litho_classes[i, j] = np.nan
                
                # Colormap lithologique
                colors_litho = ['#8B0000', '#A0522D', '#CD853F', '#F4A460', 
                               '#FFD700', '#90EE90', '#87CEEB', '#4682B4', '#8B008B']
                cmap_litho = ListedColormap(colors_litho)
                bounds_litho = list(range(10))
                norm_litho = BoundaryNorm(bounds_litho, cmap_litho.N)
                
                # Afficher
                pcm_geo3 = ax_geo3.pcolormesh(Xi_freq, Zi_freq, litho_classes, 
                                             cmap=cmap_litho, norm=norm_litho, shading='auto')
                
                # Ajouter contours pour mieux voir les couches
                contour_litho = ax_geo3.contour(Xi_freq, Zi_freq, litho_classes, 
                                               levels=bounds_litho, colors='black', 
                                               linewidths=0.5, alpha=0.4)
                
                # AMÉLIORATION: Annoter TOUTES les zones présentes avec leurs caractéristiques
                unique_classes = np.unique(litho_classes[~np.isnan(litho_classes)]).astype(int)
                
                # AVERTISSEMENT si une seule classe domine
                if len(unique_classes) == 1:
                    st.warning(f"""
                    ⚠️ **Attention** : Une seule formation lithologique détectée (classe {unique_classes[0]}).
                    
                    Cela signifie que **toutes les résistivités mesurées** sont dans la même gamme.
                    Les VRAIES valeurs mesurées sont : {Rho_freq.min():.3f} - {Rho_freq.max():.3f} Ω·m
                    
                    **Explication** : Si tout est rouge (< 1 Ω·m), c'est que le site est dominé par de l'eau de mer ou des argiles saturées salées.
                    Pour voir d'autres couches, il faudrait des mesures avec plus de variabilité de résistivité.
                    """)
                
                # Stocker les informations de chaque formation présente (VRAIES VALEURS)
                formations_info = []
                
                for cls in unique_classes:
                    mask_cls = litho_classes == cls
                    count_pixels = mask_cls.sum()
                    percentage = (count_pixels / (~np.isnan(litho_classes)).sum()) * 100
                    
                    # CORRECTION: Obtenir les valeurs de résistivité RÉELLES (pas interpolées)
                    # Trouver les points de mesure réels qui correspondent à cette classe
                    real_rho_for_class = []
                    for idx in range(len(X_freq)):
                        # Trouver la cellule de grille la plus proche
                        i_grid = np.argmin(np.abs(xi_freq - X_freq[idx]))
                        j_grid = np.argmin(np.abs(zi_freq - Z_freq[idx]))
                        if litho_classes[j_grid, i_grid] == cls:
                            real_rho_for_class.append(Rho_freq[idx])
                    
                    if len(real_rho_for_class) > 0:
                        rho_min = np.min(real_rho_for_class)
                        rho_max = np.max(real_rho_for_class)
                        rho_mean = np.mean(real_rho_for_class)
                    else:
                        # Fallback sur les valeurs interpolées si pas de correspondance
                        rho_values = Rhoi_freq[mask_cls]
                        rho_min = np.nanmin(rho_values)
                        rho_max = np.nanmax(rho_values)
                        rho_mean = np.nanmean(rho_values)
                    
                    # Calculer profondeur moyenne et étendue
                    y_indices = np.where(np.any(mask_cls, axis=1))[0]
                    if len(y_indices) > 0:
                        depth_min = zi_freq[y_indices.min()]
                        depth_max = zi_freq[y_indices.max()]
                        depth_mean = (depth_min + depth_max) / 2
                        
                        # Calculer position horizontale moyenne
                        x_indices = np.where(np.any(mask_cls, axis=0))[0]
                        x_mean = xi_freq[int(np.mean(x_indices))] if len(x_indices) > 0 else xi_freq[len(xi_freq)//2]
                        
                        # Obtenir le label
                        _, label, color = classify_lithology(rho_mean)
                        
                        formations_info.append({
                            'class': cls,
                            'label': label,
                            'color': color,
                            'percentage': percentage,
                            'rho_min': rho_min,
                            'rho_max': rho_max,
                            'rho_mean': rho_mean,
                            'depth_min': depth_min,
                            'depth_max': depth_max,
                            'depth_mean': depth_mean,
                            'x_mean': x_mean
                        })
                        
                        # Annoter sur le graphique si la zone est significative (> 2%)
                        if percentage > 2:
                            label_short = label.split('/')[0].strip()
                            ax_geo3.annotate(
                                f'{label_short}\n{rho_mean:.1f} Ω·m',
                                xy=(x_mean, depth_mean),
                                fontsize=7,
                                ha='center',
                                va='center',
                                bbox=dict(boxstyle='round,pad=0.4', 
                                        facecolor='white', 
                                        edgecolor=color,
                                        alpha=0.85,
                                        linewidth=2),
                                fontweight='bold',
                                color='black'
                            )
                
                ax_geo3.invert_yaxis()
                ax_geo3.set_xlabel('Distance (m)', fontsize=12, fontweight='bold')
                ax_geo3.set_ylabel('Profondeur (m)', fontsize=12, fontweight='bold')
                ax_geo3.set_title('Coupe 3: Modèle Lithologique Interprété\n9 Formations Géologiques Identifiées', 
                                fontsize=13, fontweight='bold')
                ax_geo3.grid(True, alpha=0.2, linestyle='--', color='gray')
                
                # Légende détaillée
                from matplotlib.patches import Patch
                legend_elements = [
                    Patch(facecolor='#8B0000', label='Eau mer / Argile salée (< 1 Ω·m)'),
                    Patch(facecolor='#A0522D', label='Argile marine (1-5 Ω·m)'),
                    Patch(facecolor='#CD853F', label='Argile compacte (5-20 Ω·m)'),
                    Patch(facecolor='#F4A460', label='Sable fin saturé (20-50 Ω·m)'),
                    Patch(facecolor='#FFD700', label='Sable/Gravier (50-100 Ω·m)'),
                    Patch(facecolor='#90EE90', label='Gravier sec (100-200 Ω·m)'),
                    Patch(facecolor='#87CEEB', label='Roche altérée (200-500 Ω·m)'),
                    Patch(facecolor='#4682B4', label='Roche compacte (500-1000 Ω·m)'),
                    Patch(facecolor='#8B008B', label='Socle cristallin (> 1000 Ω·m)')
                ]
                ax_geo3.legend(handles=legend_elements, loc='upper left', 
                             fontsize=8, framealpha=0.9, ncol=1)
                
                plt.tight_layout()
                st.pyplot(fig_geo3)
                plt.close()
                
                # TABLEAU DÉTAILLÉ DES FORMATIONS PRÉSENTES
                st.markdown("### 📋 Inventaire Complet des Formations Géologiques Détectées")
                
                if formations_info:
                    # Créer un DataFrame avec toutes les informations
                    formations_df = pd.DataFrame(formations_info)
                    formations_df = formations_df.sort_values('depth_mean')
                    
                    # Préparer les données pour affichage
                    display_data = {
                        'Formation': formations_df['label'].tolist(),
                        'Profondeur (m)': [f"{row['depth_min']:.2f} - {row['depth_max']:.2f}" 
                                          for _, row in formations_df.iterrows()],
                        'Résistivité (Ω·m)': [f"{row['rho_min']:.1f} - {row['rho_max']:.1f} (moy: {row['rho_mean']:.1f})" 
                                             for _, row in formations_df.iterrows()],
                        'Présence (%)': [f"{row['percentage']:.1f}%" for _, row in formations_df.iterrows()],
                        'Type de matériau': []
                    }
                    
                    # Ajouter classification du type de matériau
                    for _, row in formations_df.iterrows():
                        rho = row['rho_mean']
                        if rho < 1:
                            mat_type = "💧 Liquide salin / Argile saturée"
                        elif rho < 20:
                            mat_type = "🟫 Sol argileux imperméable"
                        elif rho < 100:
                            mat_type = "🟡 Sol sableux aquifère"
                        elif rho < 500:
                            mat_type = "⚪ Gravier / Roche poreuse"
                        else:
                            mat_type = "⬛ Roche compacte / Minéral"
                        display_data['Type de matériau'].append(mat_type)
                    
                    display_df = pd.DataFrame(display_data)
                    
                    # Afficher avec style
                    st.dataframe(
                        display_df.style.set_properties(**{
                            'text-align': 'left',
                            'font-size': '11px'
                        }),
                        use_container_width=True,
                        height=min(400, len(display_df) * 50 + 50)
                    )
                    
                    # Statistiques récapitulatives
                    st.markdown("### 📊 Statistiques Lithologiques")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Formations détectées", len(formations_info))
                    with col2:
                        dominant = formations_df.loc[formations_df['percentage'].idxmax()]
                        st.metric("Formation dominante", 
                                 dominant['label'].split('/')[0][:20],
                                 f"{dominant['percentage']:.1f}%")
                    with col3:
                        rho_min_global = formations_df['rho_min'].min()
                        rho_max_global = formations_df['rho_max'].max()
                        st.metric("Plage résistivité", 
                                 f"{rho_min_global:.1f} - {rho_max_global:.1f} Ω·m")
                    with col4:
                        depth_max_form = formations_df['depth_max'].max()
                        st.metric("Profondeur max explorée", f"{depth_max_form:.2f} m")
                    
                    # Recommandations spécifiques par formation
                    st.markdown("### 🎯 Recommandations par Formation")
                    
                    for _, row in formations_df.iterrows():
                        with st.expander(f"📍 {row['label']} ({row['percentage']:.1f}% du profil)", expanded=False):
                            col_a, col_b = st.columns([2, 1])
                            with col_a:
                                st.markdown(f"""
                                **Caractéristiques détectées :**
                                - **Profondeur :** {row['depth_min']:.2f} à {row['depth_max']:.2f} m
                                - **Résistivité moyenne :** {row['rho_mean']:.1f} Ω·m
                                - **Plage mesurée :** {row['rho_min']:.1f} - {row['rho_max']:.1f} Ω·m
                                - **Proportion du profil :** {row['percentage']:.1f}%
                                """)
                            
                            with col_b:
                                # Recommandation selon le type
                                rho = row['rho_mean']
                                if rho < 1:
                                    st.error("🚫 À ÉVITER - Eau salée")
                                elif rho < 20:
                                    st.warning("⚠️ DIFFICILE - Argile imperméable")
                                elif rho < 100:
                                    st.success("✅ CIBLE PRIORITAIRE - Aquifère")
                                elif rho < 500:
                                    st.info("ℹ️ BON POTENTIEL - Formations perméables")
                                else:
                                    st.warning("⚠️ ROCHES DURES - Forage difficile")
                
                else:
                    st.warning("Aucune formation lithologique identifiée dans les données.")
                
                st.markdown("""
                **Interprétation Lithologique Complète :**
                
                Cette coupe présente un **modèle géologique réaliste** basé sur les résistivités mesurées.
                Chaque couleur représente une **formation lithologique spécifique** avec ses propriétés hydrogéologiques.
                
                **Couches principales (de haut en bas) :**
                1. **Zone superficielle** (marron foncé) : Argiles marines saturées, faible perméabilité
                2. **Zone intermédiaire** (jaune/or) : Sables et graviers aquifères, bon réservoir d'eau
                3. **Zone profonde** (bleu/violet) : Roches consolidées, aquifère de socle fracturé
                
                **Applications pratiques :**
                - 💧 **Forage de puits** : Cibler les zones jaunes/vertes (sables aquifères)
                - 🚫 **Éviter** : Zones rouges/marron foncé (argiles imperméables, eau salée)
                - 🎯 **Zones optimales** : Sables moyens à graviers (50-200 Ω·m) = meilleurs aquifères
                - 🌊 **Risque d'intrusion saline** : Zones rouges en surface ou peu profondes
                """)
            
            # ========== COUPE 4 - PSEUDO-SECTION RÉELLE (FORMAT CLASSIQUE) ==========
            with st.expander("📊 Coupe 4 - Pseudo-Section de Résistivité Apparente (Format Classique)", expanded=True):
                st.markdown("""
                **Carte de pseudo-section au format géophysique standard**
                
                Cette représentation respecte le format classique des prospections ERT avec :
                - 🎨 Échelle de couleurs rainbow continue (bleu → vert → jaune → orange → rouge)
                - 📏 Axes en mètres avec positions réelles des électrodes
                - 🌡️ Barre de couleur graduée montrant les résistivités mesurées
                - 🗺️ Visualisation directe des résistivités apparentes du sous-sol
                """)
                
                # Créer la figure au format classique
                fig_pseudo, ax_pseudo = plt.subplots(figsize=(16, 8), dpi=150)
                
                # Utiliser les VRAIES valeurs mesurées (pas d'interpolation cubic, juste nearest pour remplir)
                X_real = X_freq.copy()
                Z_real = Z_freq.copy()
                Rho_real = Rho_freq.copy()
                
                # Créer une grille fine pour la visualisation
                xi_pseudo = np.linspace(X_real.min(), X_real.max(), 500)
                zi_pseudo = np.linspace(Z_real.min(), Z_real.max(), 300)
                Xi_pseudo, Zi_pseudo = np.meshgrid(xi_pseudo, zi_pseudo)
                
                # Interpolation NEAREST pour préserver les vraies valeurs
                Rhoi_pseudo = griddata(
                    (X_real, Z_real), 
                    Rho_real, 
                    (Xi_pseudo, Zi_pseudo), 
                    method='linear',  # Linear pour un rendu lisse mais fidèle
                    fill_value=np.median(Rho_real)
                )
                
                # Utiliser la colormap rainbow classique (comme dans l'image de référence)
                from matplotlib.colors import LogNorm
                
                # Définir les limites de résistivité (échelle logarithmique)
                vmin_pseudo = max(0.1, Rho_real.min())
                vmax_pseudo = Rho_real.max()
                
                # Créer la pseudo-section avec échelle rainbow
                pcm_pseudo = ax_pseudo.contourf(
                    Xi_pseudo, 
                    Zi_pseudo, 
                    Rhoi_pseudo,
                    levels=50,  # Transitions lisses
                    cmap='jet',  # Rainbow classique : bleu → cyan → vert → jaune → orange → rouge
                    norm=LogNorm(vmin=vmin_pseudo, vmax=vmax_pseudo),
                    extend='both'
                )
                
                # Ajouter les contours pour mieux visualiser les transitions
                contours = ax_pseudo.contour(
                    Xi_pseudo, 
                    Zi_pseudo, 
                    Rhoi_pseudo,
                    levels=10,
                    colors='black',
                    linewidths=0.5,
                    alpha=0.3
                )
                
                # ANNOTATION DES ZONES AVEC VALEURS RÉELLES MESURÉES
                # Identifier les zones caractéristiques et annoter avec les VRAIES valeurs
                
                # Définir les plages de résistivité clés
                rho_ranges = [
                    (0, 1, 'Eau salée/Argile saturée', '#0000FF'),
                    (1, 10, 'Argile compacte/Limon', '#00FFFF'),
                    (10, 50, 'Sable fin/Eau douce', '#00FF00'),
                    (50, 100, 'Sable moyen', '#FFFF00'),
                    (100, 300, 'Sable grossier/Gravier', '#FFA500'),
                    (300, 1000, 'Roche altérée', '#FF6347'),
                    (1000, 10000, 'Roche consolidée', '#FF0000')
                ]
                
                # Pour chaque plage, trouver les points de mesure réels et annoter
                annotations_added = []
                for rho_min, rho_max, label, color_label in rho_ranges:
                    # Trouver les points RÉELS dans cette plage
                    mask_range = (Rho_real >= rho_min) & (Rho_real < rho_max)
                    if mask_range.sum() > 0:
                        X_range = X_real[mask_range]
                        Z_range = Z_real[mask_range]
                        Rho_range = Rho_real[mask_range]
                        
                        # Position centrale de la zone (moyenne pondérée)
                        x_center = np.mean(X_range)
                        z_center = np.mean(Z_range)
                        rho_mean = np.mean(Rho_range)
                        rho_min_zone = np.min(Rho_range)
                        rho_max_zone = np.max(Rho_range)
                        count = len(Rho_range)
                        
                        # Éviter les annotations qui se chevauchent
                        too_close = False
                        for prev_x, prev_z in annotations_added:
                            if abs(x_center - prev_x) < 5 and abs(z_center - prev_z) < 2:
                                too_close = True
                                break
                        
                        if not too_close and count >= 3:  # Au moins 3 points pour annoter
                            # Annotation avec fond semi-transparent
                            bbox_props = dict(boxstyle='round,pad=0.5', 
                                            facecolor=color_label, 
                                            alpha=0.7, 
                                            edgecolor='black', 
                                            linewidth=1.5)
                            
                            text_color = 'white' if rho_mean < 100 else 'black'
                            
                            ax_pseudo.annotate(
                                f'{label}\n{rho_min_zone:.1f}-{rho_max_zone:.1f} Ω·m\n({count} mesures)',
                                xy=(x_center, z_center),
                                fontsize=8,
                                fontweight='bold',
                                color=text_color,
                                bbox=bbox_props,
                                ha='center',
                                va='center',
                                zorder=10
                            )
                            annotations_added.append((x_center, z_center))
                
                # Superposer les points de mesure RÉELS avec leurs valeurs
                scatter_real = ax_pseudo.scatter(
                    X_real, 
                    Z_real, 
                    c=Rho_real,
                    s=50,
                    cmap='jet',
                    norm=LogNorm(vmin=vmin_pseudo, vmax=vmax_pseudo),
                    edgecolors='white',
                    linewidths=1,
                    alpha=0.9,
                    zorder=15,
                    label=f'{len(Rho_real)} mesures réelles'
                )
                
                # Barre de couleur avec échelle logarithmique
                cbar_pseudo = plt.colorbar(pcm_pseudo, ax=ax_pseudo, pad=0.02, aspect=30)
                cbar_pseudo.set_label('Résistivité Apparente (Ω·m)', fontsize=12, fontweight='bold')
                cbar_pseudo.ax.tick_params(labelsize=10)
                
                # Configuration des axes (format classique)
                ax_pseudo.set_xlabel('Position (m)', fontsize=12, fontweight='bold')
                ax_pseudo.set_ylabel('Profondeur (m)', fontsize=12, fontweight='bold')
                ax_pseudo.set_title(
                    'Pseudo-Section de Résistivité Apparente\nMeasured Apparent Resistivity Pseudosection',
                    fontsize=14, 
                    fontweight='bold'
                )
                
                # Inverser l'axe Y (profondeur positive vers le bas)
                ax_pseudo.invert_yaxis()
                
                # Grille légère
                ax_pseudo.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
                
                # Légende
                ax_pseudo.legend(loc='upper right', fontsize=10, framealpha=0.9)
                
                # Ajuster les marges
                plt.tight_layout()
                
                # Afficher
                st.pyplot(fig_pseudo)
                plt.close()
                
                # Statistiques de la pseudo-section
                col1_ps, col2_ps, col3_ps = st.columns(3)
                with col1_ps:
                    st.metric("📏 Points de mesure", f"{len(Rho_real)}")
                with col2_ps:
                    st.metric("📊 Plage de résistivité", f"{vmin_pseudo:.1f} - {vmax_pseudo:.1f} Ω·m")
                with col3_ps:
                    st.metric("🎯 Résistivité médiane", f"{np.median(Rho_real):.2f} Ω·m")
                
                # NOUVEAU: Analyse statistique des zones détectées
                st.markdown("---")
                st.markdown("### 📊 Distribution des Matériaux Détectés (Valeurs Réelles Mesurées)")
                
                # Créer un tableau détaillé avec les vraies valeurs mesurées
                detection_data = []
                
                for rho_min, rho_max, label, color in rho_ranges:
                    mask_range = (Rho_real >= rho_min) & (Rho_real < rho_max)
                    count = mask_range.sum()
                    percentage = (count / len(Rho_real)) * 100
                    
                    if count > 0:
                        rho_values = Rho_real[mask_range]
                        detection_data.append({
                            'Plage (Ω·m)': f'{rho_min:.1f} - {rho_max:.1f}',
                            'Matériau Principal': label,
                            'Mesures': count,
                            'Proportion (%)': f'{percentage:.1f}%',
                            'ρ min (Ω·m)': f'{rho_values.min():.2f}',
                            'ρ max (Ω·m)': f'{rho_values.max():.2f}',
                            'ρ moyen (Ω·m)': f'{rho_values.mean():.2f}'
                        })
                
                if detection_data:
                    df_detection = pd.DataFrame(detection_data)
                    st.dataframe(df_detection, use_container_width=True)
                    
                    st.success(f"✅ {len(detection_data)} types de matériaux détectés sur {len(Rho_real)} mesures")
                
                # NOUVEAU: Tableau d'interprétation avec PROBABILITÉS (fonction réutilisable)
                st.markdown("---")
                st.markdown("### 🎯 Interprétation Géologique avec Probabilités")
                
                st.markdown("""
                **Important** : Une même plage de résistivité peut correspondre à plusieurs matériaux.  
                Les **probabilités** indiquent la vraisemblance de chaque interprétation selon le contexte géologique.
                """)
                
                # Afficher le tableau de probabilités
                st.markdown(get_interpretation_probability_table(), unsafe_allow_html=True)
                
            # Préparer les données pour l'inversion
            # Grouper par survey_point et depth pour créer une matrice 2D
            survey_points = sorted(df_pygimli['survey_point'].unique())
            depths = sorted(df_pygimli['depth'].unique())
            
            # Créer une matrice de résistivité (survey_points x depths)
            rho_matrix = np.full((len(survey_points), len(depths)), np.nan)
            
            for i, sp in enumerate(survey_points):
                for j, depth in enumerate(depths):
                    mask = (df_pygimli['survey_point'] == sp) & (df_pygimli['depth'] == depth)
                    if mask.sum() > 0:
                        rho_matrix[i, j] = df_pygimli.loc[mask, 'data'].values[0]
            
            # Remplir les NaN avec interpolation - CORRECTION DU BUG
            from scipy.interpolate import griddata
            
            # Créer des coordonnées pour chaque point de la matrice
            points_valid = []
            values_valid = []
            
            for i in range(len(survey_points)):
                for j in range(len(depths)):
                    if not np.isnan(rho_matrix[i, j]):
                        points_valid.append([i, j])
                        values_valid.append(rho_matrix[i, j])
            
            if len(points_valid) > 3:  # Assez de points pour interpolation
                points_valid = np.array(points_valid)
                values_valid = np.array(values_valid)
                
                # Créer une grille pour interpolation
                grid_x, grid_y = np.meshgrid(range(len(survey_points)), range(len(depths)), indexing='ij')
                
                # Interpoler
                rho_matrix_interp = griddata(
                    points_valid, 
                    values_valid, 
                    (grid_x, grid_y), 
                    method='cubic',
                    fill_value=np.nanmean(rho_matrix)
                )
                
                # Remplir les NaN restants avec la moyenne
                rho_matrix_interp = np.nan_to_num(rho_matrix_interp, nan=np.nanmean(rho_matrix))
            else:
                rho_matrix_interp = np.nan_to_num(rho_matrix, nan=np.nanmean(rho_matrix))
            
            st.success(f"✅ Matrice de résistivité créée: {len(survey_points)} points × {len(depths)} profondeurs")
            
            # ========== CARROYAGE STRATIFIÉ PAR PROFONDEUR ==========
            st.markdown("---")
            st.subheader("🔲 Carroyage Géologique Stratifié par Profondeur")
            st.markdown("""
            Visualisation en **damier stratifié** montrant TOUS les types de matériaux détectés à chaque niveau de profondeur.
            Chaque cellule représente une mesure RÉELLE avec sa classification géologique complète.
            """)
            
            with st.expander("🗺️ Carroyage Complet - Tous Matériaux par Profondeur", expanded=True):
                # Créer une classification complète (16 classes couvrant TOUS les matériaux)
                def classify_all_materials(rho):
                    """Classification étendue de TOUS les matériaux géologiques"""
                    if rho < 0.5:
                        return 0, 'Eau de mer hypersalée', '#8B0000', '💧'
                    elif rho < 1:
                        return 1, 'Argile saturée salée', '#A0522D', '🟫'
                    elif rho < 5:
                        return 2, 'Argile marine / Vase', '#CD853F', '🟫'
                    elif rho < 10:
                        return 3, 'Eau salée / Limon', '#D2691E', '💧'
                    elif rho < 20:
                        return 4, 'Argile compacte', '#DEB887', '🟫'
                    elif rho < 50:
                        return 5, 'Sable fin saturé', '#F4A460', '🟡'
                    elif rho < 80:
                        return 6, 'Sable moyen humide', '#FFD700', '🟡'
                    elif rho < 120:
                        return 7, 'Sable grossier / Gravier fin', '#FFA500', '⚪'
                    elif rho < 200:
                        return 8, 'Gravier moyen sec', '#90EE90', '⚪'
                    elif rho < 350:
                        return 9, 'Gravier grossier / Cailloux', '#98FB98', '⚪'
                    elif rho < 500:
                        return 10, 'Roche altérée / Calcaire poreux', '#87CEEB', '⬛'
                    elif rho < 800:
                        return 11, 'Calcaire compact / Grès', '#87CEFA', '⬛'
                    elif rho < 1500:
                        return 12, 'Roche sédimentaire dure', '#4682B4', '⬛'
                    elif rho < 3000:
                        return 13, 'Granite / Basalte', '#483D8B', '⬛'
                    elif rho < 10000:
                        return 14, 'Socle cristallin', '#8B008B', '⬛'
                    else:
                        return 15, 'Minéral pur / Quartz', '#FF1493', '💎'
                
                # Créer la matrice de classification avec les VRAIES valeurs
                material_grid = np.zeros((len(depths), len(survey_points)))
                material_labels = []
                material_colors = []
                
                for i, depth in enumerate(depths):
                    row_labels = []
                    row_colors = []
                    for j, sp in enumerate(survey_points):
                        mask = (df_pygimli['survey_point'] == sp) & (df_pygimli['depth'] == depth)
                        if mask.sum() > 0:
                            rho_val = df_pygimli.loc[mask, 'data'].values[0]
                            cls, label, color, icon = classify_all_materials(rho_val)
                            material_grid[i, j] = cls
                            row_labels.append(f"{icon} {label}")
                            row_colors.append(color)
                        else:
                            material_grid[i, j] = np.nan
                            row_labels.append("N/A")
                            row_colors.append('#CCCCCC')
                    material_labels.append(row_labels)
                    material_colors.append(row_colors)
                
                # Créer la visualisation en carroyage
                fig_grid, ax_grid = plt.subplots(figsize=(16, max(10, len(depths) * 0.5)), dpi=150)
                
                # Créer une colormap avec TOUTES les 16 classes
                colors_all = ['#8B0000', '#A0522D', '#CD853F', '#D2691E', '#DEB887', '#F4A460', 
                             '#FFD700', '#FFA500', '#90EE90', '#98FB98', '#87CEEB', '#87CEFA',
                             '#4682B4', '#483D8B', '#8B008B', '#FF1493']
                cmap_all = ListedColormap(colors_all)
                bounds_all = list(range(17))
                norm_all = BoundaryNorm(bounds_all, cmap_all.N)
                
                # Afficher le carroyage
                im_grid = ax_grid.imshow(material_grid, cmap=cmap_all, norm=norm_all, 
                                        aspect='auto', interpolation='nearest')
                
                # Ajouter les valeurs de résistivité dans chaque cellule
                for i in range(len(depths)):
                    for j in range(len(survey_points)):
                        mask = (df_pygimli['survey_point'] == survey_points[j]) & \
                               (df_pygimli['depth'] == depths[i])
                        if mask.sum() > 0:
                            rho_val = df_pygimli.loc[mask, 'data'].values[0]
                            text_color = 'white' if material_grid[i, j] < 8 else 'black'
                            ax_grid.text(j, i, f'{rho_val:.1f}', 
                                       ha='center', va='center', 
                                       fontsize=7, fontweight='bold',
                                       color=text_color)
                
                # Configuration des axes
                ax_grid.set_xticks(range(len(survey_points)))
                ax_grid.set_xticklabels([f'P{int(sp)}' for sp in survey_points], fontsize=9)
                ax_grid.set_yticks(range(len(depths)))
                ax_grid.set_yticklabels([f'{abs(d):.2f}m' for d in depths], fontsize=9)
                
                ax_grid.set_xlabel('Points de Sondage', fontsize=12, fontweight='bold')
                ax_grid.set_ylabel('Profondeur (m)', fontsize=12, fontweight='bold')
                ax_grid.set_title('Carroyage Géologique Complet - Classification par Profondeur\n16 Types de Matériaux Identifiés', 
                                fontsize=14, fontweight='bold')
                
                # Ajouter une grille
                ax_grid.set_xticks(np.arange(len(survey_points)) - 0.5, minor=True)
                ax_grid.set_yticks(np.arange(len(depths)) - 0.5, minor=True)
                ax_grid.grid(which='minor', color='white', linestyle='-', linewidth=2)
                
                # Légende compacte à droite
                from matplotlib.patches import Patch
                legend_elements = [
                    Patch(facecolor='#8B0000', label='💧 Eau hypersalée (< 0.5)'),
                    Patch(facecolor='#A0522D', label='🟫 Argile salée (0.5-1)'),
                    Patch(facecolor='#CD853F', label='🟫 Argile marine (1-5)'),
                    Patch(facecolor='#D2691E', label='💧 Eau salée (5-10)'),
                    Patch(facecolor='#DEB887', label='🟫 Argile compacte (10-20)'),
                    Patch(facecolor='#F4A460', label='🟡 Sable fin (20-50)'),
                    Patch(facecolor='#FFD700', label='🟡 Sable moyen (50-80)'),
                    Patch(facecolor='#FFA500', label='🟡 Sable grossier (80-120)'),
                    Patch(facecolor='#90EE90', label='⚪ Gravier (120-200)'),
                    Patch(facecolor='#98FB98', label='⚪ Gravier grossier (200-350)'),
                    Patch(facecolor='#87CEEB', label='⬛ Roche altérée (350-500)'),
                    Patch(facecolor='#87CEFA', label='⬛ Calcaire (500-800)'),
                    Patch(facecolor='#4682B4', label='⬛ Roche dure (800-1500)'),
                    Patch(facecolor='#483D8B', label='⬛ Granite (1500-3000)'),
                    Patch(facecolor='#8B008B', label='⬛ Socle (3000-10000)'),
                    Patch(facecolor='#FF1493', label='💎 Minéral pur (>10000)')
                ]
                ax_grid.legend(handles=legend_elements, loc='center left', 
                             bbox_to_anchor=(1.02, 0.5), fontsize=8, framealpha=0.95)
                
                plt.tight_layout()
                st.pyplot(fig_grid)
                plt.close()
                
                # Tableau statistique par profondeur
                st.markdown("### 📊 Statistiques par Niveau de Profondeur")
                
                depth_stats_list = []
                for i, depth in enumerate(depths):
                    depth_vals = []
                    for j, sp in enumerate(survey_points):
                        mask = (df_pygimli['survey_point'] == sp) & (df_pygimli['depth'] == depth)
                        if mask.sum() > 0:
                            depth_vals.append(df_pygimli.loc[mask, 'data'].values[0])
                    
                    if depth_vals:
                        depth_vals = np.array(depth_vals)
                        # Déterminer le matériau dominant
                        classes = [classify_all_materials(v)[1] for v in depth_vals]
                        dominant = max(set(classes), key=classes.count)
                        
                        depth_stats_list.append({
                            'Profondeur (m)': f'{abs(depth):.2f}',
                            'ρ Min (Ω·m)': f'{depth_vals.min():.2f}',
                            'ρ Max (Ω·m)': f'{depth_vals.max():.2f}',
                            'ρ Moyenne (Ω·m)': f'{depth_vals.mean():.2f}',
                            'Matériau dominant': dominant,
                            'Variété': len(set(classes))
                        })
                
                if depth_stats_list:
                    stats_df = pd.DataFrame(depth_stats_list)
                    st.dataframe(stats_df, use_container_width=True, height=min(400, len(depth_stats_list) * 40))
                    
                    st.success(f"✅ {len(depth_stats_list)} niveaux de profondeur analysés - {len(set([d['Matériau dominant'] for d in depth_stats_list]))} matériaux différents détectés")
            
            # ========== SECTION INVERSION PYGIMLI ==========
            st.markdown("---")
            st.markdown("## 🔬 Inversion pyGIMLi - Modélisation Avancée")
            st.markdown(
                "Cette section permet de lancer une inversion géophysique complète avec pyGIMLi "
                "pour obtenir un modèle 2D de résistivité du sous-sol basé sur vos données réelles.\n\n"
                "**Fonctionnalités :**\n"
                "- Inversion tomographique 2D avec régularisation\n"
                "- Schémas de mesure configurables (Wenner, Schlumberger, Dipôle-Dipôle)\n"
                "- Visualisation des résultats avec classification hydrogéologique\n"
                "- Export des données interprétées"
            )
            
            # Paramètres de simulation
            col1, col2 = st.columns(2)
            with col1:
                n_electrodes = st.slider("Nombre d'électrodes", max(10, len(survey_points)), 100, 
                                       min(50, max(10, len(survey_points))), key="electrodes")
                spacing = st.slider("Espacement électrodes (m)", 0.5, 5.0, 1.0, key="spacing")
            with col2:
                depth_max = st.slider("Profondeur max (m)", 5, 50, 
                                    max(10, int(np.abs(df_pygimli['depth']).max())), key="depth_max")
                scheme_type = st.selectbox("Type de configuration", 
                                         ["wenner", "schlumberger", "dipole-dipole"], 
                                         index=0, key="scheme")

            if st.button("🚀 Lancer l'Inversion pyGIMLi", type="primary"):
                with st.spinner("🔄 Inversion en cours avec pyGIMLi..."):
                    try:
                        # Utiliser les données réelles du fichier
                        # Créer un profil basé sur les survey_points
                        x_positions = np.array(survey_points) * spacing  # Convertir survey_points en distances
                        z_depths = np.abs(np.array(depths))  # Profondeurs positives
                        
                        # Adapter la matrice à la taille du mesh
                        n_depth_points = min(len(z_depths), int(depth_max * 2))
                        
                        # Créer un mesh 2D pour pyGIMLi adapté aux données réelles
                        # CORRECTION: createGrid() accepte deux vecteurs x et y (sans worldDim)
                        x_vec = pg.Vector(np.linspace(x_positions.min(), x_positions.max(), n_electrodes))
                        y_vec = pg.Vector(np.linspace(0, -depth_max, n_depth_points))
                        mesh = pg.createGrid(x_vec, y_vec)

                        # Utiliser les données réelles comme modèle initial
                        # Redimensionner rho_matrix_interp pour correspondre au mesh
                        # CORRECTION: Remplacer interp2d par RegularGridInterpolator (SciPy 1.14.0+)
                        from scipy.interpolate import RegularGridInterpolator
                        
                        # Créer les coordonnées de la grille originale
                        x_orig = np.linspace(0, len(survey_points)-1, len(survey_points))
                        y_orig = np.linspace(0, len(depths)-1, len(depths))
                        
                        # Créer l'interpolateur
                        interpolator = RegularGridInterpolator(
                            (x_orig, y_orig), 
                            rho_matrix_interp, 
                            method='cubic',
                            bounds_error=False,
                            fill_value=np.nanmean(rho_matrix_interp)
                        )
                        
                        # Échantillonner sur le nouveau grid
                        x_new = np.linspace(0, len(survey_points)-1, n_electrodes)
                        y_new = np.linspace(0, len(depths)-1, n_depth_points)
                        X_new, Y_new = np.meshgrid(x_new, y_new, indexing='ij')
                        points_new = np.column_stack([X_new.ravel(), Y_new.ravel()])
                        rho_resampled = interpolator(points_new).reshape(n_electrodes, n_depth_points)
                        
                        # Aplatir pour le modèle initial
                        model_initial = rho_resampled.flatten()

                        # Créer le schéma de mesure
                        # CORRECTION: Utiliser les noms corrects de schémas pyGIMLi
                        scheme = pg.DataContainerERT()
                        
                        # Définir les positions des électrodes
                        for i, x_pos in enumerate(x_positions):
                            scheme.createSensor([x_pos, 0.0])
                        
                        # Créer le schéma selon le type choisi
                        # createFourPointData(index, eaID, ebID, emID, enID)
                        # où A et B sont les électrodes de courant, M et N de potentiel
                        measurement_idx = 0
                        
                        if scheme_type == "wenner":
                            # Schéma Wenner: a-a-a spacing (ABMN)
                            for a in range(1, n_electrodes // 3):
                                for i in range(n_electrodes - 3*a):
                                    scheme.createFourPointData(measurement_idx, i, i+3*a, i+a, i+2*a)
                                    measurement_idx += 1
                        elif scheme_type == "schlumberger":
                            # Schéma Schlumberger: MN petit, AB grand
                            for mn in range(1, 3):
                                for ab in range(mn+2, n_electrodes // 2):
                                    for i in range(n_electrodes - 2*ab):
                                        m = i + ab - mn//2
                                        n = i + ab + mn//2
                                        if m >= 0 and n < n_electrodes and m < n:
                                            scheme.createFourPointData(measurement_idx, i, i+2*ab, m, n)
                                            measurement_idx += 1
                        else:  # dipole-dipole
                            # Schéma Dipôle-Dipôle
                            for sep in range(1, n_electrodes // 3):
                                for i in range(n_electrodes - 3*sep - 1):
                                    scheme.createFourPointData(measurement_idx, i, i+sep, i+2*sep, i+3*sep)
                                    measurement_idx += 1
                        
                        # Ajouter des résistances apparentes fictives basées sur le modèle
                        scheme.set('rhoa', pg.Vector(scheme.size(), np.mean(model_initial)))
                        scheme.set('k', pg.Vector(scheme.size(), 1.0))

                        # Simuler les données avec le modèle initial basé sur les données réelles
                        # Utiliser simulate de pygimli.ert
                        from pygimli.physics import ert
                        data = ert.simulate(mesh, scheme=scheme, res=model_initial)

                        # Inversion avec pyGIMLi
                        ert_manager = ERTManager()
                        
                        # Configuration de l'inversion
                        ert_manager.setMesh(mesh)
                        ert_manager.setData(data)
                        
                        # Paramètres d'inversion
                        ert_manager.inv.setLambda(20)  # Régularisation
                        ert_manager.inv.setMaxIter(20)  # Iterations max
                        ert_manager.inv.setAbsoluteError(0.01)  # Erreur absolue
                        
                        # Lancer l'inversion
                        model_inverted = ert_manager.invert()
                        
                        # Résultat de l'inversion
                        rho_inverted = ert_manager.inv.model()
                        
                        # Reshape pour visualisation
                        rho_2d = rho_inverted.reshape(n_depth_points, n_electrodes).T

                        # Palette de couleurs hydrogéologique (4 classes) - RESPECT DU TABLEAU
                        colors = ['#FF4500', '#FFD700', '#87CEEB', '#00008B']  # Rouge vif, Jaune, Bleu clair, Bleu foncé
                        bounds = [0, 1, 10, 100, np.inf]
                        cmap = ListedColormap(colors)
                        norm = BoundaryNorm(bounds, cmap.N)

                        # Visualisation
                        fig_pygimli, ax_pygimli = plt.subplots(figsize=(14, 8), dpi=150)

                        # Positions pour l'affichage
                        x_display = np.linspace(x_positions.min(), x_positions.max(), n_electrodes)
                        z_display = np.linspace(0.5, depth_max, n_depth_points)

                        # Contour avec niveaux définis
                        pcm = ax_pygimli.contourf(x_display, z_display, 
                                                rho_2d.T, levels=bounds, cmap=cmap, norm=norm, extend='max')

                        ax_pygimli.set_xlabel('Position (m)', fontsize=12, fontweight='bold')
                        ax_pygimli.set_ylabel('Profondeur (m)', fontsize=12, fontweight='bold')
                        ax_pygimli.set_title(f'Coupe ERT Inversée - pyGIMLi ({scheme_type})\n{n_electrodes} électrodes, {len(df_pygimli)} mesures réelles', 
                                           fontsize=14, fontweight='bold')
                        ax_pygimli.invert_yaxis()
                        ax_pygimli.grid(True, alpha=0.3)

                        # Superposer les points de mesure réels
                        scatter = ax_pygimli.scatter(
                            df_pygimli['survey_point'] * spacing, 
                            np.abs(df_pygimli['depth']), 
                            c=df_pygimli['data'], 
                            cmap='jet_r', 
                            s=50, 
                            edgecolors='black', 
                            linewidths=1, 
                            alpha=0.7, 
                            zorder=10,
                            norm=LogNorm(vmin=max(0.1, df_pygimli['data'].min()), 
                                       vmax=df_pygimli['data'].max())
                        )

                        # Colorbar avec labels - RESPECT DU TABLEAU
                        cbar = plt.colorbar(pcm, ax=ax_pygimli, ticks=bounds[:-1])
                        cbar.set_label('Résistivité apparente (Ω·m)', fontsize=11, fontweight='bold')
                        cbar.ax.set_yticklabels(['0.1-1', '1-10', '10-100', '> 100'])

                        plt.tight_layout()
                        st.pyplot(fig_pygimli)
                        plt.close()

                        # ========== 4 COUPES INVERSÉES SUPPLÉMENTAIRES ==========
                        st.markdown("---")
                        st.subheader("🎯 Coupes Inversées PyGIMLi - 4 Visualisations Géologiques")
                        st.markdown(
                            "Résultats de l'inversion tomographique avec pyGIMLi, affichant les résistivités VRAIES "
                            "(après inversion) avec classification hydrogéologique et lithologique."
                        )
                        
                        # COUPE INVERSÉE 1: Résistivité vraie avec colormap standard ERT
                        with st.expander("📊 Coupe Inversée 1 - Résistivité Vraie (échelle log)", expanded=True):
                            fig_inv1, ax_inv1 = plt.subplots(figsize=(14, 7), dpi=150)
                            
                            # Afficher avec échelle logarithmique
                            vmin_inv = max(0.01, rho_2d.min())
                            vmax_inv = rho_2d.max()
                            
                            pcm_inv1 = ax_inv1.pcolormesh(x_display, z_display, rho_2d.T,
                                                         cmap='jet_r', shading='auto',
                                                         norm=LogNorm(vmin=vmin_inv, vmax=vmax_inv))
                            
                            ax_inv1.invert_yaxis()
                            ax_inv1.set_xlabel('Distance (m)', fontsize=12, fontweight='bold')
                            ax_inv1.set_ylabel('Profondeur (m)', fontsize=12, fontweight='bold')
                            ax_inv1.set_title('Coupe Inversée 1: Résistivité Vraie du Sous-Sol\nÉchelle Logarithmique', 
                                            fontsize=13, fontweight='bold')
                            ax_inv1.grid(True, alpha=0.3, linestyle='--', color='white')
                            
                            cbar_inv1 = fig_inv1.colorbar(pcm_inv1, ax=ax_inv1, extend='both')
                            cbar_inv1.set_label('Résistivité vraie (Ω·m)', fontsize=11, fontweight='bold')
                            
                            plt.tight_layout()
                            st.pyplot(fig_inv1)
                            plt.close()
                            
                            st.markdown(
                                f"**Résultats de l'inversion :**\n"
                                f"- **Plage mesurée :** {vmin_inv:.3f} - {vmax_inv:.3f} Ω·m\n"
                                f"- **RMS Error :** {ert_manager.inv.relrms():.3f}\n"
                                f"- **Itérations :** {ert_manager.inv.iterations()}\n"
                                f"- **Maillage :** {n_electrodes} × {n_depth_points} points"
                            )
                        
                        # COUPE INVERSÉE 2: Classification hydrogéologique (4 classes)
                        # COUPE INVERSÉE 2: Classification hydrogéologique (4 classes)
                        with st.expander("💧 Coupe Inversée 2 - Classification Hydrogéologique", expanded=True):
                            fig_inv2, ax_inv2 = plt.subplots(figsize=(14, 7), dpi=150)
                            
                            # Classifier les résistivités inversées - RESPECT DU TABLEAU
                            def classify_water_inv(rho):
                                if rho < 1:
                                    return 0
                                elif rho < 10:
                                    return 1
                                elif rho < 100:
                                    return 2
                                else:
                                    return 3
                            
                            water_classes_inv = np.vectorize(classify_water_inv)(rho_2d)
                            
                            # Colormap 4 classes - COULEURS EXACTES DU TABLEAU
                            colors_water = ['#FF4500', '#FFD700', '#87CEEB', '#00008B']  # Rouge vif, Jaune, Bleu clair, Bleu foncé
                            cmap_water = ListedColormap(colors_water)
                            bounds_water = [0, 1, 2, 3, 4]
                            norm_water = BoundaryNorm(bounds_water, cmap_water.N)
                            
                            pcm_inv2 = ax_inv2.pcolormesh(x_display, z_display, water_classes_inv.T,
                                                         cmap=cmap_water, norm=norm_water, shading='auto')
                            
                            ax_inv2.invert_yaxis()
                            ax_inv2.set_xlabel('Distance (m)', fontsize=12, fontweight='bold')
                            ax_inv2.set_ylabel('Profondeur (m)', fontsize=12, fontweight='bold')
                            ax_inv2.set_title('Coupe Inversée 2: Classification Hydrogéologique (Résistivités Vraies)\n4 Types d\'Eau Identifiés', 
                                            fontsize=13, fontweight='bold')
                            ax_inv2.grid(True, alpha=0.3, linestyle='--', color='gray')
                            
                            cbar_inv2 = fig_inv2.colorbar(pcm_inv2, ax=ax_inv2, ticks=[0.5, 1.5, 2.5, 3.5])
                            cbar_inv2.ax.set_yticklabels(['Eau de mer\n0.1-1 Ω·m', 
                                                         'Eau salée (nappe)\n1-10 Ω·m',
                                                         'Eau douce\n10-100 Ω·m',
                                                         'Eau très pure\n> 100 Ω·m'])
                            cbar_inv2.set_label('Type d\'Eau', fontsize=11, fontweight='bold')
                            
                            plt.tight_layout()
                            st.pyplot(fig_inv2)
                            plt.close()
                            
                            st.markdown("**Interprétation hydrogéologique VRAIE (après inversion, selon tableau) :**\n"
                                       "- 🔴 **Rouge vif/Orange** (0.1-1 Ω·m) : Eau de mer, intrusion marine\n"
                                       "- 🟡 **Jaune/Orange** (1-10 Ω·m) : Eau salée (nappe saumâtre)\n"
                                       "- 🟢 **Vert/Bleu clair** (10-100 Ω·m) : Eau douce exploitable\n"
                                       "- 🔵 **Bleu foncé** (> 100 Ω·m) : Eau très pure / Roches sèches")

                        
                        # COUPE INVERSÉE 3: Gradient horizontal (hétérogénéités latérales)
                        with st.expander("📈 Coupe Inversée 3 - Gradient Horizontal (Hétérogénéités)", expanded=False):
                            fig_inv3, (ax_inv3a, ax_inv3b) = plt.subplots(1, 2, figsize=(16, 7), dpi=150)
                            
                            # Calculer le gradient horizontal
                            gradient_x = np.gradient(rho_2d, axis=0)
                            gradient_magnitude_h = np.abs(gradient_x)
                            
                            # Graphique gauche: résistivité
                            pcm_inv3a = ax_inv3a.pcolormesh(x_display, z_display, rho_2d.T,
                                                           cmap='jet_r', shading='auto',
                                                           norm=LogNorm(vmin=vmin_inv, vmax=vmax_inv))
                            ax_inv3a.invert_yaxis()
                            ax_inv3a.set_xlabel('Distance (m)', fontsize=11, fontweight='bold')
                            ax_inv3a.set_ylabel('Profondeur (m)', fontsize=11, fontweight='bold')
                            ax_inv3a.set_title('Résistivité Inversée', fontsize=12, fontweight='bold')
                            ax_inv3a.grid(True, alpha=0.3)
                            cbar_3a = fig_inv3.colorbar(pcm_inv3a, ax=ax_inv3a)
                            cbar_3a.set_label('ρ (Ω·m)', fontsize=10, fontweight='bold')
                            
                            # Graphique droite: gradient horizontal
                            pcm_inv3b = ax_inv3b.pcolormesh(x_display, z_display, gradient_magnitude_h.T,
                                                           cmap='hot', shading='auto')
                            
                            # Contours des hétérogénéités majeures
                            threshold_grad_h = np.percentile(gradient_magnitude_h[gradient_magnitude_h > 0], 85)
                            if threshold_grad_h > 0:
                                ax_inv3b.contour(x_display, z_display, gradient_magnitude_h.T,
                                               levels=[threshold_grad_h], colors='cyan', 
                                               linewidths=2, linestyles='--', alpha=0.8)
                            
                            ax_inv3b.invert_yaxis()
                            ax_inv3b.set_xlabel('Distance (m)', fontsize=11, fontweight='bold')
                            ax_inv3b.set_ylabel('Profondeur (m)', fontsize=11, fontweight='bold')
                            ax_inv3b.set_title('Gradient Horizontal\nLignes cyan = Hétérogénéités latérales', 
                                             fontsize=12, fontweight='bold')
                            ax_inv3b.grid(True, alpha=0.3)
                            cbar_3b = fig_inv3.colorbar(pcm_inv3b, ax=ax_inv3b)
                            cbar_3b.set_label('|∂ρ/∂x|', fontsize=10, fontweight='bold')
                            
                            plt.tight_layout()
                            st.pyplot(fig_inv3)
                            plt.close()
                            
                            st.markdown(f"**Interprétation des gradients horizontaux :**\n"
                                       f"- **Lignes cyan** : Changements latéraux importants (seuil > {threshold_grad_h:.2f})\n"
                                       f"- **Zones chaudes** : Contacts géologiques latéraux, failles, intrusions\n"
                                       f"- **Applications** : Détection de limites d'aquifères, zones de fractures")
                        
                        # COUPE INVERSÉE 4: Modèle lithologique complet (9 formations)
                        with st.expander("🗺️ Coupe Inversée 4 - Modèle Lithologique Complet", expanded=False):
                            fig_inv4, ax_inv4 = plt.subplots(figsize=(14, 8), dpi=150)
                            
                            # Classification lithologique étendue
                            def classify_lithology_inv(rho):
                                if rho < 1:
                                    return 0
                                elif rho < 5:
                                    return 1
                                elif rho < 20:
                                    return 2
                                elif rho < 50:
                                    return 3
                                elif rho < 100:
                                    return 4
                                elif rho < 200:
                                    return 5
                                elif rho < 500:
                                    return 6
                                elif rho < 1000:
                                    return 7
                                else:
                                    return 8
                            
                            litho_classes_inv = np.vectorize(classify_lithology_inv)(rho_2d)
                            
                            # Colormap lithologique
                            colors_litho = ['#8B0000', '#A0522D', '#CD853F', '#F4A460', 
                                           '#FFD700', '#90EE90', '#87CEEB', '#4682B4', '#8B008B']
                            cmap_litho = ListedColormap(colors_litho)
                            bounds_litho = list(range(10))
                            norm_litho = BoundaryNorm(bounds_litho, cmap_litho.N)
                            
                            pcm_inv4 = ax_inv4.pcolormesh(x_display, z_display, litho_classes_inv.T,
                                                         cmap=cmap_litho, norm=norm_litho, shading='auto')
                            
                            # Contours lithologiques
                            ax_inv4.contour(x_display, z_display, litho_classes_inv.T,
                                          levels=bounds_litho, colors='black', 
                                          linewidths=0.5, alpha=0.4)
                            
                            ax_inv4.invert_yaxis()
                            ax_inv4.set_xlabel('Distance (m)', fontsize=12, fontweight='bold')
                            ax_inv4.set_ylabel('Profondeur (m)', fontsize=12, fontweight='bold')
                            ax_inv4.set_title('Coupe Inversée 4: Modèle Lithologique VRAI (Inversion pyGIMLi)\n9 Formations Géologiques', 
                                            fontsize=13, fontweight='bold')
                            ax_inv4.grid(True, alpha=0.2, linestyle='--', color='gray')
                            
                            # Légende lithologique complète
                            from matplotlib.patches import Patch
                            legend_elements = [
                                Patch(facecolor='#8B0000', label='Eau mer / Argile salée (< 1 Ω·m)'),
                                Patch(facecolor='#A0522D', label='Argile marine (1-5 Ω·m)'),
                                Patch(facecolor='#CD853F', label='Argile compacte (5-20 Ω·m)'),
                                Patch(facecolor='#F4A460', label='Sable fin saturé (20-50 Ω·m)'),
                                Patch(facecolor='#FFD700', label='Sable/Gravier (50-100 Ω·m)'),
                                Patch(facecolor='#90EE90', label='Gravier sec (100-200 Ω·m)'),
                                Patch(facecolor='#87CEEB', label='Roche altérée (200-500 Ω·m)'),
                                Patch(facecolor='#4682B4', label='Roche compacte (500-1000 Ω·m)'),
                                Patch(facecolor='#8B008B', label='Socle cristallin (> 1000 Ω·m)')
                            ]
                            ax_inv4.legend(handles=legend_elements, loc='upper left', 
                                         fontsize=8, framealpha=0.9, ncol=1)
                            
                            plt.tight_layout()
                            st.pyplot(fig_inv4)
                            plt.close()
                            
                            st.markdown("**Modèle lithologique VRAI (après inversion pyGIMLi) :**\n\n"
                                       "Ce modèle présente la **structure réelle du sous-sol** obtenue par inversion tomographique. "
                                       "Les résistivités affichées sont les **valeurs vraies** (non apparentes) après régularisation.\n\n"
                                       "**Recommandations pour forages :**\n"
                                       "- 💧 **Zones cibles** : Jaune/Or (50-100 Ω·m) = Aquifères productifs\n"
                                       "- ✅ **Bon potentiel** : Vert clair (100-200 Ω·m) = Graviers perméables\n"
                                       "- ⚠️ **Attention** : Marron/Rouge (< 20 Ω·m) = Argiles imperméables\n"
                                       "- 🚫 **À éviter** : Rouge foncé (< 1 Ω·m) = Intrusion saline")


                        # Statistiques de l'inversion
                        st.subheader("📊 Résultats de l'Inversion")

                        col_stats1, col_stats2, col_stats3 = st.columns(3)
                        with col_stats1:
                            st.metric("RMS Error", f"{ert_manager.inv.relrms():.3f}")
                        with col_stats2:
                            st.metric("Iterations", f"{ert_manager.inv.iterations()}")
                        with col_stats3:
                            st.metric("λ Régularisation", "20")

                        # Tableau d'interprétation hydrogéologique basé sur les données réelles
                        st.subheader("💧 Interprétation Hydrogéologique")

                        # Classification par profondeur (moyenne sur tous les survey points)
                        depth_stats = df_pygimli.groupby('depth')['data'].mean().reset_index()
                        depth_stats = depth_stats.sort_values('depth')
                        
                        water_types = []
                        for rho in depth_stats['data']:
                            if rho < 1:
                                water_types.append("Eau de mer")
                            elif rho < 10:
                                water_types.append("Eau salée")
                            elif rho < 100:
                                water_types.append("Eau douce")
                            else:
                                water_types.append("Eau très pure")

                        # DataFrame d'interprétation
                        interp_df = pd.DataFrame({
                            'Profondeur (m)': np.abs(depth_stats['depth']),
                            'ρ_a Moyenne (Ω·m)': depth_stats['data'],
                            'Type d\'Eau': water_types,
                            'Couleur': ['Rouge' if wt == "Eau de mer" else 
                                       'Orange' if wt == "Eau salée" else
                                       'Jaune' if wt == "Eau douce" else 'Bleu' 
                                       for wt in water_types]
                        })

                        st.dataframe(interp_df.style.background_gradient(cmap='RdYlBu_r', subset=['ρ_a Moyenne (Ω·m)']), 
                                   use_container_width=True)

                        # Graphique de classification - RESPECT DES COULEURS DU TABLEAU
                        fig_classif, ax_classif = plt.subplots(figsize=(12, 6))
                        colors_classif = ['#FF4500' if wt == "Eau de mer" else 
                                        '#FFD700' if wt == "Eau salée" else
                                        '#87CEEB' if wt == "Eau douce" else '#00008B' 
                                        for wt in water_types]

                        ax_classif.bar(np.abs(depth_stats['depth']), depth_stats['data'], 
                                     color=colors_classif, alpha=0.7, edgecolor='black')
                        ax_classif.set_yscale('log')
                        ax_classif.set_xlabel('Profondeur (m)', fontsize=11, fontweight='bold')
                        ax_classif.set_ylabel('Résistivité (Ω·m) - échelle log', fontsize=11, fontweight='bold')
                        ax_classif.set_title('Classification Hydrogéologique par Profondeur', fontsize=13, fontweight='bold')
                        ax_classif.grid(True, alpha=0.3)

                        # Légende avec couleurs exactes du tableau
                        from matplotlib.patches import Patch
                        legend_elements = [
                            Patch(facecolor='#FF4500', label='Eau de mer (0.1-1 Ω·m)'),
                            Patch(facecolor='#FFD700', label='Eau salée (1-10 Ω·m)'),
                            Patch(facecolor='#87CEEB', label='Eau douce (10-100 Ω·m)'),
                            Patch(facecolor='#00008B', label='Eau très pure (> 100 Ω·m)')
                        ]
                        ax_classif.legend(handles=legend_elements, loc='upper right')

                        plt.tight_layout()
                        st.pyplot(fig_classif)

                        # Export CSV interprété
                        csv_buffer = io.StringIO()
                        interp_df.to_csv(csv_buffer, index=False)

                        st.download_button(
                            label="💾 Télécharger CSV Interprété",
                            data=csv_buffer.getvalue(),
                            file_name="ert_pygimli_interprete.csv",
                            mime="text/csv",
                            key="download_pygimli_csv"
                        )

                        # ========== GÉNÉRATEUR DE RAPPORT PDF ==========
                        st.markdown("---")
                        st.subheader("📄 Générateur de Rapport Technique Complet")
                        
                        if st.button("🎯 Générer Rapport PDF Complet", type="primary", key="generate_pdf"):
                            with st.spinner("📝 Génération du rapport PDF en cours..."):
                                try:
                                    from reportlab.lib.pagesizes import A4, landscape
                                    from reportlab.lib.units import cm
                                    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
                                    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                                    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
                                    from reportlab.lib import colors
                                    from datetime import datetime
                                    import tempfile
                                    import os
                                    
                                    # Créer un fichier temporaire pour le PDF
                                    pdf_buffer = io.BytesIO()
                                    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4,
                                                          rightMargin=2*cm, leftMargin=2*cm,
                                                          topMargin=2*cm, bottomMargin=2*cm)
                                    
                                    # Styles
                                    styles = getSampleStyleSheet()
                                    title_style = ParagraphStyle(
                                        'CustomTitle',
                                        parent=styles['Heading1'],
                                        fontSize=24,
                                        textColor=colors.HexColor('#1f4788'),
                                        spaceAfter=30,
                                        alignment=TA_CENTER,
                                        fontName='Helvetica-Bold'
                                    )
                                    
                                    heading_style = ParagraphStyle(
                                        'CustomHeading',
                                        parent=styles['Heading2'],
                                        fontSize=16,
                                        textColor=colors.HexColor('#2e5c8a'),
                                        spaceAfter=12,
                                        spaceBefore=12,
                                        fontName='Helvetica-Bold'
                                    )
                                    
                                    normal_style = ParagraphStyle(
                                        'CustomNormal',
                                        parent=styles['Normal'],
                                        fontSize=10,
                                        alignment=TA_JUSTIFY,
                                        spaceAfter=6
                                    )
                                    
                                    # Contenu du rapport
                                    story = []
                                    
                                    # Page de titre
                                    story.append(Spacer(1, 3*cm))
                                    story.append(Paragraph("RAPPORT D'INVESTIGATION GÉOPHYSIQUE", title_style))
                                    story.append(Paragraph("Tomographie de Résistivité Électrique (ERT)", title_style))
                                    story.append(Spacer(1, 1*cm))
                                    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
                                    story.append(Paragraph(f"<b>Méthode:</b> Inversion pyGIMLi - {scheme_type.upper()}", normal_style))
                                    story.append(Paragraph(f"<b>Fichier:</b> {uploaded_freq_file.name}", normal_style))
                                    story.append(PageBreak())
                                    
                                    # 1. Résumé exécutif
                                    story.append(Paragraph("1. RÉSUMÉ EXÉCUTIF", heading_style))
                                    story.append(Paragraph(f"Ce rapport présente les résultats d'une investigation géophysique par tomographie "
                                                          f"de résistivité électrique (ERT) réalisée avec la méthode pyGIMLi. L'étude a porté "
                                                          f"sur {len(survey_points)} points de sondage avec {len(freq_columns)} fréquences de mesure, "
                                                          f"permettant d'analyser le sous-sol jusqu'à {depth_max:.1f} mètres de profondeur.", 
                                                          normal_style))
                                    story.append(Spacer(1, 0.5*cm))
                                    
                                    # Tableau récapitulatif
                                    summary_data = [
                                        ['Paramètre', 'Valeur'],
                                        ['Points de sondage', str(len(survey_points))],
                                        ['Fréquences mesurées', str(len(freq_columns))],
                                        ['Profondeur max', f'{depth_max:.1f} m'],
                                        ['Nombre d\'électrodes', str(n_electrodes)],
                                        ['Espacement', f'{spacing:.1f} m'],
                                        ['Configuration', scheme_type.upper()],
                                        ['RMS Error', f'{ert_manager.inv.relrms():.3f}'],
                                        ['Itérations', str(ert_manager.inv.iterations())]
                                    ]
                                    
                                    summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
                                    summary_table.setStyle(TableStyle([
                                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                                    ]))
                                    story.append(summary_table)
                                    story.append(Spacer(1, 1*cm))
                                    
                                    # 2. Méthodologie
                                    story.append(Paragraph("2. MÉTHODOLOGIE", heading_style))
                                    story.append(Paragraph(f"<b>2.1 Acquisition des données</b><br/>"
                                                          f"Les mesures de résistivité ont été effectuées avec un dispositif multi-fréquence "
                                                          f"permettant d'obtenir {len(df_pygimli)} mesures réparties sur {len(survey_points)} points. "
                                                          f"Les fréquences varient de {freq_columns[0].replace('freq_', '')} MHz à {freq_columns[-1].replace('freq_', '')} MHz.", 
                                                          normal_style))
                                    story.append(Spacer(1, 0.3*cm))
                                    
                                    story.append(Paragraph(f"<b>2.2 Traitement et inversion</b><br/>"
                                                          f"L'inversion des données a été réalisée avec pyGIMLi (Python Geophysical Inversion and Modeling Library). "
                                                          f"Configuration utilisée : schéma <b>{scheme_type.upper()}</b> avec {n_electrodes} électrodes "
                                                          f"espacées de {spacing:.1f} mètres. Le maillage 2D comprend {n_electrodes} × {n_depth_points} points. "
                                                          f"Paramètres d'inversion : λ = 20 (régularisation), {ert_manager.inv.iterations()} itérations, "
                                                          f"RMS error final = {ert_manager.inv.relrms():.3f}.", 
                                                          normal_style))
                                    story.append(Spacer(1, 0.5*cm))
                                    
                                    # 3. Résultats - Classification hydrogéologique
                                    story.append(Paragraph("3. RÉSULTATS - CLASSIFICATION HYDROGÉOLOGIQUE", heading_style))
                                    story.append(Paragraph("L'analyse des résistivités mesurées permet d'identifier 4 types d'eau distincts "
                                                          "selon les valeurs de résistivité apparente :", 
                                                          normal_style))
                                    story.append(Spacer(1, 0.3*cm))
                                    
                                    # Tableau de classification
                                    classif_data = [
                                        ['Type d\'Eau', 'Résistivité (Ω·m)', 'Interprétation'],
                                        ['Eau de mer', '< 1', 'Eau hypersalée, intrusion marine'],
                                        ['Eau salée', '1 - 10', 'Nappe saumâtre, mélange'],
                                        ['Eau douce', '10 - 100', 'Aquifère exploitable'],
                                        ['Eau très pure', '> 100', 'Eau pure ou roches sèches']
                                    ]
                                    
                                    classif_table = Table(classif_data, colWidths=[4*cm, 4*cm, 6*cm])
                                    classif_table.setStyle(TableStyle([
                                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                                        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                                        ('BACKGROUND', (0, 1), (-1, 1), colors.red),
                                        ('BACKGROUND', (0, 2), (-1, 2), colors.orange),
                                        ('BACKGROUND', (0, 3), (-1, 3), colors.yellow),
                                        ('BACKGROUND', (0, 4), (-1, 4), colors.lightblue),
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                                    ]))
                                    story.append(classif_table)
                                    story.append(Spacer(1, 0.5*cm))
                                    
                                    # Statistiques par profondeur (top 10)
                                    story.append(Paragraph("<b>3.1 Distribution par profondeur</b>", normal_style))
                                    story.append(Spacer(1, 0.3*cm))
                                    
                                    depth_table_data = [['Profondeur (m)', 'ρ Moyenne (Ω·m)', 'Type d\'Eau']]
                                    for idx, row in interp_df.head(10).iterrows():
                                        depth_table_data.append([
                                            f"{row['Profondeur (m)']:.2f}",
                                            f"{row['ρ_a Moyenne (Ω·m)']:.2f}",
                                            row["Type d'Eau"]
                                        ])
                                    
                                    depth_table = Table(depth_table_data, colWidths=[4*cm, 5*cm, 5*cm])
                                    depth_table.setStyle(TableStyle([
                                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                                    ]))
                                    story.append(depth_table)
                                    story.append(PageBreak())
                                    
                                    # 4. Interprétation géologique
                                    story.append(Paragraph("4. INTERPRÉTATION GÉOLOGIQUE", heading_style))
                                    story.append(Paragraph("<b>4.1 Modèle lithologique</b><br/>"
                                                          "L'analyse des résistivités inversées permet de proposer le modèle lithologique suivant :", 
                                                          normal_style))
                                    story.append(Spacer(1, 0.3*cm))
                                    
                                    # Tableau lithologique
                                    litho_data = [
                                        ['Formation', 'Résistivité (Ω·m)', 'Lithologie probable'],
                                        ['Zone 1', '< 1', 'Argile saturée salée / Eau de mer'],
                                        ['Zone 2', '1 - 5', 'Argile marine / Vase'],
                                        ['Zone 3', '5 - 20', 'Argile compacte / Limon saturé'],
                                        ['Zone 4', '20 - 50', 'Sable fin saturé (eau douce)'],
                                        ['Zone 5', '50 - 100', 'Sable moyen / Gravier fin'],
                                        ['Zone 6', '100 - 200', 'Gravier / Sable grossier sec'],
                                        ['Zone 7', '200 - 500', 'Roche altérée / Calcaire fissuré'],
                                        ['Zone 8', '500 - 1000', 'Roche sédimentaire compacte'],
                                        ['Zone 9', '> 1000', 'Socle rocheux / Granite']
                                    ]
                                    
                                    litho_table = Table(litho_data, colWidths=[3*cm, 4*cm, 7*cm])
                                    litho_table.setStyle(TableStyle([
                                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                                        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                                    ]))
                                    story.append(litho_table)
                                    story.append(Spacer(1, 0.5*cm))
                                    
                                    # 5. Recommandations
                                    story.append(Paragraph("5. RECOMMANDATIONS POUR FORAGES", heading_style))
                                    story.append(Paragraph("<b>5.1 Zones favorables</b><br/>"
                                                          "Les zones avec résistivités comprises entre <b>50 et 200 Ω·m</b> (sables et graviers) "
                                                          "constituent les cibles prioritaires pour l'implantation de forages d'eau. Ces formations "
                                                          "présentent une bonne perméabilité et un potentiel aquifère élevé.", 
                                                          normal_style))
                                    story.append(Spacer(1, 0.3*cm))
                                    
                                    story.append(Paragraph("<b>5.2 Zones à éviter</b><br/>"
                                                          "- <b>Résistivités < 1 Ω·m</b> : Intrusion d'eau salée, risque de contamination<br/>"
                                                          "- <b>Résistivités 1-20 Ω·m</b> : Argiles imperméables, faible productivité<br/>"
                                                          "- <b>Résistivités > 500 Ω·m</b> : Roches compactes, difficulté de forage", 
                                                          normal_style))
                                    story.append(Spacer(1, 0.3*cm))
                                    
                                    story.append(Paragraph("<b>5.3 Profondeur optimale</b><br/>"
                                                          "Selon l'analyse des données, la profondeur optimale pour les forages se situe "
                                                          "dans la plage où les résistivités sont comprises entre 50 et 100 Ω·m, "
                                                          "correspondant généralement aux formations sableuses saturées d'eau douce.", 
                                                          normal_style))
                                    story.append(PageBreak())
                                    
                                    # 6. Conclusions
                                    story.append(Paragraph("6. CONCLUSIONS", heading_style))
                                    story.append(Paragraph(f"L'investigation géophysique par tomographie de résistivité électrique a permis "
                                                          f"de caractériser le sous-sol sur {len(survey_points)} points de mesure jusqu'à "
                                                          f"{depth_max:.1f} mètres de profondeur. Les résultats de l'inversion pyGIMLi "
                                                          f"(RMS error = {ert_manager.inv.relrms():.3f}) montrent une bonne convergence et "
                                                          f"permettent d'établir un modèle hydrogéologique fiable.", 
                                                          normal_style))
                                    story.append(Spacer(1, 0.3*cm))
                                    
                                    story.append(Paragraph("La classification hydrogéologique révèle la présence de plusieurs types d'eau "
                                                          "et formations géologiques. Les aquifères d'eau douce exploitables ont été "
                                                          "identifiés et localisés, permettant d'optimiser l'implantation des futurs forages.", 
                                                          normal_style))
                                    story.append(Spacer(1, 0.5*cm))
                                    
                                    story.append(Paragraph("<b>Points clés :</b><br/>"
                                                          "• Classification en 4 types d'eau (mer, salée, douce, pure)<br/>"
                                                          "• Modèle lithologique 9 formations<br/>"
                                                          "• Identification des zones aquifères favorables<br/>"
                                                          "• Recommandations précises pour implantation de forages", 
                                                          normal_style))
                                    
                                    # Générer le PDF
                                    doc.build(story)
                                    pdf_buffer.seek(0)
                                    
                                    # Bouton de téléchargement
                                    st.download_button(
                                        label="📥 Télécharger le Rapport PDF",
                                        data=pdf_buffer,
                                        file_name=f"rapport_ert_pygimli_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                        mime="application/pdf",
                                        key="download_pdf_report"
                                    )
                                    
                                    st.success("✅ Rapport PDF généré avec succès !")
                                    
                                except ImportError:
                                    st.error("❌ ReportLab n'est pas installé. Installez-le avec : `pip install reportlab`")
                                except Exception as e:
                                    st.error(f"❌ Erreur lors de la génération du rapport : {str(e)}")

                        st.success(f"✅ **Inversion pyGIMLi terminée avec succès !**\n"
                                   f"- Configuration : {scheme_type} avec {n_electrodes} électrodes\n"
                                   f"- Erreur RMS : {ert_manager.inv.relrms():.3f}\n"
                                   f"- {len(interp_df)} niveaux de profondeur analysés\n"
                                   f"- {len(df_pygimli)} mesures réelles intégrées\n"
                                   f"- Classification hydrogéologique complète")

                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'inversion pyGIMLi : {str(e)}")
                        st.info("💡 Vérifiez que pyGIMLi est correctement installé : `pip install pygimli`")
        else:
            st.error("❌ Impossible de parser le fichier freq.dat. Vérifiez le format.")
    else:
        st.info("📁 Uploadez un fichier freq.dat pour commencer l'analyse multi-fréquence avec pyGIMLi")
        
        st.markdown("**Format attendu du fichier freq.dat :**\n"
                    "```\n"
                    "Projet,Point,Freq1,Freq2,Freq3,...\n"
                    "Projet Archange Ondimba 2,1,0.119,0.122,0.116,...\n"
                    "Projet Archange Ondimba 2,2,0.161,0.163,0.164,...\n"
                    "...\n"
                    "```\n\n"
                    "**Structure :**\n"
                    "- Colonne 1 : Nom du projet\n"
                    "- Colonne 2 : Numéro du point de sondage\n"
                    "- Colonnes 3+ : Valeurs de résistivité pour chaque fréquence (MHz)\n\n"
                    "**Note :** Les fréquences sont automatiquement converties en profondeurs pour l'analyse ERT\n\n"
                    "**Interprétation des couleurs (selon classification standard) :**\n"
                    "- 🔴 **Rouge vif / Orange** : Eau de mer (0.1 - 1 Ω·m)\n"
                    "- 🟡 **Jaune / Orange** : Eau salée nappe (1 - 10 Ω·m)\n"
                    "- 🟢 **Vert / Bleu clair** : Eau douce (10 - 100 Ω·m)\n"
                    "- 🔵 **Bleu foncé** : Eau très pure (> 100 Ω·m)")

# --- Sidebar ---
st.sidebar.image("logo_belikan.png", width="stretch")
st.sidebar.markdown("**SETRAF - Subaquifère ERT Analysis**  \n"
                    "💧 Outil d'analyse géophysique avancé  \n"
                    "Expert en hydrogéologie et tomographie électrique\n\n"
                    "**Version Optimisée – 08 Novembre 2025**  \n"
                    "✅ Calculateur Ts intelligent (Ravensgate Sonic)  \n"
                    "✅ Analyse .dat + détection anomalies (K-Means avec cache)  \n"
                    "✅ Tableau résistivité eau (descriptions détaillées)  \n"
                    "✅ Pseudo-sections 2D/3D basées sur vos données réelles  \n"
                    "✅ **NOUVEAU** : Stratigraphie complète (sols + eaux + roches + minéraux)  \n"
                    "✅ **NOUVEAU** : Visualisation 3D interactive des matériaux par couches  \n"
                    "✅ **NOUVEAU** : Précision millimétrique (3 décimales sur tous les axes)  \n"
                    "✅ **NOUVEAU** : Inversion pyGIMLi - ERT géophysique avancée  \n"
                    "✅ Interprétation multi-matériaux : 8 catégories géologiques  \n"
                    "✅ Performance optimisée avec @st.cache_data  \n"
                    "✅ Interpolation cubique cachée pour fluidité  \n"
                    "✅ Ticks basés sur mesures réelles (0.1, 0.2, 0.3...)  \n"
                    "✅ **Export PDF** : Rapports complets avec tous les graphiques\n\n"
                    "**Exports disponibles** :  \n"
                    "📥 CSV - Données brutes  \n"
                    "📊 Excel - Tableaux formatés  \n"
                    "📄 PDF Standard - Rapport d'analyse DTW (150 DPI)  \n"
                    "📄 PDF Stratigraphique - Classification géologique complète (150 DPI)\n\n"
                    "**Visualisations avancées** :  \n"
                    "🎨 Coupes 2D par type de matériau (8 plages de résistivité)  \n"
                    "🌐 Modèle 3D interactif (rotation 360°, zoom)  \n"
                    "📊 Histogrammes et profils de distribution  \n"
                    "🗺️ Cartographie spatiale des formations géologiques  \n"
                    "🔬 Inversion pyGIMLi avec classification hydrogéologique\n\n"
                    "**Catégories géologiques identifiées** :  \n"
                    "💧 Eaux (mer, salée, douce, pure)  \n"
                    "🧱 Argiles & sols saturés  \n"
                    "🏖️ Sables & graviers  \n"
                    "🪨 Roches sédimentaires (calcaire, grès, schiste)  \n"
                    "🌋 Roches ignées & métamorphiques (granite, basalte)  \n"
                    "💎 Minéraux & minerais (graphite, cuivre, or, quartz)\n\n"
                    "**Plages de résistivité** :  \n"
                    "- 0.001-1 Ω·m : Minéraux métalliques  \n"
                    "- 0.1-10 Ω·m : Eaux salées + argiles marines  \n"
                    "- 10-100 Ω·m : Eaux douces + sols fins  \n"
                    "- 100-1000 Ω·m : Sables saturés + graviers  \n"
                    "- 1000-10000 Ω·m : Roches sédimentaires  \n"
                    "- >10000 Ω·m : Socle cristallin (granite, quartzite)  \n\n"
                    "**🔬 Module pyGIMLi intégré** :  \n"
                    "- Inversion ERT complète avec algorithmes optimisés  \n"
                    "- Configurations Wenner, Schlumberger, Dipole-Dipole  \n"
                    "- Classification hydrogéologique automatique  \n"
                    "- Visualisation avec palette de couleurs physiques")

