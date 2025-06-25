 # -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Entretien(models.Model):
    _name = 'parc.automobile.entretien'
    _description = "Entretien et réparation des véhicules"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_entretien desc'
    
    name = fields.Char(string="Référence", required=True, copy=False, readonly=True, 
                       index=True, default=lambda self: _('Nouvel entretien'))
    
    voiture_id = fields.Many2one('parc.automobile.voiture', string="Véhicule", required=True, 
                                ondelete='cascade', tracking=True)
    
    # Type et classification
    type_entretien = fields.Selection([
        ('vidange', 'Vidange'),
        ('revision', 'Révision'),
        ('reparation', 'Réparation'),
        ('controle_technique', 'Contrôle technique'),
        ('pneumatiques', 'Pneumatiques'),
        ('freinage', 'Freinage'),
        ('carrosserie', 'Carrosserie'),
        ('autre', 'Autre')
    ], string="Type d'entretien", required=True, default='vidange', tracking=True)
    
    # Dates
    date_entretien = fields.Date(string="Date d'entretien", required=True, 
                                default=fields.Date.today, tracking=True)
    date_prochain_entretien = fields.Date(string="Prochain entretien prévu")
    
    # Informations techniques
    kilometrage_entretien = fields.Float(string="Kilométrage à l'entretien", digits=(10, 2))
    description_entretien = fields.Text(string="Description des travaux", required=True)
    pieces_changees = fields.Text(string="Pièces changées")
    
    # Coûts
    cout = fields.Float(string='Coût total', digits=(10, 2), tracking=True)
    cout_main_oeuvre = fields.Float(string='Coût main d\'œuvre', digits=(10, 2))
    cout_pieces = fields.Float(string='Coût pièces', digits=(10, 2))
    
    # Prestataire
    garage = fields.Char(string="Garage/Atelier")
    responsable_entretien = fields.Char(string="Responsable de l'entretien")
    
    # Documents
    facture = fields.Binary(string="Facture")
    facture_filename = fields.Char(string="Nom de la facture")
    
    # Statut et suivi
    statut = fields.Selection([
        ('planifie', 'Planifié'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('reporte', 'Reporté'),
        ('annule', 'Annulé')
    ], string="Statut", default='planifie', required=True, tracking=True)
    
    # Champs calculés
    est_periodique = fields.Boolean(string="Entretien périodique", 
                                   compute="_compute_est_periodique", store=True)
    alerte_prochain = fields.Boolean(string="Alerte prochain entretien", 
                                    compute="_compute_alerte_prochain")
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouvel entretien')) == _('Nouvel entretien'):
            vals['name'] = self.env['ir.sequence'].next_by_code('parc.automobile.entretien') or _('Nouvel entretien')
        return super().create(vals)
    
    @api.depends('type_entretien')
    def _compute_est_periodique(self):
        types_periodiques = ['vidange', 'revision', 'controle_technique']
        for record in self:
            record.est_periodique = record.type_entretien in types_periodiques
    
    def _compute_alerte_prochain(self):
        from datetime import timedelta
        today = fields.Date.today()
        for record in self:
            if record.date_prochain_entretien:
                delta = record.date_prochain_entretien - today
                record.alerte_prochain = delta.days <= 30
            else:
                record.alerte_prochain = False
    
    @api.constrains('cout_main_oeuvre', 'cout_pieces', 'cout')
    def _check_cout_coherent(self):
        for record in self:
            if record.cout_main_oeuvre and record.cout_pieces:
                total_calcule = record.cout_main_oeuvre + record.cout_pieces
                if record.cout and abs(record.cout - total_calcule) > 0.01:
                    raise ValidationError(_("Le coût total ne correspond pas à la somme main d'œuvre + pièces"))

