# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Client(models.Model):
    _name = 'parc.automobile.client'
    _description = "Client pour location de véhicules"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    
    name = fields.Char(string='Nom et Prénom', required=True, tracking=True, index=True)
    
    # Informations personnelles
    type_client = fields.Selection([
        ('particulier', 'Particulier'),
        ('entreprise', 'Entreprise'),
        ('administration', 'Administration')
    ], string="Type de client", required=True, default='particulier', tracking=True)
    
    # Coordonnées
    adresse = fields.Text(string='Adresse')
    code_postal = fields.Char(string='Code postal')
    ville = fields.Char(string='Ville')
    pays_id = fields.Many2one('res.country', string='Pays')
    telephone = fields.Char(string='Téléphone', tracking=True)
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='E-mail', tracking=True)
    
    # Informations légales
    numero_identite = fields.Char(string="Numéro d'identité")
    numero_permis = fields.Char(string="Numéro de permis de conduire")
    date_naissance = fields.Date(string="Date de naissance")
    
    # Informations entreprise (si applicable)
    numero_siret = fields.Char(string="Numéro SIRET")
    numero_tva = fields.Char(string="Numéro TVA")
    
    # Relations
    contrat_location_ids = fields.One2many('parc.automobile.contrat.location', 'client_id', 
                                          string="Contrats de location")
    
    # Champs calculés
    nb_contrats = fields.Integer(string="Nombre de contrats", compute="_compute_nb_contrats")
    dernier_contrat_id = fields.Many2one('parc.automobile.contrat.location', 
                                        string="Dernier contrat", 
                                        compute="_compute_dernier_contrat")
    
    # Gestion
    active = fields.Boolean(string="Actif", default=True)
    notes = fields.Text(string="Notes")
    
    @api.depends('contrat_location_ids')
    def _compute_nb_contrats(self):
        for record in self:
            record.nb_contrats = len(record.contrat_location_ids)
    
    @api.depends('contrat_location_ids.date_debut')
    def _compute_dernier_contrat(self):
        for record in self:
            derniers_contrats = record.contrat_location_ids.sorted('date_debut', reverse=True)
            record.dernier_contrat_id = derniers_contrats[0] if derniers_contrats else False

