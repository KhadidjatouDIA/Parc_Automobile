# -*- coding: utf-8 -*-
  
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CarteGrise(models.Model):
    _name = 'parc.automobile.carte.grise'
    _description = "Carte grise (certificat d'immatriculation)"
    _inherit = ['mail.thread']
    _order = 'name'
    
    name = fields.Char(string="Numéro de carte grise", required=True, copy=False, 
                       readonly=True, index=True, default=lambda self: _('Nouvelle carte grise'))
    
    # Informations administratives
    date_delivrance = fields.Date(string="Date de délivrance", required=True, tracking=True)
    lieu_delivrance = fields.Char(string="Lieu de délivrance")
    date_expiration = fields.Date(string="Date d'expiration")
    
    # Propriétaire
    proprietaire = fields.Char(string="Propriétaire", required=True, tracking=True)
    adresse_proprietaire = fields.Text(string="Adresse du propriétaire")
    
    # Informations techniques du véhicule
    genre = fields.Char(string="Genre (VP, CTTE, etc.)")
    carrosserie = fields.Char(string="Carrosserie")
    couleur = fields.Char(string="Couleur")
    puissance_fiscale = fields.Integer(string="Puissance fiscale (CV)")
    puissance_reelle = fields.Integer(string="Puissance réelle (kW)")
    
    # Poids et dimensions
    poids_vide = fields.Integer(string="Poids à vide (kg)")
    ptac = fields.Integer(string="PTAC (kg)")
    nombre_places = fields.Integer(string="Nombre de places")
    
    # Relations
    voiture_ids = fields.One2many('parc.automobile.voiture', 'carte_grise_id', 
                                 string="Véhicules associés")
    
    # Champs calculés
    est_expiree = fields.Boolean(string="Expirée", compute="_compute_est_expiree", store=True)
    nb_vehicules = fields.Integer(string="Nombre de véhicules", compute="_compute_nb_vehicules")
    
    # Gestion
    active = fields.Boolean(string="Actif", default=True)
    observations = fields.Text(string="Observations")
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouvelle carte grise')) == _('Nouvelle carte grise'):
            vals['name'] = self.env['ir.sequence'].next_by_code('parc.automobile.carte.grise') or _('Nouvelle carte grise')
        return super().create(vals)
    
    @api.depends('date_expiration')
    def _compute_est_expiree(self):
        today = fields.Date.today()
        for record in self:
            record.est_expiree = record.date_expiration and record.date_expiration < today
    
    @api.depends('voiture_ids')
    def _compute_nb_vehicules(self):
        for record in self:
            record.nb_vehicules = len(record.voiture_ids)
    
    @api.constrains('date_delivrance', 'date_expiration')
    def _check_dates(self):
        for record in self:
            if record.date_delivrance and record.date_expiration:
                if record.date_delivrance > record.date_expiration:
                    raise ValidationError(_("La date de délivrance ne peut pas être supérieure à la date d'expiration."))
