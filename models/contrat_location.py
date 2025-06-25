# -*- coding: utf-8 -*-
 
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ContratLocation(models.Model):
    _name = 'parc.automobile.contrat.location'
    _description = "Contrat de location de véhicule"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_debut desc'
    
    name = fields.Char(string="Numéro de contrat", required=True, copy=False, readonly=True, 
                       index=True, default=lambda self: _('Nouveau contrat'))
    
    # Parties du contrat
    client_id = fields.Many2one('parc.automobile.client', string="Client", required=True, 
                               ondelete='restrict', tracking=True)
    
    # Dates du contrat
    date_debut = fields.Date(string="Date de début", required=True, tracking=True)
    date_fin = fields.Date(string="Date de fin", required=True, tracking=True)
    date_signature = fields.Date(string="Date de signature", tracking=True)
    
    # Véhicules loués
    voiture_ids = fields.Many2many('parc.automobile.voiture', 
                                  'contrat_location_voiture_rel',
                                  'contrat_id', 'voiture_id',
                                  string="Véhicules loués", tracking=True)
    
    # Conditions financières
    montant_total = fields.Float(string="Montant total", digits=(10, 2), tracking=True)
    montant_journalier = fields.Float(string="Montant journalier", digits=(10, 2), tracking=True)
    caution = fields.Float(string="Caution", digits=(10, 2))
    caution_rendue = fields.Boolean(string="Caution rendue", default=False)
    
    # Conditions particulières
    kilometrage_limite = fields.Float(string="Kilométrage limite", digits=(10, 2))
    tarif_km_supplementaire = fields.Float(string="Tarif km supplémentaire", digits=(6, 3))
    carburant_inclus = fields.Boolean(string="Carburant inclus", default=False)
    assurance_incluse = fields.Boolean(string="Assurance incluse", default=True)
    
    # Statut et gestion
    statut = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('confirme', 'Confirmé'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
        ('suspendu', 'Suspendu')
    ], string="Statut", default='brouillon', required=True, tracking=True)
    
    # Champs calculés
    duree_jours = fields.Integer(string="Durée (jours)", compute="_compute_duree", store=True)
    montant_calcule = fields.Float(string="Montant calculé", compute="_compute_montant_calcule")
    nb_vehicules = fields.Integer(string="Nombre de véhicules", compute="_compute_nb_vehicules")
    
    # Documents et notes
    conditions_particulieres = fields.Text(string="Conditions particulières")
    notes = fields.Text(string="Notes")
    active = fields.Boolean(string="Actif", default=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau contrat')) == _('Nouveau contrat'):
            vals['name'] = self.env['ir.sequence'].next_by_code('parc.automobile.contrat.location') or _('Nouveau contrat')
        return super().create(vals)
    
    @api.depends('date_debut', 'date_fin')
    def _compute_duree(self):
        for record in self:
            if record.date_debut and record.date_fin:
                delta = record.date_fin - record.date_debut
                record.duree_jours = delta.days + 1
            else:
                record.duree_jours = 0
    
    @api.depends('montant_journalier', 'duree_jours')
    def _compute_montant_calcule(self):
        for record in self:
            record.montant_calcule = record.montant_journalier * record.duree_jours
    
    @api.depends('voiture_ids')
    def _compute_nb_vehicules(self):
        for record in self:
            record.nb_vehicules = len(record.voiture_ids)
    
    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for record in self:
            if record.date_debut and record.date_fin:
                if record.date_debut > record.date_fin:
                    raise ValidationError(_("La date de début ne peut pas être supérieure à la date de fin."))
    
    @api.constrains('voiture_ids', 'date_debut', 'date_fin')
    def _check_vehicules_disponibles(self):
        for record in self:
            if record.voiture_ids and record.date_debut and record.date_fin:
                for voiture in record.voiture_ids:
                    # Vérifier les conflits avec d'autres contrats
                    conflits = self.search([
                        ('id', '!=', record.id),
                        ('voiture_ids', 'in', voiture.id),
                        ('statut', 'in', ['confirme', 'en_cours']),
                        '|',
                        '&', ('date_debut', '<=', record.date_debut), ('date_fin', '>=', record.date_debut),
                        '&', ('date_debut', '<=', record.date_fin), ('date_fin', '>=', record.date_fin)
                    ])
                    if conflits:
                        raise ValidationError(_("Le véhicule %s est déjà loué sur cette période par le contrat %s") % 
                                            (voiture.name, conflits[0].name))
    
    def action_confirmer(self):
        """Confirmer le contrat"""
        self.write({'statut': 'confirme'})
    
    def action_demarrer(self):
        """Démarrer le contrat"""
        self.write({'statut': 'en_cours'})
    
    def action_terminer(self):
        """Terminer le contrat"""
        self.write({'statut': 'termine'})
    
    def action_annuler(self):
        """Annuler le contrat"""
        self.write({'statut': 'annule'})
