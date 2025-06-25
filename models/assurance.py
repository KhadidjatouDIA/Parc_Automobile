# -*- coding: utf-8 -*-
  
ffrom odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Assurance(models.Model):
    _name = 'parc.automobile.assurance'
    _description = "Police d'assurance automobile"
    _inherit = ['mail.thread']
    _order = 'date_fin desc'
    
    name = fields.Char(string="Référence police", required=True, tracking=True, index=True)
    compagnie_assurance = fields.Char(string="Compagnie d'assurance", required=True, tracking=True)
    
    type_assurance = fields.Selection([
        ('tiers', 'Au tiers'),
        ('intermediaire', 'Intermédiaire'),
        ('tout_risque', 'Tous risques')
    ], string="Type d'assurance", required=True, default='tiers', tracking=True)
    
    # Dates de validité
    date_debut = fields.Date(string="Date de début", required=True, tracking=True)
    date_fin = fields.Date(string="Date de fin", required=True, tracking=True)
    
    # Informations financières
    montant_annuel = fields.Float(string='Montant prime annuelle', digits=(10, 2), tracking=True)
    franchise = fields.Float(string='Franchise', digits=(10, 2))
    
    # Informations de contact
    numero_police = fields.Char(string="Numéro de police", required=True, index=True)
    agence = fields.Char(string="Agence")
    telephone_assurance = fields.Char(string="Téléphone assurance")
    email_assurance = fields.Char(string="Email assurance")
    adresse_agence = fields.Text(string="Adresse de l'agence")
    
    # Couvertures
    couverture_vol = fields.Boolean(string="Couverture vol", default=True)
    couverture_incendie = fields.Boolean(string="Couverture incendie", default=True)
    couverture_bris_glace = fields.Boolean(string="Couverture bris de glace")
    assistance_24h = fields.Boolean(string="Assistance 24h/24")
    
    # Relations
    voiture_ids = fields.One2many('parc.automobile.voiture', 'assurance_id', string='Véhicules assurés')
    
    # Champs calculés
    est_active = fields.Boolean(string="Active", compute="_compute_est_active", store=True)
    jours_avant_expiration = fields.Integer(string="Jours avant expiration", 
                                           compute="_compute_jours_avant_expiration")
    nb_vehicules = fields.Integer(string="Nombre de véhicules", compute="_compute_nb_vehicules")
    
    # Statut
    statut_police = fields.Selection([
        ('active', 'Active'),
        ('suspendue', 'Suspendue'),
        ('expiree', 'Expirée'),
        ('resiliee', 'Résiliée')
    ], string="Statut", compute="_compute_statut_police", store=True)
    
    active = fields.Boolean(string="Actif", default=True)
    notes = fields.Text(string="Notes")
    
    @api.depends('date_debut', 'date_fin')
    def _compute_est_active(self):
        today = fields.Date.today()
        for record in self:
            record.est_active = (record.date_debut <= today <= record.date_fin 
                               if record.date_debut and record.date_fin else False)
    
    @api.depends('date_fin')
    def _compute_jours_avant_expiration(self):
        today = fields.Date.today()
        for record in self:
            if record.date_fin:
                delta = record.date_fin - today
                record.jours_avant_expiration = delta.days
            else:
                record.jours_avant_expiration = 0
    
    @api.depends('voiture_ids')
    def _compute_nb_vehicules(self):
        for record in self:
            record.nb_vehicules = len(record.voiture_ids)
    
    @api.depends('date_debut', 'date_fin')
    def _compute_statut_police(self):
        today = fields.Date.today()
        for record in self:
            if not record.date_debut or not record.date_fin:
                record.statut_police = 'active'
            elif record.date_fin < today:
                record.statut_police = 'expiree'
            elif record.date_debut <= today <= record.date_fin:
                record.statut_police = 'active'
            else:
                record.statut_police = 'active'
    
    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for record in self:
            if record.date_debut and record.date_fin:
                if record.date_debut > record.date_fin:
                    raise ValidationError(_("La date de début ne peut pas être supérieure à la date de fin."))
