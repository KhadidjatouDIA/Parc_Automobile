# -*- coding: utf-8 -*-
   
from odoo import models, fields, api

class Entretien(models.Model):
    _name = 'parc.automobile.entretien'
    _description = "Objet Entretien"
    
    name = fields.Char(string="Numéro d'entretien", required=True, default="Nouvel entretien")
    voiture_id = fields.Many2one('parc.automobile.voiture', string="Voiture", required=True)
    type_entretien = fields.Selection(string="Type d'entretien", required=True,
        selection=[('vidange', 'Vidange'),
                   ('changement_pieces', 'Changement des pièces'),
                   ('revision', 'Révision'),
                   ('controle_technique', 'Contrôle technique'),
                   ('reparation', 'Réparation')],
        default='vidange'
    )
    date_entretien = fields.Date(string="Date d'entretien", required=True, default=fields.Date.today)
    cout = fields.Float(string='Coût', digits=(10, 2))
    date_prochain_entretien = fields.Date(string="Prochain Entretien")
    description_entretien = fields.Text(string="Description")
    kilometrage_entretien = fields.Float(string="Kilométrage à l'entretien")
    garage = fields.Char(string="Garage/Atelier")
    facture = fields.Binary(string="Facture")
    
    # Champs calculés
    statut = fields.Selection([
        ('planifie', 'Planifié'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('reporte', 'Reporté')
    ], string="Statut", default='planifie')

    
    