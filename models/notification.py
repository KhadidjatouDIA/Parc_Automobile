 # -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta

class NotificationVehicule(models.Model):
    _name = 'parc.automobile.notification'
    _description = "Notifications et alertes du parc automobile"
    _inherit = ['mail.thread']
    _order = 'date_creation desc'
    
    name = fields.Char(string="Titre", required=True, tracking=True)
    vehicule_id = fields.Many2one('parc.automobile.voiture', string="Véhicule", required=True, 
                                 ondelete='cascade', tracking=True)
    
    type_notification = fields.Selection([
        ('entretien', 'Entretien à venir'),
        ('document_expire', 'Document expiré'),
        ('document_expire_bientot', 'Document expire bientôt'),
        ('anomalie_carburant', 'Anomalie carburant'),
        ('kilometrage_eleve', 'Kilométrage élevé'),
        ('assurance_expire', 'Assurance expirée'),
        ('controle_technique', 'Contrôle technique à faire'),
        ('autre', 'Autre')
    ], string="Type de notification", required=True, tracking=True)
    
    # Dates
    date_creation = fields.Datetime(string="Date de création", default=fields.Datetime.now, 
                                   readonly=True)
    date_echeance = fields.Date(string="Date d'échéance")
    date_traitement = fields.Datetime(string="Date de traitement", readonly=True)
    
    # Classification
    priorite = fields.Selection([
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('critique', 'Critique')
    ], string="Priorité", required=True, default='normale', tracking=True)
    
    statut = fields.Selection([
        ('nouvelle', 'Nouvelle'),
        ('lue', 'Lue'),
        ('en_cours', 'En cours de traitement'),
        ('traitee', 'Traitée'),
        ('ignoree', 'Ignorée'),
        ('reportee', 'Reportée')
    ], string="Statut", default='nouvelle', required=True, tracking=True)
    
    # Contenu
    description = fields.Text(string="Description", required=True)
    action_recommandee = fields.Text(string="Action recommandée")
    
    # Responsabilités
    responsable_id = fields.Many2one('res.users', string="Responsable assigné")
    createur_id = fields.Many2one('res.users', string="Créé par", default=lambda self: self.env.user, 
                                 readonly=True)
    
    # Relations
    entretien_id = fields.Many2one('parc.automobile.entretien', string="Entretien lié")
    document_id = fields.Many2one('parc.automobile.document', string="Document lié")
    carburant_id = fields.Many2one('parc.automobile.carburant', string="Plein de carburant lié")
    
    # Champs calculés
    est_en_retard = fields.Boolean(string="En retard", compute="_compute_est_en_retard")
    jours_restants = fields.Integer(string="Jours restants", compute="_compute_jours_restants")
    
    @api.depends('date_echeance', 'statut')
    def _compute_est_en_retard(self):
        today = fields.Date.today()
        for record in self:
            record.est_en_retard = (record.date_echeance and 
                                   record.date_echeance < today and 
                                   record.statut not in ['traitee', 'ignoree'])
    
    @api.depends('date_echeance')
    def _compute_jours_restants(self):
        today = fields.Date.today()
        for record in self:
            if record.date_echeance:
                delta = record.date_echeance - today
                record.jours_restants = delta.days
            else:
                record.jours_restants = 0
    
    def action_marquer_lue(self):
        """Marquer la notification comme lue"""
        self.write({'statut': 'lue'})
    
    def action_marquer_traitee(self):
        """Marquer la notification comme traitée"""
        self.write({
            'statut': 'traitee',
            'date_traitement': fields.Datetime.now()
        })
    
    def action_assigner(self):
        """Ouvrir l'assistant d'assignation"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assigner la notification',
            'res_model': 'parc.automobile.notification.assign.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_notification_id': self.id}
        }