# -*- coding: utf-8 -*-
# Ce sa présence est obligatoire pour un module Odoo
{
    'name': 'Parc Automobile',
    'version': '1.3',
    'summary': "Gestion complète d'un parc automobile",
    'sequence': -200,
    'description': """
        Module de gestion d'un parc automobile développé pour Odoo 18.
        
        Fonctionnalités principales :
        • Gestion des véhicules (voitures, utilitaires, motos, camions)
        • Suivi des entretiens et réparations
        • Gestion des affectations aux employés
        • Suivi de consommation carburant
        • Documents administratifs (assurance, carte grise, etc.)
        • Notifications et alertes automatiques
        • Tableaux de bord et rapports
        
        Conçu selon les spécifications du cahier des charges Odoo 18.
    """,
    'category': 'Industries',
    'website': 'https://www.groupeisi.com/',
    'depends': ['base', 'mail', 'hr'],
    'data': [
        # Sécurité
        'security/parc_automobile_security.xml',
        'security/ir.model.access.csv',
        
        # Données de base
        'data/parc_automobile_data.xml',
        'views/sequence.xml',
        
        # Vues
        'views/menu.xml',
        'views/marque.xml',
        'views/modele.xml',
        'views/voiture.xml',
        'views/employe.xml',
        'views/client.xml',
        'views/assurance.xml',
        'views/carte_grise.xml',
        'views/contrat_location.xml',
        'views/entretien.xml',
        'views/affectation.xml',
        'views/carburant.xml',
        'views/document_administratif.xml',
        'views/notification.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'author': "Youssoupha LAM",
}