# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Marque(models.Model):
    _name = 'parc.automobile.marque'
    _description = "Marque de véhicule"
    _order = 'name'
    
    name = fields.Char(string='Nom', required=True, index=True)
    pays_id = fields.Many2one('res.country', string="Pays d'origine")
    date_creation = fields.Date(string="Année de fondation")
    logo = fields.Binary(string="Logo")
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Actif", default=True)
    
    # Relations
    modele_ids = fields.One2many('parc.automobile.modele', 'marque_id', string='Modèles')
    
    # Champs calculés
    nb_modeles = fields.Integer(string="Nombre de modèles", compute="_compute_nb_modeles", store=True)
    nb_vehicules = fields.Integer(string="Nombre de véhicules", compute="_compute_nb_vehicules", store=True)
    
    @api.depends('modele_ids')
    def _compute_nb_modeles(self):
        for record in self:
            record.nb_modeles = len(record.modele_ids)
    
    @api.depends('modele_ids.voiture_ids')
    def _compute_nb_vehicules(self):
        for record in self:
            record.nb_vehicules = sum(len(modele.voiture_ids) for modele in record.modele_ids)