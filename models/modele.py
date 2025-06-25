# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Modele(models.Model):
    _name = 'parc.automobile.modele'
    _description = "Modèle de véhicule"
    _order = 'marque_id, name'
    
    name = fields.Char(string='Nom', required=True, index=True)
    marque_id = fields.Many2one('parc.automobile.marque', string="Marque", required=True, ondelete='cascade')
    type_carrosserie = fields.Selection([
        ('berline', 'Berline'),
        ('suv', 'SUV'),
        ('4x4', '4x4'),
        ('break', 'Break'),
        ('coupe', 'Coupé'),
        ('cabriolet', 'Cabriolet'),
        ('utilitaire', 'Utilitaire'),
        ('camion', 'Camion'),
        ('moto', 'Moto')
    ], string='Type de carrosserie', required=True)
    
    motorisation = fields.Selection([
        ('essence', 'Essence'),
        ('diesel', 'Diesel'),
        ('hybride', 'Hybride'),
        ('electrique', 'Électrique'),
        ('gpl', 'GPL')
    ], string="Motorisation", required=True)
    
    consommation_constructeur = fields.Float(string='Consommation constructeur (L/100km)', digits=(4, 1))
    puissance = fields.Integer(string='Puissance (CV)')
    annee_sortie = fields.Integer(string="Année de sortie")
    nb_places = fields.Integer(string="Nombre de places", default=5)
    active = fields.Boolean(string="Actif", default=True)
    
    # Relations
    voiture_ids = fields.One2many('parc.automobile.voiture', 'modele_id', string="Véhicules")
    
    # Champs calculés
    nb_voitures = fields.Integer(string="Nombre de véhicules", compute="_compute_nb_voitures", store=True)
    nom_complet = fields.Char(string="Nom complet", compute="_compute_nom_complet", store=True)
    
    @api.depends('voiture_ids')
    def _compute_nb_voitures(self):
        for record in self:
            record.nb_voitures = len(record.voiture_ids)
    
    @api.depends('marque_id.name', 'name')
    def _compute_nom_complet(self):
        for record in self:
            if record.marque_id and record.name:
                record.nom_complet = f"{record.marque_id.name} {record.name}"
            else:
                record.nom_complet = record.name or ""