 # -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class DocumentAdministratif(models.Model):
    _name = 'parc.automobile.document'
    _description = "Documents administratifs des véhicules"
    _inherit = ['mail.thread']
    _order = 'date_expiration'
    
    name = fields.Char(string="Nom du document", required=True, tracking=True)
    vehicule_id = fields.Many2one('parc.automobile.voiture', string="Véhicule", required=True, 
                                 ondelete='cascade', tracking=True)
    
    type_document = fields.Selection([
        ('carte_grise', 'Carte grise'),
        ('assurance', 'Assurance'),
        ('controle_technique', 'Contrôle technique'),
        ('vignette', 'Vignette'),
        ('permis_circulation', 'Permis de circulation'),
        ('certificat_conformite', 'Certificat de conformité'),
        ('autre', 'Autre')
    ], string="Type de document", required=True, tracking=True)
    
    # Dates importantes
    date_delivrance = fields.Date(string="Date de délivrance", tracking=True)
    date_expiration = fields.Date(string="Date d'expiration", tracking=True)
    
    # Informations du document
    numero_document = fields.Char(string="Numéro de document", index=True)
    organisme_delivrant = fields.Char(string="Organisme délivrant")
    lieu_delivrance = fields.Char(string="Lieu de délivrance")
    
    # Fichier et gestion
    fichier = fields.Binary(string="Fichier")
    nom_fichier = fields.Char(string="Nom du fichier")
    rappel_avant_expiration = fields.Integer(string="Rappel (jours avant)", default=30)
    
    # Champs calculés
    est_expire = fields.Boolean(string="Expiré", compute="_compute_est_expire", store=True)
    jours_avant_expiration = fields.Integer(string="Jours avant expiration", 
                                           compute="_compute_jours_avant_expiration")
    statut_validite = fields.Selection([
        ('valide', 'Valide'),
        ('expire_bientot', 'Expire bientôt'),
        ('expire', 'Expiré')
    ], string="Statut", compute="_compute_statut_validite", store=True)
    
    # Informations complémentaires
    cout_document = fields.Float(string="Coût du document", digits=(10, 2))
    observations = fields.Text(string="Observations")
    active = fields.Boolean(string="Actif", default=True)
    
    @api.depends('date_expiration')
    def _compute_est_expire(self):
        today = fields.Date.today()
        for record in self:
            record.est_expire = record.date_expiration and record.date_expiration < today
    
    @api.depends('date_expiration')
    def _compute_jours_avant_expiration(self):
        today = fields.Date.today()
        for record in self:
            if record.date_expiration:
                delta = record.date_expiration - today
                record.jours_avant_expiration = delta.days
            else:
                record.jours_avant_expiration = 0
    
    @api.depends('date_expiration', 'rappel_avant_expiration')
    def _compute_statut_validite(self):
        today = fields.Date.today()
        for record in self:
            if not record.date_expiration:
                record.statut_validite = 'valide'
            elif record.date_expiration < today:
                record.statut_validite = 'expire'
            elif record.date_expiration <= today + timedelta(days=record.rappel_avant_expiration):
                record.statut_validite = 'expire_bientot'
            else:
                record.statut_validite = 'valide'
    
    @api.constrains('date_delivrance', 'date_expiration')
    def _check_dates(self):
        for record in self:
            if record.date_delivrance and record.date_expiration:
                if record.date_delivrance > record.date_expiration:
                    raise ValidationError(_("La date de délivrance ne peut pas être supérieure à la date d'expiration."))
